# GitHub Storage Setup Checklist

## ✅ Setup Checklist

### 1. GitHub Repository

- [ ] Created public repository (e.g., `eesa-election-images`)
- [ ] Added `candidates/` folder
- [ ] Repository is public (required for image serving)

### 2. GitHub Token

- [ ] Generated Personal Access Token (classic)
- [ ] Selected `repo` and `public_repo` scopes
- [ ] Copied token securely

### 3. Environment Variables (Render)

- [ ] GITHUB_TOKEN = your_token_here
- [ ] GITHUB_IMAGES_REPO = username/repo-name
- [ ] GITHUB_IMAGES_BRANCH = main
- [ ] USE_GITHUB_STORAGE = true

### 4. Test Setup

- [ ] Run: `python manage.py migrate_photos_to_github --dry-run`
- [ ] Should show candidates with photos (if any exist)

### 5. Production Deployment

- [ ] Deploy to Render with new environment variables
- [ ] Test uploading a candidate photo via admin
- [ ] Verify image appears from GitHub URL

## 🔍 Troubleshooting

### "GitHub storage is not configured"

- Check environment variables are set correctly
- Verify token has correct permissions

### "404 Not Found" for images

- Ensure repository is public
- Check repository name format: `username/repo-name`
- Verify image exists in GitHub repository

### Upload failures

- Check token permissions
- Verify repository exists and is accessible
- Check network connectivity

## 📱 Example URLs

After setup, images will be served from:

```
https://raw.githubusercontent.com/username/eesa-election-images/main/candidates/candidate_EE001.jpg
```

## 🎉 Benefits

- ✅ Free forever
- ✅ Fast global CDN
- ✅ Version controlled
- ✅ Integrated with your deployment
- ✅ No more "msg is too long" errors!
