/**
 * Main ChatBot Component
 * Handles the entire chat interface and logic
 */
import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, Loader2, RotateCcw, Info, Moon, Sun, Download, Mic, Volume2, VolumeX } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { sendMessage, getSuggestions } from '../services/api';
import { useVoice } from '../hooks/useVoice';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(uuidv4());
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Voice hook
  const { isSupported, isListening, isSpeaking, transcript, startListening, stopListening, speak, stopSpeaking } = useVoice();

  // Handle voice transcript
  useEffect(() => {
    if (transcript) {
      setInputValue(transcript);
    }
  }, [transcript]);

  // Load dark mode preference and chat history from localStorage
  useEffect(() => {
    const savedDarkMode = localStorage.getItem('chatbot-dark-mode') === 'true';
    setDarkMode(savedDarkMode);
    
    const savedMessages = localStorage.getItem(`chatbot-history-${sessionId}`);
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (e) {
        console.error('Error loading chat history:', e);
      }
    }
  }, [sessionId]);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(`chatbot-history-${sessionId}`, JSON.stringify(messages));
    }
  }, [messages, sessionId]);

  // Save dark mode preference
  useEffect(() => {
    localStorage.setItem('chatbot-dark-mode', darkMode.toString());
  }, [darkMode]);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load suggestions on mount
  useEffect(() => {
    if (isOpen && suggestions.length === 0) {
      loadSuggestions();
    }
  }, [isOpen]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  const loadSuggestions = async () => {
    try {
      const data = await getSuggestions();
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    }
  };

  const handleSendMessage = async (text = inputValue) => {
    if (!text.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: text.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setShowSuggestions(false);

    try {
      // Convert messages to API format
      const conversationHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp,
      }));

      const response = await sendMessage(text.trim(), conversationHistory, sessionId);

      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
        processingTime: response.processing_time,
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Speak response if voice enabled
      if (voiceEnabled && !isSpeaking) {
        speak(response.response);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        role: 'assistant',
        content: "I apologize, but I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date().toISOString(),
        isError: true,
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion);
  };

  const handleClearChat = () => {
    if (window.confirm('Are you sure you want to clear the chat history?')) {
      setMessages([]);
      setShowSuggestions(true);
      localStorage.removeItem(`chatbot-history-${sessionId}`);
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const exportChat = () => {
    const chatText = messages.map(m => 
      `${m.role === 'user' ? 'You' : 'Assistant'}: ${m.content}`
    ).join('\n\n');
    
    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (!isOpen && messages.length === 0) {
      // Add welcome message
      const welcomeMessage = {
        role: 'assistant',
        content: "Hi! I'm Usama's AI assistant. I can answer questions about his background, skills, projects, and experience. What would you like to know?",
        timestamp: new Date().toISOString(),
      };
      setMessages([welcomeMessage]);
    }
  };

  return (
    <>
      {/* Chat Widget Button */}
      {!isOpen && (
        <button
          onClick={toggleChat}
          className="fixed bottom-6 right-6 bg-primary-600 hover:bg-primary-700 text-white p-4 rounded-full shadow-lg transition-all duration-300 hover:scale-110 z-50"
          aria-label="Open chat assistant"
          role="button"
          tabIndex={0}
        >
          <MessageCircle size={28} aria-hidden="true" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div 
          className={`fixed bottom-6 right-6 w-96 h-[600px] rounded-lg shadow-2xl flex flex-col z-50 animate-slide-up ${
            darkMode ? 'bg-gray-900' : 'bg-white'
          }`}
          role="dialog"
          aria-label="Portfolio chatbot"
          aria-modal="true"
        >
          {/* Header */}
          <div className={`p-4 rounded-t-lg flex justify-between items-center ${
            darkMode ? 'bg-gray-800 text-white' : 'bg-primary-600 text-white'
          }`}>
            <div className="flex items-center space-x-3">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                darkMode ? 'bg-gray-700' : 'bg-white'
              }`}>
                <MessageCircle className={darkMode ? 'text-gray-300' : 'text-primary-600'} size={24} />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Portfolio Assistant</h3>
                <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-primary-100'}`}>
                  Ask me about Usama
                </p>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={toggleDarkMode}
                className={`p-2 rounded-full transition-colors ${
                  darkMode ? 'hover:bg-gray-700' : 'hover:bg-primary-700'
                }`}
                aria-label="Toggle dark mode"
                title="Toggle dark mode"
              >
                {darkMode ? <Sun size={18} /> : <Moon size={18} />}
              </button>
              {isSupported && (
                <button
                  onClick={() => setVoiceEnabled(!voiceEnabled)}
                  className={`p-2 rounded-full transition-colors ${
                    darkMode ? 'hover:bg-gray-700' : 'hover:bg-primary-700'
                  } ${voiceEnabled ? 'bg-green-500' : ''}`}
                  aria-label="Toggle voice"
                  title="Toggle voice output"
                >
                  {voiceEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
                </button>
              )}
              <button
                onClick={exportChat}
                className={`p-2 rounded-full transition-colors ${
                  darkMode ? 'hover:bg-gray-700' : 'hover:bg-primary-700'
                }`}
                aria-label="Export chat"
                title="Export chat"
                disabled={messages.length === 0}
              >
                <Download size={18} />
              </button>
              <button
                onClick={handleClearChat}
                className={`p-2 rounded-full transition-colors ${
                  darkMode ? 'hover:bg-gray-700' : 'hover:bg-primary-700'
                }`}
                aria-label="Clear chat"
                title="Clear chat"
              >
                <RotateCcw size={18} />
              </button>
              <button
                onClick={toggleChat}
                className={`p-2 rounded-full transition-colors ${
                  darkMode ? 'hover:bg-gray-700' : 'hover:bg-primary-700'
                }`}
                aria-label="Close chat"
              >
                <X size={20} />
              </button>
            </div>
          </div>

          {/* Messages Container */}
          <div className={`flex-1 overflow-y-auto p-4 space-y-4 ${
            darkMode ? 'bg-gray-900' : 'bg-gray-50'
          }`}>
            {messages.map((message, index) => (
              <Message
                key={index}
                message={message}
                darkMode={darkMode}
              />
            ))}
            
            {isLoading && <TypingIndicator darkMode={darkMode} />}
            
            {showSuggestions && messages.length <= 1 && suggestions.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm text-gray-600 font-medium">Suggested questions:</p>
                {suggestions.slice(0, 4).map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="w-full text-left p-3 bg-white hover:bg-primary-50 border border-gray-200 rounded-lg text-sm transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className={`p-4 border-t rounded-b-lg ${
            darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
          }`}>
            <div className="flex space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything..."
                className={`flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                  darkMode 
                    ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                    : 'bg-white border-gray-300 text-gray-900'
                }`}
                disabled={isLoading}
              />
              {isSupported && (
                <button
                  onClick={isListening ? stopListening : startListening}
                  className={`p-3 rounded-lg transition-colors ${
                    isListening 
                      ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse' 
                      : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                  }`}
                  aria-label="Voice input"
                  disabled={isLoading}
                >
                  <Mic size={20} />
                </button>
              )}
              <button
                onClick={() => handleSendMessage()}
                disabled={!inputValue.trim() || isLoading}
                className="bg-primary-600 hover:bg-primary-700 text-white p-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Send message"
              >
                <Send size={20} />
              </button>
            </div>
            <p className={`text-xs mt-2 text-center ${
              darkMode ? 'text-gray-500' : 'text-gray-500'
            }`}>
              Powered by RAG & GPT-3.5
            </p>
          </div>
        </div>
      )}
    </>
  );
};

// Message Component
const Message = ({ message, darkMode }) => {
  const isUser = message.role === 'user';
  const isError = message.isError;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-lg ${
          isUser
            ? 'bg-primary-600 text-white'
            : isError
            ? 'bg-red-100 text-red-900 border border-red-300'
            : darkMode
            ? 'bg-gray-800 text-gray-100 border border-gray-700'
            : 'bg-white text-gray-800 border border-gray-200'
        }`}
      >
        <div className="p-3">
          {isUser ? (
            <p className="text-sm">{message.content}</p>
          ) : (
            <>
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ node, inline, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      return !inline && match ? (
                        <SyntaxHighlighter
                          style={vscDarkPlus}
                          language={match[1]}
                          PreTag="div"
                          {...props}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>

              {message.processingTime && (
                <p className="text-xs text-gray-400 mt-2">
                  {message.processingTime.toFixed(2)}s
                </p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

// Typing Indicator Component
const TypingIndicator = ({ darkMode }) => (
  <div className="flex justify-start">
    <div className={`p-3 rounded-lg flex items-center space-x-2 ${
      darkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
    }`}>
      <Loader2 className="animate-spin text-primary-600" size={16} />
      <span className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Thinking...</span>
    </div>
  </div>
);

export default ChatBot;
