from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from models import User, Pill, Caregiver, Patient, PillSchedule, ScheduleProperty, Pharmacy, patient_pharmacy
from app import db
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from messages import sendMessage, send_email

main = Blueprint('main', __name__)


@main.route('/popup-opened/<int:patient_id>')
@login_required
def popup_opened(patient_id):
    if not isCarer(patient_id):
        flash("You are not allowed to access this page", "failure")
        return redirect(url_for('main.home'))
    month = request.args.get('month')
    day = request.args.get('day')
    patient = Patient.query.filter_by(patientID=patient_id).first()
    schedule = patient.get_days_schedule(day, month)
    return jsonify({'status': 'success', 'message': schedule})


@main.route('/about')
@login_required
def about():
    return render_template("about.html", user=current_user.get_info())


@main.route('/privacyPolicy')
@login_required
def privacyPolicy():
    return render_template("privacy.html", user=current_user.get_info())


@main.route('/extendSchedule', methods=["POST"])
@login_required
def extendSchedule():
    scheduleID = request.form.get('scheduleID')
    print(scheduleID)
    schedule = PillSchedule.query.filter_by(scheduleID=scheduleID).first()
    patientID = schedule.patientID
    if (not isCarer(patientID)):
        flash("You are not allowed to perform this action", "failure")
    daysExtended = request.form.get('extendDaysInput')
    pillsAdded = request.form.get('refillAmount')
    schedule.extendSchedule(daysExtended, pillsAdded)
    flash("Schedule has been updated successfully", "success")
    return redirect(url_for('main.schedule', patient_id=patientID))
    # return f"{scheduleID} has been updated into {daysExtended} days and {pillsAdded} pills"


@main.route('/')
def index():
    return redirect(url_for('main.home'))


@main.route('/hey')
async def hey():
    patient = Patient.query.filter_by(patientID=2).first()
    # caregiver = Caregiver.query.filter_by(caregiverID=13).first()
    # caregiver.get_lowest_pills_schedule()
    # return "hey"
    message = await patient.miss_dose([24, 25, 26])
    # recipients_list = ["stvnmnsr@gmail.com", "steven.mansour@lau.edu"]
    # await send_email("Async Email Subject", "This is an async test email body.", recipients_list)
    # return patient.send_schedule()
    return message


@main.route('/home')
@login_required
def home():
    return render_template("home.html", user=current_user.get_stats())


@main.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    # user = User.query.filter_by(userID=user_id).first()
    user = current_user
    return render_template("profile.html", user=user.get_info())


@main.route('/assignPharmacy')
@login_required
def assignPharmacy():
    if (current_user.get_info()['role'] != 'patient'):
        flash("You are not allowed to access this page")
        return redirect(url_for('main.home'))
    patient = current_user.get_info()['patientID']
    patient = Patient.query.filter_by(patientID=patient).first()
    pharmacies = patient.pharmacies
    return render_template("assignPharmacy.html", user=current_user.get_info(), pharmaciesList=pharmacies)


@main.route('/assignPharmacy', methods=['POST'])
@login_required
def assignPharmacyPost():
    if (current_user.get_info()['role'] != 'patient'):
        flash("You are not allowed to access this page")
        return redirect(url_for('main.home'))
    patient = current_user.get_info()['patientID']
    patient = Patient.query.filter_by(patientID=patient).first()
    pharmacy = Pharmacy.query.filter_by(
        pharmacyID=request.form.get('pharmacyID')).first()
    if pharmacy and pharmacy not in patient.pharmacies:
        patient.pharmacies.append(pharmacy)
        db.session.commit()
        flash(f"Successfuly selected {pharmacy.name}", "success")
    else:
        if pharmacy:
            flash("Pharmacy already registered", "suggestion")
        else:
            flash("Pharmacy does not exist!", "failure")
    return redirect(url_for('main.assignPharmacy'))


@main.route('/unassignPharmacy', methods=['POST'])
@login_required
def unassignPharmacy():
    if (current_user.get_info()['role'] != 'patient'):
        flash("You are not allowed to access this page", "failure")
        return redirect(url_for('main.home'))
    patient = current_user.get_info()['patientID']
    patient = Patient.query.filter_by(patientID=patient).first()
    pharmacy_id = request.form.get("pharmacy-ID")
    print(pharmacy_id)
    pharmacy = Pharmacy.query.filter_by(
        pharmacyID=pharmacy_id).first()
    if pharmacy and pharmacy not in patient.pharmacies:
        flash(f"{pharmacy.name} is not registered!")
    else:
        patient.pharmacies.remove(pharmacy)
        db.session.commit()
        flash("Pharmacy has been successfully removed", "success")
        return redirect(url_for('main.assignPharmacy'))


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
    patient = Patient.query.filter_by(patientID=patient_id).first()
    role = current_user.get_info()['role']

    if ((role == 'caregiver' and patient.caregiverID != current_user.get_info()['caregiverID']) or
        ((role == 'patient' and patient.patientID != current_user.get_info()['patientID']) or
         (role == 'pharmacy' and current_user.pharmacies[0].pharmacyID not in [
          pharmacy.pharmacyID for pharmacy in patient.pharmacies])
         )):
        flash("You cannot access this patients data")
        return redirect(url_for('main.home'))
    monthlySched = patient.get_monthly_schedule()
    return render_template("calendar.html", user=current_user.get_info(), patient_id=patient_id,
                           cal=monthlySched["cal"],
                           year=monthlySched["current_year"],
                           month=monthlySched["month_name"],
                           daily_pills=monthlySched["daily_pills"],
                           current_day=monthlySched["current_day"], patient=patient)


@main.route('/deleteSchedule/<int:schedule_id>', methods=['POST'])
@login_required
def deleteSchedule(schedule_id):
    schedule = PillSchedule.query.filter_by(scheduleID=schedule_id).first()
    patient = schedule.patient
    if (not isCarer(patient.patientID)):
        flash("You are not allowed to access this route")
        return redirect(url_for('main.home'))
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
    if (current_user.get_info()['role'] not in ['caregiver', 'pharmacist']):
        flash("You are not allowed to access this route")
        return redirect(url_for('main.home'))
    carer = current_user.caregivers[0] if current_user.caregivers else current_user.pharmacies[0]
    schedules = carer.get_patients_ending_schedule(
        len(carer.patients))
    return render_template("expiringSchedules.html", user=current_user.get_stats(), schedules=schedules)


@main.route('/lowSupplySchedules')
@login_required
def lowSupplySchedules():
    if (current_user.get_info()['role'] not in ['caregiver', 'pharmacist']):
        flash("You are not allowed to access this route")
        return redirect(url_for('main.home'))
    user = current_user
    carer = current_user.caregivers[0] if current_user.caregivers else current_user.pharmacies[0]
    schedules = carer.get_lowest_pills_schedule(
        len(carer.patients))
    return render_template("lowSupplySchedules.html", user=user.get_stats(), schedules=schedules)


@main.route('/schedule/<int:patient_id>')
@login_required
def schedule(patient_id):
    if not isCarer(patient_id):
        flash("You are not allowed to access this route")
        return redirect(url_for('main.home'))
    patient = Patient.query.filter_by(patientID=patient_id).first()
    if patient:
        schedules = patient.pill_schedules
        freeContainer = patient.get_unused_container()
        session['breadcrumbs'] = [
            {'name': 'Home', 'url': url_for('main.home')},
            {'name': 'Patients', 'url': url_for('main.viewPatients')},
            {'name': 'Schedules', 'url': url_for(
                'main.schedule', patient_id=patient_id)}
        ]
        return render_template('schedule.html', patient=patient, freeContainer=freeContainer, user=current_user.get_info(), schedules=schedules)
    else:
        flash("Patient does not exist")
    return redirect(url_for('main.home'))


@main.route('/editSchedule/<int:schedule_id>')
@login_required
def editSchedule(schedule_id):
    schedule = PillSchedule.query.get_or_404(schedule_id)
    patient = schedule.patient
    if not isCarer(patient.patientID):
        flash("You are not allowed to access this route")
        return redirect(url_for('main.home'))
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


@main.route('/createSchedule/<int:patient_id>')
@login_required
def createSchedule(patient_id):
    if not isCarer(patient_id):
        flash("You are not allowed to access this route")
        return redirect(url_for('main.home'))
    patient_id = patient_id
    patient = Patient.query.filter_by(patientID=patient_id).first()
    unusedCont = patient.get_unused_container()
    if unusedCont == -1:
        flash("You need to delete a schedule before creating a new one.", "failure")
        return redirect(url_for('main.home'))
    return render_template('createSchedule.html', user=current_user.get_info(), patient_id=patient_id)


@main.route('/createSchedule/<int:patient_id>', methods=['POST'])
@login_required
def createSchedule_post(patient_id):
    if not isCarer(patient_id):
        flash("You are not allowed to access this route", "failure")
        return redirect(url_for('maini.home'))
    schedule = PillSchedule()
    patient = Patient.query.get_or_404(patient_id)
    pillID = request.form.get('pill_id')
    frequency = request.form.get('frequency')
    selected_days = [0] * int(frequency)
    containerNb = patient.get_unused_container()
    if containerNb == -1:
        flash("You cannot create more schedules, make sure to delete one before you proceed", "failure")
        return redirect(url_for('main.createSchedule'))
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
    schedule.containerNb = containerNb
    schedule.frequency = frequency
    schedule.day = selected_days
    # return redirect(url_for('main.createSchedule', schedule=schedule, patient_id=patient_id))
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
    flash(
        f"""Schedule has been created successfully: \n Make sure to use the disk named
        '{schedule.pill.shape[0].capitalize()}{schedule.pill.size}' in container {schedule.containerNb}""", "success")

    return redirect(url_for('main.schedule', patient_id=patient_id))


@main.route('/editSchedule/<int:schedule_id>', methods=['POST'])
@login_required
def editSchedule_post(schedule_id):
    schedule = PillSchedule.query.get_or_404(schedule_id)
    patient = schedule.patient
    if not isCarer(patient.patientID):
        flash("You are not allowed to access this route", "failure")
        return redirect(url_for('main.home'))
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
    flash('The schedule has been updated successfully', "success")
    return redirect(url_for('main.schedule', patient_id=patient.patientID))


@main.route('/createPill')
@login_required
def createPill():
    if current_user.get_info()['role'] != 'pharmacist':
        flash("This page requires pharmacist priveleges", "failure")
        return redirect(url_for('main.home'))
    return render_template("createPill.html", user=current_user.get_info())


@main.route('/viewPatients')
@login_required
def viewPatients():
    if current_user.get_info()['role'] not in 'caregiver pharmacist':
        return redirect(url_for('main.home'))
    session['breadcrumbs'] = [
        {'name': 'Home', 'url': url_for('main.home')},
        {'name': 'Patients', 'url': url_for('main.viewPatients')}
    ]
    carer = current_user.caregivers[0] if current_user.caregivers else current_user.pharmacies[0]
    return render_template("viewPatients.html", user=current_user.get_info(), patients=carer.patients)


@main.route('/removeCaregiver/<int:patient_id>', methods=['POST'])
@login_required
def removeCaregiver(patient_id):
    if current_user.get_info()['role'] != 'patient':
        flash('You need patient privileges!', "failure")
        return redirect(url_for('main.home'))
    if current_user.get_info()['patientID'] != patient_id:
        flash("You are not allowed to change another patient's data!", "failure")
        return redirect(url_for('main.home'))
    patient = Patient.query.filter_by(patientID=patient_id).first()
    patient.caregiver = None
    db.session.commit()
    flash("Successfully removed caregiver", "success")
    return redirect(url_for('main.assignCaregiver'))


@main.route('/assignSelfCaregiver/<int:patient_id>', methods=['POST'])
@login_required
def assignSelfCaregiver(patient_id):
    if current_user.get_info()['role'] != 'patient':
        flash('You need patient privileges!', "failure")
        return redirect(url_for('main.home'))
    if current_user.get_info()['patientID'] != patient_id:
        flash("You are not allowed to change another patient's data!", "failure")
        return redirect(url_for('main.home'))
    patient = Patient.query.filter_by(patientID=patient_id).first()
    patient.selfCarer = bool(request.form.get('self_caregiver'))
    db.session.commit()
    if patient.selfCarer == 1:
        flash("You can now manage your schedules", "success")
    elif patient.selfCarer == 0:
        flash("You no longer have caregiver privileges", "success")
    return redirect(url_for('main.assignCaregiver'))


@main.route('/assignCaregiver')
@login_required
def assignCaregiver():
    if current_user.get_info()['role'] != 'patient':
        flash('You need patient privileges!', "failure")
        return redirect(url_for('main.home'))
    caregiver = current_user.patients[0].caregiver
    return render_template("assignCaregiver.html", user=current_user.get_info(), caregiver=caregiver)


@main.route('/assignCaregiver', methods=['POST'])
@login_required
def assignCaregiver_post():
    if current_user.get_info()['role'] != 'patient':
        flash('You need patient privileges!', "failure")
        return redirect(url_for('main.home'))
    caregiverID = request.form.get('caregiverID')
    caregiverName = request.form.get('caregiver-info')
    if (not caregiverID):
        flash("Caregiver does not exist", "failure")
        return redirect(url_for('main.assignCaregiver'))
    user = current_user
    patient = user.patients[0]
    patient.caregiverID = caregiverID
    db.session.commit()
    flash(
        f"You have successfully assigned {caregiverName} as your caregiver", "success")

    return render_template("assignCaregiver.html", user=current_user.get_info(), caregiver=patient.caregiver)


@main.route('/createPill', methods=['POST'])
@login_required
def createPill_post():
    if current_user.get_info()['role'] != 'pharmacist':
        return redirect(url_for('main.home'))
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


@main.route('/search_pharmacy')
@login_required
def search_pharmacy():
    pharmacy_name = request.args.get('name', '')  # Correct parameter name

    if not pharmacy_name:
        return jsonify([])  # Return an empty list if no name is provided

    # Query the database for caregivers that match the name (case-insensitive)
    pharmacies = Pharmacy.query.filter(
        (Pharmacy.name.ilike(f'%{pharmacy_name}%'))
    ).all()

    # Convert results to a list of dictionaries
    result = [{
        'name': pharmacy.name,
        'location': pharmacy.location,
        'id': pharmacy.pharmacyID
    } for pharmacy in pharmacies]

    return jsonify(result)


def isCarer(patient_id):
    patient = Patient.query.filter_by(patientID=patient_id).first()
    if patient.selfCarer == 1 and current_user.patients[0].patientID == patient_id:
        return True
    carer = current_user.caregivers[0] if current_user.caregivers else current_user.pharmacies[0]
    if ((current_user.caregivers and patient.caregiverID == carer.caregiverID) or
            (current_user.pharmacies and carer.pharmacyID in [pharmacy.pharmacyID for pharmacy in patient.pharmacies])):
        return True
    return False
