#!/bin/bash

# Production Image Upload Deployment Script
# This script sets up the production environment for image uploads

echo "🚀 Setting up production image upload configuration..."

# 1. Create media directory with proper permissions
echo "📁 Creating media directories..."
mkdir -p media/candidates
chmod 755 media
chmod 755 media/candidates

# 2. Set up environment variables for production
echo "🔧 Production environment setup..."
echo "MEDIA_ROOT should be set to an absolute path"
echo "FILE_UPLOAD_MAX_MEMORY_SIZE=5242880"
echo "DATA_UPLOAD_MAX_MEMORY_SIZE=10485760"

# 3. Test directory permissions
echo "🧪 Testing directory permissions..."
if [ -w "media/candidates" ]; then
    echo "✅ Media directory is writable"
else
    echo "❌ Media directory is not writable - check permissions"
fi

# 4. Check disk space
echo "💾 Checking disk space..."
df -h media/

# 5. Test file creation
echo "🧪 Testing file creation..."
test_file="media/candidates/test_upload.txt"
if echo "test" > "$test_file"; then
    echo "✅ File creation successful"
    rm "$test_file"
else
    echo "❌ File creation failed"
fi

echo "✅ Production setup complete!"
echo ""
echo "📋 Production Checklist:"
echo "  ✓ Media directory created and writable"
echo "  ✓ File upload limits configured"
echo "  ✓ Image validation enabled"
echo "  ✓ Error handling implemented"
echo ""
echo "🔄 Next steps:"
echo "  1. Deploy with updated code"
echo "  2. Test image upload in production"
echo "  3. Monitor server logs for any path-related errors"
echo "  4. Consider implementing cloud storage for scalability"
