from app import db, create_app
from models import User, Patient, Caregiver, Pharmacy, PillSchedule, Pill, ScheduleProperty
from flask import Flask


with create_app().app_context():

    # Create Users
    user1 = User(email='john.doe@example.com')
    user1.set_password('hashedpassword1')  # Hash the password before storing

    user2 = User(email='jane.smith@example.com')
    user2.set_password('hashedpassword2')  # Hash the password before storing

    user3 = User(email='steven.mansour@lau.edu')
    user3.set_password('steven')  # Hash the password before storing

    user4 = User(email='steven.@lau')
    user4.set_password('123')  # Hash the password before storing

    user5 = User(email='hillary.@lau')
    user5.set_password('123')  # Hash the password before storing

    user6 = User(email='mj.@lau')
    user6.set_password('123')  # Hash the password before storing

    db.session.add_all([user1, user2, user3, user4, user5, user6])
    db.session.commit()

    # Create Caregivers
    caregiver1 = Caregiver(
        firstName='Michael', lastName='Brown', phoneNb='123456789', userID=user1.userID)

    caregiver2 = Caregiver(
        firstName='Hillary', lastName='Tannous', phoneNb='123123', userID=user5.userID
    )

    db.session.add_all([caregiver1, caregiver2])
    db.session.commit()

    # Create Patients
    patient1 = Patient(firstName='Alice', lastName='Johnson', emergencyContactNb='987654321',
                       caregiverID=caregiver1.caregiverID, userID=user2.userID)

    patient2 = Patient(firstName='Steven', lastName='Mansour', emergencyContactNb='71487515',
                       caregiverID=caregiver2.caregiverID, userID=user4.userID)

    db.session.add_all([patient1, patient2])
    db.session.commit()

    # Create Pharmacy
    pharmacy1 = Pharmacy(name='Health Pharmacy',
                         location='123 Main St', phoneNb='5551234', userID=user3.userID)

    pharmacy2 = Pharmacy(name='Tannous Pharmacy',
                         location='Kfaraabida', phoneNb='10000', userID=user6.userID)

    db.session.add_all([pharmacy1, pharmacy2])
    db.session.commit()

    # Create Pills
    pill1 = Pill(name='Paracetamol', shape='Round', size=1,
                 boxQuantity=10)

    db.session.add(pill1)
    db.session.commit()

    # Create Pill Schedule
    schedule1 = PillSchedule(day=[1], frequency=3, startDate='2025-01-01', endDate='2025-02-01', remainingQty=30, expiryDate='2025-12-31',
                             containerNb=1, patientID=patient1.patientID, caregiverID=caregiver1.caregiverID, pharmacyID=pharmacy1.pharmacyID, pillID=pill1.pillID)

    schedule2 = PillSchedule(day=[1], frequency=3, startDate='2025-01-01', endDate='2025-02-01', remainingQty=30, expiryDate='2025-12-31',
                             containerNb=1, patientID=patient2.patientID, caregiverID=caregiver2.caregiverID, pharmacyID=pharmacy2.pharmacyID, pillID=pill1.pillID)

    db.session.add_all([schedule1, schedule2])
    db.session.commit()

    # Create Schedule Properties
    schedule_property1 = ScheduleProperty(
        dose=1, time='08:00:00', scheduleID=schedule1.scheduleID)
    schedule_property2 = ScheduleProperty(
        dose=1, time='14:00:00', scheduleID=schedule1.scheduleID)
    schedule_property3 = ScheduleProperty(
        dose=1, time='20:00:00', scheduleID=schedule1.scheduleID)
    schedule_property4 = ScheduleProperty(
        dose=1, time='08:00:00', scheduleID=schedule2.scheduleID)
    schedule_property5 = ScheduleProperty(
        dose=4, time='14:00:00', scheduleID=schedule2.scheduleID)
    schedule_property6 = ScheduleProperty(
        dose=1, time='20:00:00', scheduleID=schedule2.scheduleID)

    db.session.add_all(
        [schedule_property1, schedule_property2, schedule_property3,
         schedule_property4, schedule_property5, schedule_property6
         ])
    db.session.commit()

    print("Database populated successfully!")
