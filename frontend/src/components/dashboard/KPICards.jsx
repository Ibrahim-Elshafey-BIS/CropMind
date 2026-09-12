import React from 'react';
import {
  FiDollarSign,
  FiTrendingUp,
  FiTrendingDown,
  FiUsers,
  FiActivity,
  FiAward,
} from 'react-icons/fi';
import { FaSeedling } from 'react-icons/fa';

const KPICards = ({
  financeSummary = null,
  cropsCount = 0,
  workersCount = 0,
  dnaScore = 84,
  isLoading = false,
}) => {
  const totalRevenue = financeSummary?.total_income || 0;
  const totalExpense = financeSummary?.total_expense || 0;
  const netProfit = financeSummary?.net_profit || 0;

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EGP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const kpiData = [
    {
      id: 'revenue',
      title: 'Total Revenue',
      value: formatCurrency(totalRevenue),
      icon: FiDollarSign,
      color: 'bg-green-100 text-green-600',
      trend: netProfit > 0 ? 'up' : 'down',
      trendValue: `${netProfit > 0 ? '+' : ''}${formatCurrency(netProfit)}`,
      isLoading,
    },
    {
      id: 'crops',
      title: 'Active Crops',
      value: cropsCount,
      icon: FaSeedling,
      color: 'bg-emerald-100 text-emerald-600',
      trend: 'up',
      trendValue: 'Growing',
      isLoading,
    },
    {
      id: 'workers',
      title: 'Active Workers',
      value: workersCount,
      icon: FiUsers,
      color: 'bg-blue-100 text-blue-600',
      trend: 'up',
      trendValue: 'Active',
      isLoading,
    },
    {
      id: 'dna',
      title: 'Farm DNA Score',
      value: dnaScore,
      icon: FiAward,
      color: 'bg-purple-100 text-purple-600',
      trend: dnaScore >= 70 ? 'up' : 'down',
      trendValue: dnaScore >= 70 ? 'Good' : 'Needs Attention',
      isLoading,
    },
  ];

  const getTrendColor = (trend) => {
    return trend === 'up' ? 'text-green-500' : 'text-red-500';
  };

  const getTrendIcon = (trend) => {
    return trend === 'up' ? FiTrendingUp : FiTrendingDown;
  };

  // Skeleton loader
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-xl shadow-sm p-6 animate-pulse">
            <div className="flex items-center justify-between">
              <div className="h-4 bg-gray-200 rounded w-1/3"></div>
              <div className="h-10 w-10 bg-gray-200 rounded-lg"></div>
            </div>
            <div className="mt-3 h-8 bg-gray-200 rounded w-2/3"></div>
            <div className="mt-2 h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {kpiData.map((kpi) => {
        const Icon = kpi.icon;
        const TrendIcon = getTrendIcon(kpi.trend);

        return (
          <div
            key={kpi.id}
            className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow duration-200 border border-gray-50"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-500">{kpi.title}</span>
              <div className={`p-2.5 rounded-lg ${kpi.color}`}>
                <Icon className="text-lg" />
              </div>
            </div>

            <div className="mt-3">
              <span className="text-2xl font-bold text-gray-800">
                {kpi.value}
              </span>
            </div>

            <div className="mt-2 flex items-center gap-2">
              {kpi.trendValue && (
                <>
                  <TrendIcon className={`text-sm ${getTrendColor(kpi.trend)}`} />
                  <span className={`text-sm font-medium ${getTrendColor(kpi.trend)}`}>
                    {kpi.trendValue}
                  </span>
                </>
              )}
              <span className="text-xs text-gray-400 ml-auto">
                {kpi.id === 'revenue' ? 'All time' : ''}
                {kpi.id === 'dna' ? 'Overall' : ''}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default KPICards;
