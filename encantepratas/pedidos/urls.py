from django.urls import path
from . import views

urlpatterns = [
    path('', views.pedido_list, name='pedido_list'),
    path('<int:pk>/', views.pedido_detail, name='pedido_detail'),
    path('novo/', views.pedido_create, name='pedido_create'),
    path('<int:pk>/editar/', views.pedido_update, name='pedido_update'),
    path('<int:pk>/excluir/', views.pedido_delete, name='pedido_delete'),
    path('carrinho/', views.carrinho_view, name='carrinho_view'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/comprar-agora/<int:produto_id>/', views.comprar_agora, name='comprar_agora'),
    path('carrinho/remover/<int:produto_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('carrinho/finalizar/', views.finalizar_compra, name='finalizar_compra'),
]
