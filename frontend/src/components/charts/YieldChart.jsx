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
import { FiBarChart2 } from 'react-icons/fi';
import { FaSeedling } from 'react-icons/fa';

const YieldChart = ({ yieldData = [], isLoading = false }) => {
  // Generate sample data if none provided
  const getSampleData = () => {
    const crops = ['Wheat', 'Tomato', 'Potato', 'Onion', 'Cotton'];
    return crops.map((crop) => ({
      crop,
      actual_yield: Math.round(20 + Math.random() * 60),
      predicted_yield: Math.round(25 + Math.random() * 55),
      unit: 'tons/feddan',
    }));
  };

  const sampleData = useMemo(() => getSampleData(), []);
  const data = yieldData.length > 0 ? yieldData : sampleData;

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const unit = payload[0]?.payload?.unit || 'tons/feddan';
      return (
        <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200">
          <p className="text-sm font-semibold text-gray-700 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value} {unit}
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
            <div
              className="w-3 h-3 rounded"
              style={{ backgroundColor: entry.color }}
            />
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
          {[1, 2].map((i) => (
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
  if (!yieldData || yieldData.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
        <FiBarChart2 className="text-4xl text-gray-300 mx-auto mb-3" />
        <h4 className="text-gray-600 font-medium">No Yield Data Available</h4>
        <p className="text-sm text-gray-400 mt-1">Crop yield data will appear here once available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">Crop Yield Forecast</h3>
          <p className="text-sm text-gray-400">Actual vs Predicted yield per crop</p>
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
              dataKey="crop"
              tick={{ fontSize: 12, fill: '#9ca3af' }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#9ca3af' }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
              tickFormatter={(value) => `${value}t`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend content={renderLegend} />

            {/* Actual Yield Bar - Dark Green */}
            <Bar
              dataKey="actual_yield"
              name="Actual Yield"
              fill="#1a5c38"
              radius={[4, 4, 0, 0]}
              barSize={35}
            />

            {/* Predicted Yield Bar - Light Green */}
            <Bar
              dataKey="predicted_yield"
              name="Predicted Yield"
              fill="#22c55e"
              radius={[4, 4, 0, 0]}
              barSize={35}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Footer */}
      <div className="flex flex-wrap items-center justify-between mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-[#1a5c38]"></div>
            <span className="text-xs text-gray-500">Actual Yield</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-[#22c55e]"></div>
            <span className="text-xs text-gray-500">Predicted Yield</span>
          </div>
        </div>
        <span className="text-xs text-gray-400">
          Unit: tons per feddan
        </span>
      </div>
    </div>
  );
};

export default YieldChart;
