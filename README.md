# WUTS - Wellness Updating & Tracking System

A comprehensive Flask application for managing employee wellness programs, medical examinations, and biometric screening data. WUTS provides real-time tracking of employee medical compliance, automated scheduling, and integrated reporting.

## Overview

WUTS is designed to streamline wellness program management in enterprise environments. It handles:

- **Medical Compliance Tracking**: Monitor periodic medical examinations and certifications
- **Biometric Data Processing**: Process and categorize biometric screening results
- **Employee Records Management**: Maintain comprehensive health and wellness records
- **Automated Scheduling**: Track exam due dates with customizable intervals by role
- **PDF Processing**: Extract and organize medical examination documents
- **Fuzzy Matching**: Intelligent employee name matching to reduce data entry errors
- **Real-time Dashboards**: Visual compliance metrics and department analytics
- **Audit Logging**: Track all changes to medical records with full traceability

## Technology Stack

- **Backend**: Flask 3.0.3, Python 3.x
- **Database**: MSSQL Server with SQLAlchemy ORM
- **Task Scheduling**: APScheduler for automated job processing
- **Data Processing**: Pandas, Openpyxl for Excel handling; PDFPlumber for PDF extraction
- **Authentication**: Flask-WTF with password hashing (Werkzeug)
- **Rate Limiting**: Flask-Limiter
- **Deployment**: Gunicorn + Nginx

## Quick Start

### Prerequisites
- Python 3.8+
- MSSQL Server or LocalDB instance
- Virtual environment (recommended)

### Development Setup

```bash
# Clone and navigate to project
git clone <repository-url>
cd WUTS_FINAL_copy

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate            # Windows
source venv/bin/activate         # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database, paths, and credentials

# Initialize database and seed admin user
python seed_admin.py

# Run development server
python run.py
```

Visit http://localhost:5000 in your browser. Login with the credentials you set in `.env.example`.

## Configuration

All configuration is handled through environment variables in `.env`. Key variables:

- `SECRET_KEY`: Flask session secret (generate a strong random value)
- `DATABASE_URL`: MSSQL connection string
- `SAVE_FOLDER`: Directory for PDF storage
- `EXCEL_PATH`: Master data Excel file path
- `HC_FOLDER`: Headcount data folder
- `BIOMETRIC_EXCEL_PATH`: Biometric screening Excel file
- `MEDIC_ID_FOLDER`: Medical identification files folder

See `.env.example` for a complete list and descriptions.

## Project Structure

```
WUTS_FINAL_copy/
├── app/
│   ├── __init__.py              # Flask app factory and initialization
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── user.py              # User authentication and roles
│   │   ├── periodic_record.py   # Medical examination records
│   │   ├── headcount_record.py  # Employee headcount data
│   │   ├── medic_record.py      # Medical classification records
│   │   ├── conflict_log.py      # Data conflict tracking
│   │   ├── job_run.py           # Job execution history
│   │   └── record_change_log.py # Audit trail
│   ├── routes/
│   │   ├── auth.py              # Authentication and authorization
│   │   ├── dashboard.py         # Main dashboard views
│   │   ├── admin.py             # Admin panel operations
│   │   ├── api.py               # REST API endpoints
│   │   └── stream.py            # Data import operations
│   ├── services/                # Business logic
│   │   ├── biometric_processor.py     # Biometric data processing
│   │   ├── medic_classifier.py        # Medical record classification
│   │   ├── periodic_scheduler.py      # Exam scheduling logic
│   │   └── excel_processor.py         # Excel file handling
│   ├── static/                  # CSS, JavaScript, images
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/               # Jinja2 HTML templates
│       ├── base.html            # Base template
│       ├── auth/                # Login/authentication
│       ├── dashboard/           # Dashboard views
│       ├── admin/               # Admin pages
│       └── errors/              # Error pages
├── config/
│   ├── gunicorn.conf.py         # Production server config
│   ├── nginx.conf               # Nginx reverse proxy config
│   └── logging.conf             # Logging configuration
├── tests/                       # Test suite
│   └── test_*.py                # Unit and integration tests
├── migrations/                  # Alembic database migrations
├── config.py                    # Centralized configuration
├── run.py                       # Development server entry point
├── seed_admin.py                # Admin user initialization
├── seed_demo.py                 # Demo data seeding
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template (DO NOT EDIT)
└── .gitignore                   # Git ignore rules
```

## Key Features

### Medical Compliance Management
- Track periodic medical examinations with configurable intervals
- Automatic due date calculations based on role (Executive, Top Brass, default)
- 30-day warning system for upcoming exams
- Conflict detection and logging for duplicate records

### Biometric Data Processing
- Import biometric screening Excel files
- Extract and organize biometric PDFs
- Automatic data categorization and validation
- Historical trend tracking

### Employee Records
- Import from headcount/HR systems
- Fuzzy name matching (85% threshold) for duplicate detection
- Department and role-based organization
- Custom column mapping for flexible data sources

### Real-time Analytics
- Department-level compliance dashboards
- Exam adherence rates and non-compliance metrics
- Top 8 non-compliant departments view
- Historical change tracking and audit logs

### User Management
- Role-based access control (Admin, Manager, User)
- Forced password changes on first login
- Secure temporary password generation
- Audit trail for all user actions

## API Endpoints

Key API endpoints available (with authentication):

- `GET /api/records` - List all medical records
- `POST /api/records` - Create new record
- `PUT /api/records/<id>` - Update record
- `DELETE /api/records/<id>` - Delete record
- `GET /api/analytics` - Get compliance analytics
- `POST /api/import` - Bulk import operations

See `postman_collection_wuts.json` for complete API documentation and examples.

## Production Deployment

### Prerequisites
- MSSQL Server instance (production database)
- Nginx web server
- Gunicorn WSGI server
- Systemd or supervisor for process management

### Deployment Steps

```bash
# Install production dependencies
pip install gunicorn

# Set production environment variables
export FLASK_ENV=production
export DATABASE_URL=<your-production-db>
export SECRET_KEY=<generate-strong-random-key>

# Run migrations
flask db upgrade

# Start Gunicorn server
gunicorn -c config/gunicorn.conf.py "app:create_app()"

# Configure Nginx (see config/nginx.conf)
sudo cp config/nginx.conf /etc/nginx/sites-available/wuts
sudo ln -s /etc/nginx/sites-available/wuts /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## Database

WUTS uses MSSQL Server with SQLAlchemy for ORM operations.

### Migrations

Database schema changes are managed with Alembic:

```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## Testing

Run the test suite:

```bash
pip install pytest pytest-cov
pytest
pytest --cov=app tests/  # With coverage
```

## Troubleshooting

### Database Connection Issues
- Verify MSSQL Server is running
- Check `DATABASE_URL` in `.env`
- For LocalDB: Ensure `(localdb)\MSSQLLocalDB` exists
- Verify connection string permissions

### File Path Issues
- Ensure all paths in `.env` exist and are accessible
- Use absolute paths for best results
- On Windows, use `\` or raw strings `r"C:\path"`

### Import Failures
- Check Excel file format (XLSX recommended)
- Verify column headers match `DEPT_COLUMN_MAP` in config
- Check PDF folder structure and naming conventions
- Review conflict logs for duplicate detection details

## Contributing

This is a portfolio project. Please feel free to review the code and provide feedback.

## License

All rights reserved. This project is not open source.
