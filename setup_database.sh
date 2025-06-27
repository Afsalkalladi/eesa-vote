#!/usr/bin/env bash
# Database setup script for production deployment
# Requires PostgreSQL DATABASE_URL environment variable

echo "🔄 Setting up PostgreSQL database for production..."

# Set production settings
export DJANGO_SETTINGS_MODULE=election_system.production_settings

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable is required!"
    echo "Please create a PostgreSQL database on Render and set DATABASE_URL"
    echo "Example: DATABASE_URL=postgresql://user:pass@host:port/dbname"
    exit 1
fi

echo "✅ DATABASE_URL found"

# Check database connection
echo "📋 Checking database configuration..."
python manage.py check --database default

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Setting up admin user..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@eesa.org', 'admin123')
    print('✅ Admin user created: admin/admin123')
else:
    print('ℹ️  Admin user already exists')
EOF

# Show database status
echo "📊 Database setup complete!"
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
from voting.models import Position, Candidate, Voter
User = get_user_model()
print(f"Admin users: {User.objects.filter(is_superuser=True).count()}")
print(f"Positions: {Position.objects.count()}")
print(f"Candidates: {Candidate.objects.count()}")
print(f"Voters: {Voter.objects.count()}")
EOF

echo "🎉 Database ready for EESA elections!"
