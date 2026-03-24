from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from products.models import Product, Category, Review

@ensure_csrf_cookie
def home(request):
    """
    Homepage View
    
    Handle splash screen logic and display the main storefront.
    """
    
    # --- HOMEPAGE DATA ---
    
    # 1. Fresh Drops (New Arrivals)
    new_arrivals = Product.objects.filter(is_new=True)[:8]
    
    # 2. Best Sellers
    best_sellers = Product.objects.filter(is_bestseller=True)[:6]
    
    # 3. Shop by Category
    categories = Category.objects.filter(is_featured=True)[:6]

    # 4. Loved by Givers (5-Star Reviews)
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
