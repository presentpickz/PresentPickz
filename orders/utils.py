from django.core.mail import send_mail
from django.conf import settings
from .models import DeliveryCharge

def calculate_checkout_total(cart_total, pincode, gift_wrap=False):
    """
    Calculate grand total including delivery and packing charges.
    """
    delivery_charge = 0.0
    
    if pincode:
        # Try to find specific charge for pincode
        charge_obj = DeliveryCharge.objects.filter(pincode=pincode, is_active=True).first()
        if charge_obj:
            delivery_charge = float(charge_obj.charge)
        else:
            # Default charge if no pincode match? 
            # Could be 0 or flat rate. Let's assume Free for now or specific logic.
            # If I don't know, 0 is safest to avoid overcharging without reason.
            delivery_charge = 0.0
    
    # Gift wrap charge (e.g., 30 or 50 INR)
    packing_charge = 50.0 if gift_wrap else 0.0
    
    grand_total = float(cart_total) + delivery_charge + packing_charge
    
    return {
        'grand_total': grand_total,
        'delivery_charge': delivery_charge,
        'packing_charge': packing_charge
    }

def send_order_cancel_email(order):
    subject = f"Order Cancelled #{order.order_id} - Present Pickz"
    
    refund_text = ""
    if order.payment_method == 'ONLINE':
        refund_text = "\nRefund Status: A refund has been initiated to your original payment method. Please allow 5-7 business days for the amount to reflect in your account."
    else:
        refund_text = "\nRefund Status: Not applicable (Pay on Delivery)."

    # Use cancellation note if available to add context? Maybe just reason is fine.
    
    recipient_name = order.full_name if hasattr(order, 'full_name') and order.full_name else (order.user.first_name or "Valued Customer")

    message = f"""Hi {recipient_name},

Your order #{order.order_id} has been successfully cancelled.

Reason: {order.get_cancel_reason_display()}
{refund_text}

If you have any further questions or require assistance, please feel free to contact our support team.

Best Regards,
Present Pickz Team
"""

    # Use order email if present, else user email
    # Assuming order has email field (it usually does for shipping info)
    recipient_email = order.email if hasattr(order, 'email') and order.email else order.user.email

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=True
    )
