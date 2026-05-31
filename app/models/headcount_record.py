from datetime import datetime
from app.extensions import db


class HeadcountRecord(db.Model):
    __tablename__ = "headcount_records"

    id                = db.Column(db.Integer,  primary_key=True)
    personnel_name    = db.Column(db.String(128), nullable=False)
    employee_number   = db.Column(db.Integer,     nullable=True)
    department        = db.Column(db.String(64),  nullable=True)
    personnel_subarea = db.Column(db.String(64),  nullable=True)
    position          = db.Column(db.String(64),  nullable=True)
    section           = db.Column(db.String(64),  nullable=True)
    sub_section       = db.Column(db.String(64),  nullable=True)
    ps_group          = db.Column(db.String(32),  nullable=True)
    age               = db.Column(db.Integer,     nullable=True)
    flag_type         = db.Column(db.String(16),  nullable=False)
    flagged_on        = db.Column(db.DateTime,    nullable=False,
                                  default=datetime.utcnow)
    source_file       = db.Column(db.String(256), nullable=True)
    resolved          = db.Column(db.Boolean,     nullable=False,
                                  default=False)
    job_run_id        = db.Column(db.Integer,
                                  db.ForeignKey("job_runs.id"),
                                  nullable=True)

    def to_dict(self):
        return {
            "id":                self.id,
            "personnel_name":    self.personnel_name,
            "employee_number":   self.employee_number,
            "department":        self.department,
            "personnel_subarea": self.personnel_subarea,
            "position":          self.position,
            "ps_group":          self.ps_group,
            "flag_type":         self.flag_type,
            "flagged_on":        self.flagged_on.isoformat() if self.flagged_on else None,
            "source_file":       self.source_file,
            "resolved":          self.resolved,
            "job_run_id":        self.job_run_id,
        }

    def __repr__(self):
        return f"<HeadcountRecord {self.personnel_name} [{self.flag_type}]>"