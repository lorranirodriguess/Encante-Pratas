from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Usuario
from .forms import UsuarioForm, UsuarioUpdateForm

def usuario_list(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/list.html', {'usuarios': usuarios})

def usuario_detail(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, 'usuarios/detail.html', {'usuario': usuario})

def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('usuario_list')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/form.html', {'form': form, 'titulo': 'Novo Usuário'})

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

def usuario_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuário removido.')
        return redirect('usuario_list')
    return render(request, 'usuarios/confirm_delete.html', {'usuario': usuario})