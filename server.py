import os
from flask import Flask
from app.config import Config
from app.models import db
from app.api.agent import agent_bp
from app.api.dashboard import dashboard_bp
from app.api.reports import reports_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Register API & Dashboard Blueprints
    app.register_blueprint(agent_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reports_bp)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(port=5000, debug=True)