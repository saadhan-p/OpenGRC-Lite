from flask import Blueprint, jsonify

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@reports_bp.route('/summary', methods=['GET'])
def get_summary():
    return jsonify({"status": "healthy", "message": "Reports endpoint operational"})
