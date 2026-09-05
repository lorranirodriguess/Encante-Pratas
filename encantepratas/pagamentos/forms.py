from django import forms
from .models import Pagamento


class PagamentoForm(forms.ModelForm):
    """Usado na criação — sem valor (puxa do pedido) e sem status (nasce 'pendente')."""
    class Meta:
        model = Pagamento
        fields = ['pedido', 'forma_pagamento']

    def clean_pedido(self):
        pedido = self.cleaned_data['pedido']
        if hasattr(pedido, 'pagamento'):
            raise forms.ValidationError('Este pedido já possui um pagamento registrado.')
        return pedido


class PagamentoUpdateForm(forms.ModelForm):
    """Usado na edição — dá pra mudar status (ex: aprovar/estornar) e forma de pagamento."""
    class Meta:
        model = Pagamento
        fields = ['forma_pagamento', 'status']