from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('refresh/', views.refresh_token, name='refresh-token'),
    path('verify-email/', views.verify_email, name='verify-email'),
    path('resend-verification/', views.resend_verification_email, name='resend-verification'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', views.ProfileView.as_view(), name='profile-update'),
    path('profile/location/', views.update_location, name='update-location'),
] 