from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

# Assuming db and models are imported from a central location, e.g., app.py or models.py
# For this example, we'll define basic models here. In a real app, these would be in models.py
# and db would be initialized in app.py

# --- Dummy Database and Models (Replace with actual SQLAlchemy setup) ---
class User:
    def __init__(self, id, username):
        self.id = id
        self.username = username

    def to_dict(self):
        return {"id": self.id, "username": self.username}

class Message:
    def __init__(self, id, sender_id, recipient_id, content, timestamp=None):
        self.id = id
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.content = content
        self.timestamp = timestamp if timestamp else datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

# In a real application, you would import db from your SQLAlchemy instance
# from your_app_folder.extensions import db
# and your models from your_app_folder.models import User, Message

# Dummy in-memory database for demonstration
_users = {
    1: User(1, "alice"),
    2: User(2, "bob"),
    3: User(3, "charlie"),
}
_messages = []
_message_id_counter = 1

# --- End Dummy Database and Models ---


message_bp = Blueprint('message_bp', __name__, url_prefix='/messages')

@message_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    recipient_id = data.get('recipient_id')
    content = data.get('content')

    if not recipient_id or not content:
        return jsonify({"msg": "Recipient ID and content are required"}), 400

    # In a real app, check if recipient_id exists in the database
    if recipient_id not in _users:
        return jsonify({"msg": "Recipient not found"}), 404

    global _message_id_counter
    new_message = Message(
        id=_message_id_counter,
        sender_id=current_user_id,
        recipient_id=recipient_id,
        content=content
    )
    _messages.append(new_message)
    _message_id_counter += 1

    # In a real app: db.session.add(new_message); db.session.commit()
    return jsonify({"msg": "Message sent successfully", "message": new_message.to_dict()}), 201

@message_bp.route('/conversation/<int:other_user_id>', methods=['GET'])
@jwt_required()
def get_conversation(other_user_id):
    current_user_id = get_jwt_identity()

    # In a real app, check if other_user_id exists
    if other_user_id not in _users:
        return jsonify({"msg": "User not found"}), 404

    conversation = []
    for msg in _messages:
        # Messages sent by current user to other_user, or by other_user to current user
        if (msg.sender_id == current_user_id and msg.recipient_id == other_user_id) or \
           (msg.sender_id == other_user_id and msg.recipient_id == current_user_id):
            conversation.append(msg.to_dict())

    # Sort messages by timestamp
    conversation.sort(key=lambda x: x['timestamp'])

    return jsonify(conversation), 200

@message_bp.route('/my_conversations', methods=['GET'])
@jwt_required()
def get_my_conversations():
    current_user_id = get_jwt_identity()

    # Find all unique users with whom the current user has exchanged messages
    participating_users_ids = set()
    for msg in _messages:
        if msg.sender_id == current_user_id:
            participating_users_ids.add(msg.recipient_id)
        elif msg.recipient_id == current_user_id:
            participating_users_ids.add(msg.sender_id)

    conversations_summary = []
    for user_id in participating_users_ids:
        # Get the last message in the conversation for a summary
        last_message = None
        for msg in reversed(_messages): # Iterate backwards to find the most recent quickly
            if (msg.sender_id == current_user_id and msg.recipient_id == user_id) or \
               (msg.sender_id == user_id and msg.recipient_id == current_user_id):
                last_message = msg
                break
        
        other_user = _users.get(user_id)
        if other_user and last_message:
            conversations_summary.append({
                "other_user": other_user.to_dict(),
                "last_message": last_message.to_dict()
            })
    
    # Sort summaries by the timestamp of the last message
    conversations_summary.sort(key=lambda x: x['last_message']['timestamp'], reverse=True)

    return jsonify(conversations_summary), 200

