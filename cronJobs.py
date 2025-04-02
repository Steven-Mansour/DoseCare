from models import Patient
from notifications import create_notification


def check_if_patients_need_checkup(app):
    with app.app_context():
        print("Cron job started")
        patients = Patient.query.all()
        for patient in patients:
            needsCheckup = patient.calculate_last_checkup()
            if needsCheckup[0] == "invalid":
                create_notification(patient.userID, needsCheckup[1])

    return
