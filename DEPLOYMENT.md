# Django EESA Election Voting System - Deployment Guide

## Deployment on Render

This guide will help you deploy the Django EESA Election Voting System to Render, a free hosting platform.

### Prerequisites

1. A GitHub account
2. Your project code pushed to a GitHub repository
3. A Render account (free at render.com)

### Step 1: Prepare Your Repository

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - EESA Election Voting System"
   git branch -M main
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. **Create a PostgreSQL Database (Required)**

   - In Render dashboard, click "New +"
   - Select "PostgreSQL"
   - Choose a name: `eesa-election-db`
   - Select "Free" tier
   - Click "Create Database"
   - **Copy the DATABASE_URL** from the database info page
   - **⚠️ IMPORTANT:** The web service will not start without this!

2. **Create a New Web Service**

   - Click "New +" in the top right
   - Select "Web Service"
   - Connect your GitHub repository

3. **Configure the deployment:**

   - **Name:** `eesa-election-system` (or your preferred name)
   - **Environment:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn election_system.wsgi:application --bind 0.0.0.0:$PORT`
   - **Instance Type:** `Free`

4. **Add Environment Variables (Required):**
   Click "Advanced" and add these environment variables:

   - `SECRET_KEY`: Generate a new secret key (use Django's get_random_secret_key())
   - `DJANGO_SETTINGS_MODULE`: `election_system.production_settings`
   - `DATABASE_URL`: [Paste the PostgreSQL DATABASE_URL from step 1] **REQUIRED**
   - `USE_HTTPS`: `true` (optional, for SSL)

5. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

### Step 3: Post-Deployment Setup

1. **Access your application:**

   - Your app will be available at: `https://your-app-name.onrender.com`

2. **Access Django Admin:**

   - Go to: `https://your-app-name.onrender.com/admin/`
   - Login with: username=`admin`, password=`admin123`
   - **IMPORTANT:** Change the admin password immediately!

3. **Import Voters and Set Up Election:**
   - Use the admin interface to import voters from CSV
   - Set up your election positions and candidates
   - Configure voting times

### Step 4: Security Checklist

- [ ] Change the default admin password
- [ ] Generate and set a new SECRET_KEY
- [ ] Review and update ALLOWED_HOSTS if needed
- [ ] Test all functionality on the live site
- [ ] Verify audit trail access is restricted

## 💾 Database Configuration

### Development vs Production

**Development (Local):**

- Uses SQLite database (`db.sqlite3`)
- File-based, simple setup
- Perfect for development and testing

**Production (Render):**

- **Requires PostgreSQL** - SQLite not supported in production
- PostgreSQL provides data persistence and better performance
- Mandatory DATABASE_URL environment variable

### Why PostgreSQL for Production?

- ✅ **Data Persistence**: Survives container restarts and deployments
- ✅ **Concurrent Access**: Better support for multiple voters
- ✅ **Reliability**: Industry-standard database for web applications
- ✅ **Free Tier**: Render provides free PostgreSQL databases
- ❌ **SQLite Limitations**: File-based, lost on container restarts

---

### Troubleshooting

1. **Build Fails:**

   - Check the build logs in Render dashboard
   - Ensure all dependencies are in requirements.txt

2. **Static Files Not Loading:**

   - Check that STATIC_ROOT is set correctly
   - Verify WhiteNoise is configured

3. **Database Issues:**

   - **Missing DATABASE_URL:** Production requires PostgreSQL - create database first
   - **Connection Errors:** Verify DATABASE_URL is correctly copied from Render
   - **Migration Failures:** Ensure PostgreSQL database is accessible

4. **Common Database Problems:**
   - **Build Fails:** Missing DATABASE_URL environment variable
   - **App Won't Start:** PostgreSQL connection failed - check database status
   - **Data Issues:** Ensure migrations run successfully on PostgreSQL

### Monitoring and Maintenance

- **Logs:** View logs in the Render dashboard
- **Uptime:** Free tier has some limitations, consider upgrading for production
- **Backups:** Regularly backup your database and media files

### Upgrading to Paid Plan

For production use, consider upgrading to a paid plan for:

- Better uptime guarantees
- More resources
- Custom domains
- Database backups

---

**Support:** If you need help, check the Render documentation or contact support.
