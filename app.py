from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_login import LoginManager
import os


db = SQLAlchemy()
load_dotenv()


def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    # Disable event system for performance
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "311231o2uei12vdiij1br1iy"
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(userID):
        return User.query.get(int(userID))

    # REGISTER BLUEPRINT
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
