from app.models import db

class Framework(db.Model):
    __tablename__ = 'frameworks'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)  # ISO_27001_2022, SOC2_TYPE2, NIST_CSF_2, CIS_V8
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20))
    description = db.Column(db.Text)

    controls = db.relationship('Control', backref='framework', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "control_count": len(self.controls)
        }


class Control(db.Model):
    __tablename__ = 'controls'

    id = db.Column(db.Integer, primary_key=True)
    framework_id = db.Column(db.Integer, db.ForeignKey('frameworks.id'), nullable=False)
    control_code = db.Column(db.String(50), nullable=False, index=True)  # A.8.20, CC6.6, PR.IR-01
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))

    mappings = db.relationship('ControlCheckMapping', backref='control', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "framework_code": self.framework.code if self.framework else None,
            "control_code": self.control_code,
            "title": self.title,
            "description": self.description,
            "category": self.category
        }


class CheckDefinition(db.Model):
    __tablename__ = 'check_definitions'

    id = db.Column(db.Integer, primary_key=True)
    check_id = db.Column(db.String(50), unique=True, nullable=False, index=True)  # FIREWALL_ACTIVE, DISK_ENCRYPTION, SSH_HARDENING, EDR_RUNNING
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(20), default='MEDIUM', nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW

    mappings = db.relationship('ControlCheckMapping', backref='check_definition', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "check_id": self.check_id,
            "name": self.name,
            "description": self.description,
            "severity": self.severity,
            "mapped_controls": [m.control.to_dict() for m in self.mappings if m.control]
        }


class ControlCheckMapping(db.Model):
    __tablename__ = 'control_check_mappings'

    id = db.Column(db.Integer, primary_key=True)
    check_definition_id = db.Column(db.Integer, db.ForeignKey('check_definitions.id'), nullable=False)
    control_id = db.Column(db.Integer, db.ForeignKey('controls.id'), nullable=False)
