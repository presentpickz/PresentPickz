from users.models import Wishlist

def wishlist_context(request):
    """
    Context processor to make wishlist_count available globally in all templates.
    """
    wishlist_count = 0
    wishlist_product_ids = []
    
    if request.user.is_authenticated:
        try:
            wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
            wishlist_product_ids = list(wishlist.products.values_list('id', flat=True))
            wishlist_count = len(wishlist_product_ids)
        except Exception as e:
            print(f"Wishlist context error: {e}")
            wishlist_count = 0
    else:
        # Session based wishlist for guests
        wishlist_product_ids = request.session.get('wishlist', [])
        wishlist_count = len(wishlist_product_ids)
        
    return {
        'wishlist_count': wishlist_count,
        'wishlist_product_ids': wishlist_product_ids
    }

def cart_context(request):
    """
    Context processor to make cart_count available globally in all templates.
    """
    cart = request.session.get('cart', {})
    cart_count = 0
    try:
        if isinstance(cart, dict):
            for item in cart.values():
                if isinstance(item, dict):
                    cart_count += item.get('quantity', 0)
                elif str(item).isdigit():
                    cart_count += int(item)
    except (TypeError, ValueError, AttributeError, Exception):
        cart_count = 0
        
    return {
        'cart_count': cart_count
    }
