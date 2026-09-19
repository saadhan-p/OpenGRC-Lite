from datetime import datetime
from app.models import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False, index=True)
    control_id = db.Column(db.String(50), nullable=False, index=True)  # Check ID or Control Code
    status = db.Column(db.String(20), nullable=False)  # PASS / FAIL / WARNING
    details = db.Column(db.Text)
    evidence_hash = db.Column(db.String(64))  # SHA-256 evidence verification hash
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "hostname": self.hostname,
            "control": self.control_id,
            "status": self.status,
            "details": self.details,
            "evidence_hash": self.evidence_hash,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
