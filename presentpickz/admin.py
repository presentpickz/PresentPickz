"""
Custom Admin Site with Separate Session
This ensures admin login is independent from frontend user login
"""
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse


class SeparateAdminSite(admin.AdminSite):
    """
    Custom Admin Site that uses a separate session cookie
    and requires staff/superuser status
    """
    site_header = "Present Pickz Admin"
    site_title = "Present Pickz Admin Portal"
    index_title = "Welcome to Present Pickz Administration"
    
    # Use a different session cookie for admin
    def login(self, request, extra_context=None):
        """
        Display the login form for the given HttpRequest.
        """
        from django.contrib.admin.forms import AdminAuthenticationForm
        from django.contrib.auth.views import LoginView
        
        context = {
            **self.each_context(request),
            'title': 'Admin Login',
            'app_path': request.get_full_path(),
            'username': request.user.get_username(),
        }
        if extra_context:
            context.update(extra_context)

        defaults = {
            'extra_context': context,
            'authentication_form': AdminAuthenticationForm,
            'template_name': 'admin/login.html',
        }
        
        request.session = request.session.__class__(session_key='admin_session')
        return LoginView.as_view(**defaults)(request)
    
    def has_permission(self, request):
        """
        Only allow staff members to access admin
        Regular frontend users should not have access
        """
        # Check if user is active, staff, and authenticated
        return (
            request.user.is_active and 
            request.user.is_staff and
            request.user.is_authenticated
        )
    
    def admin_view(self, view, cacheable=False):
        """
        Decorator to ensure only staff can access admin views
        """
        def inner(request, *args, **kwargs):
            if not self.has_permission(request):
                # Redirect to admin login
                return redirect_to_login(
                    request.get_full_path(),
                    reverse('admin:login')
                )
            return view(request, *args, **kwargs)
        return inner


# Create the custom admin site instance
admin_site = SeparateAdminSite(name='admin')
