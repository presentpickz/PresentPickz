from django.shortcuts import render
from django.urls import reverse

class SplashScreenMiddleware:
    """Middleware to show splash screen on specific pages only"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pages to exclude from splash screen
        excluded_paths = [
            '/static/', 
            '/media/', 
            '/admin/', 
            '/favicon.ico',
            '/shop/',        # Product list
            '/cart/',        # Cart and checkout
            '/test-images/', # Test page
        ]
        
        # Check if path should be excluded
        if any(request.path.startswith(path) for path in excluded_paths):
            return self.get_response(request)
        
        # Exclude product detail pages (e.g., /shop/1/)
        if '/shop/' in request.path and request.path != '/shop/':
            return self.get_response(request)
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.get_response(request)
        
        # Check if splash has been shown in this page load
        show_splash = request.GET.get('show_splash')
        
        # Show splash only on homepage and a few select pages
        allowed_splash_paths = ['/', '/about/', '/contact/']
        
        if request.path in allowed_splash_paths:
            # Show splash if not shown yet (checked via GET parameter)
            if show_splash is None and not request.session.get('splash_shown_this_request'):
                request.session['splash_shown_this_request'] = True
                return render(request, 'core/splash.html')
            
            # Clear the flag after showing content
            if 'splash_shown_this_request' in request.session:
                del request.session['splash_shown_this_request']
        
        response = self.get_response(request)
        return response
