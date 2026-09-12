import React, { useState } from 'react';
import {
  FiAlertCircle,
  FiCheckCircle,
  FiInfo,
  FiXCircle,
  FiCpu,
  FiChevronDown,
  FiChevronUp,
} from 'react-icons/fi';
import { FaRobot, FaSeedling, FaTint, FaChartLine, FaBoxes, FaDollarSign, FaUsers } from 'react-icons/fa';

const AIInsightsFeed = ({ insights = [], isLoading = false }) => {
  const [showAll, setShowAll] = useState(false);
  const displayInsights = showAll ? insights : insights.slice(0, 5);

  const formatTime = (timestamp) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
  };

  const getAgentIcon = (agent) => {
    const agentMap = {
      'Farm Copilot': FaRobot,
      'Farm Intelligence': FaSeedling,
      'Resource Optimization': FaTint,
      'Market Intelligence': FaChartLine,
      'Inventory Agent': FaBoxes,
      'Finance Agent': FaDollarSign,
      'Workforce Agent': FaUsers,
    };
    const Icon = agentMap[agent] || FaRobot;
    return <Icon className="text-sm" />;
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'warning':
        return <FiAlertCircle className="text-yellow-500" />;
      case 'success':
        return <FiCheckCircle className="text-green-500" />;
      case 'info':
        return <FiInfo className="text-blue-500" />;
      case 'danger':
        return <FiXCircle className="text-red-500" />;
      default:
        return <FiInfo className="text-gray-400" />;
    }
  };

  const getTypeColors = (type) => {
    switch (type) {
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-700';
      case 'success':
        return 'bg-green-50 border-green-200 text-green-700';
      case 'info':
        return 'bg-blue-50 border-blue-200 text-blue-700';
      case 'danger':
        return 'bg-red-50 border-red-200 text-red-700';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-700';
    }
  };

  const getAgentColor = (agent) => {
    const colorMap = {
      'Farm Copilot': 'text-[#1a5c38]',
      'Farm Intelligence': 'text-emerald-600',
      'Resource Optimization': 'text-cyan-600',
      'Market Intelligence': 'text-purple-600',
      'Inventory Agent': 'text-orange-600',
      'Finance Agent': 'text-blue-600',
      'Workforce Agent': 'text-indigo-600',
    };
    return colorMap[agent] || 'text-gray-600';
  };

  // Generate sample insights if none provided
  const getSampleInsights = () => {
    const now = new Date();
    return [
      {
        id: 1,
        agent: 'Market Intelligence',
        message: 'Tomato prices expected to rise 15% in next 2 weeks. Consider holding harvest.',
        type: 'warning',
        timestamp: new Date(now - 600000),
      },
      {
        id: 2,
        agent: 'Farm Intelligence',
        message: 'Crop health score increased to 87%. Wheat crops showing excellent growth.',
        type: 'success',
        timestamp: new Date(now - 1200000),
      },
      {
        id: 3,
        agent: 'Resource Optimization',
        message: 'Water usage reduced by 12% through optimized irrigation scheduling.',
        type: 'info',
        timestamp: new Date(now - 1800000),
      },
      {
        id: 4,
        agent: 'Inventory Agent',
        message: 'Low stock alert: Fertilizer (45 kg remaining, minimum 100 kg).',
        type: 'danger',
        timestamp: new Date(now - 3600000),
      },
      {
        id: 5,
        agent: 'Finance Agent',
        message: 'Monthly revenue target achieved. Current profit: EGP 12,450.',
        type: 'success',
        timestamp: new Date(now - 7200000),
      },
      {
        id: 6,
        agent: 'Workforce Agent',
        message: '3 workers assigned to irrigation task for tomorrow morning.',
        type: 'info',
        timestamp: new Date(now - 14400000),
      },
    ];
  };

  const displayData = insights.length > 0 ? insights : getSampleInsights();

  // Skeleton loader
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="h-6 bg-gray-200 rounded w-32 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-16 animate-pulse"></div>
          </div>
          <div className="h-4 bg-gray-200 rounded w-20 animate-pulse"></div>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg animate-pulse">
              <div className="w-5 h-5 bg-gray-200 rounded-full flex-shrink-0"></div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <div className="h-4 bg-gray-200 rounded w-24"></div>
                  <div className="h-3 bg-gray-200 rounded w-16"></div>
                </div>
                <div className="h-4 bg-gray-200 rounded w-full"></div>
                <div className="h-3 bg-gray-200 rounded w-20 mt-1"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Empty state
  if (!insights || insights.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
        <FiCpu className="text-4xl text-gray-300 mx-auto mb-3" />
        <h4 className="text-gray-600 font-medium">No AI Insights Available</h4>
        <p className="text-sm text-gray-400 mt-1">AI recommendations will appear here as they are generated</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-[#1a5c38] rounded-lg">
            <FiCpu className="text-white" />
          </div>
          <h3 className="text-lg font-semibold text-gray-800">AI Insights Feed</h3>
          <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
            {displayData.length} insights
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-50 text-green-700 text-xs rounded-full">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
            Live
          </span>
        </div>
      </div>

      {/* Insights List */}
      <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
        {displayData.map((item) => (
          <div
            key={item.id}
            className={`flex items-start gap-3 p-3 rounded-lg border ${getTypeColors(item.type)} transition-all duration-200 hover:shadow-sm`}
          >
            {/* Icon */}
            <div className="flex-shrink-0 mt-0.5">
              {getTypeIcon(item.type)}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center flex-wrap gap-2 mb-0.5">
                <span className={`text-xs font-semibold ${getAgentColor(item.agent)} flex items-center gap-1`}>
                  {getAgentIcon(item.agent)}
                  {item.agent}
                </span>
                <span className="text-xs text-gray-400">
                  {formatTime(item.timestamp)}
                </span>
              </div>
              <p className="text-sm text-gray-700">{item.message}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Show More Button */}
      {insights.length > 5 && (
        <button
          onClick={() => setShowAll(!showAll)}
          className="mt-4 w-full flex items-center justify-center gap-2 py-2 text-sm text-[#1a5c38] hover:bg-green-50 rounded-lg transition-colors font-medium"
        >
          {showAll ? (
            <>
              <FiChevronUp />
              Show Less
            </>
          ) : (
            <>
              <FiChevronDown />
              Show More ({insights.length - 5} more)
            </>
          )}
        </button>
      )}

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between">
        <span className="text-xs text-gray-400">
          Powered by 7 AI Agents
        </span>
        <button className="text-xs text-[#1a5c38] hover:underline font-medium">
          View All →
        </button>
      </div>
    </div>
  );
};

export default AIInsightsFeed;
