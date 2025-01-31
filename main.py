from flask import Blueprint, render_template, redirect, url_for, request
from models import User, Pill
from app import db
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return "Logged in!"


@main.route('/home')
@login_required
def home():
    return render_template("home.html", user=current_user.get_role())


@main.route('/createPill')
@login_required
def createPill():
    if current_user.get_role()['role'] != 'pharmacist':
        return redirect(url_for('auth.login'))
    return render_template("createPill.html", user=current_user.get_role())


@main.route('/createPill', methods=['POST'])
@login_required
def createPill_post():
    if current_user.get_role()['role'] != 'pharmacist':
        return redirect(url_for('auth.login'))
    pillName = request.form.get('pill-name')
    shape = request.form.get('pill-shape')
    size = request.form.get('pill-size')
    qty = request.form.get('box-quantity')

    pill = Pill(name=pillName, shape=shape, size=size, boxQuantity=qty)
    db.session.add(pill)
    db.session.commit()
    return render_template("createPill.html", user=current_user.get_role())
