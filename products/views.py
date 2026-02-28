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
    category_slug = request.GET.get('category')
    categories = Category.objects.all()
    products = Product.objects.all()

    if category_slug:
        products = products.filter(category__slug=category_slug)

    context = {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    # Get reviews
    reviews = product.reviews.filter(is_hidden=False)
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
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
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': query,
    }
    return render(request, 'products/product_list.html', context)
