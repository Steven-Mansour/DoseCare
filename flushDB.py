
from app import db, create_app
from models import User, Patient, Caregiver, Pharmacy, PillSchedule, Pill, ScheduleProperty, patient_pharmacy

with create_app().app_context():
    # Clear many-to-many relationship table first
    db.session.execute(patient_pharmacy.delete())

    # Delete all records from other tables
    db.session.query(ScheduleProperty).delete()
    db.session.query(PillSchedule).delete()
    db.session.query(Pill).delete()
    db.session.query(Pharmacy).delete()
    db.session.query(Patient).delete()
    db.session.query(Caregiver).delete()
    db.session.query(User).delete()

    db.session.commit()
    print("All tables emptied successfully!")
