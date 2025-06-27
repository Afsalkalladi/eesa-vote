# EESA Election Voting System

A secure, token-based online election system built for the Electrical Engineering Students Association (EESA) using Django. Supports multiple positions, time-limited voting, and anonymous-looking but auditable vote logging.

## 🎯 Features

### Core Functionality

- **Token-based Authentication**: Voters use unique UUID tokens for secure access
- **Multiple Position Elections**: Support for various positions (President, Secretary, etc.)
- **Time-Limited Voting**: Each position has configurable start/end times
- **Anonymous Voting**: Public-facing votes appear anonymous while maintaining audit trails
- **Real-time Results**: Live results with auto-refresh functionality
- **Final Results Display**: Clean presentation of winners and detailed statistics

### Security & Audit

- **Vote Auditing**: Complete audit trail for fraud detection (admin-only access)
- **One-time Tokens**: Each token can only be used once
- **IP Logging**: Track voting source for security analysis
- **Secure Session Management**: Robust authentication system
- **CSRF Protection**: Built-in Django security features

### Admin Tools

- **CSV Import/Export**: Bulk voter management
- **Token Generation**: Automatic secure token creation
- **Candidate Management**: Easy candidate setup for multiple positions
- **Election Settings**: Configurable election parameters
- **Results Analytics**: Comprehensive voting statistics

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Django 5.2+
- Pillow (for image handling)
- **Development**: SQLite (included with Python)
- **Production**: PostgreSQL (required)

### Installation

1. **Clone and Setup**

   ```bash
   cd /path/to/your/project
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install django pillow
   ```

2. **Database Setup**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Admin User**

   ```bash
   python manage.py createsuperuser
   ```

4. **Import Sample Voters** (Optional)

   ```bash
   python manage.py import_voters sample_voters.csv
   ```

5. **Start Development Server**

   ```bash
   python manage.py runserver
   ```

6. **Access the System**
   - Main Site: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## 📋 Usage Guide

### Setting Up an Election

1. **Access Admin Panel**

   - Go to http://127.0.0.1:8000/admin/
   - Login with your superuser credentials

2. **Configure Election Settings**

   - Navigate to "Election Settings"
   - Set election title, description, and display preferences

3. **Create Positions**

   - Add positions (e.g., President, Secretary)
   - Set voting start and end times for each position
   - Add descriptions for each role

4. **Add Candidates**

   - Create candidate profiles
   - Assign candidates to one or more positions
   - Optionally add photos and biographies

5. **Import Voters**
   - Use CSV import feature or management command
   - Format: `name,reg_no`
   - Tokens are automatically generated

### Voter Experience

1. **Access Voting**

   - Visit the main site
   - Enter the provided token
   - System validates token and shows available positions

2. **Cast Votes**

   - Select one candidate per position
   - Option to abstain from specific positions
   - Review selections before submitting

3. **View Results**
   - Live results during voting (if enabled)
   - Final results after voting ends
   - Anonymous presentation of vote counts

### Administrative Tasks

#### Import Voters from CSV

```bash
python manage.py import_voters voters.csv --update
```

#### Export Voter Tokens

```bash
python manage.py export_voters tokens.csv --tokens-only
```

#### Export Full Voter Data

```bash
python manage.py export_voters full_export.csv --include-voted
```

## 🗄️ Database Models

### Core Models

- **Voter**: Stores voter information and authentication tokens
- **Position**: Election positions with voting time windows
- **Candidate**: Candidate profiles linked to positions
- **Vote**: Individual vote records with audit information
- **ElectionSettings**: Global election configuration

### Key Relationships

- Voters → Votes (one-to-many)
- Positions → Votes (one-to-many)
- Candidates → Votes (one-to-many)
- Candidates ↔ Positions (many-to-many)

## 🛡️ Security Features

### Authentication

- UUID-based token system
- Session-based voter authentication
- One-time token usage enforcement

### Data Protection

- Anonymous public results
- Encrypted vote storage
- Audit trail access controls
- IP address logging

### Access Controls

- Staff-only admin access
- Technical head audit permissions
- CSRF protection on all forms
- Rate limiting considerations

## 🎨 Frontend Features

### Design

- Bootstrap 5 responsive design
- Modern gradient backgrounds
- Interactive UI elements
- Mobile-friendly interface

### User Experience

- Real-time form validation
- Loading states and feedback
- Auto-refresh capabilities
- Accessibility features

### Key Pages

- **Home**: Token login and election information
- **Voting**: Interactive candidate selection
- **Results**: Live and final result displays
- **Admin**: Comprehensive management interface

## 📊 API Endpoints

### Public Endpoints

- `/` - Home page with login
- `/vote/` - Voting interface
- `/live-results/` - Live results display
- `/final-results/` - Final results page

### API Endpoints

- `/api/live-results/` - JSON results data
- `/submit-vote/` - Vote submission (POST)

### Admin Endpoints

- `/admin/` - Django admin interface
- `/audit/` - Vote audit trail (restricted)
- `/export-voters/` - CSV export
- `/import-voters/` - CSV import

## 🔧 Configuration

### Election Settings

```python
# Configure in Django admin or via code
settings = ElectionSettings.get_settings()
settings.election_title = "Class Election 2025"
settings.show_live_results = True
settings.results_refresh_interval = 30  # seconds
settings.save()
```

### Environment Variables

```bash
# Optional: Set in production
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=your-database-url
```

## 📁 Project Structure

```
vote/
├── election_system/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── voting/                   # Main voting app
│   ├── models.py            # Database models
│   ├── views.py             # Business logic
│   ├── admin.py             # Admin interface
│   ├── urls.py              # URL routing
│   └── management/          # Custom commands
│       └── commands/
│           ├── import_voters.py
│           └── export_voters.py
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   └── voting/             # Voting-specific templates
└── static/                 # Static files (CSS, JS, images)
```

## 🚀 Deployment Considerations

### Production Settings

- Set `DEBUG = False`
- Configure proper `SECRET_KEY`
- Use production database (PostgreSQL recommended)
- Set up static file serving
- Configure HTTPS

### Security Checklist

- [ ] Change default admin credentials
- [ ] Set strong secret key
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS
- [ ] Set up backup procedures
- [ ] Configure logging
- [ ] Test audit trail access

### Performance Tips

- Use database indexes on frequently queried fields
- Implement caching for results pages
- Optimize image uploads
- Consider CDN for static files

## 🌐 Deployment

### Free Hosting on Render

This project is ready for deployment on [Render](https://render.com), a free hosting platform.

**Quick Deployment Steps:**

1. **Push to GitHub** (if not already done):

   ```bash
   git init
   git add .
   git commit -m "EESA Election System ready for deployment"
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

2. **Deploy on Render**:

   - Sign up at [render.com](https://render.com)
   - **Create PostgreSQL database first** (required for production)
   - Create a new Web Service
   - Connect your GitHub repository
   - Use these settings:
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn election_system.wsgi:application --bind 0.0.0.0:$PORT`
     - **Environment Variables**:
       - `DJANGO_SETTINGS_MODULE`: `election_system.production_settings`
       - `DATABASE_URL`: [PostgreSQL URL from database] **REQUIRED**
       - `SECRET_KEY`: Generate using `python generate_secret_key.py`

3. **Post-deployment**:
   - Access admin at: `https://your-app.onrender.com/admin/`
   - Default admin: username=`admin`, password=`admin123`
   - **⚠️ Change the admin password immediately!**

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Live Demo

Once deployed, your application will include:

- **Public Voting**: `https://your-app.onrender.com/`
- **Live Results**: `https://your-app.onrender.com/live-results/`
- **Final Results**: `https://your-app.onrender.com/final-results/`
- **Admin Panel**: `https://your-app.onrender.com/admin/`

## 🔧 Development

### Local Development

- Use Docker for consistent development environments
- Run `docker-compose up` to start services
- Access the app at `http://localhost:8000/`

### Testing

- Run tests with `python manage.py test`
- Use `pytest` for advanced testing features

### Troubleshooting

- Check Docker container logs for errors
- Ensure all environment variables are set
- Verify database connections and migrations

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable names
- Add docstrings to all functions/classes
- Maintain separation of concerns

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

### Common Issues

**Q: Voters can't log in with their tokens**
A: Check that tokens are correctly generated and haven't been used. Verify in admin panel.

**Q: Voting time restrictions not working**
A: Ensure position start/end times are set correctly and server time is accurate.

**Q: Results not updating**
A: Check that `show_live_results` is enabled in election settings.

**Q: Images not displaying**
A: Verify MEDIA_URL and MEDIA_ROOT settings in Django configuration.

### Getting Help

- Check the Django admin logs
- Review browser console for JavaScript errors
- Verify database migrations are up to date
- Ensure all required packages are installed

---

**Built with ❤️ using Django & Bootstrap 5**

_Secure • Transparent • Democratic_
