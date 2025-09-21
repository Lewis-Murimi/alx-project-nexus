from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@shared_task
def send_password_reset_email(
        user_email, reset_link, full_name=None, cc=None, bcc=None
):
    """
    Send password reset email asynchronously in HTML format.

    Args:
        user_email (str): recipient email
        reset_link (str): password reset link
        full_name (str, optional): user's full name
        cc (list, optional): list of CC emails
        bcc (list, optional): list of BCC emails
    """
    name = full_name or "User"

    subject = "Password Reset Request"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user_email]

    # Optional CC/BCC
    cc = cc or ["lewismurimi195@gmail.com"]
    bcc = bcc or []

    # Render HTML content from template
    html_content = render_to_string(
        "emails/password_reset.html", {"name": name, "reset_link": reset_link}
    )

    # Plain-text fallback
    text_content = (
        f"Hi {name},\n\n"
        f"Click the link below to reset your password:\n{reset_link}\n\n"
        f"If you did not request this, please ignore this email."
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
