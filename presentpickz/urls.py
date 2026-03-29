from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.http import HttpResponse

urlpatterns = [
    # Admin MUST be first to prevent catch-all patterns from intercepting
    path('admin/', admin.site.urls),
    
    # Main site URLs
    path('', include('core.urls')),
    path('shop/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('users/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    
    # Google Verification File (for Search Console)
    path('googleccfc70bcd8a6f5fe.html', lambda r: HttpResponse("google-site-verification: googleccfc70bcd8a6f5fe.html", content_type="text/html")),

    # ALWAYS serve media files (works in debug AND production)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# In debug mode, also serve static files locally
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
