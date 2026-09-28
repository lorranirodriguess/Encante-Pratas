from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.db.models import ProtectedError
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Usuario
from .forms import UsuarioForm, UsuarioUpdateForm

@login_required
@permission_required('usuarios.view_usuario', raise_exception=True)
def usuario_list(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/list.html', {'usuarios': usuarios})


@login_required
def usuario_detail(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.user.pk != usuario.pk and not request.user.has_perm('usuarios.view_usuario'):
        raise PermissionDenied
    return render(request, 'usuarios/detail.html', {'usuario': usuario})


def usuario_create(request):
    """Cadastro de novo cliente — sem @login_required, é o registro público."""
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('login')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/form.html', {'form': form, 'titulo': 'Novo Usuário'})


@login_required
def usuario_update(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.user.pk != usuario.pk and not request.user.has_perm('usuarios.change_usuario'):
        raise PermissionDenied
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
    if request.user.pk != usuario.pk and not request.user.has_perm('usuarios.delete_usuario'):
        raise PermissionDenied
    if request.method == 'POST':
        try:
            usuario.delete()
        except ProtectedError:
            messages.error(request, 'Este usuário possui pedidos e não pode ser excluído.')
            return redirect('usuario_detail', pk=pk)
        messages.success(request, 'Usuário removido.')
        return redirect('login' if request.user.pk == pk else 'usuario_list')
    return render(request, 'usuarios/confirm_delete.html', {'usuario': usuario})


def login_view(request):
    next_url = request.POST.get('next') if request.method == 'POST' else request.GET.get('next')
    if not next_url or not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse('produto_list')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'registration/login.html', {'next': next_url})


@require_POST
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('login')
