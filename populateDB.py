from app import db, create_app
from models import User, Patient, Caregiver, Pharmacy, PillSchedule, Pill, ScheduleProperty
from flask import Flask


with create_app().app_context():

    # Create Users
    user1 = User(email='john.doe@example.com', password_hash='hashedpassword1')
    user2 = User(email='jane.smith@example.com',
                 password_hash='hashedpassword2')

    db.session.add_all([user1, user2])
    db.session.commit()

    # Create Caregivers
    caregiver1 = Caregiver(
        firstName='Michael', lastName='Brown', phoneNb='123456789', userID=user1.userID)

    db.session.add(caregiver1)
    db.session.commit()

    # Create Patients
    patient1 = Patient(firstName='Alice', lastName='Johnson', emergencyContactNb='987654321',
                       caregiverID=caregiver1.caregiverID, userID=user2.userID)

    db.session.add(patient1)
    db.session.commit()

    # Create Pharmacy
    # pharmacy1 = Pharmacy(name='Health Pharmacy',
    #                      location='123 Main St', phoneNb='5551234', userID=user1.userID)

    # db.session.add(pharmacy1)
    # db.session.commit()

    # Create Pills
    pill1 = Pill(name='Paracetamol', shape='Round', size=1,
                 boxQuantity=10)

    db.session.add(pill1)
    db.session.commit()

    # Create Pill Schedule
    schedule1 = PillSchedule(day=1, frequency=3, startDate='2025-01-01', endDate='2025-02-01', remainingQty=30, expiryDate='2025-12-31',
                             containerNb=1, patientID=patient1.patientID, caregiverID=caregiver1.caregiverID, pharmacyID=None, pillID=pill1.pillID)

    db.session.add(schedule1)
    db.session.commit()

    # Create Schedule Properties
    schedule_property1 = ScheduleProperty(
        dose=1, time='08:00:00', scheduleID=schedule1.scheduleID)
    schedule_property2 = ScheduleProperty(
        dose=1, time='14:00:00', scheduleID=schedule1.scheduleID)
    schedule_property3 = ScheduleProperty(
        dose=1, time='20:00:00', scheduleID=schedule1.scheduleID)

    db.session.add_all(
        [schedule_property1, schedule_property2, schedule_property3])
    db.session.commit()

    print("Database populated successfully!")
