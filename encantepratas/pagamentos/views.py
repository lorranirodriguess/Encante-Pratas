from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Pagamento
from .forms import PagamentoForm, PagamentoUpdateForm

def pagamento_list(request):
    pagamentos = Pagamento.objects.select_related('pedido').all()
    return render(request, 'pagamentos/list.html', {'pagamentos': pagamentos})

def pagamento_detail(request, pk):
    pagamento = get_object_or_404(Pagamento, pk=pk)
    return render(request, 'pagamentos/detail.html', {'pagamento': pagamento})

@login_required
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

@login_required
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

@login_required
def pagamento_delete(request, pk):
    pagamento = get_object_or_404(Pagamento, pk=pk)
    if request.method == 'POST':
        pagamento.delete()
        messages.success(request, 'Pagamento removido.')
        return redirect('pagamento_list')
    return render(request, 'pagamentos/confirm_delete.html', {'pagamento': pagamento})