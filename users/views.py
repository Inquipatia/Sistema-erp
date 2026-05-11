from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')

    return render(request, 'users/login.html', {'form': form})


@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'core/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')
