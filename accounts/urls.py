from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import *
from django.contrib.auth import views as auth_views
from .import views
# from django.contrib.auth import views as auth_views
urlpatterns = [
    path('login/', views.login_view, name='login'),
    # path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('logout/', custom_logout, name='logout'),
    path('signup/', AdminSignupView.as_view(), name='signup'),
    path('teacher_admin_signup/', TeacherAdminSignupView.as_view(), name='teacher_admin_signup'),
    path('teacherupdate/<int:pk>/', TeacherUpdateView.as_view(), name='teacherupdate'),
    path('passwordchange/', UserPasswordChangeView.as_view(), name='passwordchange'),

    path("password_reset/", 
    auth_views.PasswordResetView.as_view(template_name='register/password_reset.html'), name="password_reset"),
    path("password_reset_done/",
        auth_views.PasswordResetDoneView.as_view(template_name='register/password_reset_done.html'),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name='register/password_reset_confirm.html'),
        name="password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name='register/password_reset_complete.html'),
        name="password_reset_complete",
    ),
    
]