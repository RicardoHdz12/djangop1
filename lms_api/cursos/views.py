from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Usuario registrado correctamente')
            return redirect('login')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


def iniciar_sesion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('perfil')
        else:
            messages.error(request, 'Credenciales incorrectas')
    
    return render(request, 'usuarios/login.html')

@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html')

def cerrar_sesion(request):
    logout(request)
    return redirect('login')

