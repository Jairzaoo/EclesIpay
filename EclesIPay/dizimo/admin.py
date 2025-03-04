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


class ParoquiaAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

admin.site.register(Paroquia, ParoquiaAdmin)
admin.site.register(Usuario, CustomUserAdmin)
admin.site.site_header = "EclesIPay Administração"
admin.site.site_title = "Portal EclesIPay"
admin.site.index_title = "Bem-vindo ao Portal EclesIPay"