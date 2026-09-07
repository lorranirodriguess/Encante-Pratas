from django import forms
from django.forms import inlineformset_factory
from .models import Pedido, ItemPedido


class PedidoForm(forms.ModelForm):
    """Usado na criação — sem 'cliente' (é sempre o usuário logado) e sem 'status' (nasce 'pendente')."""
    class Meta:
        model = Pedido
        fields = ['endereco_entrega']
        widgets = {
            'endereco_entrega': forms.TextInput(attrs={
                'placeholder': 'Deixe em branco para usar o endereço cadastrado do cliente'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['endereco_entrega'].required = False


class PedidoUpdateForm(forms.ModelForm):
    """Usado na edição — aqui sim status e cliente podem ser alterados (uso administrativo/staff)."""
    class Meta:
        model = Pedido
        fields = ['cliente', 'status', 'endereco_entrega']
        widgets = {
            'endereco_entrega': forms.TextInput(attrs={
                'placeholder': 'Deixe em branco para usar o endereço cadastrado do cliente'
            })
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['endereco_entrega'].required = False


class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['produto', 'quantidade']

    def clean(self):
        cleaned_data = super().clean()
        produto = cleaned_data.get('produto')
        quantidade = cleaned_data.get('quantidade')

        if produto and quantidade:
            if quantidade > produto.estoque:
                raise forms.ValidationError(
                    f'Estoque insuficiente para "{produto.nome}". '
                    f'Disponível: {produto.estoque} unidade(s).'
                )
        return cleaned_data


ItemPedidoFormSet = inlineformset_factory(
    Pedido, ItemPedido,
    form=ItemPedidoForm,
    extra=1, can_delete=True,
)