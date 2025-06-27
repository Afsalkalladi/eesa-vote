#!/usr/bin/env python
"""
Generate a secure Django secret key for production deployment.
"""
from django.core.management.utils import get_random_secret_key

print("Generated Django Secret Key:")
print(get_random_secret_key())
print("\nUse this key in your Render environment variables as SECRET_KEY")
