from celery import shared_task
from django.template.loader import render_to_string

from core.utils.emails import send_email
from .models import Order


@shared_task(bind=True, ignore_result=True)
def send_order_confirmation_email(self, order_id):
    """
    Send order confirmation email (async if worker available,
    otherwise synchronous fallback).
    """
    try:
        order = Order.objects.get(id=order_id)

        subject = f"Order #{order.id} Confirmation"
        to = [order.user.email]
        cc = ["lewismurimi195@gmail.com"]  # optional

        html_content = render_to_string(
            "emails/order_confirmation.html", {"order": order}
        )
        text_content = (
            f"Hi {order.user.first_name} {order.user.last_name}, "
            f"your order totaling ${order.total_price} has been placed successfully!"
        )

        send_email(subject, text_content, html_content, to, cc=cc)

    except Order.DoesNotExist:
        return "Order not found"
