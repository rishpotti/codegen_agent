import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import PropTypes from 'prop-types';

const UserProfile = ({ user, onFollowToggle }) => {
  const [isFollowing, setIsFollowing] = useState(user.isFollowing);

  useEffect(() => {
    setIsFollowing(user.isFollowing);
  }, [user.isFollowing]);

  const handleFollowToggle = () => {
    setIsFollowing(!isFollowing);
    if (onFollowToggle) {
      onFollowToggle(user.id, !isFollowing);
    }
  };

  return (
    <div className="user-profile-card">
      <div className="avatar-section">
        <img src={user.avatar} alt={`${user.username}'s avatar`} className="user-avatar" />
        <h2 className="username">{user.username}</h2>
      </div>
      <p className="user-bio">{user.bio}</p>
      <div className="follow-stats">
        <Link to={`/users/${user.username}/followers`} className="stat-link">
          <strong>{user.followers}</strong> followers
        </Link>
        <Link to={`/users/${user.username}/following`} className="stat-link">
          <strong>{user.following}</strong> following
        </Link>
      </div>
      <button
        onClick={handleFollowToggle}
        className={`follow-button ${isFollowing ? 'unfollow' : 'follow'}`}
      >
        {isFollowing ? 'Unfollow' : 'Follow'}
      </button>
    </div>
  );
};

UserProfile.propTypes = {
  user: PropTypes.shape({
    id: PropTypes.string.isRequired,
    username: PropTypes.string.isRequired,
    avatar: PropTypes.string.isRequired,
    bio: PropTypes.string.isRequired,
    followers: PropTypes.number.isRequired,
    following: PropTypes.number.isRequired,
    isFollowing: PropTypes.bool.isRequired,
  }).isRequired,
  onFollowToggle: PropTypes.func,
};

UserProfile.defaultProps = {
  onFollowToggle: () => {},
};

export default UserProfile;
