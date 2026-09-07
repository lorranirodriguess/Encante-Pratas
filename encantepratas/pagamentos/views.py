from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied

from .models import Pagamento
from .forms import PagamentoForm, PagamentoUpdateForm


@login_required
def pagamento_list(request):
    if request.user.has_perm('pagamentos.view_pagamento'):
        pagamentos = Pagamento.objects.select_related('pedido').all()
    else:
        pagamentos = Pagamento.objects.filter(pedido__cliente=request.user)
    return render(request, 'pagamentos/list.html', {'pagamentos': pagamentos})


@login_required
def pagamento_detail(request, pk):
    pagamento = get_object_or_404(Pagamento, pk=pk)
    if pagamento.pedido.cliente != request.user and not request.user.has_perm('pagamentos.view_pagamento'):
        raise PermissionDenied
    return render(request, 'pagamentos/detail.html', {'pagamento': pagamento})


@permission_required('pagamentos.add_pagamento', raise_exception=True)
def pagamento_create(request):
    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            pagamento = form.save(commit=False)
            pagamento.valor = pagamento.pedido.valor_total
            pagamento.save()
            messages.success(request, 'Pagamento registrado com sucesso!')
            return redirect('pagamento_list')
    else:
        form = PagamentoForm()
    return render(request, 'pagamentos/form.html', {'form': form, 'titulo': 'Novo Pagamento'})


@permission_required('pagamentos.change_pagamento', raise_exception=True)
def pagamento_update(request, pk):
    pagamento = get_object_or_404(Pagamento, pk=pk)
    if request.method == 'POST':
        form = PagamentoUpdateForm(request.POST, instance=pagamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pagamento atualizado!')
            return redirect('pagamento_detail', pk=pk)
    else:
        form = PagamentoUpdateForm(instance=pagamento)
    return render(request, 'pagamentos/form.html', {'form': form, 'titulo': 'Editar Pagamento'})


@permission_required('pagamentos.delete_pagamento', raise_exception=True)
def pagamento_delete(request, pk):
    pagamento = get_object_or_404(Pagamento, pk=pk)
    if request.method == 'POST':
        pagamento.delete()
        messages.success(request, 'Pagamento removido.')
        return redirect('pagamento_list')
    return render(request, 'pagamentos/confirm_delete.html', {'pagamento': pagamento})