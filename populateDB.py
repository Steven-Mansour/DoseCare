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

    user4 = User(email='steven@lau') #patient
    user4.set_password('123')  # Hash the password before storing

    user5 = User(email='hillary@lau') #careviger
    user5.set_password('123')  # Hash the password before storing

    user6 = User(email='mj@lau') #pharmacist
    user6.set_password('123')  # Hash the password before storing

    user7 = User(email='toni@lau') #patient
    user7.set_password('123')

    user8 = User(email='anthony@lau') #patient
    user8.set_password('123')

    user9 = User(email='elissa@lau') #patient
    user9.set_password('123')

    user10 = User(email='hanadi@lau') #patient
    user10.set_password('123')

    user11 = User(email='ryan@lau') #patient
    user11.set_password('123')

    user12 = User(email='ely@lau') #patient
    user12.set_password('123')

    user13 = User(email='christa@lau') #patient
    user13.set_password('123')

    user14 = User(email='erica@lau') #patient
    user14.set_password('123')

    db.session.add_all([user1, user2, user3, user4, user5, user6, user7, user8, user9, user10, user11, user12, user13, user14])
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
    
    patient3 = Patient(firstName='Toni', lastName='Tannous', emergencyContactNb='71549862',
                   caregiverID=caregiver2.caregiverID, userID=user7.userID)

    patient4 = Patient(firstName='Anthony', lastName='Tannous', emergencyContactNb='70321456',
                    caregiverID=caregiver2.caregiverID, userID=user8.userID)

    patient5 = Patient(firstName='Elissa', lastName='Tannous', emergencyContactNb='71985632',
                    caregiverID=caregiver2.caregiverID, userID=user9.userID)

    patient6 = Patient(firstName='Hanadi', lastName='Mansour', emergencyContactNb='70235489',
                    caregiverID=caregiver2.caregiverID, userID=user10.userID)

    patient7 = Patient(firstName='Ryan', lastName='Ibrahim', emergencyContactNb='71487615',
                       caregiverID=caregiver2.caregiverID, userID=user11.userID)

    patient8 = Patient(firstName='Ely', lastName='Ibrahim', emergencyContactNb='71687515',
                       caregiverID=caregiver2.caregiverID, userID=user12.userID)

    patient9 = Patient(firstName='Christa', lastName='Elias', emergencyContactNb='81467515',
                       caregiverID=caregiver2.caregiverID, userID=user13.userID)

    patient10 = Patient(firstName='Erica', lastName='Elias', emergencyContactNb='81487515',
                       caregiverID=caregiver2.caregiverID, userID=user14.userID)

    db.session.add_all([patient1, patient2, patient3, patient4, patient5, patient6, patient7, patient8, patient9, patient10])
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
    schedule1 = PillSchedule(day=[1, 1, 0], frequency=3, startDate='2025-01-01', endDate='2025-02-01', remainingQty=30, expiryDate='2025-12-31',
                             containerNb=1, patientID=patient1.patientID, caregiverID=caregiver1.caregiverID, pharmacyID=pharmacy1.pharmacyID, pillID=pill1.pillID)

    schedule2 = PillSchedule(day=[1, 0, 1], frequency=3, startDate='2025-01-01', endDate='2025-02-01', remainingQty=30, expiryDate='2025-12-31',
                             containerNb=1, patientID=patient2.patientID, caregiverID=caregiver2.caregiverID, pharmacyID=pharmacy2.pharmacyID, pillID=pill1.pillID)

    schedule3 = PillSchedule(day=[1, 0], frequency=2, startDate='2025-01-01', endDate='2025-03-01', remainingQty=40, expiryDate='2025-11-30',
                            containerNb=2, patientID=patient3.patientID, caregiverID=caregiver2.caregiverID, pharmacyID=pharmacy2.pharmacyID, pillID=pill1.pillID)

    schedule4 = PillSchedule(day=[1, 0, 0, 0], frequency=4, startDate='2025-01-10', endDate='2025-03-10', remainingQty=60, expiryDate='2025-10-15',
                            containerNb=3, patientID=patient4.patientID, caregiverID=caregiver2.caregiverID, pharmacyID=pharmacy2.pharmacyID, pillID=pill1.pillID)

    schedule5 = PillSchedule(day=[1, 1, 1, 0, 0, 0], frequency=6, startDate='2025-01-05', endDate='2025-04-05', remainingQty=30, expiryDate='2025-09-20',
                            containerNb=4, patientID=patient5.patientID, caregiverID=caregiver2.caregiverID, pharmacyID=pharmacy2.pharmacyID, pillID=pill1.pillID)

    schedule6 = PillSchedule(day=[0, 1, 1, 0, 1, 0, 1], frequency=7, startDate='2025-01-15', endDate='2025-04-15', remainingQty=50, expiryDate='2025-08-31',
                            containerNb=5, patientID=patient6.patientID, caregiverID=caregiver2.caregiverID, pharmacyID=pharmacy2.pharmacyID, pillID=pill1.pillID)

    schedule7 = PillSchedule(day=[1, 0, 0, 1, 0, 1, 1], frequency=7, startDate='2025-01-01', endDate='2025-05-01', remainingQty=90, expiryDate='2025-12-15',
                            containerNb=6, patientID=patient7.patientID, caregiverID=caregiver2.caregiverID, pharmacyID=pharmacy2.pharmacyID, pillID=pill1.pillID)

    schedule8 = PillSchedule(day=[0, 1, 0, 1, 1], frequency=5, startDate='2025-01-10', endDate='2025-05-10', remainingQty=70, expiryDate='2025-11-01',
                            containerNb=7, patientID=patient8.patientID, caregiverID=caregiver2.caregiverID, pharmacyID=pharmacy2.pharmacyID, pillID=pill1.pillID)

    schedule9 = PillSchedule(day=[1, 1, 1, 0], frequency=4, startDate='2025-01-01', endDate='2025-06-01', remainingQty=45, expiryDate='2025-10-10',
                            containerNb=8, patientID=patient9.patientID, caregiverID=caregiver2.caregiverID, pharmacyID=pharmacy2.pharmacyID, pillID=pill1.pillID)

    schedule10 = PillSchedule(day=[0, 0, 1, 1, 1, 1, 0], frequency=7, startDate='2025-01-15', endDate='2025-06-15', remainingQty=35, expiryDate='2025-09-01',
                            containerNb=9, patientID=patient10.patientID, caregiverID=caregiver2.caregiverID, pharmacyID=pharmacy2.pharmacyID, pillID=pill1.pillID)

    db.session.add_all([schedule1, schedule2, schedule3, schedule4, schedule5, schedule6, schedule7, schedule8, schedule9, schedule10])
    db.session.commit()

    # Create Schedule Properties
    schedule_properties = [
        ScheduleProperty(dose=1, time='08:00:00', scheduleID=schedule1.scheduleID),
        ScheduleProperty(dose=1, time='14:00:00', scheduleID=schedule1.scheduleID),
        ScheduleProperty(dose=1, time='20:00:00', scheduleID=schedule1.scheduleID),

        ScheduleProperty(dose=1, time='08:00:00', scheduleID=schedule2.scheduleID),
        ScheduleProperty(dose=4, time='14:00:00', scheduleID=schedule2.scheduleID),
        ScheduleProperty(dose=1, time='20:00:00', scheduleID=schedule2.scheduleID),

        ScheduleProperty(dose=2, time='07:30:00', scheduleID=schedule3.scheduleID),
        ScheduleProperty(dose=1, time='18:00:00', scheduleID=schedule3.scheduleID),

        ScheduleProperty(dose=3, time='08:00:00', scheduleID=schedule4.scheduleID),
        ScheduleProperty(dose=2, time='14:30:00', scheduleID=schedule4.scheduleID),
        ScheduleProperty(dose=1, time='20:00:00', scheduleID=schedule4.scheduleID),

        ScheduleProperty(dose=1, time='09:00:00', scheduleID=schedule5.scheduleID),

        ScheduleProperty(dose=2, time='06:00:00', scheduleID=schedule6.scheduleID),
        ScheduleProperty(dose=2, time='18:00:00', scheduleID=schedule6.scheduleID),

        ScheduleProperty(dose=4, time='08:00:00', scheduleID=schedule7.scheduleID),
        ScheduleProperty(dose=2, time='12:00:00', scheduleID=schedule7.scheduleID),
        ScheduleProperty(dose=3, time='16:00:00', scheduleID=schedule7.scheduleID),
        ScheduleProperty(dose=1, time='22:00:00', scheduleID=schedule7.scheduleID),

        ScheduleProperty(dose=3, time='07:00:00', scheduleID=schedule8.scheduleID),
        ScheduleProperty(dose=2, time='19:00:00', scheduleID=schedule8.scheduleID),

        ScheduleProperty(dose=2, time='10:30:00', scheduleID=schedule9.scheduleID),
        ScheduleProperty(dose=1, time='23:00:00', scheduleID=schedule9.scheduleID),

        ScheduleProperty(dose=1, time='13:00:00', scheduleID=schedule10.scheduleID),
    ]

    db.session.add_all(schedule_properties)

    # schedule_property1 = ScheduleProperty(
    #     dose=1, time='08:00:00', scheduleID=schedule1.scheduleID)
    # schedule_property2 = ScheduleProperty(
    #     dose=1, time='14:00:00', scheduleID=schedule1.scheduleID)
    # schedule_property3 = ScheduleProperty(
    #     dose=1, time='20:00:00', scheduleID=schedule1.scheduleID)
    # schedule_property4 = ScheduleProperty(
    #     dose=1, time='08:00:00', scheduleID=schedule2.scheduleID)
    # schedule_property5 = ScheduleProperty(
    #     dose=4, time='14:00:00', scheduleID=schedule2.scheduleID)
    # schedule_property6 = ScheduleProperty(
    #     dose=1, time='20:00:00', scheduleID=schedule2.scheduleID)

    # db.session.add_all(
    #     [schedule_property1, schedule_property2, schedule_property3,
    #      schedule_property4, schedule_property5, schedule_property6
    #      ])
    db.session.commit()

    print("Database populated successfully!")
