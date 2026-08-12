from django.db import models
from categorias.models import Categoria


class Produto(models.Model):
    MATERIAL_CHOICES = [
        ('prata_925', 'Prata 925'),
        ('prata_950', 'Prata 950'),
        ('prata_banhada_ouro', 'Prata banhada a ouro'),
        ('prata_oxidada', 'Prata oxidada'),
    ]

    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name='produtos'
    )
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    material = models.CharField(max_length=30, choices=MATERIAL_CHOICES, default='prata_925')
    estoque = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    def __str__(self):
        return self.nome
