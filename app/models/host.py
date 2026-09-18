import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db

class AgentHost(db.Model):
    """
    Represents an enrolled endpoint agent in the GRC network.
    Stores host identity, IP, OS details, cryptographic key hash, and heartbeat status.
    """
    __tablename__ = 'agent_hosts'

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), unique=True, nullable=False, index=True)
    ip_address = db.Column(db.String(45))
    os_type = db.Column(db.String(50))
    api_key = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(20), default='ONLINE')  # ONLINE, OFFLINE, UNREACHABLE
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_api_key(self, raw_api_key: str):
        """Stores the secret API key for HMAC signing."""
        self.api_key = raw_api_key

    def verify_api_key(self, raw_api_key: str) -> bool:
        """Verifies an incoming raw API key."""
        return hmac.compare_digest(self.api_key, raw_api_key)

    def update_heartbeat(self, ip: str = None):
        """Updates the last_seen timestamp and sets status to ONLINE."""
        self.last_seen = datetime.utcnow()
        self.status = 'ONLINE'
        if ip:
            self.ip_address = ip

    def to_dict(self):
        """Serializes model attributes to JSON dictionary format."""
        return {
            "id": self.id,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "os_type": self.os_type,
            "status": self.status,
            "last_seen": self.last_seen.strftime("%Y-%m-%d %H:%M:%S") if self.last_seen else None,
            "enrolled_at": self.enrolled_at.strftime("%Y-%m-%d %H:%M:%S") if self.enrolled_at else None
        }

class EnrollmentToken(db.Model):
    """
    One-time or time-limited tokens used by endpoint agents during initial enrollment handshake.
    """
    __tablename__ = 'enrollment_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    @classmethod
    def create_token(cls, expires_in_hours: int = 24) -> 'EnrollmentToken':
        """Generates a secure random 32-character hexadecimal token."""
        secure_token = secrets.token_hex(16)
        expiry = datetime.utcnow() + timedelta(hours=expires_in_hours)
        return cls(token=secure_token, expires_at=expiry)

    def is_valid(self) -> bool:
        """Checks if the token has not been used and has not expired."""
        return not self.is_used and datetime.utcnow() < self.expires_at

    def mark_used(self):
        """Marks token as used so it cannot be re-used for unauthorized enrollment."""
        self.is_used = True

