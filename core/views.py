from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Avg, Sum, Case, When, IntegerField
from django import forms
from django.contrib import messages
from decimal import Decimal
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta
from django.http import JsonResponse
from .models import Event, Cue, Notification, Attendance, Booking, Rating, Complaint, Salary, User, ChatMessage
from .forms import EventForm, CueForm, RatingForm, ComplaintForm, AdminReplyForm, BookingForm, CustomerRegisterForm



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
        "booking": booking,
        "can_create_cue": booking.approval_status == "Accepted",
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

    booking_notifications = list(
        Booking.objects.filter(
            customer=request.user,
            customer_notified=False
        )
        .exclude(approval_status="Pending")
        .select_related("event")
        .order_by("-admin_action_at")
    )
    if booking_notifications:
        Booking.objects.filter(
            id__in=[booking.id for booking in booking_notifications]
        ).update(customer_notified=True)

    return render(request, "customer_dashboard.html", {
        "events": events,
        "unread_replies": unread_replies,
        "booking_notifications": booking_notifications,
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
    # 🔐 Only admin allowed
    if request.user.role != "admin":
        return redirect("login")

    # =========================
    # System Overview
    # =========================
    total_events = Event.objects.filter(
        admin=request.user
    ).count()

    total_cues = Cue.objects.count()

    total_operators = Attendance.objects.filter(
        check_out_time__isnull=True
    ).values("operator").distinct().count()

    # =========================
    # Latest Bookings
    # =========================
    bookings = Booking.objects.filter(
        event__admin=request.user
    ).select_related(
        "event", "customer"
    ).annotate(
        status_priority=Case(
            When(approval_status="Pending", then=0),
            When(approval_status="Accepted", then=1),
            When(approval_status="Rejected", then=2),
            default=3,
            output_field=IntegerField(),
        )
    ).order_by("status_priority", "-booking_date")

    # =========================
    # User Management Lists
    # =========================
    admins = User.objects.filter(role="admin")
    operators = User.objects.filter(role="operator")
    customers = User.objects.filter(role="customer")

    # =========================
    # 🔴 Unread Chat Messages
    # =========================
    from .models import ChatMessage

    unread_count = ChatMessage.objects.filter(
        receiver=request.user,
        is_seen=False
    ).count()

    # =========================
    # Render Dashboard
    # =========================
    return render(request, "admin_dashboard.html", {
        "total_events": total_events,
        "total_cues": total_cues,
        "total_operators": total_operators,
        "bookings": bookings,
        "admins": admins,
        "operators": operators,
        "customers": customers,
        "unread_count": unread_count,  # 🔥 for red dot
    })


@login_required
@require_POST
def update_booking_status(request, pk):
    if request.user.role != "admin":
        return redirect("login")

    booking = get_object_or_404(
        Booking,
        id=pk,
        event__admin=request.user,
    )

    action = request.POST.get("action", "").strip().lower()
    if action not in {"accept", "reject"}:
        messages.error(request, "Invalid booking action.")
        return redirect("admin_dashboard")

    booking.approval_status = "Accepted" if action == "accept" else "Rejected"
    booking.admin_action_at = timezone.now()
    booking.customer_notified = False
    booking.save(update_fields=["approval_status", "admin_action_at", "customer_notified"])

    messages.success(
        request,
        f"Booking for {booking.customer.username} has been {booking.approval_status.lower()}."
    )
    return redirect("admin_dashboard")


# =========================
# OPERATOR DASHBOARD
# =========================
from .models import Attendance

@login_required
def operator_dashboard(request):

    if request.user.role != "operator":
        return redirect("login")

    cues = Cue.objects.filter(
        operator=request.user,
        cue_status="Pending"
    ).select_related("event").order_by("cue_date", "cue_time")

    from .models import ChatMessage

    unread_count = ChatMessage.objects.filter(
        receiver=request.user,
        is_seen=False
    ).count()

    open_attendance = Attendance.objects.filter(
        operator=request.user,
        check_out_time__isnull=True
    ).first()

    is_checked_in = True if open_attendance else False

    check_in_time = None
    if open_attendance:
        check_in_time = open_attendance.check_in_time

    return render(request, "operator_dashboard.html", {
        "cues": cues,
        "unread_count": unread_count,
        "is_checked_in": is_checked_in,
        "check_in_time": check_in_time,   # 🔥 new
    })


# =========================
# EVENT CRUD
# =========================

@login_required
def event_list(request):
    if request.user.role != "admin":
        return redirect("login")

    events = Event.objects.filter(
        admin=request.user
    ).annotate(
        avg_rating=Avg("ratings__stars")
    )

    return render(request, "event_list.html", {
        "events": events
    })


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

    # 🔥 Latest first (newest on top)
    pending_cues = Cue.objects.filter(
        cue_status="Pending"
    ).order_by("-cue_date", "-cue_time")

    completed_cues = Cue.objects.filter(
        cue_status="Completed"
    ).order_by("-cue_date", "-cue_time")

    return render(request, "cue_list.html", {
        "pending_cues": pending_cues,
        "completed_cues": completed_cues
    })


@login_required
def cue_create(request):
    if request.user.role != "admin":
        return redirect("login")

    event_id = request.GET.get("event_id")
    booking_id = request.GET.get("booking_id")
    allowed_events = Event.objects.filter(
        admin=request.user,
        bookings__approval_status="Accepted",
    ).distinct()
    allowed_event_ids = set(allowed_events.values_list("id", flat=True))

    if booking_id:
        booking = get_object_or_404(
            Booking,
            id=booking_id,
            event__admin=request.user,
        )
        if booking.approval_status != "Accepted":
            messages.error(request, "You can create cues only after booking is accepted.")
            return redirect("booking_detail", pk=booking.id)
        event_id = str(booking.event_id)

    if event_id:
        try:
            event_id_int = int(event_id)
        except (TypeError, ValueError):
            messages.error(request, "Invalid event selected for cue creation.")
            return redirect("admin_dashboard")
        if event_id_int not in allowed_event_ids:
            messages.error(request, "Cues can be created only for accepted bookings.")
            return redirect("admin_dashboard")

    if request.method == "POST":
        form = CueForm(request.POST, event_id=event_id, admin_user=request.user)
        if form.is_valid():
            selected_event = form.cleaned_data["event"]
            if selected_event.id not in allowed_event_ids:
                form.add_error("event", "This event is not approved for cue creation.")
            else:
                form.save()
                return redirect("cue_list")
    else:
        form = CueForm(event_id=event_id, admin_user=request.user)
        if not form.fields["event"].queryset.exists():
            messages.info(request, "No accepted bookings found. Accept a booking to create cues.")
            return redirect("admin_dashboard")

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
    if request.user.role != "admin":
        return redirect("login")

    records = Attendance.objects.select_related(
        "operator", "event"
    ).order_by("-id")

    for record in records:

        # Calculate worked seconds and salary
        if record.check_in_time and record.check_out_time:
            total_seconds = int(
                (record.check_out_time - record.check_in_time).total_seconds()
            )
            record.total_time = total_seconds
            record.calculated_salary = total_seconds
        else:
            record.total_time = None
            record.calculated_salary = None

        # Total salary paid to this operator
        record.operator_total_salary = (
            Salary.objects.filter(operator=record.operator)
            .aggregate(Sum("total_amount"))["total_amount__sum"] or 0
        )

    # Overall total paid salary
    total_paid = (
        Salary.objects.aggregate(Sum("total_amount"))["total_amount__sum"] or 0
    )

    return render(request, "attendance.html", {
        "attendance": records,
        "total_paid": total_paid
    })


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


@login_required
def complete_cue(request, pk):
    if request.user.role != "operator":
        return redirect("login")

    cue = get_object_or_404(
        Cue,
        id=pk,
        operator=request.user
    )

    cue.cue_status = "Completed"
    cue.save()

    return redirect("operator_dashboard")


@login_required
def check_in(request):
    if request.user.role != "operator":
        return redirect("login")

    # Get latest assigned event from cue (any status)
    cue = Cue.objects.filter(
        operator=request.user
    ).select_related("event").order_by("-cue_date").first()

    if not cue:
        messages.error(request, "No event assigned.")
        return redirect("operator_dashboard")

    # Prevent double check-in
    already_checked = Attendance.objects.filter(
        operator=request.user,
        check_out_time__isnull=True
    ).exists()

    if already_checked:
        messages.warning(request, "Already checked in.")
        return redirect("operator_dashboard")

    Attendance.objects.create(
        operator=request.user,
        event=cue.event,
        check_in_time=timezone.now(),
        status="Present"
    )

    messages.success(request, "Checked in successfully.")
    return redirect("operator_dashboard")


@login_required
def check_out(request):
    if request.user.role != "operator":
        return redirect("login")

    attendance = Attendance.objects.filter(
        operator=request.user,
        check_out_time__isnull=True
    ).last()

    if attendance:
        attendance.check_out_time = timezone.now()
        attendance.save()
        messages.success(request, "Checked out successfully.")
    else:
        messages.error(request, "You are not checked in.")

    return redirect("operator_dashboard")



@login_required
@require_POST
def pay_salary(request, attendance_id):
    if request.user.role != "admin":
        return redirect("login")

    attendance = get_object_or_404(Attendance, id=attendance_id)

    if not attendance.check_in_time or not attendance.check_out_time:
        messages.error(request, "Attendance incomplete.")
        return redirect("attendance")

    # 🔥 Prevent double payment
    if hasattr(attendance, "salary_record"):
        messages.warning(request, "Salary already paid for this attendance.")
        return redirect("attendance")

    total_seconds = int(
        (attendance.check_out_time - attendance.check_in_time).total_seconds()
    )

    base_amount = Decimal(total_seconds)

    bonus_input = request.POST.get("bonus")
    bonus = Decimal(bonus_input) if bonus_input else Decimal(0)

    total_amount = base_amount + bonus

    Salary.objects.create(
        operator=attendance.operator,
        attendance=attendance,
        base_amount=base_amount,
        bonus=bonus,
        total_amount=total_amount
    )

    messages.success(request, "Salary paid successfully.")
    return redirect("attendance")


@login_required
def earnings_view(request):
    if request.user.role != "operator":
        return redirect("login")

    salaries = Salary.objects.filter(operator=request.user).order_by("-paid_date")

    from django.db.models import Sum
    from django.utils.timezone import now

    current_month = now().month
    current_year = now().year

    monthly_total = salaries.filter(
        paid_date__month=current_month,
        paid_date__year=current_year
    ).aggregate(Sum("total_amount"))["total_amount__sum"] or 0

    return render(request, "earnings.html", {
        "salaries": salaries,
        "monthly_total": monthly_total
    })




def register_view(request):
    if request.user.is_authenticated:
        return redirect("customer_dashboard")

    if request.method == "POST":
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login
            return redirect("customer_dashboard")
    else:
        form = CustomerRegisterForm()

    return render(request, "register.html", {"form": form})



@login_required
def update_user_role(request, user_id):
    if request.user.role != "admin":
        return JsonResponse({"error": "Unauthorized"}, status=403)

    user_obj = get_object_or_404(User, id=user_id)

    # 🔥 Prevent admin from modifying their own role
    if user_obj == request.user:
        return JsonResponse({
            "error": "You cannot change your own role."
        }, status=400)

    if request.method == "POST":
        new_role = request.POST.get("role")
        new_operator_role = request.POST.get("operator_role")

        if new_role != "none":
            user_obj.role = new_role

            if new_role == "operator":
                user_obj.operator_role = (
                    None if new_operator_role == "none"
                    else new_operator_role
                )
            else:
                user_obj.operator_role = None

        user_obj.save()

        return JsonResponse({
            "success": True,
            "new_role": user_obj.role,
            "new_operator_role": user_obj.operator_role
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


def about_us(request):
    return render(request, "about_us.html")


@login_required
def chat_view(request):

    if request.user.role not in ["admin", "operator"]:
        return redirect("login")

    # 🔥 Determine opposite users
    if request.user.role == "admin":
        users = User.objects.filter(role="operator")
        dashboard_url_name = "admin_dashboard"
    else:
        users = User.objects.filter(role="admin")
        dashboard_url_name = "operator_dashboard"

    selected_user_id = request.GET.get("user")
    selected_user = None
    messages = []

    # 🔥 Get unread senders list (who sent unseen messages)
    unread_senders = ChatMessage.objects.filter(
        receiver=request.user,
        is_seen=False
    ).values_list("sender_id", flat=True).distinct()

    if selected_user_id:
        selected_user = get_object_or_404(users, id=selected_user_id)

        messages = ChatMessage.objects.filter(
            sender__in=[request.user, selected_user],
            receiver__in=[request.user, selected_user]
        ).order_by("created_at")

        # 🔥 Mark messages as seen
        ChatMessage.objects.filter(
            sender=selected_user,
            receiver=request.user,
            is_seen=False
        ).update(is_seen=True)

    return render(request, "chat.html", {
        "users": users,
        "messages": messages,
        "selected_user": selected_user,
        "unread_senders": unread_senders,
        "dashboard_url_name": dashboard_url_name,
    })



@login_required
def send_message(request, user_id):

    if request.user.role not in ["admin", "operator"]:
        return redirect("login")

    if request.user.role == "admin":
        receiver = get_object_or_404(User, id=user_id, role="operator")
    else:
        receiver = get_object_or_404(User, id=user_id, role="admin")

    if request.method == "POST":
        message_text = (request.POST.get("message") or "").strip()

        if message_text:
            ChatMessage.objects.create(
                sender=request.user,
                receiver=receiver,
                message=message_text
            )

    return redirect(f"/chat/?user={receiver.id}")


@login_required
@require_POST
def delete_message(request, message_id):

    if request.user.role not in ["admin", "operator"]:
        return redirect("login")

    chat_message = get_object_or_404(ChatMessage, id=message_id)

    if request.user not in [chat_message.sender, chat_message.receiver]:
        return redirect("chat")

    if chat_message.sender == request.user:
        other_user = chat_message.receiver
    else:
        other_user = chat_message.sender

    chat_message.delete()
    return redirect(f"/chat/?user={other_user.id}")
