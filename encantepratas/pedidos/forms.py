from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['endereco_entrega'].required = False


class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['produto', 'quantidade']

class BaseItemPedidoFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        quantities = {}
        products = {}
        for form in self.forms:
            data = form.cleaned_data
            if not data or data.get('DELETE'):
                continue
            product = data.get('produto')
            quantity = data.get('quantidade')
            if product is None or quantity is None:
                continue
            if not product.ativo or quantity < 1:
                raise forms.ValidationError('Selecione produtos ativos e quantidades maiores que zero.')
            if product.pk in quantities:
                raise forms.ValidationError(
                    f'O produto "{product.nome}" foi incluído mais de uma vez no pedido.'
                )
            quantities[product.pk] = quantities.get(product.pk, 0) + quantity
            products[product.pk] = product

        if not quantities:
            raise forms.ValidationError('Adicione pelo menos um item ao pedido.')

        existing = {}
        if self.instance.pk:
            for item in self.instance.itens.all():
                existing[item.produto_id] = existing.get(item.produto_id, 0) + item.quantidade
        for product_id, quantity in quantities.items():
            product = products[product_id]
            available = product.estoque + existing.get(product_id, 0)
            if quantity > available:
                raise forms.ValidationError(
                    f'Estoque insuficiente para "{product.nome}". Disponível: {available} unidade(s).'
                )

    def save_existing_objects(self, commit=True):
        if not commit:
            return super().save_existing_objects(commit=False)
        self.changed_objects = []
        self.deleted_objects = []
        releases = []
        reservations = []
        for form in self.initial_forms:
            obj = form.instance
            if not obj._is_pk_set():
                continue
            if form in self.deleted_forms:
                self.deleted_objects.append(obj)
                self.delete_existing(obj, commit=True)
            elif form.has_changed():
                previous = ItemPedido.objects.get(pk=obj.pk)
                product = form.cleaned_data['produto']
                quantity = form.cleaned_data['quantidade']
                if product.pk == previous.produto_id and quantity < previous.quantidade:
                    releases.append(form)
                else:
                    reservations.append(form)

        saved = []
        for form in releases + reservations:
            obj = form.instance
            self.changed_objects.append((obj, form.changed_data))
            saved.append(self.save_existing(form, obj, commit=True))
        return saved


ItemPedidoFormSet = inlineformset_factory(
    Pedido, ItemPedido,
    form=ItemPedidoForm, formset=BaseItemPedidoFormSet,
    extra=1, can_delete=True,
)
