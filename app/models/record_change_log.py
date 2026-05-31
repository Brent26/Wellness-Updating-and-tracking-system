from datetime import datetime
from app.extensions import db


class RecordChangeLog(db.Model):
    __tablename__ = "record_change_logs"

    id = db.Column(db.Integer, primary_key=True)
    record_source = db.Column(db.String(32), nullable=False)
    record_id = db.Column(db.Integer, nullable=True)
    employee_number = db.Column(db.Integer, nullable=True, index=True)
    personnel_name = db.Column(db.String(128), nullable=False)
    changed_fields = db.Column(db.Text, nullable=False)
    change_reason = db.Column(db.Text, nullable=True)
    changed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "record_source": self.record_source,
            "record_id": self.record_id,
            "employee_number": self.employee_number,
            "personnel_name": self.personnel_name,
            "changed_fields": self.changed_fields,
            "change_reason": self.change_reason,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None,
        }
