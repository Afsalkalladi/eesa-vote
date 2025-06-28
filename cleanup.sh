#!/bin/bash

# Cleanup script for removing development/test files
# Run this before production deployment

echo "🧹 Cleaning up development and test files..."

# Remove test files
echo "📁 Removing test files..."
rm -f test_*.py test_*.html *_test.py *_test.html 2>/dev/null || true

# Remove temporary documentation
echo "📄 Removing temporary documentation..."
rm -f *_FIX*.md *_DEBUG*.md *_TEMP*.md 2>/dev/null || true

# Remove test media files
echo "🖼️ Removing test media files..."
rm -f media/candidates/*TEST*.* media/candidate_photos/*TEST*.* 2>/dev/null || true

# Remove Python cache
echo "🗑️ Removing Python cache..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove logs
echo "📋 Removing log files..."
rm -f *.log 2>/dev/null || true

# Show remaining structure
echo "✅ Cleanup complete!"
echo ""
echo "📁 Current project structure:"
ls -la | grep -E '^d|\.py$|\.md$|\.sh$|\.txt$' | head -20
