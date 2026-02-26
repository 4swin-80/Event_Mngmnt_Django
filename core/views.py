from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count
from django.utils import timezone
from .models import Event, Cue, Notification, Attendance, Booking
from .forms import EventForm, CueForm


# =========================
# CANCEL BOOKING
# =========================
@login_required
def cancel_booking(request, pk):
    if request.user.role != "customer":
        return redirect("login")

    booking = get_object_or_404(
        Booking,
        id=pk,
        customer=request.user   # 🔐 security check
    )

    booking.delete()

    return redirect("my_bookings")


# =========================
# CUSTOMER DASHBOARD
# =========================
@login_required
def customer_dashboard(request):
    if request.user.role != "customer":
        return redirect("login")

    events = Event.objects.filter(event_status="Scheduled")
    return render(request, "customer_dashboard.html", {
        "events": events
    })


# =========================
# BOOK EVENT
# =========================
@login_required
def book_event(request, pk):
    if request.user.role != "customer":
        return redirect("login")

    event = get_object_or_404(Event, id=pk)

    # Prevent duplicate booking
    if not Booking.objects.filter(customer=request.user, event=event).exists():
        Booking.objects.create(
            customer=request.user,
            event=event
        )

    return redirect("my_bookings")


# =========================
# MY BOOKINGS
# =========================
@login_required
def my_bookings(request):
    if request.user.role != "customer":
        return redirect("login")

    bookings = Booking.objects.filter(customer=request.user)
    return render(request, "my_bookings.html", {
        "bookings": bookings
    })


# =========================
# LOGIN
# =========================
def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == "admin":
            return redirect("admin_dashboard")
        elif request.user.role == "operator":
            return redirect("operator_dashboard")
        else:
            return redirect("customer_dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if request.user.role == "admin":
                return redirect("admin_dashboard")
            elif request.user.role == "operator":
                return redirect("operator_dashboard")
            else:
                return redirect("customer_dashboard")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


# =========================
# ADMIN DASHBOARD
# =========================
@login_required
def admin_dashboard(request):
    if request.user.role != "admin":
        return redirect("login")

    total_events = Event.objects.filter(admin=request.user).count()
    total_cues = Cue.objects.count()
    total_operators = Attendance.objects.values("operator").distinct().count()

    return render(request, "admin_dashboard.html", {
        "total_events": total_events,
        "total_cues": total_cues,
        "total_operators": total_operators,
    })


# =========================
# OPERATOR DASHBOARD
# =========================
@login_required
def operator_dashboard(request):
    if request.user.role != "operator":
        return redirect("login")

    cues = Cue.objects.filter(operator=request.user, cue_status="Pending")

    return render(request, "operator_dashboard.html", {
        "cues": cues
    })


# =========================
# EVENT CRUD
# =========================
@login_required
def event_list(request):
    if request.user.role != "admin":
        return redirect("login")

    events = Event.objects.filter(admin=request.user)
    return render(request, "event_list.html", {"events": events})


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


@login_required
def event_update(request, pk):
    event = get_object_or_404(Event, id=pk)

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


@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, id=pk)

    if request.user.role != "admin":
        return redirect("login")

    event.delete()
    return redirect("event_list")


# =========================
# CUE
# =========================
@login_required
def cue_list(request):
    if request.user.role != "admin":
        return redirect("login")

    cues = Cue.objects.all()
    return render(request, "cue_list.html", {"cues": cues})


@login_required
def cue_create(request):
    if request.user.role != "admin":
        return redirect("login")

    if request.method == "POST":
        form = CueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("cue_list")
    else:
        form = CueForm()

    return render(request, "cue_form.html", {"form": form})


# =========================
# NOTIFICATIONS
# =========================
@login_required
def notification_list(request):
    notifications = Notification.objects.all().order_by("-id")
    return render(request, "notification_list.html", {"notifications": notifications})


# =========================
# ATTENDANCE
# =========================
@login_required
def attendance_view(request):
    attendance = Attendance.objects.all()
    return render(request, "attendance.html", {"attendance": attendance})


# =========================
# PERFORMANCE
# =========================
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