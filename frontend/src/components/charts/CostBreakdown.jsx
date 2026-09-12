import React, { useMemo } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { FiPieChart } from 'react-icons/fi';

const CostBreakdown = ({ costData = [], isLoading = false }) => {
  // Colors for different categories
  const COLORS = {
    Seeds: '#1a5c38',
    Fertilizer: '#22c55e',
    Labor: '#3b82f6',
    Irrigation: '#06b6d4',
    Pesticide: '#8b5cf6',
    Other: '#f59e0b',
  };

  const CATEGORY_ORDER = ['Seeds', 'Fertilizer', 'Labor', 'Irrigation', 'Pesticide', 'Other'];

  // Generate sample data if none provided
  const getSampleData = () => {
    const amounts = {
      Seeds: 4500,
      Fertilizer: 3200,
      Labor: 5800,
      Irrigation: 2100,
      Pesticide: 1800,
      Other: 900,
    };
    return CATEGORY_ORDER.map((category) => ({
      category,
      amount: amounts[category] || 0,
    }));
  };

  const sampleData = useMemo(() => getSampleData(), []);
  const data = costData.length > 0 ? costData : sampleData;

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-EG', {
      style: 'currency',
      currency: 'EGP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Calculate total
  const total = data.reduce((sum, item) => sum + (item.amount || 0), 0);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const percentage = ((data.amount / total) * 100).toFixed(1);
      return (
        <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200">
          <p className="text-sm font-semibold text-gray-700 mb-1">{data.category}</p>
          <p className="text-sm text-gray-600">{formatCurrency(data.amount)}</p>
          <p className="text-xs text-gray-400">{percentage}% of total</p>
        </div>
      );
    }
    return null;
  };

  // Custom legend
  const renderLegend = (props) => {
    const { payload } = props;
    return (
      <div className="flex flex-wrap justify-center gap-4 mt-4">
        {payload.map((entry, index) => {
          const category = entry.value;
          const item = data.find((d) => d.category === category);
          const percentage = item ? ((item.amount / total) * 100).toFixed(1) : 0;
          return (
            <div key={`item-${index}`} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-sm text-gray-600">
                {category} ({percentage}%)
              </span>
            </div>
          );
        })}
      </div>
    );
  };

  // Custom label for center of donut
  const renderCenterLabel = ({ cx, cy }) => {
    return (
      <text x={cx} y={cy} textAnchor="middle" dominantBaseline="central">
        <tspan x={cx} dy="-0.5em" fontSize="11" fill="#9ca3af">
          Total
        </tspan>
        <tspan x={cx} dy="1.4em" fontSize="14" fontWeight="bold" fill="#1f2937">
          {formatCurrency(total)}
        </tspan>
      </text>
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
        <div className="flex flex-col items-center">
          <div className="w-48 h-48 bg-gray-100 rounded-full animate-pulse"></div>
          <div className="flex flex-wrap justify-center gap-4 mt-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="flex items-center gap-2">
                <div className="w-3 h-3 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded w-16 animate-pulse"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Empty state
  if (!costData || costData.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
        <FiPieChart className="text-4xl text-gray-300 mx-auto mb-3" />
        <h4 className="text-gray-600 font-medium">No Cost Data Available</h4>
        <p className="text-sm text-gray-400 mt-1">Cost breakdown will appear here once available</p>
      </div>
    );
  }

  // Filter out zero amounts for display
  const chartData = data.filter((item) => item.amount > 0);

  if (chartData.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
        <FiPieChart className="text-4xl text-gray-300 mx-auto mb-3" />
        <h4 className="text-gray-600 font-medium">No Cost Data Available</h4>
        <p className="text-sm text-gray-400 mt-1">Add cost transactions to see breakdown</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">Cost Breakdown</h3>
          <p className="text-sm text-gray-400">Total: {formatCurrency(total)}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-50 text-green-700 text-xs rounded-full">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
            Live
          </span>
        </div>
      </div>

      {/* Chart */}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              dataKey="amount"
              nameKey="category"
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={2}
              label={renderCenterLabel}
              labelLine={false}
            >
              {chartData.map((entry) => (
                <Cell
                  key={`cell-${entry.category}`}
                  fill={COLORS[entry.category] || '#9ca3af'}
                  stroke="#fff"
                  strokeWidth={2}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend content={renderLegend} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-gray-100 text-center">
        <span className="text-xs text-gray-400">
          Categories: {chartData.map((d) => d.category).join(', ')}
        </span>
      </div>
    </div>
  );
};

export default CostBreakdown;
