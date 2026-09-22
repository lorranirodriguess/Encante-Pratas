from django import forms
from .models import Produto

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['categoria', 'imagem', 'nome', 'descricao', 'preco', 'material', 'estoque', 'ativo']

    def clean_preco(self):
        preco = self.cleaned_data['preco']
        if preco <= 0:
            raise forms.ValidationError('O preço deve ser maior que zero.')
        return preco