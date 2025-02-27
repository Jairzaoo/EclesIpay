# dizimo/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class Paroquia(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    data_criacao = models.DateTimeField(default=timezone.now)  # Mantenha esta linha
    
    def __str__(self):
        return self.nome

class Usuario(AbstractUser):
    username = None
    first_name = None
    last_name = None
    
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=20)
    paroquia = models.ForeignKey(Paroquia, on_delete=models.SET_NULL, null=True)
    email_confirmado = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField(default=timezone.now)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'data_nascimento', 'telefone']

    def send_confirmation_email(self, request):
        token = default_token_generator.make_token(self)
        uid = urlsafe_base64_encode(force_bytes(self.pk))
        
        confirmation_url = request.build_absolute_uri(
            reverse('confirmar_email', kwargs={'uidb64': uid, 'token': token})
        )
        
        subject = "Confirme seu cadastro no EclesIPay"
        message = f"""
        Olá {self.nome},
        
        Por favor, confirme seu endereço de email clicando no link abaixo:
        {confirmation_url}
        
        Atenciosamente,
        Equipe EclesIPay
        """
        html_message = f"""
        <h2 style="color: #4B0082;">Confirmação de Email</h2>
        <p>Olá {self.nome},</p>
        <p>Clique no botão abaixo para confirmar seu endereço de email:</p>
        <a href="{confirmation_url}" style="
            background: #D4AF37;
            color: white;
            padding: 12px 25px;
            border-radius: 5px;
            text-decoration: none;
            display: inline-block;
            margin: 15px 0;">
            Confirmar Email
        </a>
        <p>Se você não criou esta conta, por favor ignore este email.</p>
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            html_message=html_message
        )

    def __str__(self):
        return f"{self.nome} ({self.email})"