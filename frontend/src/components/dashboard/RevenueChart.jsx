import React, { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { FiTrendingUp } from 'react-icons/fi';

const RevenueChart = ({ revenueData = [], isLoading = false }) => {
  // Generate sample data if none provided
  const getSampleData = () => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    return months.map((month) => ({
      month,
      revenue: Math.round(15000 + Math.random() * 25000),
      expenses: Math.round(8000 + Math.random() * 15000),
      profit: 0, // Will be calculated
    })).map(item => ({
      ...item,
      profit: item.revenue - item.expenses,
    }));
  };

  const sampleData = useMemo(() => getSampleData(), []);
  const data = revenueData.length > 0 ? revenueData : sampleData;

  // Format currency
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-EG', {
      style: 'currency',
      currency: 'EGP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200">
          <p className="text-sm font-semibold text-gray-700 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {formatCurrency(entry.value)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Custom legend
  const renderLegend = (props) => {
    const { payload } = props;
    return (
      <div className="flex flex-wrap justify-center gap-6 mt-4">
        {payload.map((entry, index) => (
          <div key={`item-${index}`} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: entry.color }} />
            <span className="text-sm text-gray-600">{entry.value}</span>
          </div>
        ))}
      </div>
    );
  };

  // Skeleton loader
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <div className="flex items-center justify-between mb-6">
          <div className="h-6 bg-gray-200 rounded w-40 animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded w-24 animate-pulse"></div>
        </div>
        <div className="h-64 bg-gray-100 rounded-lg animate-pulse"></div>
        <div className="flex justify-center gap-8 mt-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center gap-2">
              <div className="w-3 h-3 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-16 animate-pulse"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Empty state
  if (!revenueData || revenueData.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
        <FiTrendingUp className="text-4xl text-gray-300 mx-auto mb-3" />
        <h4 className="text-gray-600 font-medium">No Revenue Data Available</h4>
        <p className="text-sm text-gray-400 mt-1">Revenue data will appear here once available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">Revenue vs Expenses</h3>
          <p className="text-sm text-gray-400">Monthly overview</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-50 text-green-700 text-xs rounded-full">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
            Live
          </span>
        </div>
      </div>

      {/* Chart */}
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 5, right: 5, left: -15, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="month"
              tick={{ fontSize: 12, fill: '#9ca3af' }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#9ca3af' }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
              tickFormatter={(value) => `EGP ${(value / 1000).toFixed(0)}K`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend content={renderLegend} />

            {/* Revenue Bar - Green */}
            <Bar
              dataKey="revenue"
              name="Revenue"
              fill="#1a5c38"
              radius={[4, 4, 0, 0]}
              barSize={30}
            />

            {/* Expenses Bar - Red */}
            <Bar
              dataKey="expenses"
              name="Expenses"
              fill="#ef4444"
              radius={[4, 4, 0, 0]}
              barSize={30}
            />

            {/* Profit Bar - Blue */}
            <Bar
              dataKey="profit"
              name="Profit"
              fill="#3b82f6"
              radius={[4, 4, 0, 0]}
              barSize={30}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Footer */}
      <div className="flex flex-wrap items-center justify-between mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-[#1a5c38]"></div>
            <span className="text-xs text-gray-500">Revenue</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-[#ef4444]"></div>
            <span className="text-xs text-gray-500">Expenses</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-[#3b82f6]"></div>
            <span className="text-xs text-gray-500">Profit</span>
          </div>
        </div>
        <span className="text-xs text-gray-400">
          Last 6 months
        </span>
      </div>
    </div>
  );
};

export default RevenueChart;
