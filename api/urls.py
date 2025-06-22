from django.urls import path
from . import views

urlpatterns = [
    path('profiles/<int:profile_id>/trigger-meal-plan/', views.trigger_meal_plan_view, name='trigger-meal-plan'),
    path('email-verification-status/', views.check_email_verification_status, name='email-verification-status'),
] 