from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import ProtectedError
from django.http import Http404
from .models import Produto
from .forms import ProdutoForm

def produto_list(request):
    produtos = Produto.objects.select_related('categoria').all()
    if not request.user.has_perm('produtos.change_produto'):
        produtos = produtos.filter(ativo=True)
    query = request.GET.get('q', '').strip()
    if query:
        produtos = produtos.filter(nome__icontains=query)
    return render(request, 'produtos/list.html', {'produtos': produtos, 'query': query})

def produto_detail(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if not produto.ativo and not request.user.has_perm('produtos.change_produto'):
        raise Http404('Produto indisponível.')
    relacionados = Produto.objects.filter(
        ativo=True, categoria=produto.categoria
    ).exclude(pk=produto.pk)[:4]
    return render(request, 'html-template/product.html', {
        'produto': produto,
        'relacionados': relacionados,
    })

@permission_required('produtos.add_produto', raise_exception=True)
def produto_create(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto criado com sucesso!')
            return redirect('produto_list')
    else:
        form = ProdutoForm()
    return render(request, 'produtos/form.html', {'form': form, 'titulo': 'Novo Produto'})

@permission_required('produtos.change_produto', raise_exception=True)
def produto_update(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado!')
            return redirect('produto_detail', pk=pk)
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'produtos/form.html', {'form': form, 'titulo': 'Editar Produto'})

@permission_required('produtos.delete_produto', raise_exception=True)
def produto_delete(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        try:
            produto.delete()
        except ProtectedError:
            messages.error(request, 'Este produto está em pedidos e não pode ser excluído.')
            return redirect('produto_detail', pk=pk)
        messages.success(request, 'Produto removido.')
        return redirect('produto_list')
    return render(request, 'produtos/confirm_delete.html', {'produto': produto})
