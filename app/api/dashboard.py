from flask import Blueprint, render_template
from app.models.audit import AuditLog

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    total_checks = AuditLog.query.count()
    failed_checks = AuditLog.query.filter_by(status="FAIL").count()
    compliance_score = 100
    if total_checks > 0:
        compliance_score = round(((total_checks - failed_checks) / total_checks) * 100, 1)

    return render_template('dashboard.html', logs=logs, score=compliance_score)
