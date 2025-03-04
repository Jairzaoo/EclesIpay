from django.urls import path
from django.contrib import admin
from django.views.generic import TemplateView
from dizimo import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.CustomLoginView.as_view(), name='login'),  # Use the custom login view
    path('registro/', views.CustomRegistroView.as_view(), name='registro'),  # Use the custom registration view
    path('home/', views.home, name='home'),
    path('logout/', views.user_logout, name='logout'),
    path('confirmar-email/<uidb64>/<token>/', views.confirmar_email, name='confirmar_email'),
    path('email-confirmacao-enviado/', TemplateView.as_view(template_name='email_confirmation_sent.html'), name='email_confirmation_sent'),
    path('email-confirmado/', TemplateView.as_view(template_name='email_confirmed.html'), name='email_confirmed'),
    path('atualizar-paroquia/', views.atualizar_paroquia, name='atualizar_paroquia'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),  # Add the edit profile view
    path('fazer-oferta/', views.fazer_oferta, name='fazer_oferta'),  # Add the make offer view
    path('pagamentoefetuado/', views.pagamento_efetuado, name='pagamentoefetuado'),  # Add the make offer view
    path('historico-contribuicao/', views.historico_contribuicao, name='historico_contribuicao'),
    path('admin-contribuicoes/', views.admin_contribuicoes, name='admin_contribuicoes'),
    
]