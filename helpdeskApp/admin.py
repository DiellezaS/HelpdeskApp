

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Ticket, FAQ

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role']
    
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Ticket)
admin.site.register(FAQ)