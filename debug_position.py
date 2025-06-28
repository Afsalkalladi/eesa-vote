#!/usr/bin/env python
"""
Debug script to test Position model creation in production.
Run this script on your production server to identify the issue.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, '/opt/render/project/src')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'election_system.production_settings')
django.setup()

from django.utils import timezone
from django.core.exceptions import ValidationError
from voting.models import Position
import traceback

def test_position_creation():
    """Test creating a position to identify the issue."""
    print("🔍 Testing Position model creation...")
    
    try:
        # Test timezone
        print(f"Current timezone: {timezone.get_current_timezone()}")
        print(f"Current time: {timezone.now()}")
        
        # Test creating a simple position
        test_position = Position(
            title="Test Position",
            description="Test description",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=1)
        )
        
        # Test model validation
        print("Testing model validation...")
        test_position.clean()
        print("✅ Model validation passed")
        
        # Test saving (but don't actually save)
        print("Testing model creation (dry run)...")
        # test_position.save()  # Uncomment to actually save
        print("✅ Model creation would succeed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def check_database_connection():
    """Check if database connection is working."""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✅ Database connection working: {result}")
            return True
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False

def check_existing_positions():
    """Check existing positions in database."""
    try:
        positions = Position.objects.all()
        print(f"📊 Existing positions: {positions.count()}")
        for pos in positions[:5]:  # Show first 5
            print(f"  - {pos.title} ({pos.start_time} to {pos.end_time})")
        return True
    except Exception as e:
        print(f"❌ Error querying positions: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 EESA Election System - Position Debug Script")
    print("=" * 50)
    
    print("\n1. Checking database connection...")
    check_database_connection()
    
    print("\n2. Checking existing positions...")
    check_existing_positions()
    
    print("\n3. Testing position creation...")
    success = test_position_creation()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ No issues found in Position model")
        print("The 500 error might be related to:")
        print("  - Admin interface configuration")
        print("  - Static files not loading")
        print("  - CSRF token issues")
        print("  - Database permissions")
    else:
        print("❌ Issue found in Position model")
        print("Check the error details above")
    
    print("\n💡 Next steps:")
    print("  1. Check Render logs for detailed error messages")
    print("  2. Verify all migrations have run")
    print("  3. Check static files are served correctly")
    print("  4. Verify database permissions")
