from flask import Blueprint, jsonify
from app.services.compliance_engine import ComplianceEngine
from app.models.framework import Framework, CheckDefinition

compliance_bp = Blueprint('compliance_api', __name__, url_prefix='/api/v1/compliance')


@compliance_bp.route('/summary', methods=['GET'])
def get_compliance_summary():
    """Returns global compliance score and multi-framework score breakdowns."""
    summary = ComplianceEngine.calculate_overall_summary()
    return jsonify(summary), 200


@compliance_bp.route('/frameworks', methods=['GET'])
def get_frameworks():
    """Returns all registered compliance frameworks and their mapped controls."""
    frameworks = Framework.query.all()
    return jsonify({
        "frameworks": [f.to_dict() for f in frameworks]
    }), 200


@compliance_bp.route('/checks', methods=['GET'])
def get_check_definitions():
    """Returns technical check definitions and cross-framework control mappings."""
    check_defs = CheckDefinition.query.all()
    return jsonify({
        "checks": [cd.to_dict() for cd in check_defs]
    }), 200
