from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin


class SplashScreenMiddleware(MiddlewareMixin):
    """
    Show splash on every homepage visit, using short-lived cookie to prevent loop.
    """
    
    def process_request(self, request):
        # Skip splash for admin, API, static files, and media
        skip_paths = [
            '/admin/',
            '/api/',
            '/static/',
            '/media/',
            '/accounts/',
            '/shop/',
            '/cart/',
            '/orders/',
            '/users/',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Check if we just came from splash (cookie set by JavaScript)
        if request.COOKIES.get('from_splash'):
            return None
        
        # Show splash on homepage
        if request.path == '/':
            return render(request, 'core/splash.html')
        
        return None
