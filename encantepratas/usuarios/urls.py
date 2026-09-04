from django.urls import path
from . import views

urlpatterns = [
    path('', views.usuario_list, name='usuario_list'),
    path('<int:pk>/', views.usuario_detail, name='usuario_detail'),
    path('novo/', views.usuario_create, name='usuario_create'),
    path('<int:pk>/editar/', views.usuario_update, name='usuario_update'),
    path('<int:pk>/excluir/', views.usuario_delete, name='usuario_delete'),
]