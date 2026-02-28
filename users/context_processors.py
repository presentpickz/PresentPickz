from users.models import Wishlist

def wishlist_context(request):
    """
    Context processor to make wishlist_count available globally in all templates.
    """
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist_count = wishlist.products.count()
    else:
        # Session based wishlist for guests
        wishlist_ids = request.session.get('wishlist', [])
        wishlist_count = len(wishlist_ids)
        
    return {
        'wishlist_count': wishlist_count
    }

def cart_context(request):
    """
    Context processor to make cart_count available globally in all templates.
    """
    cart = request.session.get('cart', {})
    cart_count = 0
    for item in cart.values():
        cart_count += item.get('quantity', 0)
        
    return {
        'cart_count': cart_count
    }
