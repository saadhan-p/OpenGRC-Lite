import secrets
from flask import Blueprint, request, jsonify
from app.models import db
from app.models.audit import AuditLog
from app.models.host import AgentHost, EnrollmentToken
from app.services.auth_service import require_agent_auth

agent_bp = Blueprint('agent_api', __name__, url_prefix='/api/v1/agent')

REQUIRED_REPORT_FIELDS = {"hostname", "control_id", "status", "details"}
REQUIRED_ENROLL_FIELDS = {"enrollment_token", "hostname"}


@agent_bp.route('/enroll', methods=['POST'])
def enroll_agent():
    """
    Handshake Endpoint: Accepts enrollment token and registers new endpoint agent.
    Returns host-specific API Key upon successful token verification.
    """
    data = request.get_json(silent=True)

    if not data or not REQUIRED_ENROLL_FIELDS.issubset(data.keys()):
        return jsonify({"error": "Invalid payload: missing required fields"}), 400

    token_str = data["enrollment_token"]
    hostname = data["hostname"].strip()
    os_type = data.get("os_type", "Unknown")
    ip_address = request.remote_addr

    # 1. Lookup and validate enrollment token
    token_record = EnrollmentToken.query.filter_by(token=token_str).first()
    if not token_record or not token_record.is_valid():
        return jsonify({"error": "Invalid or expired enrollment token"}), 401

    # 2. Check if host already exists
    existing_host = AgentHost.query.filter_by(hostname=hostname).first()

    # 3. Generate raw secret API key for agent
    raw_api_key = secrets.token_hex(32)

    if existing_host:
        host = existing_host
        host.os_type = os_type
        host.ip_address = ip_address
        host.set_api_key(raw_api_key)
        host.update_heartbeat(ip_address)
    else:
        host = AgentHost(
            hostname=hostname,
            ip_address=ip_address,
            os_type=os_type
        )
        host.set_api_key(raw_api_key)
        db.session.add(host)

    # 4. Mark token as used so it cannot be re-used
    token_record.mark_used()
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Agent enrolled successfully",
        "hostname": host.hostname,
        "agent_api_key": raw_api_key
    }), 201


@agent_bp.route('/generate-token', methods=['POST'])
def generate_token():
    """Admin helper endpoint to generate a new 24-hour enrollment token."""
    token_record = EnrollmentToken.create_token(expires_in_hours=24)
    db.session.add(token_record)
    db.session.commit()

    return jsonify({
        "status": "success",
        "enrollment_token": token_record.token,
        "expires_at": token_record.expires_at.strftime("%Y-%m-%d %H:%M:%S")
    }), 201


@agent_bp.route('/report', methods=['POST'])
@require_agent_auth
def report_status():
    """Protected Endpoint: Receives HMAC-signed telemetry reports from agents."""
    data = request.get_json(silent=True)

    if not data or not REQUIRED_REPORT_FIELDS.issubset(data.keys()):
        return jsonify({"error": "Invalid payload: missing required fields"}), 400

    if data["status"] not in ("PASS", "FAIL", "WARNING"):
        return jsonify({"error": "Invalid status value"}), 400

    new_log = AuditLog(
        hostname=data['hostname'],
        control_id=data['control_id'],
        status=data['status'],
        details=data['details']
    )
    db.session.add(new_log)
    db.session.commit()

    return jsonify({"message": "Authenticated Report Received"}), 200
