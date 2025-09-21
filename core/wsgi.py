"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from decouple import config
from django.contrib.auth import get_user_model
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()

# --- Auto create superuser ---
User = get_user_model()
first_name = config("DJANGO_SUPERUSER_FIRST_NAME", default="Admin")
last_name = config("DJANGO_SUPERUSER_LAST_NAME", default="User")
email = config("DJANGO_SUPERUSER_EMAIL", default="admin@ecommerce.com")
password = config("DJANGO_SUPERUSER_PASSWORD", default="Password@123")

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email, 
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
