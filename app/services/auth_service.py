import hmac
import hashlib
import time
from functools import wraps
from flask import request, jsonify
from app.models.host import AgentHost

MAX_TIMESTAMP_DRIFT_SECONDS = 300  # 5 minutes


def compute_hmac(payload_bytes: bytes, timestamp_str: str, api_key: str) -> str:
    """Computes HMAC-SHA256 signature over raw payload + timestamp using agent API key."""
    message = payload_bytes + timestamp_str.encode('utf-8')
    return hmac.new(api_key.encode('utf-8'), message, hashlib.sha256).hexdigest()


def require_agent_auth(f):
    """
    Decorator for API endpoints requiring HMAC signature authentication.
    Validates X-Agent-ID, X-Timestamp, and X-Signature headers.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        hostname = request.headers.get('X-Agent-ID')
        timestamp_str = request.headers.get('X-Timestamp')
        received_signature = request.headers.get('X-Signature')

        # 1. Verify headers presence
        if not hostname or not timestamp_str or not received_signature:
            return jsonify({
                "error": "Unauthorized: Missing authentication headers (X-Agent-ID, X-Timestamp, X-Signature)"
            }), 401

        # 2. Check timestamp freshness (Replay attack defense)
        try:
            req_timestamp = float(timestamp_str)
            current_time = time.time()
            if abs(current_time - req_timestamp) > MAX_TIMESTAMP_DRIFT_SECONDS:
                return jsonify({"error": "Unauthorized: Request timestamp expired (replay protection)"}), 401
        except ValueError:
            return jsonify({"error": "Unauthorized: Invalid timestamp format"}), 400

        # 3. Lookup agent host record
        host = AgentHost.query.filter_by(hostname=hostname).first()
        if not host:
            return jsonify({"error": f"Unauthorized: Agent host '{hostname}' not enrolled"}), 401

        # 4. Verify HMAC signature against host's raw API key
        raw_payload = request.get_data()
        
        # We check HMAC against verified host secret API key
        expected_signature = compute_hmac(raw_payload, timestamp_str, host.api_key)

        if not hmac.compare_digest(expected_signature, received_signature):
            return jsonify({"error": "Unauthorized: Invalid HMAC signature"}), 401

        # 5. Update host heartbeat & last_seen
        host.update_heartbeat(request.remote_addr)
        from app.models import db
        db.session.commit()

        # Pass host instance to route handler if needed
        request.current_host = host
        return f(*args, **kwargs)

    return decorated_function
