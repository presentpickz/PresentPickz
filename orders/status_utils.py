"""
Order status transition logic
Ensures status updates follow allowed paths only
"""

# Allowed status transitions (Flipkart/Amazon pattern)
ALLOWED_TRANSITIONS = {
    'PLACED': ['CONFIRMED', 'CANCELLED'],
    'Processing': ['CONFIRMED', 'CANCELLED'],  # Handle legacy/COD status
    'CONFIRMED': ['PACKED', 'CANCELLED'],
    'PACKED': ['SHIPPED'],
    'SHIPPED': ['OUT_FOR_DELIVERY'],
    'OUT_FOR_DELIVERY': ['DELIVERED'],
    'DELIVERED': [],  # Final state
    'CANCELLED': [],  # Final state
}


def can_update_status(current_status, new_status):
    """
    Check if status transition is allowed
    
    Args:
        current_status (str): Current order status
        new_status (str): Desired new status
    
    Returns:
        bool: True if transition is allowed, False otherwise
    """
    return new_status in ALLOWED_TRANSITIONS.get(current_status, [])


def update_order_status(order, new_status, is_admin=False):
    """
    Safely update order status with validation (ADMIN ONLY)
    
    Args:
        order (Order): Order instance
        new_status (str): New status to set
        is_admin (bool): Whether the user is an admin
    
    Returns:
        bool: True if update successful, False otherwise
    """
    # Only admins can update status
    if not is_admin:
        return False
    
    # Delivered orders are locked and cannot be changed
    if order.status == 'DELIVERED':
        return False
    
    # Cancelled orders cannot be changed
    if order.status == 'CANCELLED':
        return False
    
    # Check if transition is allowed
    if can_update_status(order.status, new_status):
        order.status = new_status
        order.save()
        return True
    
    return False


def get_next_allowed_statuses(current_status):
    """
    Get list of allowed next statuses for current status
    
    Args:
        current_status (str): Current order status
    
    Returns:
        list: List of allowed next statuses
    """
    return ALLOWED_TRANSITIONS.get(current_status, [])
