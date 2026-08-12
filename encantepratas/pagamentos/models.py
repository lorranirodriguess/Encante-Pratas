from django.db import models
from pedidos.models import Pedido


class Pagamento(models.Model):
    FORMA_CHOICES = [
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'Pix'),
        ('boleto', 'Boleto'),
    ]
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
        ('estornado', 'Estornado'),
    ]

    pedido = models.OneToOneField(
        Pedido, on_delete=models.CASCADE, related_name='pagamento'
    )
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_pagamento = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'

    def __str__(self):
        return f'Pagamento #{self.pk} - {self.pedido}'
