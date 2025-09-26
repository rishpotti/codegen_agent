import pytest
from flask import Flask
from unittest.mock import patch

# Assuming the provided code is in a file named 'user_routes.py'
from user_routes import user_bp, User, users_db

# Create a deep copy of the initial users_db state for resetting
initial_users_db_state = {}
for uid, user_obj in users_db.items():
    new_user = User(user_obj.id, user_obj.username, user_obj.email)
    new_user.followers = list(user_obj.followers)
    new_user.following = list(user_obj.following)
    initial_users_db_state[uid] = new_user

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(user_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def reset_db_and_mocks():
    """
    Resets the users_db to its initial state before each test.
    Also patches jwt_required to be a pass-through and get_jwt_identity
    to return a controllable value.
    """
    # Reset users_db
    users_db.clear()
    for uid, user_obj in initial_users_db_state.items():
        new_user = User(user_obj.id, user_obj.username, user_obj.email)
        new_user.followers = list(user_obj.followers)
        new_user.following = list(user_obj.following)
        users_db[uid] = new_user

    # Mock jwt_required to simply pass through
    with patch('user_routes.jwt_required', lambda fn: fn):
        # Patch get_jwt_identity to return a specific ID, can be overridden per test
        with patch('user_routes.get_jwt_identity', return_value=1) as mock_get_jwt_identity:
            yield mock_get_jwt_identity

# --- Tests for get_user_profile ---
def test_get_user_profile_success(client, reset_db_and_mocks):
    """
    Tests successful retrieval of a user profile.
    """
    # Ensure current user is not relevant for this GET, but JWT is required
    response = client.get('/profile/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == 'testuser1'
    assert data['email'] == 'test1@example.com'
    assert data['followers_count'] == 0
    assert data['following_count'] == 0

def test_get_user_profile_not_found(client, reset_db_and_mocks):
    """
    Tests retrieval of a non-existent user profile.
    """
    response = client.get('/profile/999')
    assert response.status_code == 404
    assert response.get_json() == {"msg": "User not found"}

# --- Tests for update_user_profile ---
def test_update_user_profile_success(client, reset_db_and_mocks):
    """
    Tests successful update of the authenticated user's profile.
    """
    # Set the current user to 1 for this test
    reset_db_and_mocks.return_value = 1
    
    new_email = "updated_test1@example.com"
    response = client.put('/profile', json={'email': new_email})
    assert response.status_code == 200
    data = response.get_json()
    assert data['msg'] == "Profile updated successfully"
    assert data['user']['email'] == new_email
    assert users_db[1].email == new_email # Verify direct update in db

def test_update_user_profile_user_not_found_jwt_mismatch(client, reset_db_and_mocks):
    """
    Tests updating profile when JWT identity does not map to a user (unlikely but possible).
    """
    reset_db_and_mocks.return_value = 999 # A user ID that doesn't exist
    response = client.put('/profile', json={'email': 'nonexistent@example.com'})
    assert response.status_code == 404
    assert response.get_json() == {"msg": "User not found"}

def test_update_user_profile_no_data(client, reset_db_and_mocks):
    """
    Tests updating profile with no data provided.
    """
    reset_db_and_mocks.return_value = 1
    original_email = users_db[1].email
    response = client.put('/profile', json={})
    assert response.status_code == 200
    data = response.get_json()
    assert data['msg'] == "Profile updated successfully"
    assert data['user']['email'] == original_email # Email should remain unchanged
    assert users_db[1].email == original_email

# --- Tests for follow_user ---
def test_follow_user_success(client, reset_db_and_mocks):
    """
    Tests a user successfully following another user.
    """
    reset_db_and_mocks.return_value = 1 # User 1 tries to follow
    
    response = client.post('/follow/2') # User 1 follows User 2
    assert response.status_code == 200
    assert response.get_json() == {"msg": "Successfully followed testuser2"}
    
    assert 2 in users_db[1].following # User 1 is following User 2
    assert 1 in users_db[2].followers # User 2 is followed by User 1

def test_follow_user_cannot_follow_self(client, reset_db_and_mocks):
    """
    Tests a user trying to follow themselves.
    """
    reset_db_and_mocks.return_value = 1
    response = client.post('/follow/1')
    assert response.status_code == 400
    assert response.get_json() == {"msg": "Cannot follow yourself"}

def test_follow_user_already_following(client, reset_db_and_mocks):
    """
    Tests a user trying to follow someone they are already following.
    """
    reset_db_and_mocks.return_value = 1
    # Manually set up the state: User 1 is already following User 2
    users_db[1].following.append(2)
    users_db[2].followers.append(1)

    response = client.post('/follow/2')
    assert response.status_code == 400
    assert response.get_json() == {"msg": "Already following this user"}

def test_follow_user_follower_not_found(client, reset_db_and_mocks):
    """
    Tests trying to follow when the follower (current_user_id) does not exist.
    """
    reset_db_and_mocks.return_value = 999 # Non-existent follower
    response = client.post('/follow/1')
    assert response.status_code == 404
    assert response.get_json() == {"msg": "User not found"}

def test_follow_user_followed_not_found(client, reset_db_and_mocks):
    """
    Tests trying to follow when the followed user does not exist.
    """
    reset_db_and_mocks.return_value = 1
    response = client.post('/follow/999') # User 1 follows non-existent user
    assert response.status_code == 404
    assert response.get_json() == {"msg": "User not found"}

# --- Tests for unfollow_user ---
def test_unfollow_user_success(client, reset_db_and_mocks):
    """
    Tests a user successfully unfollowing another user.
    """
    reset_db_and_mocks.return_value = 1
    # Manually set up the state: User 1 is following User 2
    users_db[1].following.append(2)
    users_db[2].followers.append(1)

    response = client.post('/unfollow/2')
    assert response.status_code == 200
    assert response.get_json() == {"msg": "Successfully unfollowed testuser2"}

    assert 2 not in users_db[1].following
    assert 1 not in users_db[2].followers

def test_unfollow_user_cannot_unfollow_self(client, reset_db_and_mocks):
    """
    Tests a user trying to unfollow themselves.
    """
    reset_db_and_mocks.return_value = 1
    response = client.post('/unfollow/1')
    assert response.status_code == 400
    assert response.get_json() == {"msg": "Cannot unfollow yourself"}

def test_unfollow_user_not_following(client, reset_db_and_mocks):
    """
    Tests a user trying to unfollow someone they are not following.
    """
    reset_db_and_mocks.return_value = 1
    response = client.post('/unfollow/2') # User 1 is not following User 2 initially
    assert response.status_code == 400
    assert response.get_json() == {"msg": "Not following this user"}

def test_unfollow_user_follower_not_found(client, reset_db_and_mocks):
    """
    Tests trying to unfollow when the follower (current_user_id) does not exist.
    """
    reset_db_and_mocks.return_value = 999
    response = client.post('/unfollow/1')
    assert response.status_code == 404
    assert response.get_json() == {"msg": "User not found"}

def test_unfollow_user_followed_not_found(client, reset_db_and_mocks):
    """
    Tests trying to unfollow when the followed user does not exist.
    """
    reset_db_and_mocks.return_value = 1
    response = client.post('/unfollow/999')
    assert response.status_code == 404
    assert response.get_json() == {"msg": "User not found"}
