from app.extensions import db
from datetime import datetime


class JobRun(db.Model):
    __tablename__ = "job_runs"

    id         = db.Column(db.Integer, primary_key=True)
    task_name  = db.Column(db.String(64), nullable=False)
    status     = db.Column(db.String(16), default="pending")  # pending/running/done/failed/warning
    duration_s = db.Column(db.Float, nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at= db.Column(db.DateTime, nullable=True)
    notes      = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id":          self.id,
            "task_name":   self.task_name,
            "status":      self.status,
            "duration_s":  self.duration_s,
            "started_at":  self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "notes":       self.notes,
        }
