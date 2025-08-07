from django.urls import path
from . import views

urlpatterns = [
    path('trigger-meal-plan/', views.trigger_meal_plan_view, name='trigger-meal-plan'),
] 