from django.urls import path
from . import views

urlpatterns = [
    path('profiles/<int:profile_id>/trigger-scrape/', views.trigger_scrape_view, name='trigger-scrape'),
] 