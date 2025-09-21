from celery import shared_task
from django.core.mail import send_mail

from .models import Order


@shared_task
def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.get(id=order_id)
        message = (
            f"Hi {order.user.first_name} {order.user.last_name}, "
            f"your order totaling ${order.total_price} has been placed successfully!"
        )
        send_mail(
            subject=f"Order #{order.id} Confirmation",
            message=message,
            from_email="no-reply@ecommerce.com",
            recipient_list=["lewismurimi195@gmail.com"],
        )
    except Order.DoesNotExist:
        pass
