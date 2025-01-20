from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://stvn:password@localhost/dosecaredb'
    # Disable event system for performance
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # init
    db.init_app(app)

    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
