from celery import shared_task
from django.utils import timezone
from .models import Order, DeliveryCode

# Celery tasks for background processing of delivery code expiration and pending order rebroadcasting

# This task checks for delivery codes that have expired (i.e., their expiry time has passed) and deletes them, while also resetting the associated order to 'in_transit' status if the code was not confirmed by either the rider or the customer
@shared_task
def expire_delivery_codes():
    """Expire delivery codes that have passed their expiry time and reset order to in_transit"""
    expired_codes = DeliveryCode.objects.filter(
        expires_at__lt=timezone.now(),
        rider_confirmed=False,
        customer_confirmed=False
    )

    for code in expired_codes:
        order = code.order
        order.current_status = 'in_transit'
        order.save()
        code.delete()

    return f"{expired_codes.count()} expired codes cleaned up"

# This task can be scheduled to run every 10 minutes to check for pending orders that have not been accepted by any rider and flag them for rebroadcasting
@shared_task
def rebroadcast_pending_orders():
    """Flag orders that have been pending for more than 10 minutes with no rider"""
    timeout = timezone.now() - timezone.timedelta(minutes=10)
    
    pending_orders = Order.objects.filter(
        current_status='pending',
        created_at__lt=timeout
    )

    count = pending_orders.count()
    # For now just log — later this triggers a notification
    return f"{count} orders have been pending for more than 10 minutes"