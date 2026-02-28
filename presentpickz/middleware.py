"""
Authentication & Role Separation Middleware
Enforces strict separation between Admin (Staff) and Customer (User) accounts.
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse


class RoleBasedAccessMiddleware:
    """
    Enforces strict role separation:
    1. Frontend users (non-staff) cannot access /admin/
    2. Admin users (staff) appear as AnonymousUser on frontend pages
       (This prevents admins from accidentally using customer features)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 1. ADMIN AREA PROTECTION
        if request.path.startswith('/admin/'):
            # allow allowed paths (login/logout/static) to pass through normal checks
            allowed_paths = [
                '/admin/login/',
                '/admin/logout/', 
                '/admin/jsi18n/',
            ]
            
            if any(request.path.startswith(path) for path in allowed_paths):
                return self.get_response(request)
                
            if request.user.is_authenticated:
                if not request.user.is_staff:
                    # BLOCK: Frontend user trying to access admin
                    messages.error(request, "Access denied. Admin area is restricted.")
                    return redirect('home')
            
            # If unauthenticated, Django admin will handle the redirect to login
            
        # 2. FRONTEND AREA PROTECTION (Session Masking)
        else:
            # If an admin is browsing the frontend, mask them as a Guest
            # This ensures 'Logging in as Admin must NOT automatically log in to frontend'
            if request.user.is_authenticated and request.user.is_staff:
                # Mask the user as anonymous for this request cycle only
                # The session remains valid for /admin/ access
                request.user = AnonymousUser()

        response = self.get_response(request)
        return response
