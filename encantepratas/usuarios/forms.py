from django import forms
from django.contrib.auth.models import Group
from .models import Usuario


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Senha')

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'cpf', 'telefone', 'cep', 'bairro', 'cidade', 'estado', 'rua', 'numero_casa']

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
            grupo_clientes, _ = Group.objects.get_or_create(name='Clientes')
            usuario.groups.add(grupo_clientes)
        return usuario


class UsuarioUpdateForm(forms.ModelForm):
    """Edição não mexe em username/senha, só nos dados de perfil."""
    class Meta:
        model = Usuario
        fields = ['cpf', 'telefone', 'cep', 'bairro', 'cidade', 'estado', 'rua', 'numero_casa']