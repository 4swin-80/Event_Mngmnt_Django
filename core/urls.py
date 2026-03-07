from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('operator-dashboard/', views.operator_dashboard, name='operator_dashboard'),

    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/update/<int:pk>/', views.event_update, name='event_update'),
    path('events/delete/<int:pk>/', views.event_delete, name='event_delete'),

    path('cues/', views.cue_list, name='cue_list'),
    path('cue/create/', views.cue_create, name='cue_create'),

    path('notifications/', views.notification_list, name='notification_list'),
    path('attendance/', views.attendance_view, name='attendance'),

    path('performance/', views.performance_dashboard, name='performance'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('book-event/<int:pk>/', views.book_event, name='book_event'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:pk>/', views.cancel_booking, name='cancel_booking'),
    path('give-rating/', views.give_rating, name='give_rating'),
    path('submit-complaint/', views.submit_complaint, name='submit_complaint'),
    path('my-complaints/', views.view_complaints, name='view_complaints'),
    path('admin-complaints/', views.admin_complaints, name='admin_complaints'),
    path('reply-complaint/<int:pk>/', views.reply_complaint, name='reply_complaint'),
    path('view-event/<int:pk>/', views.view_event, name='view_event'),
    path('delete-rating/<int:pk>/', views.delete_rating, name='delete_rating'),

    path('booking-detail/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('booking-status/<int:pk>/', views.update_booking_status, name='update_booking_status'),

    path('complete-cue/<int:pk>/', views.complete_cue, name='complete_cue'),

    path('check-in/', views.check_in, name='check_in'),
    path('check-out/', views.check_out, name='check_out'),

    path('pay-salary/<int:attendance_id>/', views.pay_salary, name='pay_salary'),
    path('earnings/', views.earnings_view, name='earnings'),

    path('register/', views.register_view, name='register'),
    path('update-user-role/<int:user_id>/', views.update_user_role, name='update_user_role'),
    path('about-us/', views.about_us, name='about_us'),
    path('chat/', views.chat_view, name='chat'),
    path('send-message/<int:user_id>/', views.send_message, name='send_message'),
    path('delete-message/<int:message_id>/', views.delete_message, name='delete_message'),
]
