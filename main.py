from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import User, Pill, Caregiver, Patient
from app import db
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return "Logged in!"


@main.route('/home')
@login_required
def home():
    return render_template("home.html", user=current_user.get_info())


@main.route('/createPill')
@login_required
def createPill():
    if current_user.get_info()['role'] != 'pharmacist':
        return redirect(url_for('auth.login'))
    return render_template("createPill.html", user=current_user.get_info())


@main.route('/viewPatients')
@login_required
def viewPatients():
    if current_user.get_info()['role'] != 'caregiver':
        return redirect(url_for('auth.login'))
    caregiver = current_user.caregivers[0]
    return render_template("viewPatients.html", user=current_user.get_info(), patients=caregiver.patients)


@main.route('/assignCaregiver')
@login_required
def assignCaregiver():
    if current_user.get_info()['role'] != 'patient':
        flash('You need patient privileges!')
        return redirect(url_for('auth.login'))
    caregiver = current_user.patients[0].caregiver
    return render_template("assignCaregiver.html", user=current_user.get_info(), caregiver=caregiver)


@main.route('/assignCaregiver', methods=['POST'])
@login_required
def assignCaregiver_post():
    if current_user.get_info()['role'] != 'patient':
        flash('You need patient privileges!')
        return redirect(url_for('auth.login'))
    caregiverInfo = request.form.get('caregiver-info')
    user = current_user
    patient = user.patients[0]
    if '@' in caregiverInfo:
        caregiver_user = User.query.filter_by(email=caregiverInfo).first()
        if caregiver_user:
            caregiver = Caregiver.query.filter_by(
                userID=caregiver_user.userID).first()
            if caregiver:
                flash(
                    f"You have successfully assigned {caregiver.firstName} as your caregiver")
                patient.caregiverID = caregiver.caregiverID
                db.session.commit()
            else:
                flash(f"The user is not a caregiver")
        else:
            flash("No caregiver was found for the email provided")
    else:
        caregiver = Caregiver.query.filter_by(
            caregiverID=caregiverInfo).first()
        if caregiver:
            flash(
                f"You have successfully assigned {caregiver.firstName} as your caregiver")
            patient.caregiverID = caregiver.caregiverID
            db.session.commit()
        else:
            flash(f"The user is not a caregiver")

    return render_template("assignCaregiver.html", user=current_user.get_info(), caregiver=patient.caregiver)


@main.route('/createPill', methods=['POST'])
@login_required
def createPill_post():
    if current_user.get_info()['role'] != 'pharmacist':
        return redirect(url_for('auth.login'))
    pillName = request.form.get('pill-name')
    shape = request.form.get('pill-shape')
    size = request.form.get('pill-size')
    qty = request.form.get('box-quantity')

    pill = Pill(name=pillName, shape=shape, size=size, boxQuantity=qty)
    db.session.add(pill)
    db.session.commit()
    return render_template("createPill.html", user=current_user.get_info())
