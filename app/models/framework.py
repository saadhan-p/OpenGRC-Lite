from app.models import db

class Framework(db.Model):
    __tablename__ = 'frameworks'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)  # ISO_27001_2022, SOC2_TYPE2
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20))

class Control(db.Model):
    __tablename__ = 'controls'

    id = db.Column(db.Integer, primary_key=True)
    framework_id = db.Column(db.Integer, db.ForeignKey('frameworks.id'), nullable=False)
    control_code = db.Column(db.String(50), nullable=False)  # A.8.20, CC6.6
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)

class CheckDefinition(db.Model):
    __tablename__ = 'check_definitions'

    id = db.Column(db.Integer, primary_key=True)
    check_id = db.Column(db.String(50), unique=True, nullable=False)  # FIREWALL_ACTIVE
    name = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), default='MEDIUM')  # CRITICAL, HIGH, MEDIUM, LOW
