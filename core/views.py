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
    
    # 3. Shop by Category (All Categories)
    categories = Category.objects.all()

    # 4. Loved by Givers (5-Star Reviews)
    loved_reviews = Review.objects.filter(rating=5, is_hidden=False).select_related('user', 'product').order_by('-created_at')[:3]

    # Handle wishlist status
    wishlisted_ids = []
    if request.user.is_authenticated:
        from users.models import Wishlist
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlisted_ids = list(wishlist.products.values_list('id', flat=True))

    context = {
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'categories': categories,
        'loved_reviews': loved_reviews,
        'wishlisted_ids': wishlisted_ids,
    }
    return render(request, 'core/home.html', context)

def image_test(request):
    """Test page to verify images are loading"""
    products = Product.objects.all()
    return render(request, 'core/image_test.html', {'products': products})
