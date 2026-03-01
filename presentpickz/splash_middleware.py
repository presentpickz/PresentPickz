from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin


class SplashScreenMiddleware(MiddlewareMixin):
    """
    Show splash screen only ONCE per browser session on the homepage.
    Uses Django sessions for reliable tracking (not short-lived cookies).
    """
    
    def process_request(self, request):
        # Only show splash on homepage
        if request.path != '/':
            return None
        
        # Skip for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return None
        
        # Check if user has already seen the splash this session
        if request.session.get('splash_seen'):
            return None
        
        # Mark splash as seen in session
        request.session['splash_seen'] = True
        
        # Show the splash screen
        return render(request, 'core/splash.html')
