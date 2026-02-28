from django.contrib import admin
from .models import Order, OrderItem, DeliveryCharge, Refund

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

class RefundInline(admin.StackedInline):
    model = Refund
    extra = 0
    can_delete = False
    readonly_fields = ['created_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Secure Order Admin - Following Amazon/Flipkart Pattern
    - Admin CANNOT place orders (add disabled)
    - Admin CANNOT delete orders (delete disabled)
    - Admin CAN ONLY update status
    - Orders are immutable audit records
    """
    list_display = ['order_id', 'user', 'full_name', 'status', 'payment_method', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_id', 'full_name', 'email', 'mobile', 'user__username']
    inlines = [OrderItemInline, RefundInline]
    
    # Make most fields readonly - Only status can be changed
    readonly_fields = [
        'user', 'order_id', 'full_name', 'email', 'mobile', 'address',
        'payment_method', 'total_amount', 'delivery_charge', 'packing_charge',
        'gift_wrap', 'gift_message', 'cancelled_by', 'cancel_reason',
        'cf_order_id', 'payment_id', 'created_at', 'updated_at'
    ]
    
    # Only allow editing status field
    fields = [
        'user', 'order_id', 'status', 'cancelled_by', 'cancel_reason',
        'full_name', 'email', 'mobile', 'address',
        'payment_method', 'total_amount', 'delivery_charge', 'packing_charge',
        'gift_wrap', 'gift_message',
        'cf_order_id', 'payment_id', 'created_at', 'updated_at'
    ]
    
    # Disable bulk delete action
    actions = None
    
    # Security Methods
    def has_add_permission(self, request):
        """Admin CANNOT place orders - Users place orders through frontend"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Admin CANNOT delete orders - Orders are audit-safe immutable records"""
        return False
    
    def get_readonly_fields(self, request, obj=None):
        """
        Lock delivered and cancelled orders completely
        Only allow status updates for active orders
        """
        if obj:  # Editing existing order
            if obj.status in ['DELIVERED', 'CANCELLED']:
                # Delivered/Cancelled orders are completely locked
                return self.readonly_fields + ['status']  # Convert tuple to list
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        """
        Override save to enforce status transition rules
        """
        if change:  # Only for updates
            # Get original object from database
            try:
                original = Order.objects.get(pk=obj.pk)
                
                # Import status validation
                from .status_utils import can_update_status
                
                # Check if status changed
                if original.status != obj.status:
                    # Validate transition
                    if not can_update_status(original.status, obj.status):
                        from django.contrib import messages
                        messages.error(
                            request,
                            f"Invalid status transition from {original.get_status_display()} to {obj.get_status_display()}"
                        )
                        # Revert to original status
                        obj.status = original.status
                    
                    # Prevent changes to delivered/cancelled orders
                    if original.status in ['DELIVERED', 'CANCELLED']:
                        from django.contrib import messages
                        messages.error(request, "Cannot modify delivered or cancelled orders")
                        obj.status = original.status
            except Order.DoesNotExist:
                pass
        
        super().save_model(request, obj, form, change)

@admin.register(DeliveryCharge)
class DeliveryChargeAdmin(admin.ModelAdmin):
    list_display = ['location_name', 'pincode', 'charge', 'is_active']
    search_fields = ['location_name', 'pincode']
    list_filter = ['is_active']
    list_editable = ['charge', 'is_active']

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_id', 'order__email']
    readonly_fields = ['amount', 'created_at', 'order']
    list_editable = ['status']
