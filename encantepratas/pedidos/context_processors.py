def carrinho_context(request):
    if request.user.is_authenticated:
        carrinho = request.session.get('carrinho', {})
        return {'carrinho_qtd': sum(carrinho.values())}
    return {'carrinho_qtd': 0}