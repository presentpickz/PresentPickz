from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('payment-return/', views.payment_return, name='payment_return'),
    path('mock-payment/<str:order_id>/', views.mock_payment, name='mock_payment'),
    path('success/<str:order_id>/', views.order_success, name='order_success'),
    # Order Management
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<str:order_id>/', views.order_detail, name='order_detail'),
    path('invoice/<str:order_id>/', views.download_invoice, name='download_invoice'),
    path('track/', views.track_order, name='track_order'),
    path('cancel/<str:order_id>/', views.cancel_order, name='cancel_order'),
    
    # Reviews
    path('review/<str:order_id>/', views.rate_review, name='rate_review'),
    path('review/<str:order_id>/submit/<int:product_id>/', views.submit_review, name='submit_review'),
]
