from django.db import models
from usuarios.models import Usuario
from produtos.models import Produto
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.db.models.signals import post_delete
from django.dispatch import receiver


PEDIDO_STATUS_CHOICES = [
    ('pendente', 'Pendente'),
    ('confirmado', 'Confirmado'),
    ('enviado', 'Enviado'),
    ('entregue', 'Entregue'),
    ('cancelado', 'Cancelado'),
]


class Pedido(models.Model):

    cliente = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, related_name='pedidos'
    )
    data_pedido = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PEDIDO_STATUS_CHOICES, default='pendente')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    endereco_entrega = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-data_pedido']
        permissions = [
            ('ver_proprios_pedidos', 'Pode ver os próprios pedidos'),
        ]

    def __str__(self):
        return f'Pedido #{self.pk} - {self.cliente}'

    def atualizar_valor_total(self):
        total = sum((item.subtotal for item in self.itens.all()), 0)
        self.valor_total = total
        self.save(update_fields=['valor_total'])


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name='itens'
    )
    produto = models.ForeignKey(
        Produto, on_delete=models.PROTECT, related_name='itens_pedido'
    )
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome}'

    def save(self, *args, **kwargs):
        if self.quantidade < 1:
            raise ValidationError('A quantidade deve ser maior que zero.')
        with transaction.atomic():
            previous = None
            if self.pk:
                previous = ItemPedido.objects.select_for_update().get(pk=self.pk)

            if previous is None or previous.produto_id != self.produto_id:
                self.preco_unitario = self.produto.preco
            elif self.preco_unitario is None:
                self.preco_unitario = previous.preco_unitario
            self.subtotal = self.preco_unitario * self.quantidade

            needed = self.quantidade
            if previous and previous.produto_id == self.produto_id:
                needed -= previous.quantidade
            if needed > 0:
                reserved = Produto.objects.filter(
                    pk=self.produto_id, estoque__gte=needed
                ).update(estoque=F('estoque') - needed)
                if not reserved:
                    raise ValidationError('Estoque insuficiente para este produto.')
            elif needed < 0:
                Produto.objects.filter(pk=self.produto_id).update(estoque=F('estoque') - needed)

            if previous and previous.produto_id != self.produto_id:
                Produto.objects.filter(pk=previous.produto_id).update(
                    estoque=F('estoque') + previous.quantidade
                )

            if kwargs.get('update_fields') is not None:
                kwargs['update_fields'] = set(kwargs['update_fields']) | {
                    'preco_unitario', 'subtotal'
                }
            super().save(*args, **kwargs)
            self.pedido.atualizar_valor_total()
            if previous and previous.pedido_id != self.pedido_id:
                Pedido.objects.get(pk=previous.pedido_id).atualizar_valor_total()


@receiver(post_delete, sender=ItemPedido)
def restore_stock_when_item_deleted(sender, instance, **kwargs):
    Produto.objects.filter(pk=instance.produto_id).update(
        estoque=F('estoque') + instance.quantidade
    )
    if Pedido.objects.filter(pk=instance.pedido_id).exists():
        Pedido.objects.get(pk=instance.pedido_id).atualizar_valor_total()
