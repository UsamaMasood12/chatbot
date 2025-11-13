/**
 * Analytics Dashboard Component
 * Displays chatbot usage statistics and metrics
 */
import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, MessageSquare, Clock, Users, Activity } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const AnalyticsDashboard = () => {
  const [stats, setStats] = useState(null);
  const [cacheStats, setCacheStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const [analyticsRes, cacheRes] = await Promise.all([
        axios.get(`${API_URL}/analytics`),
        axios.get(`${API_URL}/cache/stats`)
      ]);

      setStats(analyticsRes.data.data);
      setCacheStats(cacheRes.data.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Loading analytics...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Portfolio Chatbot Analytics
        </h1>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            icon={<MessageSquare className="text-blue-600" size={24} />}
            title="Total Queries"
            value={stats?.total_queries || 0}
            bgColor="bg-blue-50"
          />
          <MetricCard
            icon={<Users className="text-green-600" size={24} />}
            title="Total Sessions"
            value={stats?.total_sessions || 0}
            bgColor="bg-green-50"
          />
          <MetricCard
            icon={<Clock className="text-purple-600" size={24} />}
            title="Avg Response Time"
            value={`${stats?.average_response_time || 0}s`}
            bgColor="bg-purple-50"
          />
          <MetricCard
            icon={<Activity className="text-orange-600" size={24} />}
            title="Cache Hit Rate"
            value={`${cacheStats?.total_hits || 0}`}
            bgColor="bg-orange-50"
          />
        </div>

        {/* Category Distribution */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <BarChart3 className="mr-2 text-gray-700" size={20} />
            Query Categories
          </h2>
          <div className="space-y-3">
            {stats?.category_distribution &&
              Object.entries(stats.category_distribution).map(([category, count]) => (
                <CategoryBar
                  key={category}
                  category={category}
                  count={count}
                  total={stats.total_queries}
                />
              ))}
          </div>
        </div>

        {/* Common Queries */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <TrendingUp className="mr-2 text-gray-700" size={20} />
            Most Common Queries
          </h2>
          <div className="space-y-2">
            {stats?.common_queries?.map((item, index) => (
              <div
                key={index}
                className="flex justify-between items-center p-3 bg-gray-50 rounded"
              >
                <span className="text-gray-700">{item.query}</span>
                <span className="text-sm font-semibold text-blue-600">
                  {item.count} times
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Queries */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Queries</h2>
          <div className="space-y-3">
            {stats?.recent_queries?.map((query, index) => (
              <div
                key={index}
                className="border-l-4 border-blue-500 pl-4 py-2 bg-gray-50"
              >
                <p className="text-gray-800">{query.query}</p>
                <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                  <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {query.category}
                  </span>
                  <span>{query.processing_time.toFixed(2)}s</span>
                  <span>{new Date(query.timestamp).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Cache Stats */}
        {cacheStats && (
          <div className="bg-white rounded-lg shadow-md p-6 mt-8">
            <h2 className="text-xl font-semibold mb-4">Cache Statistics</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-gray-600">Total Cached Entries</p>
                <p className="text-2xl font-bold text-gray-900">
                  {cacheStats.total_entries}
                </p>
              </div>
              <div>
                <p className="text-gray-600">Total Cache Hits</p>
                <p className="text-2xl font-bold text-gray-900">
                  {cacheStats.total_hits}
                </p>
              </div>
            </div>
            <div className="mt-4">
              <h3 className="font-semibold mb-2">Top Cached Queries</h3>
              {cacheStats.top_cached_queries?.map((item, index) => (
                <div key={index} className="text-sm text-gray-600 mb-1">
                  {item.query} - {item.hits} hits
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Metric Card Component
const MetricCard = ({ icon, title, value, bgColor }) => (
  <div className={`${bgColor} rounded-lg p-6 shadow-sm`}>
    <div className="flex items-center justify-between mb-2">
      {icon}
      <span className="text-2xl font-bold text-gray-900">{value}</span>
    </div>
    <p className="text-sm text-gray-600">{title}</p>
  </div>
);

// Category Bar Component
const CategoryBar = ({ category, count, total }) => {
  const percentage = ((count / total) * 100).toFixed(1);

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-700 capitalize">{category}</span>
        <span className="text-gray-600">
          {count} ({percentage}%)
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
