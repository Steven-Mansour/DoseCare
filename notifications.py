from flask import request, Blueprint, jsonify
from models import User, Pill, Caregiver, Patient, PillSchedule, ScheduleProperty, Notification
from infrastructure import socketio, db
from flask_socketio import join_room, leave_room

notification = Blueprint('notification', __name__)


@socketio.on('connect')
def handle_connect():
    # Retrieve the user_id from query parameters when connecting
    user_id = request.args.get('user_id')
    if user_id:
        join_room(user_id)  # Add the user to a room named with their user_id
        print(f"User {user_id} connected.")


@socketio.on('disconnect')
def handle_disconnect():
    # Retrieve the user_id from query parameters when disconnecting
    user_id = request.args.get('user_id')
    if user_id:
        leave_room(user_id)  # Remove the user from their room
        print(f"User {user_id} disconnected.")


@socketio.on("send_notification")
def handle_send_notification(data):
    user_id = data.get("user_id")
    message = data.get("message")

    # Store the notification in the database
    notif = Notification(userID=user_id, message=message)
    db.session.add(notif)
    db.session.commit()

    # Emit the notification to the specific user's room
    socketio.emit(f"notification_{user_id}", {
                  "message": message}, room=user_id)


def create_notification(user_id, message):
    if not user_id:
        return
    user = User.query.filter_by(userID=user_id).first()
    if not user:
        return
    # Create a new Notification instance
    notification = Notification(userID=user_id, message=message)

    # Add the notification to the session and commit it to the database
    db.session.add(notification)
    db.session.commit()

    # Count unread notifications for the user
    notifications_count = Notification.query.filter_by(
        userID=user_id, isRead=False).count()
    socketio.emit(
        f"update_notification_count_{user_id}",
        {"count": notifications_count},
        # Ensure the user is in a room named after their user_id
        room=str(user_id)
    )


@notification.route("/notifications/<int:user_id>")
def get_notifications(user_id):
    # Retrieve all notifications for the given user, ordered by timestamp (newest first)
    notifications = Notification.query.filter_by(
        userID=user_id).order_by(Notification.timestamp.desc()).all()
    return jsonify([{
        "message": n.message,
        "timestamp": n.timestamp,
        "is_read": n.isRead
    } for n in notifications])
