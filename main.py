from flask import Blueprint, render_template
from models import User
from app import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    #    new_user = User(name="steven")
    #    db.session.add(new_user)
    #    db.session.commit()
    return render_template('signUp.html')
