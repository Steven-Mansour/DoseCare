from flask import Flask, render_template, jsonify, request, Blueprint

from models import User, Pill, Caregiver, Patient, PillSchedule, ScheduleProperty
from infrastructure import socketio
rpi = Blueprint('rpi', __name__)


# Dictionary to store connected Raspberry Pis
clients = {}

# Register a Raspberry Pi when it connects


@socketio.on('register_id')
def register_id(data):
    pi_id = data['id']
    print(pi_id)
    patient = Patient.query.filter_by(raspberryPiId=pi_id).first()
    if patient:
        clients[pi_id] = request.sid  # Store session ID for communication
        print(
            f"Raspberry Pi {pi_id} connected for patient {patient.firstName} {patient.lastName}.")
    send_json_to_pi(pi_id)

# Function to send JSON data to Raspberry Pi


def send_json_to_pi(pi_id):
    if pi_id in clients:
        patient = Patient.query.filter_by(raspberryPiId=pi_id).first()
        json_data = patient.send_schedule()
        socketio.emit('json_data', json_data, room=clients[pi_id])  # Send data
        print(f"Sent JSON to {pi_id}: {json_data}")
        return {"status": "success", "message": f"JSON sent to {pi_id}"}
    else:
        return {"status": "error", "message": f"Raspberry Pi {pi_id} not connected"}


@socketio.on('notify_event')
def handle_notification(data):
    event = data.get("event")
    dose_info = data.get("dose_info")

    print(f"\n🔔 Notification received from Raspberry Pi:")
    print(f"  Event: {event}")
    print(f"  Dose Info: {dose_info}\n")

# Route to trigger JSON sending via button


@rpi.route('/send_json')
def send_json():
    # Send to specific Raspberry Pi
    response = send_json_to_pi("raspberry_pi_1")
    return jsonify(response)
