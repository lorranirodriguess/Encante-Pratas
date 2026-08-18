from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['cpf', 'telefone', 'cidade', 'estado']
    search_fields = ['cpf', 'user__username']