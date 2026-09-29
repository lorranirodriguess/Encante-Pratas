from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.core.exceptions import ValidationError
from usuarios.models import Usuario
from .models import Pedido, ItemPedido
from .forms import PedidoForm, PedidoUpdateForm, ItemPedidoFormSet
from django.views.decorators.http import require_POST
from produtos.models import Produto
from usuarios.models import Usuario
from pagamentos.models import Pagamento


def _endereco_do_cliente(cliente):
    return f'{cliente.rua}, {cliente.numero_casa} - {cliente.bairro}, {cliente.cidade}/{cliente.estado} - CEP {cliente.cep}'


@login_required
@permission_required('pedidos.ver_proprios_pedidos', raise_exception=True)
def pedido_list(request):
    if request.user.has_perm('pedidos.view_pedido'):
        pedidos = Pedido.objects.select_related('cliente').all()
    else:
        pedidos = Pedido.objects.filter(cliente_id=request.user.pk)
    return render(request, 'pedidos/list.html', {'pedidos': pedidos})


@login_required
@permission_required('pedidos.ver_proprios_pedidos', raise_exception=True)
def pedido_detail(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if pedido.cliente_id != request.user.pk and not request.user.has_perm('pedidos.view_pedido'):
        raise PermissionDenied
    return render(request, 'pedidos/detail.html', {'pedido': pedido})


@login_required
@permission_required('pedidos.add_pedido', raise_exception=True)
def pedido_create(request):
    cliente = Usuario.objects.filter(pk=request.user.pk).first()
    if cliente is None:
        messages.error(request, 'É necessário ter um cadastro de cliente para criar um pedido.')
        return redirect('pedido_list')
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        formset = ItemPedidoFormSet(request.POST, instance=Pedido())

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    pedido = form.save(commit=False)
                    pedido.cliente = cliente
                    if not pedido.endereco_entrega:
                        pedido.endereco_entrega = _endereco_do_cliente(cliente)
                    pedido.save()
                    formset.instance = pedido
                    formset.save()
            except ValidationError as error:
                formset._non_form_errors = formset.error_class(error.messages)
            else:
                messages.success(request, 'Pedido criado com sucesso!')
                return redirect('pedido_detail', pk=pedido.pk)
    else:
        form = PedidoForm()
        formset = ItemPedidoFormSet()
    return render(request, 'pedidos/form.html', {'form': form, 'formset': formset, 'titulo': 'Novo Pedido'})

@login_required
@permission_required('pedidos.change_pedido', raise_exception=True)
def pedido_update(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        form = PedidoUpdateForm(request.POST, instance=pedido)
        formset = ItemPedidoFormSet(request.POST, instance=pedido)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    pedido = form.save(commit=False)
                    if not pedido.endereco_entrega:
                        pedido.endereco_entrega = _endereco_do_cliente(pedido.cliente)
                    pedido.save()
                    formset.save()
            except ValidationError as error:
                formset._non_form_errors = formset.error_class(error.messages)
            else:
                messages.success(request, 'Pedido atualizado!')
                return redirect('pedido_detail', pk=pk)
    else:
        form = PedidoUpdateForm(instance=pedido)
        formset = ItemPedidoFormSet(instance=pedido)
    return render(request, 'pedidos/form.html', {'form': form, 'formset': formset, 'titulo': 'Editar Pedido'})

@login_required
@permission_required('pedidos.delete_pedido', raise_exception=True)
def pedido_delete(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        pedido.delete()
        messages.success(request, 'Pedido removido.')
        return redirect('pedido_list')
    return render(request, 'pedidos/confirm_delete.html', {'pedido': pedido})

#carrinho

def _get_carrinho(request):
    return request.session.get('carrinho', {})


def _salvar_carrinho(request, carrinho):
    request.session['carrinho'] = carrinho
    request.session.modified = True


@login_required
def carrinho_view(request):
    carrinho = _get_carrinho(request)
    itens = []
    total = 0
    for produto_id, quantidade in carrinho.items():
        produto = Produto.objects.filter(pk=produto_id, ativo=True).first()
        if not produto:
            continue
        subtotal = produto.preco * quantidade
        total += subtotal
        itens.append({'produto': produto, 'quantidade': quantidade, 'subtotal': subtotal})
    return render(request, 'pedidos/carrinho.html', {'itens': itens, 'total': total})


@login_required
@require_POST
def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id, ativo=True)
    quantidade = int(request.POST.get('quantidade', 1))
    carrinho = _get_carrinho(request)
    chave = str(produto_id)
    carrinho[chave] = carrinho.get(chave, 0) + quantidade
    _salvar_carrinho(request, carrinho)
    messages.success(request, f'"{produto.nome}" adicionado ao carrinho.')
    return redirect('carrinho_view')


@login_required
@require_POST
def comprar_agora(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id, ativo=True)
    quantidade = int(request.POST.get('quantidade', 1))
    carrinho = _get_carrinho(request)
    chave = str(produto_id)
    carrinho[chave] = carrinho.get(chave, 0) + quantidade
    _salvar_carrinho(request, carrinho)
    return redirect('finalizar_compra')


@login_required
@require_POST
def remover_do_carrinho(request, produto_id):
    carrinho = _get_carrinho(request)
    carrinho.pop(str(produto_id), None)
    _salvar_carrinho(request, carrinho)
    messages.success(request, 'Item removido do carrinho.')
    return redirect('carrinho_view')


@login_required
@permission_required('pedidos.add_pedido', raise_exception=True)
@permission_required('pagamentos.add_pagamento', raise_exception=True)
def finalizar_compra(request):
    carrinho = _get_carrinho(request)
    if not carrinho:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('produto_list')

    cliente = Usuario.objects.filter(pk=request.user.pk).first()
    itens_info = []
    total = 0
    erro_estoque = None
    for produto_id, quantidade in carrinho.items():
        produto = Produto.objects.filter(pk=produto_id, ativo=True).first()
        if not produto:
            continue
        if quantidade > produto.estoque:
            erro_estoque = f'Estoque insuficiente para "{produto.nome}". Disponível: {produto.estoque}.'
        subtotal = produto.preco * quantidade
        total += subtotal
        itens_info.append({'produto': produto, 'quantidade': quantidade, 'subtotal': subtotal})

    endereco_padrao = _endereco_do_cliente(cliente) if cliente else ''

    if request.method == 'POST':
        if erro_estoque:
            messages.error(request, erro_estoque)
            return redirect('carrinho_view')

        endereco = request.POST.get('endereco_entrega') or endereco_padrao
        forma_pagamento = request.POST.get('forma_pagamento', 'pix')

        with transaction.atomic():
            pedido = Pedido.objects.create(cliente=cliente, endereco_entrega=endereco)
            for info in itens_info:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=info['produto'],
                    quantidade=info['quantidade'],
                )
            pedido.atualizar_valor_total()
            pagamento = Pagamento.objects.create(
                pedido=pedido, forma_pagamento=forma_pagamento, valor=pedido.valor_total
            )

        _salvar_carrinho(request, {})
        messages.success(request, 'Pedido realizado! Agora é só confirmar o pagamento.')
        return redirect('pagamento_confirmar', pk=pagamento.pk)

    return render(request, 'pedidos/checkout.html', {
        'itens': itens_info, 'total': total,
        'endereco_padrao': endereco_padrao, 'erro_estoque': erro_estoque,
    })