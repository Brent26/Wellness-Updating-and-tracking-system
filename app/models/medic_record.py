from datetime import datetime
from app.extensions import db


class MedicRecord(db.Model):
    __tablename__ = "medic_records"

    id                     = db.Column(db.Integer,   primary_key=True)
    personnel_name         = db.Column(db.String(128), nullable=False)
    employee_number        = db.Column(db.Integer,     nullable=True)
    department             = db.Column(db.String(64),  nullable=True)
    personnel_subarea      = db.Column(db.String(64),  nullable=True)
    position               = db.Column(db.String(64),  nullable=True)
    ps_group               = db.Column(db.String(32),  nullable=True)
    record_type            = db.Column(db.String(16),  nullable=False)
    date_in_periodics      = db.Column(db.String(32),  nullable=True)
    date_in_medic_id       = db.Column(db.String(32),  nullable=True)
    date_to_update_to      = db.Column(db.String(32),  nullable=True)
    difference_days        = db.Column(db.Integer,     nullable=True)
    type_of_medical        = db.Column(db.String(64),  nullable=True)
    last_medical_periodics = db.Column(db.String(32),  nullable=True)
    exit_status            = db.Column(db.String(128), nullable=True)
    flagged_on             = db.Column(db.DateTime,    nullable=False,
                                       default=datetime.utcnow)
    resolved               = db.Column(db.Boolean,     nullable=False,
                                       default=False)
    source_file            = db.Column(db.String(256), nullable=True)
    job_run_id             = db.Column(db.Integer,
                                       db.ForeignKey("job_runs.id"),
                                       nullable=True)

    def to_dict(self):
        return {
            "id":                     self.id,
            "personnel_name":         self.personnel_name,
            "employee_number":        self.employee_number,
            "department":             self.department,
            "position":               self.position,
            "ps_group":               self.ps_group,
            "record_type":            self.record_type,
            "date_in_periodics":      self.date_in_periodics,
            "date_in_medic_id":       self.date_in_medic_id,
            "date_to_update_to":      self.date_to_update_to,
            "difference_days":        self.difference_days,
            "type_of_medical":        self.type_of_medical,
            "last_medical_periodics": self.last_medical_periodics,
            "exit_status":            self.exit_status,
            "flagged_on":             self.flagged_on.isoformat() if self.flagged_on else None,
            "resolved":               self.resolved,
            "source_file":            self.source_file,
            "job_run_id":             self.job_run_id,
        }

    def __repr__(self):
        return f"<MedicRecord {self.personnel_name} [{self.record_type}]>"