# dizimo/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string

class Paroquia(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    data_criacao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nome

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, data_nascimento, telefone, password=None):
        if not email:
            raise ValueError('O usuário deve ter um endereço de email')
        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, data_nascimento=data_nascimento, telefone=telefone)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, data_nascimento, telefone, password=None):
        user = self.create_user(email, nome, data_nascimento, telefone, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Usuario(AbstractBaseUser, PermissionsMixin):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=20)
    cpf = models.CharField(max_length=11, null=True, blank=True, default=None)  # Now unique but still nullable
    paroquia = models.ForeignKey(Paroquia, on_delete=models.SET_NULL, null=True, blank=True)
    email_confirmado = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'data_nascimento', 'telefone']  # Keep CPF out for now

    def send_confirmation_email(self, request):
        token = default_token_generator.make_token(self)
        uid = urlsafe_base64_encode(force_bytes(self.pk))
        url = reverse('confirmar_email', kwargs={'uidb64': uid, 'token': token})
        full_url = request.build_absolute_uri(url)
        message = render_to_string('email_confirmation.html', {
            'user': self,
            'url': full_url,
        })
        send_mail(
            'Confirme seu email',
            message,
            'noreply@eclesipay.com',
            [self.email],
            fail_silently=False,
        )

    def __str__(self):
        return f"{self.nome} ({self.email})"

class EmailLog(models.Model):
    """Model to track email sending history"""
    EMAIL_TYPES = (
        ('monthly', 'Lembrete Mensal'),
        ('confirmation', 'Confirmação de Email'),
        ('password_reset', 'Redefinição de Senha'),
        ('other', 'Outro'),
    )

    user = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='email_logs')
    email_type = models.CharField(max_length=20, choices=EMAIL_TYPES)
    sent_at = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=255)
    successful = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Log de Email'
        verbose_name_plural = 'Logs de Email'
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.email_type} para {self.user.email} em {self.sent_at.strftime('%d/%m/%Y %H:%M')}"

    @classmethod
    def has_received_monthly_email_this_month(cls, user):
        """Check if the user has already received a monthly email this month"""
        now = timezone.now()
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return cls.objects.filter(
            user=user,
            email_type='monthly',
            sent_at__gte=first_day_of_month,
            successful=True
        ).exists()
