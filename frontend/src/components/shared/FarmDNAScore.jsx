import React from 'react';
import { FaLeaf, FaTint, FaChartLine, FaCogs, FaShoppingCart, FaExclamationTriangle } from 'react-icons/fa';

const FarmDNAScore = ({ overallScore = 84, dimensions = null }) => {
  const defaultDimensions = [
    { name: 'Crop Health', value: 22, icon: FaLeaf, color: '#22c55e' },
    { name: 'Soil Health', value: 20, icon: FaTint, color: '#22c55e' },
    { name: 'Water Efficiency', value: 18, icon: FaTint, color: '#22c55e' },
    { name: 'Operational Efficiency', value: 15, icon: FaCogs, color: '#22c55e' },
    { name: 'Market Readiness', value: 13, icon: FaShoppingCart, color: '#f59e0b' },
    { name: 'Risk Exposure', value: 12, icon: FaExclamationTriangle, color: '#f59e0b' },
  ];

  const displayDimensions = dimensions || defaultDimensions;

  const getScoreColor = (score) => {
    if (score >= 70) return 'bg-green-500';
    if (score >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getScoreTextColor = (score) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score) => {
    if (score >= 70) return 'Good';
    if (score >= 50) return 'Fair';
    return 'Needs Attention';
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-800">Farm DNA Score</h3>
        <span className="text-xs text-gray-400">Powered by AI</span>
      </div>

      {/* Overall Score */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="text-4xl font-bold text-[#1a5c38]">{overallScore}</div>
          <div className="text-sm text-gray-500">Overall Health</div>
        </div>
        <div className="text-right">
          <div className={`text-lg font-semibold ${getScoreTextColor(overallScore)}`}>
            {getScoreLabel(overallScore)}
          </div>
          <div className="text-xs text-gray-400">Out of 100</div>
        </div>
      </div>

      {/* Progress Bar - Overall */}
      <div className="w-full bg-gray-200 rounded-full h-3 mb-6">
        <div
          className={`h-3 rounded-full transition-all duration-1000 ${getScoreColor(overallScore)}`}
          style={{ width: `${overallScore}%` }}
        />
      </div>

      {/* Dimensions */}
      <div className="space-y-4">
        {displayDimensions.map((dim, index) => {
          const Icon = dim.icon;
          const score = dim.value;
          const isGood = score >= 70;
          const isFair = score >= 50 && score < 70;
          const progressColor = isGood ? 'bg-green-500' : isFair ? 'bg-yellow-500' : 'bg-red-500';
          const textColor = isGood ? 'text-green-600' : isFair ? 'text-yellow-600' : 'text-red-600';

          return (
            <div key={index} className="space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Icon className={`text-sm ${textColor}`} />
                  <span className="text-sm font-medium text-gray-700">{dim.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-sm font-semibold ${textColor}`}>{score}%</span>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-1000 ${progressColor}`}
                  style={{ width: `${score}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-gray-100 flex items-center justify-between">
        <span className="text-xs text-gray-400">Last updated: Today</span>
        <button className="text-xs text-[#1a5c38] hover:underline font-medium">
          View Details →
        </button>
      </div>
    </div>
  );
};

export default FarmDNAScore;
