from django.urls import path
from . import views

urlpatterns = [
    path('', views.produto_list, name='produto_list'),
    path('<int:pk>/', views.produto_detail, name='produto_detail'),
    path('novo/', views.produto_create, name='produto_create'),
    path('<int:pk>/editar/', views.produto_update, name='produto_update'),
    path('<int:pk>/excluir/', views.produto_delete, name='produto_delete'),
]