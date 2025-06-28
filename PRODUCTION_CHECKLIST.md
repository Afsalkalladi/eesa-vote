# Production Deployment Checklist

Use this checklist to ensure your EESA Election System is properly configured for production deployment.

## 📋 Pre-Deployment Setup

### 1. GitHub Image Storage
- [ ] Created a dedicated GitHub repository for candidate images
- [ ] Generated a GitHub Personal Access Token with repo permissions
- [ ] Configured environment variables in `.env.github`
- [ ] Tested image upload functionality

### 2. Environment Configuration
- [ ] Copied `.env.example` to `.env.github`
- [ ] Set `DEBUG=False` for production
- [ ] Generated a secure `SECRET_KEY`
- [ ] Configured `GITHUB_TOKEN`
- [ ] Set `GITHUB_IMAGES_REPO` to your image repository
- [ ] Set `USE_GITHUB_STORAGE=true`

### 3. Database Setup
- [ ] Created PostgreSQL database (required for production)
- [ ] Configured `DATABASE_URL` in environment variables
- [ ] Tested database connection

## 🚀 Deployment Steps

### 1. Platform Setup (Render.com example)
- [ ] Created account on deployment platform
- [ ] Connected GitHub repository
- [ ] Created PostgreSQL database service
- [ ] Configured web service with correct build/start commands:
  - **Build Command**: `./build.sh`
  - **Start Command**: `gunicorn election_system.wsgi:application`

### 2. Environment Variables
Set these in your deployment platform:
- [ ] `DJANGO_SETTINGS_MODULE=election_system.production_settings`
- [ ] `DATABASE_URL` (from your PostgreSQL service)
- [ ] `SECRET_KEY` (generate a new secure key)
- [ ] `GITHUB_TOKEN` (your GitHub Personal Access Token)
- [ ] `GITHUB_IMAGES_REPO` (format: username/repo-name)
- [ ] `GITHUB_IMAGES_BRANCH=main`
- [ ] `USE_GITHUB_STORAGE=true`

### 3. Security Configuration
- [ ] `ALLOWED_HOSTS` configured for your domain
- [ ] `CSRF_TRUSTED_ORIGINS` set for your domain
- [ ] SSL/HTTPS enabled
- [ ] Strong admin passwords set

## ✅ Post-Deployment Verification

### 1. Basic Functionality
- [ ] Application loads without errors
- [ ] Admin panel accessible
- [ ] Database migrations completed successfully
- [ ] Static files serving correctly

### 2. Election Features
- [ ] Can create admin user
- [ ] Can import voters from CSV
- [ ] Can import candidates from CSV
- [ ] Can upload candidate photos
- [ ] Voting process works end-to-end
- [ ] Results display correctly

### 3. Image Storage
- [ ] Candidate photos upload to GitHub repository
- [ ] Images display correctly on voting page
- [ ] Images display correctly on results page
- [ ] Fallback images work when no photo uploaded

## 🔧 Troubleshooting

### Common Issues
1. **"msg is too long" error**: Ensure `USE_GITHUB_STORAGE=true` and GitHub variables are set
2. **Images not displaying**: Check GitHub token permissions and repository name
3. **Database errors**: Verify PostgreSQL configuration and migrations
4. **Static files not loading**: Ensure `DEBUG=False` and static files collected

### Debug Commands
```bash
# Check GitHub storage configuration
python manage.py shell -c "from voting.github_storage import github_storage; print(github_storage.test_connection())"

# Verify environment variables
python manage.py shell -c "from django.conf import settings; print(f'GitHub Storage: {settings.USE_GITHUB_STORAGE}')"
```

## 📚 Additional Resources

- [GITHUB_STORAGE_SETUP.md](GITHUB_STORAGE_SETUP.md) - Detailed GitHub setup instructions
- [CLOUD_STORAGE_GUIDE.md](CLOUD_STORAGE_GUIDE.md) - Cloud storage options and configuration
- [README.md](README.md) - Full project documentation

## 🆘 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review the detailed setup guides
3. Verify all environment variables are set correctly
4. Check application logs for specific error messages
