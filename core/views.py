from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect_dashboard(request.user)

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect_dashboard(user)
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


def redirect_dashboard(user):
    if user.role == "admin":
        return redirect("admin_dashboard")
    elif user.role == "operator":
        return redirect("operator_dashboard")
    return redirect("login")


@login_required
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")


@login_required
def operator_dashboard(request):
    return render(request, "operator_dashboard.html")