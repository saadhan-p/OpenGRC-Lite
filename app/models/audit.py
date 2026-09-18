from datetime import datetime
from app.models import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    control_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # PASS / FAIL / WARNING
    details = db.Column(db.String(250))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "hostname": self.hostname,
            "control": self.control_id,
            "status": self.status,
            "details": self.details,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
