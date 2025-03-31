from flask import request, Blueprint, jsonify, redirect, url_for, render_template
from models import User, Pill, Caregiver, Patient, PillSchedule, ScheduleProperty, Notification
from infrastructure import socketio, db
from flask_socketio import join_room, leave_room
from flask_login import login_required, current_user

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


# @socketio.on("send_notification")
# def handle_send_notification(data):
#     user_id = data.get("user_id")
#     message = data.get("message")

#     # Store the notification in the database
#     notif = Notification(userID=user_id, message=message)
#     db.session.add(notif)
#     db.session.commit()

#     # Emit the notification to the specific user's room
#     socketio.emit(f"notification_{user_id}", {
#                   "message": message}, room=user_id)


def create_notification(user_id, message, notifyCaregiver=True):
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

    update_notification_count(user_id)
    # Notify the caregiver
    if notifyCaregiver == True:
        patient = user.patients[0]
        if patient and patient.caregiver:
            caregiverUserID = patient.caregiver.userID
            notification = Notification(
                userID=caregiverUserID, message=message)

            # Add the notification to the session and commit it to the database
            db.session.add(notification)
            db.session.commit()

            update_notification_count(caregiverUserID)


def update_notification_count(userID):
    notifications_count = Notification.query.filter_by(
        userID=userID, isRead=False).count()
    socketio.emit(
        f"update_notification_count_{userID}",
        {"count": notifications_count},
        # Ensure the user is in a room named after their user_id
        room=str(userID)
    )


@notification.route("/notifications/<int:user_id>")
@login_required
def get_notifications(user_id):
    if current_user.userID == user_id:
        # Get page number from query parameters
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Number of notifications per page
        pagination = Notification.query.filter_by(userID=user_id).order_by(
            Notification.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)

        notifications_snapshot = [notif.to_dict()
                                  for notif in pagination.items]
        # Modify the notifications in the database, mark as read, but don't modify them on the page
        notifications = pagination.items
        for notif in notifications:
            if not notif.isRead:  # If unread, mark as read in the database
                notif.isRead = True
        db.session.commit()
        update_notification_count(user_id)
        return render_template('notifications.html',
                               notifications=notifications_snapshot,
                               page=page,
                               total_pages=pagination.pages,
                               user=current_user.get_info())

    else:
        return redirect(url_for('main.home'))
