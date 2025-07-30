#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'admin'
email = 'admin@xcraper.com'
password = 'admin123'

if User.objects.filter(username=username).exists():
    print(f"User '{username}' already exists")
    user = User.objects.get(username=username)
    user.set_password(password)
    user.save()
    print("Password updated successfully")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created successfully")
