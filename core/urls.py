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
]