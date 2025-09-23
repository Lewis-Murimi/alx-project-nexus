from celery import shared_task
from django.template.loader import render_to_string

from core.utils.emails import send_email


@shared_task(bind=True, ignore_result=True)
def send_password_reset_email(
        self, user_email, reset_link, full_name=None, cc=None, bcc=None
):
    """
    Send password reset email (async if worker available,
    otherwise synchronous fallback).
    """
    name = full_name or "User"

    subject = "Password Reset Request"
    to = [user_email]
    cc = cc or ["lewismurimi195@gmail.com"]

    html_content = render_to_string(
        "emails/password_reset.html", {"name": name, "reset_link": reset_link}
    )
    text_content = (
        f"Hi {name},\n\n"
        f"Click the link below to reset your password:\n{reset_link}\n\n"
        f"If you did not request this, please ignore this email."
    )

    send_email(subject, text_content, html_content, to, cc=cc, bcc=bcc)
