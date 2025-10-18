from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile


class ProfileInline(admin.StackedInline):
    """Inline admin for Profile model"""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    """Extended UserAdmin with Profile inline"""
    inlines = [ProfileInline]


# Unregister the original User admin and register our customized version
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin for Profile model"""
    list_display = ['user', 'gender', 'city', 'country', 'created_at']
    list_filter = ['gender', 'country', 'created_at']
    search_fields = ['user__username', 'user__email', 'city', 'country']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Personal Info', {'fields': ('bio', 'gender', 'profile_picture')}),
        ('Address', {'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
