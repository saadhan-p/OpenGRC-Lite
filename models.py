from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    control_id = db.Column(db.String(50), nullable=False) # e.g., A.13.1
    status = db.Column(db.String(20), nullable=False) # PASS / FAIL
    details = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "hostname": self.hostname,
            "control": self.control_id,
            "status": self.status,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }