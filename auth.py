from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import User, Patient, Caregiver, Pharmacy
from flask_login import login_user, logout_user, login_required
from app import db

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    role = request.form.get('role')
    if user:
        flash("The email is already registered!")
        return redirect(url_for('auth.signup'))

    user = User(email=email)
    user.set_password(password=password)
    db.session.add(user)
    db.session.commit()

    if role == 'patient':
        # Handle patient logic
        firstName = request.form.get('first-name')
        lastName = request.form.get('last-name')
        emergencyContact = request.form.get('emergency-contact')
        patient = Patient(firstName=firstName, lastName=lastName, emergencyContactNb=emergencyContact,
                          caregiverID=None, userID=user.userID)
        db.session.add(patient)
        db.session.commit()
        flash("You are registered as a patient.", "success")
        return redirect(url_for('auth.login'))

    elif role == 'caregiver':
        # Handle caregiver logic
        firstName = request.form.get('first-name')
        lastName = request.form.get('last-name')
        phoneNumber = request.form.get('phone-number')
        caregiver = Caregiver(
            firstName=firstName, lastName=lastName, phoneNb=phoneNumber, userID=user.userID)
        db.session.add(caregiver)
        db.session.commit()

        flash("You are registered as a caregiver.", "success")
        return redirect(url_for('auth.login'))

    elif role == 'pharmacist':
        # Handle pharmacist logic
        pharmacyName = request.form.get('pharmacy-name')
        location = request.form.get('location')
        phoneNumber = request.form.get('phone-number')
        pharmacy = Pharmacy(name=pharmacyName,
                            location=location, phoneNb=phoneNumber, userID=user.userID)
        db.session.add(pharmacy)
        db.session.commit()
        flash("You are registered as a pharmacist.", "success")
        return redirect(url_for('auth.login'))

    else:
        # Handle unknown role (optional)
        flash("Invalid role selected.", "danger")
        return redirect(url_for('main.index'))


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return redirect('login')

    login_user(user, remember=remember)
    return redirect(url_for('main.home'))


@auth.route('/signup')
def signup():
    return render_template('signUp.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
