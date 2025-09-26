from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from project_files2.backend.models import db, Notification, User  # Assuming models.py exists and defines these

notification_bp = Blueprint('notifications', __name__)

@notification_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """
    Get all notifications for the authenticated user.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.timestamp.desc()).all()
    
    output = []
    for notification in notifications:
        output.append({
            "id": notification.id,
            "message": notification.message,
            "type": notification.type,
            "read": notification.read,
            "timestamp": notification.timestamp.isoformat()
        })
    return jsonify(output), 200

@notification_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_as_read(notification_id):
    """
    Mark a specific notification as read.
    """
    user_id = get_jwt_identity()
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()

    if not notification:
        return jsonify({"msg": "Notification not found or not authorized"}), 404

    notification.read = True
    db.session.commit()
    return jsonify({"msg": "Notification marked as read"}), 200

@notification_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """
    Delete a specific notification.
    """
    user_id = get_jwt_identity()
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()

    if not notification:
        return jsonify({"msg": "Notification not found or not authorized"}), 404

    db.session.delete(notification)
    db.session.commit()
    return jsonify({"msg": "Notification deleted"}), 200
