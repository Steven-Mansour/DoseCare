from flask import Flask
from infrastructure import db, socketio
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from flask_apscheduler import APScheduler
from cronJobs import check_if_patients_need_checkup


load_dotenv()
scheduler = APScheduler()  # For Cron jobs


def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    # Disable event system for performance
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "311231o2uei12vkafdsfjkdiij1br1iy"
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    from models import User

    @login_manager.user_loader
    def load_user(userID):
        return User.query.get(int(userID))

    # REGISTER BLUEPRINT
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from notifications import notification as notification_blueprint
    app.register_blueprint(notification_blueprint, url_prefix='/notification')

    from rpi import rpi as rpi_blueprint
    app.register_blueprint(rpi_blueprint, url_prefix='/rpi')
    # **Initialize the scheduler with app context**
    scheduler.init_app(app)
    scheduler.start()

    # Add cron job
    scheduler.add_job(id='Monthly Checkup Task',
                      func=check_if_patients_need_checkup,
                      args=[app],
                      trigger='cron',
                      day=1,  # Runs on the 1st day of each month
                      hour=0,  # At midnight (00:00)
                      minute=0)  # Runs every 5 seconds

    if __name__ == '__main__':
        socketio.run(app, debug=True, host="0.0.0.0", port=5000)
    return app
