from django.urls import path
from . import views

urlpatterns = [
    path('profiles/<int:profile_id>/trigger-meal-plan/', views.trigger_meal_plan_view, name='trigger-meal-plan'),
    path('meal-plan/', views.get_meal_plan, name='get-meal-plan'),
    path('meal-plan/history/', views.get_meal_plan_history, name='get-meal-plan-history'),
    path('meal-plan/history/<int:history_id>/', views.get_meal_plan_history_detail, name='get-meal-plan-history-detail'),
    path('meal-plan/history/<int:history_id>/update/', views.update_meal_plan_history, name='update-meal-plan-history'),
    path('meal-plan/archive/', views.archive_current_meal_plan, name='archive-current-meal-plan'),
    path('email-verification-status/', views.check_email_verification_status, name='email-verification-status'),
] 