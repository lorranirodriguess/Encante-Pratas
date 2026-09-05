from django.db import models
from usuarios.models import Usuario
from produtos.models import Produto


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, related_name='pedidos'
    )
    data_pedido = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    endereco_entrega = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-data_pedido']

    def __str__(self):
        return f'Pedido #{self.pk} - {self.cliente}'

    def atualizar_valor_total(self):
        total = sum(item.subtotal for item in self.itens.all())
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
        is_novo = self.pk is None
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco
        self.subtotal = self.preco_unitario * self.quantidade
        super().save(*args, **kwargs)

        if is_novo:
            self.produto.estoque -= self.quantidade
            self.produto.save(update_fields=['estoque'])

        self.pedido.atualizar_valor_total()

    def delete(self, *args, **kwargs):
        pedido = self.pedido
        produto = self.produto
        quantidade = self.quantidade
        super().delete(*args, **kwargs)
        produto.estoque += quantidade
        produto.save(update_fields=['estoque'])
        pedido.atualizar_valor_total()