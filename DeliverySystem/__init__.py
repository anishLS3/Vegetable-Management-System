from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_session import Session
from DeliverySystem.config import Config

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
login_manager.login_view = 'admin.login'
login_manager.login_message_category = 'info'
mail = Mail()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    Session(app)

    from DeliverySystem.users.routes import users
    from DeliverySystem.admin.routes import admin
    from DeliverySystem.main.routes import main
    
    app.register_blueprint(users)
    app.register_blueprint(admin)
    app.register_blueprint(main)
    
    return app