import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { IoNotificationsOutline, IoNotifications } from 'react-icons/io5';
import { FiBell, FiBellOff } from 'react-icons/fi';
import useFarmStore from '../../store/farmStore';
import { alerts } from '../../services/api';

const AlertBadge = () => {
  const navigate = useNavigate();
  const { currentFarm } = useFarmStore();
  const [alertCount, setAlertCount] = useState(0);
  const [alertsList, setAlertsList] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const farmId = currentFarm?.id;

  const fetchAlerts = async () => {
    if (!farmId) {
      setAlertCount(0);
      setAlertsList([]);
      return;
    }

    setIsLoading(true);
    try {
      const data = await alerts.getFarmAlerts(farmId);
      setAlertCount(data.total_count || 0);
      setAlertsList(data.alerts || []);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
      setAlertCount(0);
      setAlertsList([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    // Poll for new alerts every 60 seconds
    const interval = setInterval(fetchAlerts, 60000);
    return () => clearInterval(interval);
  }, [farmId]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleClick = () => {
    if (alertCount > 0) {
      setIsDropdownOpen(!isDropdownOpen);
    } else {
      // Navigate to alerts page even if no alerts
      navigate('/alerts');
    }
  };

  const handleViewAll = () => {
    setIsDropdownOpen(false);
    navigate('/alerts');
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600 bg-red-100 border-red-300';
      case 'high':
        return 'text-orange-600 bg-orange-100 border-orange-300';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 border-yellow-300';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-300';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return '🔴';
      case 'high':
        return '🟠';
      case 'medium':
        return '🟡';
      default:
        return '⚪';
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={handleClick}
        className="relative p-2 rounded-lg hover:bg-[#2d7a4a] transition-colors focus:outline-none"
        aria-label={`Alerts ${alertCount > 0 ? `(${alertCount})` : ''}`}
      >
        <FiBell className={`text-2xl ${alertCount > 0 ? 'text-white' : 'text-[#a8d5a2]'}`} />
        {alertCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center animate-pulse">
            {alertCount > 99 ? '99+' : alertCount}
          </span>
        )}
        {isLoading && (
          <span className="absolute -top-1 -right-1 h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#a8d5a2] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-[#a8d5a2]"></span>
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isDropdownOpen && alertCount > 0 && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-50 max-h-96 overflow-hidden">
          <div className="p-3 border-b border-gray-200 flex justify-between items-center">
            <span className="font-semibold text-gray-800">
              Alerts ({alertCount})
            </span>
            <button
              onClick={handleViewAll}
              className="text-sm text-[#1a5c38] hover:underline"
            >
              View All
            </button>
          </div>
          <div className="overflow-y-auto max-h-72">
            {alertsList.slice(0, 5).map((alert, index) => (
              <div
                key={index}
                className={`px-3 py-2 border-b border-gray-100 hover:bg-gray-50 transition-colors ${getSeverityColor(alert.severity)}`}
              >
                <div className="flex items-start gap-2">
                  <span className="text-sm">{getSeverityIcon(alert.severity)}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1">
                      <span className="text-xs font-medium uppercase text-gray-500">
                        {alert.type.replace('_', ' ')}
                      </span>
                      <span className="text-xs px-1.5 py-0.5 rounded-full bg-gray-200 text-gray-600 capitalize">
                        {alert.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-800 truncate">
                      {alert.message}
                    </p>
                  </div>
                </div>
              </div>
            ))}
            {alertsList.length > 5 && (
              <div className="px-3 py-2 text-center text-sm text-[#1a5c38] font-medium border-t border-gray-200">
                +{alertsList.length - 5} more alerts
              </div>
            )}
          </div>
        </div>
      )}

      {/* No alerts message */}
      {isDropdownOpen && alertCount === 0 && (
        <div className="absolute right-0 mt-2 w-72 bg-white rounded-lg shadow-xl border border-gray-200 z-50 p-4 text-center">
          <FiBellOff className="text-4xl text-gray-300 mx-auto mb-2" />
          <p className="text-gray-500">No alerts</p>
          <p className="text-xs text-gray-400 mt-1">All systems are running smoothly</p>
        </div>
      )}
    </div>
  );
};

export default AlertBadge;
