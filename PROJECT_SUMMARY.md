# WUTS - Project Summary

## 🏥 Wellness Updating & Tracking System

A production-ready Flask application for enterprise-scale employee wellness and medical compliance management. WUTS automates the tracking, scheduling, and reporting of employee medical examinations and biometric screening data.

### 🎯 Problem Solved

Enterprises struggle with managing employee wellness programs at scale:
- **Manual tracking** of periodic medical examinations and certifications
- **Data silos** across HR systems, biometric services, and medical providers
- **Compliance risks** from missed exams or incomplete documentation
- **Reporting inefficiency** across departments and roles

WUTS provides a **centralized, automated solution** that reduces administrative overhead and ensures compliance visibility.

---

## ✨ Key Features

### 📋 Medical Compliance Management
- Periodic medical examination tracking with role-based intervals
- Automatic due-date calculations and 30-day warning system
- Conflict detection and reconciliation for duplicate records
- Real-time compliance dashboards by department

### 📊 Biometric Data Processing
- Automated Excel import for biometric screening data
- PDF extraction and organization from medical providers
- Data validation and categorization
- Historical trend analysis

### 👥 Employee Records
- Headcount synchronization with HR systems
- Intelligent fuzzy name matching (85% threshold) to reduce duplicates
- Department and role-based organization
- Flexible column mapping for diverse data sources

### 📈 Analytics & Reporting
- Department-level compliance metrics
- Real-time exam adherence dashboards
- Top non-compliant departments view
- Complete audit trail and change logging

### 🔐 Security & Access Control
- Role-based access control (Admin, Manager, User)
- Forced password changes on first login
- Comprehensive audit logging of all changes
- No hardcoded secrets or credentials

---

## 🏗️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask 3.0.3 |
| **Database** | MSSQL Server with SQLAlchemy ORM |
| **Task Scheduling** | APScheduler |
| **Data Processing** | Pandas, Openpyxl, PDFPlumber |
| **Authentication** | Flask-WTF with secure password hashing |
| **Rate Limiting** | Flask-Limiter |
| **Deployment** | Gunicorn + Nginx |
| **Testing** | pytest |

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/Brent-T/Wellness-Updating-and-tracking-system.git
cd Wellness-Updating-and-tracking-system

# Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your database and file paths

# Initialize
python seed_admin.py

# Run
python run.py
```

Visit `http://localhost:5000` and login with credentials from `.env`

See [SETUP.md](SETUP.md) for detailed setup, database configuration, and production deployment instructions.

---

## 📁 Project Architecture

```
app/
├── routes/              # Flask blueprints (dashboard, API, auth, admin)
├── models/              # SQLAlchemy ORM models
│   ├── user.py         # Authentication & roles
│   ├── periodic_record.py
│   ├── headcount_record.py
│   ├── medic_record.py
│   └── job_run.py
├── services/           # Business logic
│   ├── biometric_processor.py
│   ├── medic_classifier.py
│   ├── periodic_scheduler.py
│   └── excel_processor.py
├── static/             # CSS, JavaScript, images
└── templates/          # Jinja2 HTML templates
```

---

## 🔌 API Endpoints

**Authentication Required**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/records` | List all medical records |
| POST | `/api/records` | Create new record |
| PUT | `/api/records/<id>` | Update record |
| DELETE | `/api/records/<id>` | Delete record |
| GET | `/api/analytics` | Get compliance analytics |
| POST | `/api/import` | Bulk data import |

See [postman_collection_wuts.json](postman_collection_wuts.json) for complete API documentation with examples.

---

## 📊 Real-World Data Flow

```
Excel Files (HR, Biometric Data)
         ↓
    WUTS Processor
    (Validation, Matching, Classification)
         ↓
    MSSQL Database
    (Normalized Records, Audit Trail)
         ↓
    API / Dashboard
    (Analytics, Reports, Actions)
         ↓
    User Interface / Exports
```

---

## 🧪 Testing

```bash
pip install pytest pytest-cov
pytest                              # Run all tests
pytest --cov=app --cov-report=html  # With coverage
```

---

## 🌐 Production Deployment

WUTS is production-ready and can be deployed to:
- **Ubuntu/Linux** with Nginx + Gunicorn
- **Windows Server** with IIS
- **Docker** containerization (configuration provided)
- **Cloud platforms** (AWS, Azure, GCP)

Comprehensive deployment guide in [SETUP.md](SETUP.md)

---

## 📖 Documentation

- **[README.md](README.md)** - Full project documentation
- **[SETUP.md](SETUP.md)** - Development and deployment guides
- **[postman_collection_wuts.json](postman_collection_wuts.json)** - API testing collection

---

## 🎓 What This Project Demonstrates

### Software Architecture
- **Layered Architecture** - Separation of concerns (routes, services, models)
- **MVC Pattern** - Flask blueprints for modular route organization
- **ORM Best Practices** - SQLAlchemy for database abstraction
- **Service Layer** - Business logic encapsulation

### Data Processing
- **ETL Pipeline** - Extract, transform, load from multiple sources
- **Fuzzy Matching** - Advanced record deduplication
- **Excel/PDF Handling** - Complex document processing
- **Data Validation** - Input validation and conflict resolution

### Security
- **Authentication** - Secure password hashing and session management
- **Authorization** - Role-based access control
- **Audit Logging** - Complete change tracking
- **Secret Management** - Environment-based configuration (no hardcoded secrets)

### DevOps & Deployment
- **Database Migrations** - Alembic for schema versioning
- **Production Ready** - Gunicorn + Nginx setup
- **Logging & Monitoring** - Comprehensive logging configuration
- **Testing** - pytest suite with fixtures

### Best Practices
- **Code Organization** - Modular, maintainable structure
- **Documentation** - Comprehensive setup and API docs
- **Error Handling** - Graceful error responses
- **Performance** - Optimized queries, caching strategies

---

## 🤝 Contributing

This is a portfolio project showcasing production-quality code and architecture. Feedback and questions are welcome!

---

## 📄 License

All Rights Reserved - See [LICENSE](LICENSE) file

---

## 📞 Contact

Built with attention to detail for enterprise-scale requirements.

**Repository:** https://github.com/Brent-T/Wellness-Updating-and-tracking-system
