from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import User, Pill, Caregiver, Patient, PillSchedule, ScheduleProperty
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


@main.route('/schedule/<int:patient_id>')
@login_required
def schedule(patient_id):
    if (current_user.get_info()['role'] != 'pharmacist') and (current_user.get_info()['role'] != 'caregiver'):
        flash("You are not allowed to access this route")
        return redirect(url_for('auth.login'))
    patient = Patient.query.filter_by(patientID=patient_id).first()
    if patient:
        if patient.caregiverID == current_user.caregivers[0].caregiverID:
            schedules = patient.pill_schedules
            return render_template('schedule.html', patient=patient, user=current_user.get_info(), schedules=schedules)
        else:
            flash("You are not allowed to access this patients schedule")
    else:
        flash("Patient does not exist")
    return redirect(url_for('main.home'))


@main.route('/editSchedule/<int:schedule_id>')
@login_required
def editSchedule(schedule_id):
    if (current_user.get_info()['role'] != 'pharmacist') and (current_user.get_info()['role'] != 'caregiver'):
        flash("You are not allowed to access this route")
        return redirect(url_for('auth.login'))
    schedule = PillSchedule.query.get_or_404(schedule_id)
    if schedule:
        return render_template('editSchedule.html', user=current_user.get_info(), schedule=schedule)

    else:
        flash("Schedule does not exist")
    return redirect(url_for('main.home'))


@main.route('/editSchedule/<int:schedule_id>', methods=['POST'])
@login_required
def editSchedule_post(schedule_id):
    if (current_user.get_info()['role'] != 'pharmacist') and (current_user.get_info()['role'] != 'caregiver'):
        flash("You are not allowed to access this route")
        return redirect(url_for('auth.login'))
    schedule = PillSchedule.query.get_or_404(schedule_id)
    frequency = request.form.get('frequency')
    selected_days = [0] * int(frequency)
    # Loop through each checkbox and update the corresponding index to 1 if checked
    for i in range(int(frequency)):
        if f"day_{i}" in request.form:  # If the checkbox for that day is checked
            selected_days[i] = 1
    startDate = request.form.get('startDate')
    endDate = request.form.get('endDate')
    expiryDate = request.form.get('expiryDate')
    remQty = request.form.get('remainingQty')
    containerNb = request.form.get('containerNb')
    schedule.frequency = frequency
    schedule.day = selected_days
    schedule.startDate = startDate
    schedule.endDate = endDate
    schedule.expiryDate = expiryDate
    schedule.remainingQty = remQty
    schedule.containerNb = containerNb

    # Handle the schedule_properties (edit and delete)
    for index, schedule_property in enumerate(schedule.schedule_properties):
        # Check if the property is marked for deletion
        delete_property = request.form.get(f'delete_{index + 1}')
        if delete_property == '1':  # If marked for deletion
            db.session.delete(schedule_property)
        else:
            # Otherwise, update the time and dose
            time = request.form.get(f'time_{index + 1}')
            dose = request.form.get(f'dose_{index + 1}')
            schedule_property.time = time
            schedule_property.dose = dose
    max_index = len(schedule.schedule_properties)

    # Assuming only time and dose are part of the form
    for index in range(max_index, len(request.form) // 2):
        # Get the new time and dose fields
        time = request.form.get(f'time_{index + 1}')
        dose = request.form.get(f'dose_{index + 1}')

        # If time or dose is provided, add a new schedule property
        if time and dose:
            new_schedule_property = ScheduleProperty(
                time=time, dose=dose, scheduleID=schedule.scheduleID)
            db.session.add(new_schedule_property)
        db.session.commit()
    return "hey"


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
