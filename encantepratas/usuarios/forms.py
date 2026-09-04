from django import forms
from django.contrib.auth.models import User
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Usuário (login)')
    password = forms.CharField(widget=forms.PasswordInput, label='Senha')
    email = forms.EmailField(required=False)

    class Meta:
        model = Usuario
        fields = ['cpf', 'telefone', 'cep', 'bairro', 'cidade', 'estado', 'rua', 'numero_casa']

    def save(self, commit=True):
        usuario = super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data.get('email', ''),
        )
        usuario.user = user
        if commit:
            usuario.save()
        return usuario


class UsuarioUpdateForm(forms.ModelForm):
    """Edição não mexe em username/senha, só nos dados de perfil."""
    class Meta:
        model = Usuario
        fields = ['cpf', 'telefone', 'cep', 'bairro', 'cidade', 'estado', 'rua', 'numero_casa']