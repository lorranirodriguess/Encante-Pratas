from django.db import models
from django.contrib.auth.models import User

class Usuario(User):
    cpf = models.CharField(max_length=11, unique=True)
    telefone = models.CharField(max_length=20)
    cep = models.CharField(max_length=9)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    rua = models.CharField(max_length=200)
    numero_casa = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.user.get_full_name() or self.user.username
