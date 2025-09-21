from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Order


@shared_task
def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.get(id=order_id)

        # Render the email content from a template
        subject = f"Order #{order.id} Confirmation"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [order.user.email]
        cc = ["lewismurimi195@gmail.com"]  # optional
        bcc = []  # optional

        # HTML content
        html_content = render_to_string(
            "emails/order_confirmation.html", {"order": order}
        )

        # Plain text fallback
        text_content = (
            f"Hi {order.user.first_name} {order.user.last_name}, "
            f"your order totaling ${order.total_price} has been placed successfully!"
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to,
            cc=cc,
            bcc=bcc,
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

    except Order.DoesNotExist:
        pass
