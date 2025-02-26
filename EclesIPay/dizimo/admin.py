from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Paroquia

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'data_nascimento', 'telefone', 'paroquia')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    list_display = ('email', 'nome', 'paroquia')
    ordering = ('email',)

admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(Paroquia)