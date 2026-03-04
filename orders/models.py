from django.db import models
from django.conf import settings
from products.models import Product

class DeliveryCharge(models.Model):
    """
    Configuration for location-based delivery charges.
    Admin controlled.
    """
    location_name = models.CharField(max_length=100)  # City / Zone
    pincode = models.CharField(max_length=10, unique=True)
    charge = models.DecimalField(max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.location_name} ({self.pincode}) - ₹{self.charge}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('PLACED', 'Order Placed'),
        ('CONFIRMED', 'Order Confirmed'),
        ('PACKED', 'Packed'),
        ('SHIPPED', 'Shipped'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('ONLINE', 'Online Payment (Cashfree)'),
    )

    # User (for order tracking) - PROTECT prevents accidental user deletion
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    
    # Customer Details
    full_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    
    # Order Details
    order_id = models.CharField(max_length=100, unique=True, blank=True) # Cashfree or Internal ID
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLACED')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='COD')
    
    # Financials
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    packing_charge = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    @property
    def get_subtotal(self):
        return self.total_amount - self.delivery_charge - self.packing_charge
    
    # Gift Options
    gift_wrap = models.BooleanField(default=False)
    gift_message = models.CharField(max_length=200, blank=True)
    
    # Audit
    cancelled_by = models.CharField(
        max_length=10,
        choices=[('USER', 'User'), ('ADMIN', 'Admin')],
        blank=True,
        null=True
    )

    CANCEL_REASON_CHOICES = [
        ('CHANGED_MIND', 'Changed my mind'),
        ('WRONG_ITEM', 'Ordered wrong item'),
        ('DELAYED', 'Delivery taking too long'),
        ('FOUND_CHEAPER', 'Found cheaper elsewhere'),
        ('STOCK_ISSUE', 'Stock unavailable'),
        ('OTHER', 'Other'),
    ]

    cancel_reason = models.CharField(
        max_length=30,
        choices=CANCEL_REASON_CHOICES,
        blank=True,
        null=True
    )
    cancellation_note = models.TextField(blank=True, null=True, help_text="Custom reason if Other selected")
    
    # Payment Details (Cashfree)
    cf_order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_id} - {self.full_name}"

    def decrement_stock(self):
        """Decrease product stock for all items in this order"""
        for item in self.items.all():
            product = item.product
            # Only subtract if stock > 0
            if product.stock >= item.quantity:
                product.stock -= item.quantity
                product.save()

    def increment_stock(self):
        """Increase product stock for all items (e.g., on cancellation)"""
        for item in self.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()

    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate a simple order ID if not present
            import uuid
            self.order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def get_status_instruction(self):
        """Return user-friendly instruction based on status"""
        instructions = {
            'PLACED': 'Your order has been placed successfully.',
            'CONFIRMED': 'Your order has been confirmed and is being prepared.',
            'PACKED': 'Your items are packed and ready to ship.',
            'SHIPPED': 'Your order has been shipped.',
            'OUT_FOR_DELIVERY': 'Out for delivery. Expected today.',
            'DELIVERED': 'Order delivered successfully.',
            'CANCELLED': 'This order has been cancelled.',
        }
        return instructions.get(self.status, '')
    
    def get_status_progress(self):
        """Return progress percentage for status bar"""
        progress_map = {
            'PLACED': 16,
            'CONFIRMED': 33,
            'PACKED': 50,
            'SHIPPED': 66,
            'OUT_FOR_DELIVERY': 83,
            'DELIVERED': 100,
            'CANCELLED': 0,
        }
        return progress_map.get(self.status, 0)



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    # Gift Options
    is_gift_wrapped = models.BooleanField(default=False)
    gift_message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Unknown'}"

    @property
    def get_cost(self):
        return self.price * self.quantity
        
    @property
    def is_reviewed(self):
        """Check if this item has been reviewed"""
        # We need to import Review here to avoid circular imports
        from products.models import Review
        return Review.objects.filter(
            order=self.order,
            product=self.product,
            user=self.order.user
        ).exists()

class Refund(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Refund Initiated'),
        ('PROCESSING', 'Refund Processing'),
        ('COMPLETED', 'Refund Completed'),
        ('FAILED', 'Refund Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name='refund')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Refund {self.order.order_id} - {self.status}"
