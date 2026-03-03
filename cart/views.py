from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from django.contrib import messages

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    # Logic to add item
    cart_id = str(product_id)
    if cart_id in cart:
        cart[cart_id]['quantity'] += 1
    else:
        cart[cart_id] = {
            'quantity': 1,
            'price': str(product.price),
            'name': product.name,
            'image': product.get_image_url(),
        }
    
    # Auto-add Gift Wrap for every product
    cart[cart_id]['gift_wrap'] = True

    request.session['cart'] = cart
    messages.success(request, f"{product.name} added to cart!")
    return redirect('cart:cart')

def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, item_data in cart.items():
        subtotal = float(item_data['price']) * item_data['quantity']
        if item_data.get('gift_wrap'):
            subtotal += 50
        
        item_data['subtotal'] = subtotal
        item_data['id'] = product_id
        cart_items.append(item_data)
        total += subtotal

    return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total': total})

def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart_id = str(product_id)
    action = request.POST.get('action')
    
    if cart_id in cart:
        if action == 'increment':
            cart[cart_id]['quantity'] += 1
        elif action == 'decrement':
            cart[cart_id]['quantity'] -= 1
            if cart[cart_id]['quantity'] <= 0:
                del cart[cart_id]
        elif action == 'remove':
            del cart[cart_id]
            
    request.session['cart'] = cart
    return redirect('cart:cart')

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('products:product_list')
        
    total = 0
    for item in cart.values():
        total += float(item['price']) * item['quantity']
        if item.get('gift_wrap'):
            total += 50
            
    return render(request, 'cart/checkout.html', {'total': total})

def place_order(request):
    if request.method == 'POST':
        # Get form data
        payment_method = request.POST.get('payment', 'UPI')
        
        # Store order info in session (you can save to DB later)
        request.session['last_order'] = {
            'payment_method': payment_method,
        }
        
        # Clear cart
        request.session['cart'] = {}
        
        # Redirect to success page
        return redirect('cart:order_success')
    
    return redirect('cart:checkout')

def order_success(request):
    from datetime import datetime
    
    order_info = request.session.get('last_order', {})
    
    context = {
        'order_date': datetime.now().strftime('%B %d, %Y'),
        'payment_method': order_info.get('payment_method', 'COD'),
    }
    
    return render(request, 'cart/success.html', context)

