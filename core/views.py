from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, EventForm, CueForm
from .models import Event, Cue
from django.db.models import Count


@login_required
def performance_dashboard(request):
    if request.user.role != "admin":
        return redirect("login")

    data = (
        Cue.objects
        .values("operator__username")
        .annotate(total_tasks=Count("id"))
    )

    return render(request, "performance.html", {"data": data})


@login_required
def cue_create(request):
    if request.user.role != "admin":
        return redirect("login")

    if request.method == "POST":
        form = CueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("event_list")
    else:
        form = CueForm()

    return render(request, "cue_form.html", {"form": form})


# =========================
# EVENT LIST
# =========================
@login_required
def event_list(request):
    if request.user.role != "admin":
        return redirect("login")

    events = Event.objects.filter(admin=request.user)
    return render(request, "event_list.html", {"events": events})


# =========================
# CREATE EVENT
# =========================
@login_required
def event_create(request):
    if request.user.role != "admin":
        return redirect("login")

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.admin = request.user
            event.save()
            return redirect("event_list")
    else:
        form = EventForm()

    return render(request, "event_form.html", {"form": form})


# =========================
# UPDATE EVENT
# =========================
@login_required
def event_update(request, pk):
    event = Event.objects.get(id=pk)

    if request.user.role != "admin":
        return redirect("login")

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect("event_list")
    else:
        form = EventForm(instance=event)

    return render(request, "event_form.html", {"form": form})


# =========================
# DELETE EVENT
# =========================
@login_required
def event_delete(request, pk):
    event = Event.objects.get(id=pk)

    if request.user.role != "admin":
        return redirect("login")

    event.delete()
    return redirect("event_list")


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