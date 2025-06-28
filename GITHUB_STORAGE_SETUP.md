# GitHub Storage Setup Guide

## Overview

This guide shows how to set up free GitHub storage for candidate photos in your Django election system.

## Step 1: Create a GitHub Repository for Images

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it something like `eesa-election-images`
3. Make it **public** (required for direct image serving)
4. Initialize with a README
5. Create a `candidates` folder in the repository

## Step 2: Get a GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "EESA Election Images"
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `public_repo` (Access public repositories)
5. Copy the token (save it securely!)

## Step 3: Configure Environment Variables

Add these to your Render environment variables or `.env` file:

```bash
# GitHub Storage Configuration
GITHUB_TOKEN=your_personal_access_token_here
GITHUB_IMAGES_REPO=yourusername/eesa-election-images
GITHUB_IMAGES_BRANCH=main
USE_GITHUB_STORAGE=true
```

## Step 4: Install Dependencies

```bash
pip install requests
```

## Step 5: Test the Setup

Run the migration command to test:

```bash
python manage.py migrate_photos_to_github --dry-run
```

## Step 6: Upload Images

### Option A: Via Django Admin

1. Upload images normally in the admin
2. They'll automatically be uploaded to GitHub

### Option B: Via CSV Import

Create a CSV with GitHub URLs:

```csv
name,reg_no,description,position,photo_url
John Doe,EE001,Student leader,President,https://raw.githubusercontent.com/yourusername/eesa-election-images/main/candidates/john_doe.jpg
```

### Option C: Migrate Existing Images

```bash
python manage.py migrate_photos_to_github
```

## How It Works

1. **Local Upload**: Images uploaded via admin are saved locally first
2. **GitHub Upload**: The model automatically uploads to GitHub on save
3. **URL Storage**: GitHub raw URL is stored in `photo_url` field
4. **Template Display**: Templates use `candidate.get_photo_url()` which prioritizes GitHub URLs

## Image URLs

Images are served from GitHub at:

```
https://raw.githubusercontent.com/yourusername/eesa-election-images/main/candidates/candidate_ID.jpg
```

## Benefits

- ✅ **100% Free**: No costs for public repositories
- ✅ **Reliable**: GitHub's global CDN infrastructure
- ✅ **Version Control**: All images are versioned
- ✅ **Integration**: Works seamlessly with Render deployment
- ✅ **Backup**: Images are automatically backed up in Git
- ✅ **Scalable**: No storage limits for reasonable use

## Troubleshooting

### Images not uploading

- Check GITHUB_TOKEN is valid
- Verify repository name format: `username/repo-name`
- Ensure repository is public

### Images not displaying

- Check if GitHub URLs are stored in `photo_url` field
- Verify raw URLs are accessible in browser
- Check for typos in repository configuration

### Migration issues

- Run with `--dry-run` first to check configuration
- Check Django logs for detailed error messages
- Ensure candidates have local photos before migration

## Security Notes

- Repository must be public for direct image serving
- Don't store sensitive images in this setup
- Personal access tokens should be kept secure
- Consider using GitHub Apps for production environments
