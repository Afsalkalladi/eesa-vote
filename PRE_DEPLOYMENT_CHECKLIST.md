# Pre-Deployment Checklist

## ✅ Files Created for Deployment

- [x] `production_settings.py` - Production Django settings
- [x] `build.sh` - Render build script
- [x] `Procfile` - Process configuration for Render
- [x] `runtime.txt` - Python version specification
- [x] `requirements.txt` - Updated with gunicorn and whitenoise
- [x] `generate_secret_key.py` - Secret key generator
- [x] `DEPLOYMENT.md` - Detailed deployment guide

## ⚠️ Before Deployment

### 1. Repository Preparation

- [ ] Push all code to GitHub
- [ ] Ensure `.gitignore` excludes sensitive files
- [ ] Verify all tests pass: `python manage.py test`

### 2. Security Configuration

- [ ] Generate new SECRET_KEY using `python generate_secret_key.py`
- [ ] Review ALLOWED_HOSTS in production_settings.py
- [ ] Ensure admin default password will be changed post-deployment

### 3. Content Preparation

- [ ] Have your voter CSV file ready for import
- [ ] Plan your election positions and candidates
- [ ] Set appropriate voting time windows

## 🚀 Deployment Steps

### On Render.com:

1. **Create PostgreSQL Database (Required First)**

   - Render Dashboard → "New +" → "PostgreSQL"
   - Name: `eesa-election-db`
   - Copy the DATABASE_URL (starts with `postgresql://`)

2. **Create Web Service**

   - Connect GitHub repository
   - Set build command: `./build.sh`
   - Set start command: `gunicorn election_system.wsgi:application --bind 0.0.0.0:$PORT`

3. **Environment Variables (All Required)**

   - `DJANGO_SETTINGS_MODULE`: `election_system.production_settings`
   - `SECRET_KEY`: [Generated secure key]
   - `DATABASE_URL`: [PostgreSQL URL from step 1] **REQUIRED**
   - `USE_HTTPS`: `true` (optional)

4. **Deploy & Verify**
   - Wait for build to complete
   - Test main functionality
   - Access admin panel
   - Change default admin password

## 📋 Post-Deployment Tasks

### Immediate (Within 1 hour)

- [ ] Change admin password from default
- [ ] Test voting workflow end-to-end
- [ ] Import voter data via admin
- [ ] Set up election positions and candidates
- [ ] Configure voting time windows

### First Week

- [ ] Monitor application logs
- [ ] Test with sample voters
- [ ] Verify audit trail functionality
- [ ] Check mobile responsiveness
- [ ] Share voting links with test users

### Ongoing

- [ ] Regular database backups (if using external DB)
- [ ] Monitor application performance
- [ ] Update voter lists as needed
- [ ] Review security logs periodically

## 🔧 Troubleshooting

### Common Issues:

1. **Static files not loading**: Check WhiteNoise configuration
2. **Admin panel not accessible**: Verify staff_member_required permissions
3. **Database errors**: Ensure migrations run successfully
4. **Environment variables**: Double-check all required env vars are set

### Support Resources:

- Render Documentation: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/5.2/howto/deployment/
- Project Issues: [Your GitHub Issues Page]

---

**Ready to deploy? Follow the steps in [DEPLOYMENT.md](DEPLOYMENT.md)!**
