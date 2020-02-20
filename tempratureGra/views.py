from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect


# Create your views here.


def acc_login(req):
    error = {}
    if req.method == 'POST':
        email = req.POST.get('email')
        password = req.POST.get('password')
        user = authenticate(req, username=email, password=password)
        if user is not None:
            login(req, user)
            next_url = req.GET.get('next', '/')
            return redirect(next_url)
        else:
            error['error'] = '用户名或密码错误'
    return render(req, 'signin.html', {'errors': error})


def acc_logout(req):
    logout(req)
    return redirect('/user/')
