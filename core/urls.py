from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('test-images/', views.image_test, name='image_test'),
    
    # Static Pages
    path('help-center/', TemplateView.as_view(template_name='pages/help_center.html'), name='help_center'),
    path('faqs/', TemplateView.as_view(template_name='pages/faqs.html'), name='faqs'),
    path('returns-policy/', TemplateView.as_view(template_name='pages/returns_policy.html'), name='returns_policy'),
    path('terms/', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
    path('privacy/', TemplateView.as_view(template_name='pages/privacy.html'), name='privacy'),
    path('shipping-policy/', TemplateView.as_view(template_name='pages/shipping_policy.html'), name='shipping_policy'),
]
