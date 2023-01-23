from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager

mail = Mail()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"


def create_app(config_name) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    from app.main import main as main_blueprint
    from app.auth import auth as auth_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    return app
