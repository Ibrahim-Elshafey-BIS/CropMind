import React, { useState, useRef, useEffect } from 'react';
import { FiSend, FiTrash2, FiMessageSquare, FiUser, FiCpu } from 'react-icons/fi';
import { FaSeedling } from 'react-icons/fa';
import useAgentStore from '../../store/agentStore';
import useFarmStore from '../../store/farmStore';

const CopilotChat = () => {
  const { messages, isTyping, sendMessage, clearMessages } = useAgentStore();
  const { currentFarm } = useFarmStore();
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Handle send message
  const handleSend = async () => {
    const trimmedMessage = inputMessage.trim();
    if (!trimmedMessage || isTyping) return;

    setInputMessage('');
    await sendMessage(trimmedMessage, currentFarm?.id);
  };

  // Handle Enter key
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
    // Focus and send after a brief delay
    setTimeout(() => {
      inputRef.current?.focus();
      handleSend();
    }, 100);
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex flex-col h-[600px] bg-gray-50 rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-[#1a5c38] text-white px-4 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
            <FiCpu className="text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-sm">Farm Copilot</h3>
            <p className="text-xs text-[#a8d5a2]">
              {currentFarm ? `🌾 ${currentFarm.name}` : 'No farm selected'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              if (window.confirm('Clear all messages?')) {
                clearMessages();
              }
            }}
            className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
            title="Clear chat"
          >
            <FiTrash2 className="text-white/80" />
          </button>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-[#1a5c38]/10 rounded-full flex items-center justify-center mb-4">
              <FaSeedling className="text-3xl text-[#1a5c38]" />
            </div>
            <h4 className="text-lg font-medium text-gray-700">Ask me anything about your farm</h4>
            <p className="text-sm text-gray-400 max-w-sm mt-1">
              🌱 I'm your AI farm assistant. Ask about crop health, irrigation, market prices, or any farm-related question.
            </p>
            <div className="flex flex-wrap gap-2 mt-6 justify-center">
              <button
                onClick={() => handleSuggestionClick("What's the current health status of my crops?")}
                className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-xs text-gray-600 transition-colors"
              >
                🌾 Crop health
              </button>
              <button
                onClick={() => handleSuggestionClick("How is the market outlook for tomatoes?")}
                className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-xs text-gray-600 transition-colors"
              >
                📊 Market outlook
              </button>
              <button
                onClick={() => handleSuggestionClick("What irrigation schedule do you recommend?")}
                className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-xs text-gray-600 transition-colors"
              >
                💧 Irrigation
              </button>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-2' : 'order-1'}`}>
                <div
                  className={`px-4 py-2.5 rounded-2xl ${
                    msg.role === 'user'
                      ? 'bg-[#1a5c38] text-white rounded-br-sm'
                      : 'bg-white text-gray-800 rounded-bl-sm shadow-sm border border-gray-100'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap break-words">{msg.content}</p>
                </div>
                {msg.timestamp && (
                  <div className={`text-xs text-gray-400 mt-1 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                    {formatTime(msg.timestamp)}
                  </div>
                )}
                {/* Suggestions */}
                {msg.role === 'assistant' && msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {msg.suggestions.map((suggestion, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="px-3 py-1 bg-[#1a5c38]/10 hover:bg-[#1a5c38]/20 text-[#1a5c38] rounded-full text-xs transition-colors border border-[#1a5c38]/20"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              {/* Avatar */}
              <div className={`flex-shrink-0 ${msg.role === 'user' ? 'order-1 ml-2' : 'order-2 mr-2'}`}>
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    msg.role === 'user'
                      ? 'bg-gray-200 text-gray-600'
                      : 'bg-[#1a5c38] text-white'
                  }`}
                >
                  {msg.role === 'user' ? (
                    <FiUser className="text-sm" />
                  ) : (
                    <FiCpu className="text-sm" />
                  )}
                </div>
              </div>
            </div>
          ))
        )}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 max-w-[80%]">
              <div className="w-8 h-8 rounded-full bg-[#1a5c38] flex items-center justify-center flex-shrink-0">
                <FiCpu className="text-white text-sm" />
              </div>
              <div className="bg-white px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm border border-gray-100">
                <div className="flex gap-1.5">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="border-t border-gray-200 bg-white p-3 flex-shrink-0">
        <div className="flex items-end gap-2">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask your farm assistant..."
              disabled={isTyping}
              rows={1}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-[#1a5c38] focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              style={{ minHeight: '44px', maxHeight: '120px' }}
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!inputMessage.trim() || isTyping}
            className="p-2.5 bg-[#1a5c38] text-white rounded-xl hover:bg-[#2d7a4a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
          >
            <FiSend className="text-lg" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default CopilotChat;