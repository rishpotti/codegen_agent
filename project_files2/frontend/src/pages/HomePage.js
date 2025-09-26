import React, { useState, useEffect } from 'react';
import axios from 'axios';

const HomePage = () => {
  const [timelineTweets, setTimelineTweets] = useState([]);
  const [trendingContent, setTrendingContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHomePageData = async () => {
      try {
        setLoading(true);
        // Fetch personalized timeline tweets
        const timelineResponse = await axios.get('/api/timeline');
        setTimelineTweets(timelineResponse.data);

        // Fetch general trending content
        const trendingResponse = await axios.get('/api/trending');
        setTrendingContent(trendingResponse.data);

      } catch (err) {
        setError('Failed to fetch home page data.');
        console.error('Error fetching home page data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHomePageData();
  }, []); // Empty dependency array means this effect runs once after the initial render

  if (loading) {
    return <div className="p-4">Loading your timeline...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="homepage-container p-4">
      <h1 className="text-2xl font-bold mb-4">Your Timeline</h1>

      <div className="timeline-section mb-8">
        {timelineTweets.length === 0 ? (
          <p>No tweets to display in your timeline. Follow more users to see their tweets!</p>
        ) : (
          timelineTweets.map((tweet) => (
            <div key={tweet.id} className="tweet-card bg-white shadow-md rounded-lg p-4 mb-4">
              <p className="font-semibold text-blue-600">{tweet.user.username}</p>
              <p className="text-gray-800 mt-1">{tweet.content}</p>
              {/* Add more tweet details like timestamp, likes, comments if available */}
            </div>
          ))
        )}
      </div>

      <h2 className="text-xl font-bold mb-4">Trending Now</h2>

      <div className="trending-section">
        {trendingContent.length === 0 ? (
          <p>No trending content available at the moment.</p>
        ) : (
          trendingContent.map((trend, index) => (
            <div key={index} className="trend-item bg-white shadow-sm rounded-lg p-3 mb-2">
              <p className="font-semibold text-gray-700">#{trend.topic}</p>
              <p className="text-sm text-gray-500">{trend.count} tweets</p>
              {/* Add more trend details if available */}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default HomePage;
