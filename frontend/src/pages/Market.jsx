import React, { useState, useEffect } from 'react';
import { FiTrendingUp, FiTrendingDown, FiMinus, FiRefreshCw, FiSearch, FiArrowUp, FiArrowDown } from 'react-icons/fi';
import { FaSeedling } from 'react-icons/fa';
import useFarmStore from '../store/farmStore';
import useAgentStore from '../store/agentStore';
import { market as marketApi } from '../services/api';

const Market = () => {
  const { currentFarm } = useFarmStore();
  const { marketIntel, getMarketIntel, isLoading: agentLoading } = useAgentStore();
  const [latestPrices, setLatestPrices] = useState([]);
  const [priceHistory, setPriceHistory] = useState([]);
  const [selectedCommodity, setSelectedCommodity] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isIntelLoading, setIsIntelLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const farmId = currentFarm?.id;

  // Fetch latest prices
  const fetchLatestPrices = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await marketApi.getLatestPrices();
      setLatestPrices(data || []);
    } catch (err) {
      console.error('Error fetching latest prices:', err);
      setError('Failed to load market prices. Please refresh.');
      setLatestPrices([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch price history for a commodity
  const fetchPriceHistory = async (commodity) => {
    if (!commodity) {
      setPriceHistory([]);
      return;
    }

    setIsLoading(true);
    try {
      const data = await marketApi.getCommodityPrices(commodity);
      setPriceHistory(data || []);
    } catch (err) {
      console.error('Error fetching price history:', err);
      setPriceHistory([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLatestPrices();
  }, []);

  useEffect(() => {
    if (selectedCommodity) {
      fetchPriceHistory(selectedCommodity);
    } else {
      setPriceHistory([]);
    }
  }, [selectedCommodity]);

  // Get unique commodities for filter
  const commodities = [...new Set(latestPrices.map(p => p.commodity))];

  // Filter price history by search
  const filteredHistory = priceHistory.filter((item) =>
    item.market_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-EG', {
      style: 'currency',
      currency: 'EGP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Get trend icon and color
  const getTrend = (changePercent) => {
    if (changePercent > 5) {
      return { icon: FiTrendingUp, color: 'text-green-600', label: 'Up' };
    } else if (changePercent < -5) {
      return { icon: FiTrendingDown, color: 'text-red-600', label: 'Down' };
    } else {
      return { icon: FiMinus, color: 'text-gray-400', label: 'Stable' };
    }
  };

  // Handle AI Market Intel
  const handleGetMarketIntel = async () => {
    if (!farmId) {
      setError('Please select a farm first');
      return;
    }

    setIsIntelLoading(true);
    setError(null);
    try {
      await getMarketIntel(farmId);
    } catch (err) {
      console.error('Error fetching market intel:', err);
      setError(err.response?.data?.detail || 'Failed to get market intelligence');
    } finally {
      setIsIntelLoading(false);
    }
  };

  // Skeleton loader
  const SkeletonCard = () => (
    <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
      <div className="h-6 bg-gray-200 rounded w-32 mb-1"></div>
      <div className="h-3 bg-gray-200 rounded w-20"></div>
    </div>
  );

  const SkeletonRow = () => (
    <div className="p-4 border-b border-gray-100 animate-pulse">
      <div className="flex items-center gap-4">
        <div className="h-4 bg-gray-200 rounded w-24"></div>
        <div className="h-4 bg-gray-200 rounded w-32"></div>
        <div className="h-4 bg-gray-200 rounded w-16"></div>
        <div className="h-4 bg-gray-200 rounded w-20"></div>
      </div>
    </div>
  );

  return (
    <div className="p-4 lg:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Market</h1>
            <p className="text-sm text-gray-400">
              Commodity prices and market intelligence
            </p>
          </div>
          <button
            onClick={handleGetMarketIntel}
            disabled={!farmId || isIntelLoading || agentLoading}
            className="flex items-center gap-2 px-4 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FiRefreshCw className={isIntelLoading ? 'animate-spin' : ''} />
            Get AI Insights
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Latest Prices */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Latest Prices</h2>
          {isLoading && !latestPrices.length ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : latestPrices.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
              <FaSeedling className="text-4xl text-gray-300 mx-auto mb-3" />
              <h4 className="text-gray-600 font-medium">No Market Data Available</h4>
              <p className="text-sm text-gray-400 mt-1">Commodity prices will appear here once available</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              {latestPrices.map((price) => (
                <div
                  key={`${price.commodity}-${price.market_name}`}
                  className="bg-white rounded-xl shadow-sm p-4 border border-gray-100 hover:shadow-md transition-shadow"
                >
                  <div className="text-xs text-gray-400 font-medium">{price.commodity}</div>
                  <div className="text-xl font-bold text-gray-800">{formatCurrency(price.price)}</div>
                  <div className="text-xs text-gray-500">{price.unit || 'EGP/kg'}</div>
                  <div className="text-xs text-gray-400 truncate">{price.market_name}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Market Intelligence */}
        {marketIntel && marketIntel.price_forecasts && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-3">AI Market Insights</h2>
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="p-4 bg-green-50 border-b border-gray-200 flex flex-wrap items-center justify-between gap-2">
                <div>
                  <span className="text-sm font-medium text-gray-700">Market Sentiment: </span>
                  <span className={`text-sm font-semibold ${
                    marketIntel.market_sentiment === 'positive' ? 'text-green-600' :
                    marketIntel.market_sentiment === 'negative' ? 'text-red-600' : 'text-yellow-600'
                  }`}>
                    {marketIntel.market_sentiment || 'Neutral'}
                  </span>
                </div>
                {marketIntel.best_time_to_sell && (
                  <div className="text-sm">
                    <span className="text-gray-500">Best time to sell: </span>
                    <span className="font-semibold text-[#1a5c38]">{marketIntel.best_time_to_sell}</span>
                  </div>
                )}
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Commodity</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Forecast</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Change</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trend</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Recommendation</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {marketIntel.price_forecasts.map((item, index) => {
                      const TrendIcon = getTrend(item.change_percent).icon;
                      const trendColor = getTrend(item.change_percent).color;
                      return (
                        <tr key={index} className="hover:bg-gray-50 transition-colors">
                          <td className="px-4 py-3 font-medium text-gray-800">{item.commodity}</td>
                          <td className="px-4 py-3 text-gray-600">{formatCurrency(item.current_price)}</td>
                          <td className="px-4 py-3 text-gray-600">{formatCurrency(item.forecast_price)}</td>
                          <td className={`px-4 py-3 font-semibold ${trendColor}`}>
                            {item.change_percent > 0 ? '+' : ''}{item.change_percent?.toFixed(1)}%
                          </td>
                          <td className="px-4 py-3">
                            <TrendIcon className={trendColor} />
                          </td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              item.recommendation?.includes('Sell') ? 'bg-red-100 text-red-700' :
                              item.recommendation?.includes('Hold') || item.recommendation?.includes('Maintain') ? 'bg-yellow-100 text-yellow-700' :
                              'bg-green-100 text-green-700'
                            }`}>
                              {item.recommendation || 'Hold'}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Price History */}
        <div>
          <div className="flex flex-wrap items-center justify-between gap-4 mb-3">
            <h2 className="text-lg font-semibold text-gray-800">Price History</h2>
            <div className="flex flex-wrap items-center gap-3">
              <select
                value={selectedCommodity}
                onChange={(e) => setSelectedCommodity(e.target.value)}
                className="px-3 py-1.5 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-[#1a5c38] focus:border-transparent"
              >
                <option value="">Select Commodity</option>
                {commodities.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
              {selectedCommodity && (
                <div className="relative">
                  <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search by market..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#1a5c38] focus:border-transparent"
                  />
                </div>
              )}
            </div>
          </div>

          {selectedCommodity ? (
            isLoading && !priceHistory.length ? (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                {[1, 2, 3, 4, 5].map((i) => (
                  <SkeletonRow key={i} />
                ))}
              </div>
            ) : filteredHistory.length === 0 ? (
              <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
                <p className="text-gray-500">No price history found for {selectedCommodity}</p>
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Market</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Min</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Max</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {filteredHistory.map((item) => (
                        <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-4 py-3 text-gray-800">{item.market_name}</td>
                          <td className="px-4 py-3 font-semibold text-[#1a5c38]">{formatCurrency(item.price)}</td>
                          <td className="px-4 py-3 text-gray-500">{item.min_price ? formatCurrency(item.min_price) : '—'}</td>
                          <td className="px-4 py-3 text-gray-500">{item.max_price ? formatCurrency(item.max_price) : '—'}</td>
                          <td className="px-4 py-3 text-gray-500">{item.unit || 'EGP/kg'}</td>
                          <td className="px-4 py-3 text-gray-500">
                            {item.date ? new Date(item.date).toLocaleDateString() : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )
          ) : (
            <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
              <p className="text-gray-500">Select a commodity to view price history</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Market;