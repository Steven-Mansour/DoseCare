
from app import db, create_app
from models import User, Patient, Caregiver, Pharmacy, PillSchedule, Pill, ScheduleProperty, Notification, patient_pharmacy
from flask import Flask

with create_app().app_context():
    # Create Users
    users_data = [
        ('john.doe@example.com', 'hashedpassword1'),  # caregiver
        ('jane.smith@example.com', 'hashedpassword2'),  # patient
        ('steven.mansour@lau.edu', 'steven'),  # pharmacist
        ('steven@lau', '123'),  # patient
        ('hillarytannous@gmail.com', '123'),  # caregiver
        ('mj@lau', '123'),  # pharmacist
        ('toni@lau', '123'),  # patient
        ('anthony@lau', '123'),  # patient
        ('elissa@lau', '123'),  # patient
        ('hanadi@lau', '123'),  # patient
        ('ryan@lau', '123'),  # patient
        ('ely@lau', '123'),  # patient
        ('christa@lau', '123'),  # patient
        ('erica@lau', '123'),  # patient
    ]
    users = []
    for email, pwd in users_data:
        user = User(email=email)
        user.set_password(pwd)
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    # Create Caregivers
    caregiver1 = Caregiver(firstName='Michael', lastName='Brown',
                           phoneNb='123456789', userID=users[0].userID)
    caregiver2 = Caregiver(firstName='Hillary', lastName='Tannous',
                           phoneNb='123123', userID=users[4].userID)
    db.session.add_all([caregiver1, caregiver2])
    db.session.commit()

    # Create Patients
    patient_info = [
        ('Alice', 'Johnson', '987654321', caregiver1, users[1]),
        ('Steven', 'Mansour', '71487515', caregiver2, users[3]),
        ('Toni', 'Tannous', '71549862', caregiver2, users[6]),
        ('Anthony', 'Tannous', '70321456', caregiver2, users[7]),
        ('Elissa', 'Tannous', '71985632', caregiver2, users[8]),
        ('Hanadi', 'Mansour', '70235489', caregiver2, users[9]),
        ('Ryan', 'Ibrahim', '71487615', caregiver2, users[10]),
        ('Ely', 'Ibrahim', '71687515', caregiver2, users[11]),
        ('Christa', 'Elias', '81467515', caregiver2, users[12]),
        ('Erica', 'Elias', '81487515', caregiver2, users[13]),
    ]
    patients = [
        Patient(firstName=f, lastName=l, emergencyContactNb=phone,
                caregiverID=cg.caregiverID, userID=u.userID)
        for f, l, phone, cg, u in patient_info
    ]
    db.session.add_all(patients)
    db.session.commit()

    # Create Pharmacies
    pharmacy1 = Pharmacy(name='Health Pharmacy', location='123 Main St',
                         phoneNb='5551234', userID=users[2].userID)
    pharmacy2 = Pharmacy(name='Tannous Pharmacy', location='Kfaraabida',
                         phoneNb='10000', userID=users[5].userID)
    db.session.add_all([pharmacy1, pharmacy2])
    db.session.commit()

    # Link Patients with Pharmacies
    patients[0].pharmacies.extend([pharmacy1, pharmacy2])
    patients[1].pharmacies.append(pharmacy1)
    patients[2].pharmacies.append(pharmacy2)
    db.session.commit()

    # Create Pills
    pills = [
        Pill(name='Paracetamol', shape='Round', size=1, boxQuantity=10),
        Pill(name='Ibuprofen', shape='Oval', size=2, boxQuantity=20),
        Pill(name='Aspirin', shape='Round', size=1, boxQuantity=15),
        Pill(name='Metformin', shape='Capsule', size=3, boxQuantity=30),
        Pill(name='Lisinopril', shape='Oval', size=2, boxQuantity=25),
        Pill(name='Amoxicillin', shape='Capsule', size=3, boxQuantity=21),
        Pill(name='Atorvastatin', shape='Oval', size=2, boxQuantity=28),
        Pill(name='Omeprazole', shape='Capsule', size=3, boxQuantity=14),
        Pill(name='Cetirizine', shape='Round', size=1, boxQuantity=10),
        Pill(name='Vitamin C', shape='Chewable', size=2, boxQuantity=50),
    ]
    db.session.add_all(pills)
    db.session.commit()

    # Create Pill Schedules
    schedules = [
        ([1, 1, 0], 3, '2025-01-01', '2025-02-01',
         30, '2025-12-31', 1, patients[0]),
        ([1, 0, 1], 3, '2025-01-01', '2025-02-01',
         30, '2025-12-31', 1, patients[1]),
        ([1, 0], 2, '2025-01-01', '2025-03-01', 40, '2025-11-30', 2, patients[2]),
        ([1, 0, 0, 0], 4, '2025-01-10', '2025-03-10',
         60, '2025-10-15', 3, patients[3]),
        ([1, 1, 1, 0, 0, 0], 6, '2025-01-05',
         '2025-04-05', 30, '2025-09-20', 2, patients[4]),
        ([0, 1, 1, 0, 1, 0, 1], 7, '2025-01-15',
         '2025-04-15', 50, '2025-08-31', 3, patients[5]),
        ([1, 0, 0, 1, 0, 1, 1], 7, '2025-01-01',
         '2025-05-01', 90, '2025-12-15', 2, patients[6]),
        ([0, 1, 0, 1, 1], 5, '2025-01-10', '2025-05-10',
         70, '2025-11-01', 3, patients[7]),
        ([1, 1, 1, 0], 4, '2025-01-01', '2025-06-01',
         45, '2025-12-01', 1, patients[8]),
        ([0, 1, 1], 3, '2025-01-05', '2025-06-30',
         60, '2025-10-01', 2, patients[9]),
    ]
    db.session.add_all([
        PillSchedule(
            day=day, frequency=freq, startDate=start, endDate=end, remainingQty=qty, expiryDate=exp,
            containerNb=cont, patientID=pat.patientID, pillID=pills[0].pillID
        )
        for day, freq, start, end, qty, exp, cont, pat in schedules
    ])
    db.session.commit()
