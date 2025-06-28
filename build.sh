#!/usr/bin/env bash
# Build script for production deployment
# This script is used by platforms like Render.com

set -o errexit  # Exit on error

echo "🚀 Starting production build..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🗄️ Running database migrations..."
python manage.py migrate

echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed successfully!"
