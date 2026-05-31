# WUTS Setup and Deployment Guide

This guide covers local development setup, testing, and production deployment of the Wellness Updating & Tracking System (WUTS).

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Database Configuration](#database-configuration)
3. [Application Configuration](#application-configuration)
4. [Testing](#testing)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Prerequisites

- **Python 3.8 or higher**
  ```bash
  python --version
  ```

- **MSSQL Server or LocalDB**
  - For Windows: Install [MSSQL LocalDB](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/sql-server-express-localdb)
  - For Linux/Mac: Install [MSSQL Server](https://learn.microsoft.com/en-us/sql/linux/quickstart-install-connect-ubuntu)

- **Git**
  ```bash
  git --version
  ```

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd WUTS_FINAL_copy
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings
# On Windows: notepad .env
# On macOS/Linux: nano .env
```

Edit the following critical variables in `.env`:

```env
# Database connection string (example for LocalDB)
DATABASE_URL=mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BODBC+Driver+17+for+SQL+Server%7D%3BSERVER%3D%28localdb%29%5CMSSQLLocalDB%3BDATABASE%3DWUTS%3BTrusted_Connection%3Dyes%3BEncrypt%3Dno

# Generate a strong secret key
SECRET_KEY=<generate-with-python-secrets-module>

# Set admin credentials
INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_PASSWORD=<secure-password>
INITIAL_ADMIN_EMAIL=admin@example.com

# File paths (create these directories first)
SAVE_FOLDER=C:\path\to\periodics_pdfs
EXCEL_PATH=C:\path\to\master_data.xlsx
HC_FOLDER=C:\path\to\headcount
CONFLICT_LOG=C:\path\to\logs\conflict_log.csv
```

#### Generate a Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as your `SECRET_KEY` value.

### Step 5: Initialize Database

```bash
# Create database tables
flask db upgrade

# Seed initial admin user
python seed_admin.py
```

### Step 6: (Optional) Load Demo Data

```bash
python seed_demo.py
```

### Step 7: Run Development Server

```bash
python run.py
```

The application will start on `http://localhost:5000`

**Default Admin Login:**
- Username: `admin`
- Password: (whatever you set in `.env` as `INITIAL_ADMIN_PASSWORD`)

---

## Database Configuration

### MSSQL LocalDB (Windows)

LocalDB is a lightweight version of SQL Server Express included with Visual Studio.

**Connection String Format:**
```
mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BODBC+Driver+17+for+SQL+Server%7D%3BSERVER%3D%28localdb%29%5CMSSQLLocalDB%3BDATABASE%3DWUTS%3BTrusted_Connection%3Dyes%3BEncrypt%3Dno
```

**Verify LocalDB is Running:**
```bash
sqllocaldb info
sqllocaldb start MSSQLLocalDB
```

### MSSQL Server (Any Platform)

**Connection String Format:**
```
mssql+pyodbc://username:password@server:port/database?driver=ODBC+Driver+17+for+SQL+Server
```

**Example:**
```
mssql+pyodbc://sa:YourPassword@192.168.1.100:1433/WUTS?driver=ODBC+Driver+17+for+SQL+Server
```

### Database Migrations

Manage schema changes with Alembic:

```bash
# Show current migration version
flask db current

# Create new migration (auto-detect changes)
flask db migrate -m "Add new column to users table"

# Review migration script before applying
cat migrations/versions/xxxxx_add_new_column.py

# Apply migrations
flask db upgrade

# Rollback to previous version
flask db downgrade
```

---

## Application Configuration

### Directory Structure for File Operations

Create these directories on your system and update `.env` accordingly:

```
C:\WUTS_Data\
├── PERIODICS_PDFS\        (SAVE_FOLDER)
├── MASTER_DATA\           (EXCEL_PATH parent)
├── HEADCOUNT\             (HC_FOLDER)
├── LOGS\                  (CONFLICT_LOG parent)
├── BIOMETRICS_DATA\       (BIOMETRIC_EXCEL_PATH parent)
│   └── PDFS\              (BIOMETRIC_PDF_FOLDER)
└── MEDIC_IDENTIFICATION\  (MEDIC_ID_FOLDER)
    └── OUTPUT\            (MEDIC_ID_OUTPUT_FOLDER)
```

### Master Data Excel File

The `EXCEL_PATH` should point to an Excel file with the following columns (configurable in `config.py`):

| Required Columns | Example |
|---|---|
| Personnel Names | John Smith |
| Employee Number | EMP12345 |
| Department | Operations |
| Role | Executive |
| Sub Area | Finance |
| Section | Accounting |
| Sub Section | Payroll |
| Age | 45 |
| PSGroup | Management |
| Last Medical | 2025-06-15 |
| Due Date | 2026-06-15 |

**Column Mapping** can be customized in `config.py`:

```python
"DEPT_COLUMN_MAP": {
    "Personnel Names": "YourColumnName",
    "Employee Number": "YourEmployeeIdColumn",
    # ... etc
}
```

### Email Configuration

Configure email notifications in `.env`:

```env
NOTIFY_EMAIL=notifications@example.com
NOTIFY_CC=manager@example.com
EMAIL_HOURS=24  # Send digests every 24 hours
```

For production, configure SMTP server credentials (add to `.env`):

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

## Testing

### Run Test Suite

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html tests/

# Run specific test file
pytest tests/test_auth.py

# Run specific test function
pytest tests/test_auth.py::test_login
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── test_auth.py             # Authentication tests
├── test_api.py              # API endpoint tests
├── test_models.py           # Model tests
└── test_services.py         # Business logic tests
```

---

## Production Deployment

### Prerequisites

- Ubuntu 20.04+ or CentOS 7+
- MSSQL Server instance
- Nginx web server
- Python 3.8+
- Systemd (for process management)

### Step 1: Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx curl -y

# Install ODBC driver for MSSQL
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo apt-add-repository "$(curl https://packages.microsoft.com/config/ubuntu/20.04/mssql-server-2019.list)"
sudo apt install msodbcsql17 -y
```

### Step 2: Application Deployment

```bash
# Create application directory
sudo mkdir -p /var/www/wuts
cd /var/www/wuts

# Clone repository (or upload files)
sudo git clone <repository-url> .

# Create virtual environment
sudo python3 -m venv venv

# Install dependencies
sudo venv/bin/pip install --upgrade pip
sudo venv/bin/pip install -r requirements.txt
sudo venv/bin/pip install gunicorn

# Set permissions
sudo chown -R www-data:www-data /var/www/wuts
```

### Step 3: Production Environment Configuration

```bash
# Create production .env file
sudo nano /var/www/wuts/.env

# Add production configuration:
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_URL=mssql+pyodbc://...
DEBUG=False
# ... other variables
```

### Step 4: Initialize Database

```bash
cd /var/www/wuts
sudo -u www-data venv/bin/flask db upgrade
sudo -u www-data venv/bin/python seed_admin.py
```

### Step 5: Configure Gunicorn

Create `/var/www/wuts/wsgi.py`:

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

Or use the existing `config/gunicorn.conf.py`.

### Step 6: Create Systemd Service

Create `/etc/systemd/system/wuts.service`:

```ini
[Unit]
Description=WUTS Flask Application
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/wuts
ExecStart=/var/www/wuts/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 "app:create_app()"
Environment="FLASK_ENV=production"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable wuts
sudo systemctl start wuts
sudo systemctl status wuts
```

### Step 7: Configure Nginx

Edit `/etc/nginx/sites-available/wuts`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/wuts/app/static/;
        expires 30d;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/wuts /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 8: SSL Configuration (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Step 9: Monitoring and Maintenance

```bash
# View application logs
sudo journalctl -u wuts -f

# View Nginx logs
sudo tail -f /var/log/nginx/error.log

# Monitor disk space
df -h

# Check service status
sudo systemctl status wuts
```

---

## Troubleshooting

### Common Issues

**Issue: "Database connection refused"**

Solution:
```bash
# Verify MSSQL is running
systemctl status mssql-server

# Test connection string
python
>>> import pyodbc
>>> pyodbc.connect(your_connection_string)

# Check firewall
sudo ufw allow 1433/tcp
```

**Issue: "Module not found" errors**

Solution:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Issue: File paths not found**

Solution:
```bash
# Verify directories exist
ls -la /path/to/your/data

# Check file permissions
sudo chown -R www-data:www-data /path/to/your/data
sudo chmod -R 755 /path/to/your/data
```

**Issue: 502 Bad Gateway from Nginx**

Solution:
```bash
# Check Gunicorn is running
sudo systemctl status wuts

# Restart Gunicorn
sudo systemctl restart wuts

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log
```

### Debug Mode

For development debugging:

```bash
# Set debug mode
export FLASK_DEBUG=1
export FLASK_ENV=development

# Run with verbose output
python -u run.py
```

**Never enable `DEBUG=True` in production!**

---

## Support and Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [MSSQL Documentation](https://learn.microsoft.com/en-us/sql/)
- [Nginx Documentation](https://nginx.org/en/docs/)
