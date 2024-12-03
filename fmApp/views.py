from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'home.html')


def user_login(request):
    if request.user.is_authenticated:
        messages.success(request, 'Ви вже увійшли до системи.')
        return redirect('')

    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('')
            else:
                messages.error(request, 'Неправильний логін чи пароль.')
    else:
        form = AuthenticationForm()

    context = {
        'form': form,
    }
    return render(request, 'login.html', context)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'registration.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
