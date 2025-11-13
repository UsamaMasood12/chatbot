/**
 * API service for communicating with the chatbot backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

/**
 * Send a chat message to the backend
 * @param {string} message - User message
 * @param {Array} conversationHistory - Previous conversation history
 * @param {string} sessionId - Session identifier
 * @returns {Promise} Response from the backend
 */
export const sendMessage = async (message, conversationHistory = [], sessionId = null) => {
  try {
    const response = await api.post('/chat', {
      message,
      conversation_history: conversationHistory,
      session_id: sessionId,
    });
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

/**
 * Get health status of the backend
 * @returns {Promise} Health status
 */
export const getHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Error getting health status:', error);
    throw error;
  }
};

/**
 * Get suggested questions
 * @returns {Promise} List of suggested questions
 */
export const getSuggestions = async () => {
  try {
    const response = await api.get('/suggestions');
    return response.data;
  } catch (error) {
    console.error('Error getting suggestions:', error);
    throw error;
  }
};

/**
 * Clear conversation history
 * @param {string} sessionId - Session identifier
 * @returns {Promise} Success message
 */
export const clearHistory = async (sessionId) => {
  try {
    const response = await api.post('/clear-history', null, {
      params: { session_id: sessionId }
    });
    return response.data;
  } catch (error) {
    console.error('Error clearing history:', error);
    throw error;
  }
};

/**
 * Get chatbot information
 * @returns {Promise} Chatbot info
 */
export const getChatbotInfo = async () => {
  try {
    const response = await api.get('/info');
    return response.data;
  } catch (error) {
    console.error('Error getting chatbot info:', error);
    throw error;
  }
};

export default api;
