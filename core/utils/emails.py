from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_email(subject, text_content, html_content, to, cc=None, bcc=None):
    """
    Helper to send email with HTML + plain text fallback.
    """
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
        cc=cc or [],
        bcc=bcc or [],
    )
    if html_content:
        email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)
