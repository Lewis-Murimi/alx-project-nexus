"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()

# --- Auto create superuser ---
from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()
username = config("DJANGO_SUPERUSER_USERNAME", default="admin")
email = config("DJANGO_SUPERUSER_EMAIL", default="admin@ecommerce.com")
password = config("DJANGO_SUPERUSER_PASSWORD", default="Password@123")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
