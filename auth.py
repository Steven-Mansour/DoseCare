from flask import Blueprint, render_template, request, redirect, url_for
from models import User
from flask_login import login_user, logout_user, login_required
from app import db

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return redirect('login')

    login_user(user, remember=remember)
    return redirect(url_for('main.index'))


@auth.route('/signup')
def signup():
    return render_template('signUp.html')
