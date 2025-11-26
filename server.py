from flask import Flask, render_template, jsonify, request
from models import db, AuditLog

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grc_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 1. API ENDPOINT (Receives data from Agent)
@app.route('/api/report', methods=['POST'])
def report_status():
    data = request.json
    # Save to Database
    new_log = AuditLog(
        hostname=data['hostname'],
        control_id=data['control_id'],
        status=data['status'],
        details=data['details']
    )
    db.session.add(new_log)
    db.session.commit()
    return jsonify({"message": "Report Received"}), 200

# 2. DASHBOARD (View Data)
@app.route('/')
def dashboard():
    # Get the latest 10 logs
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    # Calculate simple stats
    total_checks = AuditLog.query.count()
    failed_checks = AuditLog.query.filter_by(status="FAIL").count()
    compliance_score = 100
    if total_checks > 0:
        compliance_score = round(((total_checks - failed_checks) / total_checks) * 100, 1)

    return render_template('dashboard.html', logs=logs, score=compliance_score)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Create DB if not exists
    app.run(port=5000, debug=True)  