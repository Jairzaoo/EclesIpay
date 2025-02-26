from django.urls import path
from django.contrib import admin
from django.views.generic import TemplateView  # Adicione esta importação
from django.contrib.auth import views as auth_views
from dizimo import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('registro/', views.registro, name='registro'),
    path('home/', views.home, name='home'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('confirmar-email/<uidb64>/<token>/', views.confirmar_email, name='confirmar_email'),
    path('email-confirmacao-enviado/', TemplateView.as_view(template_name='email_confirmation_sent.html'), name='email_confirmation_sent'),
    path('email-confirmado/', TemplateView.as_view(template_name='email_confirmed.html'), name='email_confirmed'),
]