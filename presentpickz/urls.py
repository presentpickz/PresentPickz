from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

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
    
    # ALWAYS serve media files (works for ALL users, logged in or not)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Also add static files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
