#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --settings=election_system.production_settings

# Run migrations
python manage.py migrate --settings=election_system.production_settings

# Create superuser if it doesn't exist (for admin access)
python manage.py shell --settings=election_system.production_settings <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: username=admin, password=admin123')
else:
    print('Superuser already exists')
EOF

echo "Build completed successfully!"
