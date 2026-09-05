from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

from .models import Usuario
from .forms import UsuarioForm, UsuarioUpdateForm


def usuario_list(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/list.html', {'usuarios': usuarios})


def usuario_detail(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, 'usuarios/detail.html', {'usuario': usuario})


def usuario_create(request):
    """Cadastro de novo cliente — sem @login_required, é o registro público."""
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('usuario_list')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/form.html', {'form': form, 'titulo': 'Novo Usuário'})


@login_required
def usuario_update(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados atualizados!')
            return redirect('usuario_detail', pk=pk)
    else:
        form = UsuarioUpdateForm(instance=usuario)
    return render(request, 'usuarios/form.html', {'form': form, 'titulo': 'Editar Usuário'})


@login_required
def usuario_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuário removido.')
        return redirect('usuario_list')
    return render(request, 'usuarios/confirm_delete.html', {'usuario': usuario})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or 'produto_list'

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    next_url = request.GET.get('next', '')
    return render(request, 'registration/login.html', {'next': next_url})


def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('login')