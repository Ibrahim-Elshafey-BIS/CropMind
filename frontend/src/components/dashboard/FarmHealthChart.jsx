import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { FiActivity } from 'react-icons/fi';

const FarmHealthChart = ({ healthData = [], isLoading = false }) => {
  // Generate sample data if none provided
  const getSampleData = () => {
    const data = [];
    const now = new Date();
    for (let i = 29; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      data.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        score: 75 + Math.random() * 15,
        crop_health: 70 + Math.random() * 20,
        water_efficiency: 65 + Math.random() * 25,
        soil_health: 60 + Math.random() * 30,
      });
    }
    return data;
  };

  // Memoize sample data to prevent flickering
  const sampleData = useMemo(() => getSampleData(), []);
  const data = healthData.length > 0 ? healthData : sampleData;

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200">
          <p className="text-sm font-semibold text-gray-700 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value.toFixed(1)}%
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
      <div className="flex flex-wrap justify-center gap-4 mt-4">
        {payload.map((entry, index) => (
          <div key={`item-${index}`} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
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
              <div className="w-3 h-3 bg-gray-200 rounded-full"></div>
              <div className="h-4 bg-gray-200 rounded w-16 animate-pulse"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Empty state
  if (!healthData || healthData.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
        <FiActivity className="text-4xl text-gray-300 mx-auto mb-3" />
        <h4 className="text-gray-600 font-medium">No Health Data Available</h4>
        <p className="text-sm text-gray-400 mt-1">Health data will appear here once available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">Farm Health Overview</h3>
          <p className="text-sm text-gray-400">Last 30 days</p>
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
          <LineChart
            data={data}
            margin={{ top: 5, right: 5, left: -15, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11, fill: '#9ca3af' }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 11, fill: '#9ca3af' }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend content={renderLegend} />

            {/* Overall Score */}
            <Line
              type="monotone"
              dataKey="score"
              name="Overall"
              stroke="#1a5c38"
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 5 }}
            />

            {/* Crop Health */}
            <Line
              type="monotone"
              dataKey="crop_health"
              name="Crop Health"
              stroke="#22c55e"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />

            {/* Water Efficiency */}
            <Line
              type="monotone"
              dataKey="water_efficiency"
              name="Water Efficiency"
              stroke="#06b6d4"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />

            {/* Soil Health */}
            <Line
              type="monotone"
              dataKey="soil_health"
              name="Soil Health"
              stroke="#8b5cf6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Footer */}
      <div className="flex flex-wrap items-center justify-between mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full bg-[#1a5c38]"></div>
            <span className="text-xs text-gray-500">Overall Score</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full bg-[#22c55e]"></div>
            <span className="text-xs text-gray-500">Crop Health</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full bg-[#06b6d4]"></div>
            <span className="text-xs text-gray-500">Water Efficiency</span>
          </div>
        </div>
        <span className="text-xs text-gray-400">
          Updated: {new Date().toLocaleDateString()}
        </span>
      </div>
    </div>
  );
};

export default FarmHealthChart;
