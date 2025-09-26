from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
# Assuming you have a models.py with User and db (SQLAlchemy instance)
# from .models import User, db

user_bp = Blueprint('user', __name__)

# Placeholder for a User model and db object for demonstration
class User:
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email
        self.followers = []
        self.following = []

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "followers_count": len(self.followers),
            "following_count": len(self.following)
        }

# In a real application, this would come from a database
users_db = {
    1: User(1, "testuser1", "test1@example.com"),
    2: User(2, "testuser2", "test2@example.com")
}


@user_bp.route('/profile/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    """
    Retrieve details of a specific user.
    """
    # current_user_id = get_jwt_identity() # Use this if you need to check if the current user can view this profile

    # In a real app, query the database for the user
    user = users_db.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    return jsonify(user.to_dict()), 200

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """
    Update the profile of the authenticated user.
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # In a real app, retrieve user from db using current_user_id
    user = users_db.get(current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404 # Should not happen if JWT is valid

    # Update user fields (example: email)
    if 'email' in data:
        user.email = data['email']
    # Add more fields as needed

    # In a real app, commit changes to the database
    # db.session.commit()

    return jsonify({"msg": "Profile updated successfully", "user": user.to_dict()}), 200

@user_bp.route('/follow/<int:user_id>', methods=['POST'])
@jwt_required()
def follow_user(user_id):
    """
    Follow a user.
    """
    current_user_id = get_jwt_identity()

    if current_user_id == user_id:
        return jsonify({"msg": "Cannot follow yourself"}), 400

    follower = users_db.get(current_user_id)
    followed = users_db.get(user_id)

    if not follower or not followed:
        return jsonify({"msg": "User not found"}), 404

    if followed.id in follower.following:
        return jsonify({"msg": "Already following this user"}), 400

    follower.following.append(followed.id)
    followed.followers.append(follower.id)
    # In a real app, commit changes to the database

    return jsonify({"msg": f"Successfully followed {followed.username}"}), 200

@user_bp.route('/unfollow/<int:user_id>', methods=['POST'])
@jwt_required()
def unfollow_user(user_id):
    """
    Unfollow a user.
    """
    current_user_id = get_jwt_identity()

    if current_user_id == user_id:
        return jsonify({"msg": "Cannot unfollow yourself"}), 400

    follower = users_db.get(current_user_id)
    followed = users_db.get(user_id)

    if not follower or not followed:
        return jsonify({"msg": "User not found"}), 404

    if followed.id not in follower.following:
        return jsonify({"msg": "Not following this user"}), 400

    follower.following.remove(followed.id)
    followed.followers.remove(follower.id)
    # In a real app, commit changes to the database

    return jsonify({"msg": f"Successfully unfollowed {followed.username}"}), 200
