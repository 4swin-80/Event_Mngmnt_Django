from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Avg
from django import forms
from django.contrib import messages
from django.utils import timezone
from .models import Event, Cue, Notification, Attendance, Booking, Rating, Complaint
from .forms import EventForm, CueForm, RatingForm, ComplaintForm, AdminReplyForm, BookingForm



@login_required
def booking_detail(request, pk):
    if request.user.role != "admin":
        return redirect("login")

    booking = get_object_or_404(
        Booking,
        id=pk,
        event__admin=request.user
    )

    return render(request, "booking_detail.html", {
        "booking": booking
    })


# =========================
# DELETE RATING
# =========================
@login_required
def delete_rating(request, pk):
    if request.user.role != "customer":
        return redirect("login")

    rating = get_object_or_404(
        Rating,
        id=pk,
        customer=request.user   # 🔐 Security: only own rating
    )

    event_id = rating.event.id
    rating.delete()

    return redirect("view_event", pk=event_id)



@login_required
def reply_complaint(request, pk):
    if request.user.role != "admin":
        return redirect("login")

    complaint = get_object_or_404(Complaint, id=pk)

    if request.method == "POST":
        form = AdminReplyForm(request.POST, instance=complaint)
        if form.is_valid():
            obj = form.save(commit=False)

            # 🔥 Automatically update status
            obj.status = "Replied"
            obj.reply_seen = False  # notify customer
            obj.save()

            return redirect("admin_complaints")
    else:
        form = AdminReplyForm(instance=complaint)

    return render(request, "reply_complaint.html", {"form": form})


@login_required
def admin_complaints(request):
    if request.user.role != "admin":
        return redirect("login")

    complaints = Complaint.objects.all()
    return render(request, "admin_complaints.html", {
        "complaints": complaints
    })


@login_required
def view_complaints(request):
    if request.user.role != "customer":
        return redirect("login")

    complaints = Complaint.objects.filter(customer=request.user)

    # Mark replies as seen
    complaints.filter(status="Replied").update(reply_seen=True)

    return render(request, "view_complaints.html", {
        "complaints": complaints
    })


@login_required
def submit_complaint(request):
    if request.user.role != "customer":
        return redirect("login")

    if request.method == "POST":
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.customer = request.user
            complaint.save()
            return redirect("view_complaints")
    else:
        form = ComplaintForm()

    return render(request, "submit_complaint.html", {"form": form})



@login_required
def give_rating(request):
    if request.user.role != "customer":
        return redirect("login")

    if request.method == "POST":
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.customer = request.user
            rating.save()
            return redirect("customer_dashboard")
    else:
        form = RatingForm()

    return render(request, "give_rating.html", {"form": form})



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
        customer=request.user
    )

    event_name = booking.event.name
    admin_user = booking.event.admin

    booking.delete()

    messages.warning(
        request,
        f"{request.user.username} cancelled booking for {event_name}"
    )

    return redirect("my_bookings")


# =========================
# CUSTOMER DASHBOARD
# =========================
@login_required
def customer_dashboard(request):
    if request.user.role != "customer":
        return redirect("login")

    # Annotate average rating
    events = Event.objects.filter(
        event_status="Scheduled"
    ).annotate(
        avg_rating=Avg('ratings__stars')
    )

    # 🔔 Unseen admin replies
    unread_replies = Complaint.objects.filter(
        customer=request.user,
        status="Replied",
        reply_seen=False
    ).count()

    return render(request, "customer_dashboard.html", {
        "events": events,
        "unread_replies": unread_replies
    })


# =========================
# BOOK EVENT
# =========================
@login_required
def book_event(request, pk):
    if request.user.role != "customer":
        return redirect("login")

    event = get_object_or_404(Event, id=pk)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.event = event
            booking.save()

            # 🔔 Notify Admin
            messages.success(
                request,
                f"{request.user.username} booked {event.name}"
            )

            return redirect("my_bookings")
    else:
        form = BookingForm()

    return render(request, "book_event.html", {
        "form": form,
        "event": event
    })


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

    # 🔥 Get all bookings of admin's events
    bookings = Booking.objects.filter(
        event__admin=request.user
    ).select_related("event", "customer").order_by("-booking_date")

    return render(request, "admin_dashboard.html", {
        "total_events": total_events,
        "total_cues": total_cues,
        "total_operators": total_operators,
        "bookings": bookings,
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
        form = EventForm(request.POST, request.FILES)
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
        form = EventForm(request.POST, request.FILES, instance=event)
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


# =========================
# VIEW EVENT DETAILS
# =========================

@login_required
def view_event(request, pk):
    if request.user.role != "customer":
        return redirect("login")

    event = get_object_or_404(Event, id=pk)

    already_booked = Booking.objects.filter(
        customer=request.user,
        event=event
    ).exists()

    # ⭐ Average Rating
    avg_rating = Rating.objects.filter(event=event).aggregate(
        Avg('stars')
    )['stars__avg']

    # Prevent multiple ratings
    existing_rating = Rating.objects.filter(
        customer=request.user,
        event=event
    ).first()

    if request.method == "POST":
        form = RatingForm(request.POST)
        if form.is_valid() and not existing_rating:
            rating = form.save(commit=False)
            rating.customer = request.user
            rating.event = event   # 🔥 auto assign
            rating.save()
            return redirect('view_event', pk=event.id)
    else:
        form = RatingForm()

    return render(request, "view_event.html", {
        "event": event,
        "already_booked": already_booked,
        "avg_rating": avg_rating,
        "form": form,
        "existing_rating": existing_rating,
    })