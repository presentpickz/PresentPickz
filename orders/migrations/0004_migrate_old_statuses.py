# Generated migration to convert old order statuses to new system

from django.db import migrations


def migrate_old_statuses(apps, schema_editor):
    """
    Convert old order statuses to new standardized statuses
    """
    Order = apps.get_model('orders', 'Order')
    
    # Mapping of old statuses to new statuses
    status_mapping = {
        'Pending': 'PLACED',
        'Payment Pending': 'PLACED',
        'Paid': 'CONFIRMED',
        'Processing': 'CONFIRMED',
        'Shipped': 'SHIPPED',
        'Delivered': 'DELIVERED',
        'Cancelled': 'CANCELLED',
        'Failed': 'CANCELLED',
    }
    
    # Update all orders with old statuses
    for old_status, new_status in status_mapping.items():
        Order.objects.filter(status=old_status).update(status=new_status)
        count = Order.objects.filter(status=new_status).count()
        print(f"Migrated {old_status} → {new_status}")


def reverse_migration(apps, schema_editor):
    """
    Reverse migration - convert new statuses back to old
    (Not recommended - only for rollback)
    """
    Order = apps.get_model('orders', 'Order')
    
    reverse_mapping = {
        'PLACED': 'Pending',
        'CONFIRMED': 'Processing',
        'PACKED': 'Processing',
        'SHIPPED': 'Shipped',
        'OUT_FOR_DELIVERY': 'Shipped',
        'DELIVERED': 'Delivered',
        'CANCELLED': 'Cancelled',
    }
    
    for new_status, old_status in reverse_mapping.items():
        Order.objects.filter(status=new_status).update(status=old_status)


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_order_user'),
    ]

    operations = [
        migrations.RunPython(migrate_old_statuses, reverse_migration),
    ]
