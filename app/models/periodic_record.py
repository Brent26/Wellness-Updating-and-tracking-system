from datetime import datetime
from app.extensions import db


class PeriodicRecord(db.Model):
    __tablename__ = "periodic_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_number = db.Column(db.Integer, nullable=True, index=True)
    personnel_name = db.Column(db.String(128), nullable=False, index=True)
    gender = db.Column(db.String(16), nullable=True)
    role = db.Column(db.String(128), nullable=True)
    department = db.Column(db.String(128), nullable=True)
    subarea = db.Column(db.String(128), nullable=True)
    ps_group = db.Column(db.String(64), nullable=True)
    grade = db.Column(db.String(64), nullable=True)
    base = db.Column(db.String(128), nullable=True)
    date_done = db.Column(db.String(32), nullable=True)
    next_due = db.Column(db.String(32), nullable=True)
    update_status = db.Column(db.String(64), nullable=True)
    update_date = db.Column(db.String(32), nullable=True)
    days_remaining = db.Column(db.Integer, nullable=True)
    status_flag = db.Column(db.String(64), nullable=True)
    fallback_used = db.Column(db.String(128), nullable=True)
    source_file = db.Column(db.String(256), nullable=True)
    form_type = db.Column(db.String(64), nullable=True)
    surname = db.Column(db.String(128), nullable=True)
    clinic = db.Column(db.String(128), nullable=True)
    needs_review = db.Column(db.String(32), nullable=True)
    review_reason = db.Column(db.Text, nullable=True)
    synced_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "employee_number": self.employee_number,
            "personnel_name": self.personnel_name,
            "gender": self.gender,
            "role": self.role,
            "department": self.department,
            "subarea": self.subarea,
            "ps_group": self.ps_group,
            "grade": self.grade,
            "base": self.base,
            "date_done": self.date_done,
            "next_due": self.next_due,
            "update_status": self.update_status,
            "update_date": self.update_date,
            "days_remaining": self.days_remaining,
            "status_flag": self.status_flag,
            "fallback_used": self.fallback_used,
            "source_file": self.source_file,
            "form_type": self.form_type,
            "surname": self.surname,
            "clinic": self.clinic,
            "needs_review": self.needs_review,
            "review_reason": self.review_reason,
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
        }
