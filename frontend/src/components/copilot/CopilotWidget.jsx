import React, { useState, useEffect, useRef } from 'react';
import { FiMessageSquare, FiX, FiCpu } from 'react-icons/fi';
import { FaSeedling } from 'react-icons/fa';
import CopilotChat from './CopilotChat';
import useAgentStore from '../../store/agentStore';

const CopilotWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { messages } = useAgentStore();
  const widgetRef = useRef(null);

  // Count unread messages (only assistant messages when panel is closed)
  const unreadCount = messages.filter(msg => msg.role === 'assistant').length;

  // Toggle panel
  const togglePanel = () => {
    setIsOpen(!isOpen);
  };

  // Close panel on outside click
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (widgetRef.current && !widgetRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div ref={widgetRef} className="fixed bottom-6 right-6 z-50">
      {/* Chat Panel */}
      <div
        className={`absolute bottom-16 right-0 w-[380px] h-[500px] bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden transition-all duration-300 transform origin-bottom-right ${
          isOpen
            ? 'opacity-100 scale-100 pointer-events-auto'
            : 'opacity-0 scale-95 pointer-events-none'
        }`}
      >
        <CopilotChat />
      </div>

      {/* Floating Button */}
      <button
        onClick={togglePanel}
        className={`relative w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 ${
          isOpen
            ? 'bg-gray-200 hover:bg-gray-300 text-gray-700'
            : 'bg-[#1a5c38] hover:bg-[#2d7a4a] text-white'
        }`}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
      >
        {isOpen ? (
          <FiX className="text-2xl" />
        ) : (
          <FiMessageSquare className="text-2xl" />
        )}

        {/* Unread Badge */}
        {!isOpen && unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center animate-pulse">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}

        {/* Pulse ring animation */}
        {!isOpen && (
          <span className="absolute inset-0 rounded-full border-2 border-[#1a5c38] animate-ping opacity-30"></span>
        )}
      </button>

      {/* Label below button */}
      {!isOpen && (
        <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 text-[10px] text-gray-400 font-medium whitespace-nowrap">
          Farm Copilot
        </div>
      )}
    </div>
  );
};

export default CopilotWidget;
