from flask import Blueprint, render_template
from models import User
from app import db

auth = Blueprint('auth', __name__)


@auth.route('/')
def index():
    new_user = User()
    db.session.add(new_user)
    db.session.commit()
    return "Hi auth"
