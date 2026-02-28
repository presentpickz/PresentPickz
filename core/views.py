from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from products.models import Product, Category, Review

@ensure_csrf_cookie
def home(request):
    """
    Homepage View
    
    Handle splash screen logic and display the main storefront.
    
    NOTE ON SPLASH SCREEN:
    Originally implemented as Middleware, but moved here for better stability 
    with Python 3.14 + Django 6.0 setup. It uses session variables to track state.
    """

    # --- SPLASH SCREEN NOW HANDLED BY MIDDLEWARE ---
    # See: presentpickz/splash_middleware.py
    # Splash shows once per session on ANY page visit
    
    # --- HOMEPAGE DATA ---
    
    # 1. Fresh Drops (New Arrivals)
    # Fetches up to 8 products marked with is_new=True
    new_arrivals = Product.objects.filter(is_new=True)[:8]
    
    # 2. Best Sellers
    # Fetches up to 6 products marked with is_bestseller=True
    best_sellers = Product.objects.filter(is_bestseller=True)[:6]
    
    # 3. Shop by Category
    # Fetches up to 6 categories marked with is_featured=True
    # (Limit increased from 4 to 6 per user request)
    categories = Category.objects.filter(is_featured=True)[:6]

    # 4. Loved by Givers (5-Star Reviews)
    # Fetches up to 3 latest 5-star reviews
    loved_reviews = Review.objects.filter(rating=5, is_hidden=False).select_related('user', 'product').order_by('-created_at')[:3]

    context = {
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'categories': categories,
        'loved_reviews': loved_reviews,
    }
    return render(request, 'core/home.html', context)

def image_test(request):
    """Test page to verify images are loading"""
    products = Product.objects.all()
    return render(request, 'core/image_test.html', {'products': products})

