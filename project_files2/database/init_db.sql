-- Create Users Table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Tweets Table
CREATE TABLE tweets (
    tweet_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Followers Table
CREATE TABLE follows (
    follower_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    following_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, following_id),
    CHECK (follower_id != following_id)
);

-- Create Likes Table
CREATE TABLE likes (
    like_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    tweet_id UUID NOT NULL REFERENCES tweets(tweet_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, tweet_id) -- A user can only like a tweet once
);

-- Optional: Add some initial data for testing
-- INSERT INTO users (username, email, password_hash) VALUES
-- ('testuser1', 'test1@example.com', 'hashedpassword1'),
-- ('testuser2', 'test2@example.com', 'hashedpassword2');

-- INSERT INTO tweets (user_id, content) VALUES
-- ((SELECT user_id FROM users WHERE username = 'testuser1'), 'This is the first tweet!'),
-- ((SELECT user_id FROM users WHERE username = 'testuser2'), 'Hello Twitter clone world!');

-- INSERT INTO follows (follower_id, following_id) VALUES
-- ((SELECT user_id FROM users WHERE username = 'testuser1'), (SELECT user_id FROM users WHERE username = 'testuser2'));

-- INSERT INTO likes (user_id, tweet_id) VALUES
-- ((SELECT user_id FROM users WHERE username = 'testuser1'), (SELECT tweet_id FROM tweets WHERE content = 'Hello Twitter clone world!'));
