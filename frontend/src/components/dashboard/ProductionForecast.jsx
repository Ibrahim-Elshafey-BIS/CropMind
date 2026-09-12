import React, { useState, useMemo } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { FiTrendingUp, FiFilter } from 'react-icons/fi';

const ProductionForecast = ({ forecastData = [], isLoading = false }) => {
  const [selectedCrop, setSelectedCrop] = useState('all');

  // Generate sample data if none provided
  const getSampleData = () => {
    const crops = ['Wheat', 'Tomato', 'Potato', 'Onion', 'Cotton'];
    const months = ['Jan', 'Feb', 'Mar'];
    const data = [];
    
    crops.forEach((crop) => {
      months.forEach((month, index) => {
        const base = Math.random() * 50 + 20;
        data.push({
          month: `${month} ${new Date().getFullYear()}`,
          crop,
          predicted: Math.round(base + Math.random() * 30),
          actual: index < 2 ? Math.round(base + Math.random() * 20 - 5) : null,
        });
      });
    });
    return data;
  };

  const sampleData = useMemo(() => getSampleData(), []);
  const data = forecastData.length > 0 ? forecastData : sampleData;

  // Get unique crops for filter
  const crops = useMemo(() => {
    const unique = [...new Set(data.map(item => item.crop))];
    return ['all', ...unique];
  }, [data]);

  // Filter data by selected crop
  const filteredData = useMemo(() => {
    if (selectedCrop === 'all') return data;
    return data.filter(item => item.crop === selectedCrop);
  }, [data, selectedCrop]);

  // Group by month for display
  const chartData = useMemo(() => {
    const grouped = {};
    filteredData.forEach(item => {
      if (!grouped[item.month]) {
        grouped[item.month] = {
          month: item.month,
          predicted: 0,
          actual: 0,
        };
      }
      grouped[item.month].predicted += item.predicted || 0;
      if (item.actual !== null) {
        grouped[item.month].actual += item.actual || 0;
      }
    });
    return Object.values(grouped);
  }, [filteredData]);

  // Format currency
  const formatTons = (value) => {
    return `${value.toFixed(1)} tons`;
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200">
          <p className="text-sm font-semibold text-gray-700 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {formatTons(entry.value)}
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
              style={{ 
                backgroundColor: entry.color,
                opacity: entry.dataKey === 'actual' ? 0.5 : 1,
              }} 
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
          <div className="h-8 bg-gray-200 rounded w-32 animate-pulse"></div>
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
  if (!forecastData || forecastData.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
        <FiTrendingUp className="text-4xl text-gray-300 mx-auto mb-3" />
        <h4 className="text-gray-600 font-medium">No Production Forecast Available</h4>
        <p className="text-sm text-gray-400 mt-1">Forecast data will appear here once available</p>
      </div>
    );
  }

  // Gradient colors for area
  const greenGradient = 'url(#greenGradient)';
  const lightGreenGradient = 'url(#lightGreenGradient)';

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between mb-6 gap-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">Production Forecast</h3>
          <p className="text-sm text-gray-400">Next 3 months prediction</p>
        </div>
        
        {/* Filter Dropdown */}
        <div className="flex items-center gap-2">
          <FiFilter className="text-gray-400" />
          <select
            value={selectedCrop}
            onChange={(e) => setSelectedCrop(e.target.value)}
            className="px-3 py-1.5 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-[#1a5c38] focus:border-transparent"
          >
            {crops.map((crop) => (
              <option key={crop} value={crop}>
                {crop === 'all' ? 'All Crops' : crop}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Chart */}
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            margin={{ top: 5, right: 5, left: -15, bottom: 5 }}
          >
            <defs>
              <linearGradient id="greenGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#1a5c38" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#1a5c38" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="lightGreenGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            
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
              tickFormatter={(value) => `${value}t`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend content={renderLegend} />

            {/* Predicted Area */}
            <Area
              type="monotone"
              dataKey="predicted"
              name="Predicted"
              stroke="#1a5c38"
              strokeWidth={2}
              fill={greenGradient}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />

            {/* Actual Area */}
            <Area
              type="monotone"
              dataKey="actual"
              name="Actual"
              stroke="#22c55e"
              strokeWidth={2}
              strokeDasharray="5 5"
              fill={lightGreenGradient}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Footer */}
      <div className="flex flex-wrap items-center justify-between mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-[#1a5c38]"></div>
            <span className="text-xs text-gray-500">Predicted</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-[#22c55e] border border-[#22c55e] border-dashed"></div>
            <span className="text-xs text-gray-500">Actual</span>
          </div>
        </div>
        <span className="text-xs text-gray-400">
          {selectedCrop === 'all' ? 'All crops combined' : selectedCrop}
        </span>
      </div>
    </div>
  );
};

export default ProductionForecast;
