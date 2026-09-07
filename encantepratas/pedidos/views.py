from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.db import transaction

from .models import Pedido
from .forms import PedidoForm, PedidoUpdateForm, ItemPedidoFormSet


def _endereco_do_cliente(cliente):
    return f'{cliente.rua}, {cliente.numero_casa} - {cliente.bairro}, {cliente.cidade}/{cliente.estado} - CEP {cliente.cep}'


@login_required
def pedido_list(request):
    if request.user.has_perm('pedidos.view_pedido'):
        pedidos = Pedido.objects.select_related('cliente').all()
    else:
        pedidos = Pedido.objects.filter(cliente=request.user.usuario)
    return render(request, 'pedidos/list.html', {'pedidos': pedidos})


@login_required
def pedido_detail(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if pedido.cliente != request.user.usuario and not request.user.has_perm('pedidos.view_pedido'):
        raise PermissionDenied
    return render(request, 'pedidos/detail.html', {'pedido': pedido})


@login_required
def pedido_create(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        formset = ItemPedidoFormSet(request.POST, instance=Pedido())

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                pedido = form.save(commit=False)
                pedido.cliente = request.user.usuario
                if not pedido.endereco_entrega:
                    pedido.endereco_entrega = _endereco_do_cliente(pedido.cliente)
                pedido.save()

                formset.instance = pedido
                formset.save()
                pedido.atualizar_valor_total()

            messages.success(request, 'Pedido criado com sucesso!')
            return redirect('pedido_detail', pk=pedido.pk)
    else:
        form = PedidoForm()
        formset = ItemPedidoFormSet()
    return render(request, 'pedidos/form.html', {'form': form, 'formset': formset, 'titulo': 'Novo Pedido'})


@permission_required('pedidos.change_pedido', raise_exception=True)
def pedido_update(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        form = PedidoUpdateForm(request.POST, instance=pedido)
        formset = ItemPedidoFormSet(request.POST, instance=pedido)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                pedido = form.save(commit=False)
                if not pedido.endereco_entrega:
                    pedido.endereco_entrega = _endereco_do_cliente(pedido.cliente)
                pedido.save()
                formset.save()
                pedido.atualizar_valor_total()

            messages.success(request, 'Pedido atualizado!')
            return redirect('pedido_detail', pk=pk)
    else:
        form = PedidoUpdateForm(instance=pedido)
        formset = ItemPedidoFormSet(instance=pedido)
    return render(request, 'pedidos/form.html', {'form': form, 'formset': formset, 'titulo': 'Editar Pedido'})


@permission_required('pedidos.delete_pedido', raise_exception=True)
def pedido_delete(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        pedido.delete()
        messages.success(request, 'Pedido removido.')
        return redirect('pedido_list')
    return render(request, 'pedidos/confirm_delete.html', {'pedido': pedido})