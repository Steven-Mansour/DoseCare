from flask import Flask, render_template, jsonify, request, Blueprint
from flask_socketio import SocketIO
from datetime import datetime, time


socketio = SocketIO(cors_allowed_origins="*")
rpi = Blueprint('rpi', __name__)

json_data = {
    55: {
        "pillName": "Panadol",
        "containerNb": 1,
        "remainingQty": 3,
        "day": [1, 1, 0],
        "index": 0,
        "startDate": "2025-01-15",
        "endDate": "2025-02-15",
        "properties": [{"propertyID": 1, "time": "10:30:00", "dose": 1},
                       {"propertyID": 2, "time": "23:00:00", "dose": 2}
                       ]
    },
    56: {
        "pillName": "Motilium",
        "containerNb": 2,
        "remainingQty": 5,
        "day": [1, 1, 0, 1, 0],
        "index": 0,
        "startDate": "2025-01-15",  # Store as datetime.date
        "endDate": "2025-02-17",    # Store as datetime.date
        "properties": [{"propertyID": 3, "time": "20:30:00", "dose": 2}]
    }
}
# Dictionary to store connected Raspberry Pis
clients = {}

# Register a Raspberry Pi when it connects


@socketio.on('register_id')
def register_id(data):
    pi_id = data['id']
    clients[pi_id] = request.sid  # Store session ID for communication
    print(f"Raspberry Pi {pi_id} connected.")
    send_json_to_pi(pi_id)

# Function to send JSON data to Raspberry Pi


def send_json_to_pi(pi_id):
    if pi_id in clients:
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
