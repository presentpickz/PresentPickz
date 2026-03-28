from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Review
from orders.models import Order

def can_user_review(user, product, order):
    """
    Check if user can review a product:
    1. Order must belong to user
    2. Order status must be DELIVERED
    3. Product must be in the order
    4. User hasn't already reviewed this product for this order
    """
    if order.user != user:
        return False
    
    if order.status != 'DELIVERED':
        return False
        
    if not order.items.filter(product=product).exists():
        return False
        
    # Check if review already exists
    if Review.objects.filter(user=user, product=product, order=order).exists():
        return False
        
    return True

def product_list(request):
    try:
        category_slug = request.GET.get('category')
        categories = Category.objects.all()
        products = Product.objects.all().select_related('category')

        if category_slug:
            products = products.filter(category__slug=category_slug)

        # Handle wishlist status
        wishlisted_ids = []
        if request.user.is_authenticated:
            from users.models import Wishlist
            wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
            wishlisted_ids = list(wishlist.products.values_list('id', flat=True))

        context = {
            'products': products,
            'categories': categories,
            'current_category': category_slug,
            'wishlisted_ids': wishlisted_ids,
        }
        return render(request, 'products/product_list.html', context)
    except Exception as e:
        print(f"Product list error: {e}")
        # Fallback to simple list if query fails
        return render(request, 'products/product_list.html', {
            'products': Product.objects.all()[:20],
            'categories': Category.objects.all(),
        })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    # Get reviews
    reviews = product.reviews.filter(is_hidden=False)
    
    # Check if in wishlist
    is_in_wishlist = False
    if request.user.is_authenticated:
        from users.models import Wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        is_in_wishlist = wishlist.products.filter(id=product.id).exists()
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'is_in_wishlist': is_in_wishlist,
    }
    return render(request, 'products/product_detail.html', context)

@login_required
def add_review(request, order_id, product_id):
    order = get_object_or_404(Order, order_id=order_id)
    product = get_object_or_404(Product, id=product_id)

    # Validate eligibility
    if not can_user_review(request.user, product, order):
        messages.error(request, "You are not eligible to review this product.")
        return redirect('orders:my_orders')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not rating or not comment:
            messages.error(request, "Please provide both rating and comment.")
            return render(request, 'products/add_review.html', {'product': product, 'order': order})

        Review.objects.create(
            user=request.user,
            product=product,
            order=order,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Review submitted successfully!")
        return redirect('products:product_detail', product_id=product.id)
        
    return render(request, 'products/add_review.html', {
        'product': product,
        'order': order
    })

def product_search(request):
    from django.db.models import Q
    query = request.GET.get('q')
    products = Product.objects.all()
    categories = Category.objects.all()
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Handle wishlist status
    wishlisted_ids = []
    if request.user.is_authenticated:
        from users.models import Wishlist
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlisted_ids = list(wishlist.products.values_list('id', flat=True))

    context = {
        'products': products,
        'categories': categories,
        'search_query': query,
        'wishlisted_ids': wishlisted_ids,
    }
    return render(request, 'products/product_list.html', context)
