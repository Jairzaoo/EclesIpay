from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Paroquia

class CustomUserAdmin(UserAdmin):
    model = Usuario
    list_display = ['email', 'nome', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['email', 'nome']
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('nome', 'data_nascimento', 'telefone', 'paroquia')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'data_nascimento', 'telefone', 'paroquia', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}
        ),
    )

admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(Paroquia)