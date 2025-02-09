from app import db
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import JSON
from datetime import datetime, timedelta
import calendar


class User(db.Model, UserMixin):
    userID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True,
                      nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        """Hash and store the password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the provided password against the stored hash"""
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Return the user ID for Flask-Login"""
        return str(self.userID)  # Ensure it's returned as a string

    def get_info(self):
        """Check if the user is a patient, caregiver, or pharmacist and return a dictionary."""
        if self.patients:  # Checks if the user has an associated patient record
            return {"role": "patient", "name": self.patients[0].firstName, "patientID": self.patients[0].patientID, "email": self.email, }
        elif self.caregivers:  # Checks if the user has an associated caregiver record
            return {"role": "caregiver", "name": self.caregivers[0].firstName, "caregiverID": self.caregivers[0].caregiverID, "email": self.email, }
        elif self.pharmacies:  # Checks if the user has an associated pharmacy record
            return {"role": "pharmacist", "name": self.pharmacies[0].name, "pharmacyID": self.pharmacies[0].pharmacyID, "email": self.email, }
        # If the user doesn't belong to any category
        return {"role": "unknown", "name": "N/A"}

    def get_stats(self):
        """Check if the user is a patient, caregiver, or pharmacist and return a dictionary."""
        if self.patients:  # Checks if the user has an associated patient record
            return {"role": "patient", "name": self.patients[0].firstName, "patientID": self.patients[0].patientID, "email": self.email,  "patient": self.patients[0], "caregiver": self.patients[0].caregiver}
        elif self.caregivers:  # Checks if the user has an associated caregiver record
            return {"role": "caregiver", "name": self.caregivers[0].firstName, "caregiverID": self.caregivers[0].caregiverID, "email": self.email, "caregiver": self.caregivers[0]}
        elif self.pharmacies:  # Checks if the user has an associated pharmacy record
            return {"role": "pharmacist", "name": self.pharmacies[0].name, "pharmacyID": self.pharmacies[0].pharmacyID, "email": self.email, "pharmacy": self.pharmacies[0]}
        # If the user doesn't belong to any category
        return {"role": "unknown", "name": "N/A"}


class Caregiver(db.Model):
    caregiverID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    phoneNb = db.Column(db.String(15), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('user.userID'),
                       nullable=False)  # References User table

    # Define relationship with User
    user = db.relationship('User', backref='caregivers', lazy=True)


class Patient(db.Model):
    patientID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    emergencyContactNb = db.Column(db.String(15), nullable=False)
    caregiverID = db.Column(db.Integer, db.ForeignKey(
        'caregiver.caregiverID'), nullable=True)  # Foreign Key from CAREGIVER
    userID = db.Column(db.Integer, db.ForeignKey('user.userID'),
                       nullable=False)  # Foreign Key from USER

    # Define relationships with User and Caregiver
    caregiver = db.relationship('Caregiver', backref='patients', lazy=True)
    user = db.relationship('User', backref='patients', lazy=True)

    def get_monthly_schedule(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        month_name = calendar.month_name[current_month]
        cal = calendar.Calendar().monthdayscalendar(current_year, current_month)
        daily_pills = {day: [] for week in cal for day in week if day != 0}
        schedules = self.pill_schedules
        for schedule in schedules:
            start_date = schedule.startDate
            end_date = schedule.endDate
            frequency = schedule.frequency
            days = schedule.day

            for week in cal:
                for day in week:
                    # Skip days that don't exist in the current month (0 means no day in this slot)
                    if day == 0:
                        continue
                    current_date = datetime(current_year, current_month, day)
                    if start_date <= current_date.date() <= end_date:
                        date_difference = current_date.date() - start_date
                        days_difference = date_difference.days
                        if days[days_difference % frequency == 1]:
                            if schedule.pill.name not in daily_pills[current_date.day]:
                                daily_pills[current_date.day].append(
                                    schedule.pill.name)

        return {
            "cal": cal,
            "current_year": current_year,
            "month_name": month_name,
            "daily_pills": daily_pills
        }


class Pharmacy(db.Model):
    pharmacyID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    phoneNb = db.Column(db.String(20), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey(
        'user.userID'), nullable=False)

    # Relationship with User
    user = db.relationship('User', backref='pharmacies', lazy=True)


class PillSchedule(db.Model):
    scheduleID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    day = db.Column(JSON, nullable=False)
    frequency = db.Column(db.Integer, nullable=False)
    startDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    remainingQty = db.Column(db.Integer, nullable=False)
    expiryDate = db.Column(db.Date, nullable=False)
    containerNb = db.Column(db.Integer, nullable=False)

    # Foreign Keys
    patientID = db.Column(db.Integer, db.ForeignKey(
        'patient.patientID'), nullable=False)
    caregiverID = db.Column(db.Integer, db.ForeignKey(
        'caregiver.caregiverID'), nullable=True)
    pharmacyID = db.Column(db.Integer, db.ForeignKey(
        'pharmacy.pharmacyID'), nullable=True)
    pillID = db.Column(db.Integer, db.ForeignKey(
        'pill.pillID'), nullable=False)  # Added pillID foreign key

    # Relationships
    patient = db.relationship('Patient', backref='pill_schedules', lazy=True)
    caregiver = db.relationship(
        'Caregiver', backref='pill_schedules', lazy=True)
    pharmacy = db.relationship('Pharmacy', backref='pill_schedules', lazy=True)
    pill = db.relationship('Pill', backref='pill_schedules',
                           lazy=True)  # Relationship with Pill


class Pill(db.Model):
    pillID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    shape = db.Column(db.String(50), nullable=False)  # Example: round, oval
    size = db.Column(db.Integer, nullable=False)   # Example: 4mm, 8mm ...
    # Total number of pills in a box
    boxQuantity = db.Column(db.Integer, nullable=False)


class ScheduleProperty(db.Model):
    propertyID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dose = db.Column(db.Integer, nullable=False)
    time = db.Column(db.Time, nullable=False)

    # Foreign Key
    scheduleID = db.Column(db.Integer, db.ForeignKey(
        'pill_schedule.scheduleID'), nullable=False)

    # Relationship
    schedule = db.relationship(
        'PillSchedule', backref='schedule_properties', lazy=True)
