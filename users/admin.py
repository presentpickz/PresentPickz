"""
HIGH-FIDELITY AUTH ADMIN
Admins and Staff have ZERO access to user passwords.
All password operations are fully automated and user-controlled.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Wishlist, UserProfile, Address, PasswordResetToken


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'updated_at']
    filter_horizontal = ['products']
    readonly_fields = ['user', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_photo', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['updated_at']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'city', 'state', 'address_type', 'is_default']
    list_filter = ['address_type', 'is_default', 'state']
    search_fields = ['user__username', 'name', 'city']


class SecureUserAdmin(BaseUserAdmin):
    """
    SECURITY POLICY: ZERO PASSWORD ACCESS
    - Admins CANNOT view password hashes
    - Admins CANNOT change user passwords
    - Admins CANNOT reset user passwords
    - Admins CANNOT trigger password reset emails
    
    Password management is 100% user-controlled via automated "Forgot Password" flow.
    """
    
    # Remove password from all fieldsets
    fieldsets = (
        (None, {'fields': ('username',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Remove password from add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active'),
            'description': 'New users will receive an automated email to set their password.'
        }),
    )
    
    # Display fields
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    # Make password-related fields completely inaccessible
    readonly_fields = ['last_login', 'date_joined']
    
    # Remove password change link
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Disable password field completely
        if 'password' in form.base_fields:
            del form.base_fields['password']
        return form
    
    # Override to remove password change link from user detail page
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        # Remove password change link
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    # Completely disable password-related actions
    actions = []  # No bulk actions for password
    
    class Meta:
        verbose_name = 'User Account'
        verbose_name_plural = 'User Accounts'


# Unregister default User admin and register secure version
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, SecureUserAdmin)


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Read-only view of password reset tokens for security auditing only.
    Admins CANNOT create, modify, or use these tokens.
    """
    list_display = ['user', 'created_at', 'expires_at', 'is_used', 'is_expired_display']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user', 'token', 'created_at', 'expires_at', 'is_used', 'ip_address', 'user_agent']
    
    def is_expired_display(self, obj):
        return obj.is_expired()
    is_expired_display.boolean = True
    is_expired_display.short_description = 'Expired'
    
    def has_add_permission(self, request):
        # Admins CANNOT create reset tokens manually
        return False
    
    def has_change_permission(self, request, obj=None):
        # Admins CANNOT modify reset tokens
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Admins CAN delete old tokens for cleanup
        return True
    
    class Meta:
        verbose_name = 'Password Reset Token (Audit Only)'
        verbose_name_plural = 'Password Reset Tokens (Audit Only)'
