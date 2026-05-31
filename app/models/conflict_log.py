from app.extensions import db
from datetime import datetime


class ConflictLog(db.Model):
    __tablename__ = "conflict_logs"

    id          = db.Column(db.Integer, primary_key=True)
    source      = db.Column(db.String(64))
    description = db.Column(db.Text)
    resolved    = db.Column(db.Boolean, default=False)
    logged_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":          self.id,
            "source":      self.source,
            "description": self.description,
            "resolved":    self.resolved,
            "logged_at":   self.logged_at.isoformat() if self.logged_at else None,
        }
