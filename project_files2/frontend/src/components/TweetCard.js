import React from 'react';
import { Link } from 'react-router-dom';

const TweetCard = ({ tweet }) => {
  if (!tweet) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-4 mb-4">
      <div className="flex items-start">
        <Link to={`/profile/${tweet.user.handle}`} className="flex-shrink-0">
          <img
            className="h-10 w-10 rounded-full object-cover"
            src={tweet.user.avatar}
            alt={`${tweet.user.name}'s avatar`}
          />
        </Link>
        <div className="ml-3 flex-grow">
          <div className="flex items-center">
            <Link to={`/profile/${tweet.user.handle}`} className="font-bold text-gray-900 dark:text-white hover:underline">
              {tweet.user.name}
            </Link>
            <span className="ml-1 text-sm text-gray-500 dark:text-gray-400">@{tweet.user.handle}</span>
            <span className="ml-1 text-sm text-gray-500 dark:text-gray-400">· {tweet.timestamp}</span>
          </div>
          <p className="mt-1 text-gray-800 dark:text-gray-200">
            {tweet.text}
          </p>
          {tweet.media && (
            <div className="mt-3 rounded-lg overflow-hidden">
              <img
                src={tweet.media}
                alt="Tweet media"
                className="w-full h-auto object-cover"
              />
            </div>
          )}
          <div className="mt-4 flex justify-around text-gray-500 dark:text-gray-400">
            <button className="flex items-center space-x-1 hover:text-blue-400">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
              <span>{tweet.comments}</span>
            </button>
            <button className="flex items-center space-x-1 hover:text-green-400">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004 12v1m-4 5h.582m15.356 2A8.001 8.001 0 0020 12v-1m-4-7h.582m15.356 2A8.001 8.001 0 0020 12v-1"></path></svg>
              <span>{tweet.retweets}</span>
            </button>
            <button className="flex items-center space-x-1 hover:text-red-400">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>
              <span>{tweet.likes}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TweetCard;
