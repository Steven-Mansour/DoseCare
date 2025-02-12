from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from models import User, Pill, Caregiver, Patient, PillSchedule, ScheduleProperty
from app import db
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from messages import sendMessage

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return redirect(url_for('main.home'))


@main.route('/hey')
def hey():
    # patient = Patient.query.filter_by(patientID=31).first()
    caregiver = Caregiver.query.filter_by(caregiverID=13).first()
    caregiver.get_lowest_pills_schedule()
    return "hey"
    # return patient.send_schedule()


@main.route('/home')
@login_required
def home():
    return render_template("home.html", user=current_user.get_stats())


@main.route('/profile')
@login_required
def profile():
    return render_template("profile.html", user=current_user.get_info())


# @main.route('/assignPharmacy')
# @login_required
# def assignPharmacy():
#     if (current_user.get_info()['role'] != 'patient'):
#         flash("You are not allowed to access this page")
#         return redirect(url_for('main.home'))
#     patient = current_user.get_info()['patientID']
#     patient = Patient.query.first_or_404(patient)
#     pharmacy = patient.pharmacy
#     return render_template("assignPharmacy.html", user=current_user.get_info(), pharmacy=pharmacy)

@main.route('/getNextDose/<int:patient_id>')
@login_required
def getNextDose(patient_id):
    if (current_user.get_info()['role'] != 'patient'):
        flash("You are not allowed to access this page")
        return redirect(url_for('main.home'))
    patient = Patient.query.filter_by(patientID=patient_id).first()
    return f"{patient.get_next_dose()}"


@main.route('/viewCalendar/<int:patient_id>')
@login_required
def viewCalendar(patient_id):
    if (current_user.get_info()['role'] != 'patient' and current_user.get_info()['role'] != 'caregiver'):
        flash("You are not allowed to access this page")
        return redirect(url_for('main.home'))
    patient = Patient.query.filter_by(patientID=patient_id).first()
    if (current_user.get_info()['role'] == 'caregiver'):
        if (patient.caregiverID != current_user.get_info()['caregiverID']):
            flash("You cannot access this patients data")
            return redirect(url_for('main.home'))
    current_year = datetime.now().year
    monthlySched = patient.get_monthly_schedule()
    return render_template("calendar.html", user=current_user.get_info(),
                           cal=monthlySched["cal"],
                           year=monthlySched["current_year"],
                           month=monthlySched["month_name"],
                           daily_pills=monthlySched["daily_pills"],
                           current_day=monthlySched["current_day"], patient=patient)


@main.route('/createSchedule/<int:patient_id>')
@login_required
def createSchedule(patient_id):
    if (current_user.get_info()['role'] != 'pharmacist') and (current_user.get_info()['role'] != 'caregiver'):
        flash("You are not allowed to access this route")
        return redirect(url_for('auth.login'))
    patient_id = patient_id
    return render_template('createSchedule.html', user=current_user.get_info(), patient_id=patient_id)


@main.route('/deleteSchedule/<int:schedule_id>', methods=['POST'])
@login_required
def deleteSchedule(schedule_id):
    if (current_user.get_info()['role'] != 'caregiver'):
        flash("You are not allowed to access this route")
        return redirect(url_for('auth.login'))
    schedule = PillSchedule.query.filter_by(scheduleID=schedule_id).first()
    patient = schedule.patient
    if (patient.caregiverID != current_user.get_info()['caregiverID']):
        print(patient.firstName)
        print(current_user.get_info()['caregiverID'])
        flash("You are not allowed to perform this action")

    if schedule:
        for prop in schedule.schedule_properties:
            db.session.delete(prop)
        db.session.delete(schedule)
        db.session.commit()
        flash("Schedule deleted successfully", "success")
    else:
        flash("Schedule not found", "error")

    return redirect(url_for('main.schedule', patient_id=patient.patientID))


@main.route('/expiringSchedules')
@login_required
def expiringSchedules():
    if (current_user.get_info()['role'] != 'caregiver'):
        flash("You are not allowed to access this route")
        return redirect(url_for('auth.login'))
    user = current_user
    caregiver = user.caregivers[0]
    schedules = caregiver.get_patients_ending_schedule(
        len(caregiver.patients))
    return render_template("expiringSchedules.html", user=user.get_stats(), schedules=schedules)


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
            session['breadcrumbs'] = [
                {'name': 'Home', 'url': url_for('main.home')},
                {'name': 'Patients', 'url': url_for('main.viewPatients')},
                {'name': 'Schedules', 'url': url_for(
                    'main.schedule', patient_id=patient_id)}
            ]
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
        session['breadcrumbs'] = [
            {'name': 'Home', 'url': url_for('main.home')},
            {'name': 'Patients', 'url': url_for('main.viewPatients')},
            {'name': 'Schedules', 'url': url_for(
                'main.schedule', patient_id=schedule.patientID)},
            {'name': f'{schedule.pill.name} schedule', 'url': url_for(
                'main.editSchedule', schedule_id=schedule.scheduleID)},

        ]
        return render_template('editSchedule.html', user=current_user.get_info(), schedule=schedule)

    else:
        flash("Schedule does not exist")
    return redirect(url_for('main.home'))


@main.route('/createSchedule/<int:patient_id>', methods=['POST'])
@login_required
def createSchedule_post(patient_id):
    if (current_user.get_info()['role'] != 'pharmacist') and (current_user.get_info()['role'] != 'caregiver'):
        flash("You are not allowed to access this route")
        return redirect(url_for('auth.login'))
    schedule = PillSchedule()
    patient = Patient.query.get_or_404(patient_id)
    pillID = request.form.get('pill_id')
    frequency = request.form.get('frequency')
    selected_days = [0] * int(frequency)
    # Loop through each checkbox and update the corresponding index to 1 if checked
    for i in range(int(frequency)):
        if f"day_{i}" in request.form:  # If the checkbox for that day is checked
            selected_days[i] = 1
    schedule.pillID = pillID
    schedule.patientID = patient.patientID
    schedule.startDate = request.form.get('startDate')
    schedule.endDate = request.form.get('endDate')
    schedule.expiryDate = request.form.get('expiryDate')
    schedule.remainingQty = request.form.get('remainingQty')
    schedule.containerNb = request.form.get('containerNb')
    schedule.frequency = frequency
    schedule.day = selected_days
    db.session.add(schedule)
    db.session.commit()
    # Assuming only time and dose are part of the form
    for index in range(0, len(request.form) // 2):
        # Get the new time and dose fields
        time = request.form.get(f'time_{index + 1}')
        dose = request.form.get(f'dose_{index + 1}')

        # If time or dose is provided, add a new schedule property
        if time and dose:
            new_schedule_property = ScheduleProperty(
                time=time, dose=dose, scheduleID=schedule.scheduleID)
            db.session.add(new_schedule_property)
        db.session.commit()
    return redirect(url_for('main.schedule', patient_id=patient_id))


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
    flash('The schedule has been updated')
    return redirect(url_for('main.editSchedule', schedule_id=schedule_id))


@main.route('/createPill')
@login_required
def createPill():
    if current_user.get_info()['role'] != 'pharmacist':
        flash("This page requires pharmacist priveleges")
        return redirect(url_for('auth.login'))
    return render_template("createPill.html", user=current_user.get_info())


@main.route('/viewPatients')
@login_required
def viewPatients():
    if current_user.get_info()['role'] != 'caregiver':
        return redirect(url_for('auth.login'))
    session['breadcrumbs'] = [
        {'name': 'Home', 'url': url_for('main.home')},
        {'name': 'Patients', 'url': url_for('main.viewPatients')}
    ]
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
    caregiverID = request.form.get('caregiverID')
    caregiverName = request.form.get('caregiver-info')
    if (not caregiverID):
        flash("Caregiver does not exist")
        return redirect(url_for('main.assignCaregiver'))
    user = current_user
    patient = user.patients[0]
    patient.caregiverID = caregiverID
    db.session.commit()
    flash(f"You have successfully assigned {caregiverName} as your caregiver")

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


@main.route('/search_pill')
def search_pill():
    pill_name = request.args.get('pill', '')
    # Query the database for pills that match the name
    pills = Pill.query.filter(Pill.name.ilike(f'%{pill_name}%')).all()
    # Convert results to a list of dictionaries
    result = [{'name': pill.name, 'id': pill.pillID, 'shape': pill.shape}
              for pill in pills]

    return jsonify(result)


@main.route('/search_caregiver')
@login_required
def search_caregiver():
    caregiver_name = request.args.get('name', '')  # Correct parameter name

    if not caregiver_name:
        return jsonify([])  # Return an empty list if no name is provided

    # Query the database for caregivers that match the name (case-insensitive)
    caregivers = Caregiver.query.filter(
        (Caregiver.firstName.ilike(f'%{caregiver_name}%')) |
        (Caregiver.lastName.ilike(f'%{caregiver_name}%'))
    ).all()

    # Convert results to a list of dictionaries
    result = [{
        'firstName': caregiver.firstName,
        'lastName': caregiver.lastName,
        'id': caregiver.caregiverID
    } for caregiver in caregivers]

    return jsonify(result)
