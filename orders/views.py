from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Order, OrderItem
from products.models import Product
from .cashfree_client import CashfreeClient
import uuid

def place_order(request):
    if request.method != 'POST':
        return redirect('cart:checkout')

    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('products:product_list')

    # Get Form Data
    full_name = request.POST.get('full_name')
    mobile = request.POST.get('mobile')
    email = request.POST.get('email', '')
    address = request.POST.get('address')
    pincode = request.POST.get('pincode')  # New field
    payment_method = request.POST.get('payment')
    
    # Gift Options
    gift_wrap = request.POST.get('gift_wrap') == 'on'
    gift_message = request.POST.get('gift_message', '')

    # Calculate Totals
    cart_total = 0
    for item in cart.values():
        val = float(item['price']) * item['quantity']
        cart_total += val
    
    # Calculate Charges
    from .utils import calculate_checkout_total
    totals = calculate_checkout_total(cart_total, pincode, gift_wrap)
    
    total_amount = totals['grand_total']
    delivery_charge = totals['delivery_charge']
    packing_charge = totals['packing_charge']

    # Create Order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        full_name=full_name,
        mobile=mobile,
        email=email,
        address=address,
        payment_method='ONLINE' if payment_method == 'UPI' else 'COD',
        total_amount=total_amount,
        delivery_charge=delivery_charge,
        packing_charge=packing_charge,
        gift_wrap=gift_wrap,
        gift_message=gift_message,
        status='PLACED'
    )

    # Create Items
    for product_id, item_data in cart.items():
        product = Product.objects.get(id=product_id)
        OrderItem.objects.create(
            order=order,
            product=product,
            price=item_data['price'],
            quantity=item_data['quantity']
        )

    # Clear Cart if COD (For Online, we clear after success or keep it until confirmed? usually clear after creating order to avoid duplicates)
    # Standard: Clear cart after order creation.
    request.session['cart'] = {}

    if payment_method == 'COD':
        order.status = 'PLACED'
        order.save()
        messages.success(request, "Order placed successfully!")
        return redirect('orders:order_success', order_id=order.order_id)
    
    else:
        # Initializing Cashfree Payment
        client = CashfreeClient()
        domain = request.build_absolute_uri('/')[:-1] # Get base domain
        return_url = f"{domain}{reverse('orders:payment_return')}?order_id={order.order_id}"
        
        # Customer ID (use mobile or unique hash)
        customer_id = f"CUST_{mobile}"
        
        resp = client.create_order(
            order_id=order.order_id,
            amount=total_amount,
            customer_id=customer_id,
            customer_phone=mobile,
            return_url=return_url
        )

        if "payment_session_id" in resp:
            # For embedded checkout or seamless, we might need just the session ID.
            # However, for a simple redirection flow, Cashfree usually provides a link or we use the payments page.
            # Cashfree's new API often uses a payment_session_id to render a drop-in JS or redirect.
            # IF using redirect flow, we might need to construct the URL or use the response `payment_link` if available (depends on API version).
            # The '2022-09-01' API returns 'payment_session_id'. We typically need to render a page that auto-submits or redirects.
            # But wait, looking at standard integrations, usually you redirect to `cf_link` or use the JS SDK.
            # Let's check the response structure for `payments` -> `url` or similar.
            
            # Since I cannot easily debug headers/response structures in this environment, I'll use the check logic.
            # If 'payment_link' is not directly there, we should assume we need to use the checkout UI.
            # However, for this task, I will assume we can redirect to the 'payment_link' if provided, or render a page with the JS SDK.
            
            # Let's try to see if there is a payment_link. 
            # If not, I will render a template that uses the Cashfree JS SDK with the session ID.
            
            if "payment_link" in resp:
                 return redirect(resp['payment_link'])
            
            # Fallback: Render a pay page
            return render(request, 'orders/pay.html', {
                'payment_session_id': resp['payment_session_id'],
                'order': order,
                'env': 'TEST' # Should match settings
            })

        else:
            messages.error(request, "Error communicating with payment gateway.")
            order.status = "Failed"
            order.save()
            return redirect('cart:checkout')

def payment_return(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, order_id=order_id)

    # Verify logic
    client = CashfreeClient()
    verification = client.verify_order(order_id)
    
    if verification and verification.get('order_status') == 'PAID':
        order.status = 'CONFIRMED'
        order.save()
        return redirect('orders:order_success', order_id=order_id)
    else:
        order.status = 'CANCELLED' # Or keep as Failed? 'CANCELLED' is generic.
        # User request says: "If not allowed... show message".
        # Valid statuses: PLACED, CONFIRMED...
        # If payment fails, order is basically Cancelled or Pending Payment.
        # 'Failed' works if I handle it. But to be safe with choices:
        # I'll use 'CANCELLED' or 'PLACED' (to retry?).
        # For now, I'll stick to 'CONFIRMED' for success.
        order.status = 'CANCELLED' # Failed payment = Cancelled order usually.
        order.save()
        messages.error(request, "Payment failed or was cancelled.")
        return redirect('cart:checkout')

def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'orders/success.html', {'order': order})

from django.contrib.auth.decorators import login_required

@login_required
def my_orders(request):
    """Display user's order history with real-time status tracking"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    """Display detailed order information with status timeline"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

def track_order(request):
    """Order Tracking with Security"""
    if request.method == 'GET' and 'order_id' in request.GET:
        order_id = request.GET.get('order_id')
        email = request.GET.get('email', '').strip()
        mobile = request.GET.get('mobile', '').strip()
        
        try:
            # If logged in user, check if they own this order
            if request.user.is_authenticated:
                order = Order.objects.filter(order_id=order_id, user=request.user).first()
                if order:
                    return redirect('orders:order_detail', order_id=order_id)
                else:
                    messages.error(request, 'This order does not belong to your account.')
                    return render(request, 'orders/track_order.html')
            
            # For non-authenticated users, require email OR mobile verification
            if not email and not mobile:
                messages.error(request, 'Please enter your email or mobile number to track this order.')
                return render(request, 'orders/track_order.html', {'order_id': order_id})
            
            # Try to find order with matching order_id AND (email OR mobile)
            order = None
            if email and mobile:
                # Both provided - match either
                order = Order.objects.filter(
                    order_id=order_id
                ).filter(
                    Q(email__iexact=email) | Q(mobile=mobile)
                ).first()
            elif email:
                order = Order.objects.filter(order_id=order_id, email__iexact=email).first()
            elif mobile:
                order = Order.objects.filter(order_id=order_id, mobile=mobile).first()
            
            if not order:
                messages.error(request, 'Order not found or the email/mobile number does not match our records.')
                return render(request, 'orders/track_order.html', {'order_id': order_id})
            
            return render(request, 'orders/track_order_result.html', {'order': order})
            
        except Exception as e:
            messages.error(request, 'An error occurred while tracking your order.')
            return render(request, 'orders/track_order.html')
    
    return render(request, 'orders/track_order.html')

@login_required
def cancel_order(request, order_id):
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('orders:my_orders')
        
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    if order.status not in ['PLACED', 'CONFIRMED', 'Paid', 'Processing']:
        messages.error(request, 'This order can no longer be cancelled.')
        return redirect('orders:my_orders')

    reason = request.POST.get('cancel_reason')
    if not reason:
        # If no reason provided (e.g. from old form), just default or error?
        # User requested MANDATORY reason.
        messages.error(request, 'Please select a cancellation reason.')
        # Redirect back to where they came from? Hard to know exactly, usually logic is simpler.
        return redirect('orders:my_orders') 

    # Restore Stock
    for item in order.items.all():
        if item.product:
            item.product.stock += item.quantity
            item.product.save()

    order.status = 'CANCELLED'
    order.cancelled_by = 'USER'
    order.cancel_reason = reason
    order.cancellation_note = request.POST.get('cancellation_note', '')
    order.save()
    
    # Create Refund if not COD
    if order.payment_method != 'COD':
        from .models import Refund
        # Check if exists (idempotency)
        if not hasattr(order, 'refund'):
            Refund.objects.create(order=order, amount=order.total_amount)
    
    # Send Email
    try:
        from .utils import send_order_cancel_email
        send_order_cancel_email(order)
    except Exception as e:
        print(f"Email failed: {e}")

    msg = 'Order cancelled successfully.'
    if order.payment_method == 'ONLINE':
        msg += ' A refund has been initiated (5-7 business days).'
        
    messages.success(request, msg)
    return redirect('orders:my_orders')

from django.http import JsonResponse

def check_pincode(request):
    """API endpoint to check delivery charge for a pincode"""
    pincode = request.GET.get('pincode', '')
    cart_total = request.GET.get('cart_total', 0)
    
    try:
        cart_total = float(cart_total)
    except ValueError:
        cart_total = 0.0

    from .utils import calculate_checkout_total
    totals = calculate_checkout_total(cart_total, pincode, gift_wrap=False)
    
    return JsonResponse({
        'delivery_charge': totals['delivery_charge']
    })

@login_required
def rate_review(request, order_id):
    """Page to list items in order for review"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    if order.status != 'DELIVERED':
        messages.error(request, "You can only rate delivered orders.")
        return redirect('orders:my_orders')

    return render(request, 'orders/rate_review.html', {'order': order})

@login_required
def submit_review(request, order_id, product_id):
    """Handle review submission for a specific product in an order"""
    if request.method != 'POST':
        return redirect('orders:rate_review', order_id=order_id)
        
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    from products.models import Product, Review
    product = get_object_or_404(Product, id=product_id)
    
    # Check if purchased in this order
    if not order.items.filter(product=product).exists():
        messages.error(request, "Invalid product for this order.")
        return redirect('orders:rate_review', order_id=order_id)
        
    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '')
    
    if not rating:
        messages.error(request, "Please select a star rating.")
        return redirect('orders:rate_review', order_id=order_id)
        
    # Create or Update Review
    Review.objects.update_or_create(
        user=request.user,
        product=product,
        order=order,
        defaults={
            'rating': int(rating),
            'comment': comment
        }
    )
    
    messages.success(request, "Review submitted successfully!")
    return redirect('orders:rate_review', order_id=order_id)

def mock_payment(request, order_id):
    """Mock payment page for development"""
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'orders/mock_pay.html', {'order': order})

@login_required
def download_invoice(request, order_id):
    """
    Render invoice for printing/download.
    """
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'orders/invoice.html', {'order': order})

