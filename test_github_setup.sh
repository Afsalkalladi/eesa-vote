#!/bin/bash

# Test GitHub Storage Setup
# Replace these with your actual values before running

echo "🧪 Testing GitHub Storage Setup..."

# Set environment variables (replace with your actual values)
export GITHUB_TOKEN="your_token_here"
export GITHUB_IMAGES_REPO="yourusername/eesa-election-images" 
export GITHUB_IMAGES_BRANCH="main"
export USE_GITHUB_STORAGE="true"

echo "Environment variables set:"
echo "GITHUB_REPO: $GITHUB_IMAGES_REPO"
echo "USE_GITHUB_STORAGE: $USE_GITHUB_STORAGE"

# Test the migration command
echo ""
echo "Testing migration command..."
python manage.py migrate_photos_to_github --dry-run

echo ""
echo "If you see candidate photos listed above, the setup is working!"
echo "Remove --dry-run to actually migrate photos to GitHub."
