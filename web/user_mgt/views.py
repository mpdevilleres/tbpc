from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import LoginForm, ChangePasswordForm
# Create your views here.

def _login(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('main:index')
            else:
                messages.warning(request, 'User is Inactive, Please Contact the Administrator')
        else:
            messages.warning(request, 'Invalid Username or Password')
    context = {
        "form" : form
    }
    return render(request, 'user_mgt/login.html', context)

@login_required
def _logout(request):
    logout(request)
    messages.warning(request, 'Logout Successful')
    return redirect('user_mgt:login')

@login_required
def _change_password(request):
    form = ChangePasswordForm(request.POST or None, user=request.user)

    if form.is_valid():
        old = form.cleaned_data.get('old_password')
        new = form.cleaned_data.get('new_password')

        if old == new:
            user = User.objects.get(id=request.user.id)
            user.set_password(new)
            user.save()
            messages.info(request, "Password Change Successful")
    context = {
        'forms': form
    }
    return render(request, 'user_mgt/change_password.html', context=context)
