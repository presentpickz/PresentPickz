from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    
    # Profile & Account
    path('account/', views.account_dashboard, name='account'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/photo/upload/', views.upload_profile_photo, name='upload_profile_photo'),
    path('profile/photo/delete/', views.delete_profile_photo, name='delete_profile_photo'),
    path('reviews/', views.my_reviews, name='my_reviews'),
    
    # Address Management
    path('addresses/', views.saved_addresses, name='saved_addresses'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    
    # Debug (remove in production)
    path('profile/debug/', views.debug_profile, name='debug_profile'),
    
    # Password Change (for logged-in users)
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    
    # Password Reset (FULLY AUTOMATED - Zero Admin Access)
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/sent/', views.password_reset_sent, name='password_reset_sent'),
    path('password-reset/confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/complete/', views.password_reset_complete, name='password_reset_complete'),
]

