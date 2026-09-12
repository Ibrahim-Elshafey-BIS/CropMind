import React, { useState, useEffect } from 'react';
import { FiDollarSign, FiPackage, FiUsers, FiPrinter, FiAlertTriangle, FiTrendingUp, FiDownload } from 'react-icons/fi';
import { FaSeedling } from 'react-icons/fa';
import FarmDNAScore from '../components/shared/FarmDNAScore';
import useFarmStore from '../store/farmStore';
import { finance, crops, workforce, inventory } from '../services/api';

const Reports = () => {
  const { currentFarm } = useFarmStore();
  const [financeSummary, setFinanceSummary] = useState(null);
  const [cropsData, setCropsData] = useState([]);
  const [workersData, setWorkersData] = useState([]);
  const [inventoryData, setInventoryData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const farmId = currentFarm?.id;

  // Fetch all data
  const fetchReportsData = async () => {
    if (!farmId) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const [
        summaryRes,
        cropsRes,
        workersRes,
        inventoryRes,
      ] = await Promise.allSettled([
        finance.getFinanceSummary(farmId),
        crops.getCrops({ farm_id: farmId, limit: 1000 }),
        workforce.getWorkers({ farm_id: farmId, limit: 1000 }),
        inventory.getInventory({ farm_id: farmId, limit: 1000 }),
      ]);

      // Process finance summary
      if (summaryRes.status === 'fulfilled') {
        setFinanceSummary(summaryRes.value);
      } else {
        console.error('Failed to fetch finance summary:', summaryRes.reason);
        setFinanceSummary(null);
      }

      // Process crops
      if (cropsRes.status === 'fulfilled') {
        setCropsData(cropsRes.value || []);
      } else {
        console.error('Failed to fetch crops:', cropsRes.reason);
        setCropsData([]);
      }

      // Process workers
      if (workersRes.status === 'fulfilled') {
        setWorkersData(workersRes.value || []);
      } else {
        console.error('Failed to fetch workers:', workersRes.reason);
        setWorkersData([]);
      }

      // Process inventory
      if (inventoryRes.status === 'fulfilled') {
        setInventoryData(inventoryRes.value || []);
      } else {
        console.error('Failed to fetch inventory:', inventoryRes.reason);
        setInventoryData([]);
      }

      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching reports data:', error);
      setError('Failed to load reports data. Please refresh.');
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReportsData();
  }, [farmId]);

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-EG', {
      style: 'currency',
      currency: 'EGP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Get health color
  const getHealthColor = (score) => {
    if (score === null || score === undefined) return 'text-gray-400';
    if (score >= 70) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Get status badge
  const getStatusBadge = (status) => {
    const statusMap = {
      growing: { color: 'bg-green-100 text-green-700', label: 'Growing' },
      harvested: { color: 'bg-gray-100 text-gray-700', label: 'Harvested' },
      failed: { color: 'bg-red-100 text-red-700', label: 'Failed' },
    };
    return statusMap[status] || { color: 'bg-gray-100 text-gray-700', label: status };
  };

  // Handle print
  const handlePrint = () => {
    window.print();
  };

  // Low stock items
  const lowStockItems = inventoryData.filter(
    (item) => item.quantity < item.min_quantity
  );

  // Active crops
  const activeCrops = cropsData.filter((crop) => crop.status === 'growing');

  // Summary cards
  const summaryCards = [
    {
      id: 'finance',
      title: 'Finance',
      value: formatCurrency(financeSummary?.net_profit || 0),
      subtitle: `${financeSummary?.transactions_count || 0} transactions`,
      icon: FiDollarSign,
      color: 'bg-green-100 text-green-600',
      bg: 'bg-green-50',
    },
    {
      id: 'crops',
      title: 'Crops',
      value: cropsData.length,
      subtitle: `${activeCrops.length} active`,
      icon: FaSeedling,
      color: 'bg-emerald-100 text-emerald-600',
      bg: 'bg-emerald-50',
    },
    {
      id: 'workers',
      title: 'Workers',
      value: workersData.length,
      subtitle: `${workersData.filter(w => w.is_active).length} active`,
      icon: FiUsers,
      color: 'bg-blue-100 text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      id: 'inventory',
      title: 'Inventory Items',
      value: inventoryData.length,
      subtitle: `${lowStockItems.length} low stock`,
      icon: FiPackage,
      color: 'bg-purple-100 text-purple-600',
      bg: 'bg-purple-50',
    },
  ];

  // Skeleton loader
  const SkeletonCard = () => (
    <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100 animate-pulse">
      <div className="flex items-center gap-3">
        <div className="h-12 w-12 bg-gray-200 rounded-lg"></div>
        <div className="flex-1">
          <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
          <div className="h-6 bg-gray-200 rounded w-24"></div>
          <div className="h-3 bg-gray-200 rounded w-16 mt-1"></div>
        </div>
      </div>
    </div>
  );

  const SkeletonSection = () => (
    <div className="animate-pulse">
      <div className="h-6 bg-gray-200 rounded w-48 mb-4"></div>
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="p-4 border border-gray-100 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-32 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-24"></div>
              </div>
              <div className="h-6 bg-gray-200 rounded w-16"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="p-4 lg:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Reports</h1>
            <p className="text-sm text-gray-400">
              {farmId ? `Farm report for ${currentFarm?.name || 'Farm'}` : 'Select a farm to view reports'}
            </p>
          </div>
          <button
            onClick={handlePrint}
            disabled={!farmId || isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FiPrinter />
            Export Report
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Farm DNA Score */}
        {farmId && (
          <div className="mb-6 max-w-sm">
            <FarmDNAScore overallScore={84} />
          </div>
        )}

        {/* Summary Cards */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Summary</h2>
          {isLoading && !financeSummary ? (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {summaryCards.map((card) => {
                const Icon = card.icon;
                return (
                  <div
                    key={card.id}
                    className={`${card.bg} rounded-xl p-4 border border-gray-100`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-2.5 rounded-lg ${card.color}`}>
                        <Icon className="text-lg" />
                      </div>
                      <div>
                        <div className="text-xs text-gray-400 font-medium uppercase tracking-wider">
                          {card.title}
                        </div>
                        <div className="text-xl font-bold text-gray-800">{card.value}</div>
                        <div className="text-xs text-gray-500">{card.subtitle}</div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Low Stock Items */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">
            Low Stock Items
            {lowStockItems.length > 0 && (
              <span className="ml-2 text-sm font-normal text-red-500">
                ({lowStockItems.length} items)
              </span>
            )}
          </h2>
          {isLoading ? (
            <SkeletonSection />
          ) : lowStockItems.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 text-center">
              <FiPackage className="text-3xl text-gray-300 mx-auto mb-2" />
              <p className="text-gray-500">No low stock items</p>
              <p className="text-xs text-gray-400">All inventory items are above minimum quantity</p>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <ul className="divide-y divide-gray-100">
                {lowStockItems.slice(0, 10).map((item) => (
                  <li key={item.id} className="p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-gray-800">{item.name}</div>
                        <div className="text-sm text-gray-500">
                          {item.category} • {item.quantity} / {item.min_quantity} {item.unit}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <FiAlertTriangle className="text-red-500" />
                        <span className="text-sm font-medium text-red-600">
                          {Math.round(((item.min_quantity - item.quantity) / item.min_quantity) * 100)}% below min
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
              {lowStockItems.length > 10 && (
                <div className="p-3 text-center text-sm text-gray-400 border-t border-gray-100">
                  +{lowStockItems.length - 10} more low stock items
                </div>
              )}
            </div>
          )}
        </div>

        {/* Active Crops */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">
            Active Crops
            {activeCrops.length > 0 && (
              <span className="ml-2 text-sm font-normal text-gray-400">
                ({activeCrops.length} crops)
              </span>
            )}
          </h2>
          {isLoading ? (
            <SkeletonSection />
          ) : activeCrops.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 text-center">
              <FaSeedling className="text-3xl text-gray-300 mx-auto mb-2" />
              <p className="text-gray-500">No active crops</p>
              <p className="text-xs text-gray-400">Add crops to start tracking growth</p>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <ul className="divide-y divide-gray-100">
                {activeCrops.slice(0, 10).map((crop) => {
                  const status = getStatusBadge(crop.status);
                  return (
                    <li key={crop.id} className="p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-800">{crop.name}</div>
                          <div className="text-sm text-gray-500">
                            {crop.variety || 'Unknown variety'} • Area: {crop.area || '—'} feddans
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            Planted: {crop.planting_date ? new Date(crop.planting_date).toLocaleDateString() : '—'}
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          {crop.health_score !== null && crop.health_score !== undefined && (
                            <div className="text-right">
                              <div className={`text-sm font-semibold ${getHealthColor(crop.health_score)}`}>
                                {crop.health_score.toFixed(1)}%
                              </div>
                              <div className="text-xs text-gray-400">Health</div>
                            </div>
                          )}
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.color}`}>
                            {status.label}
                          </span>
                        </div>
                      </div>
                    </li>
                  );
                })}
              </ul>
              {activeCrops.length > 10 && (
                <div className="p-3 text-center text-sm text-gray-400 border-t border-gray-100">
                  +{activeCrops.length - 10} more active crops
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-xs text-gray-400 border-t border-gray-200 pt-4 print:hidden">
          CropMind — AI-Powered Farm Management System
          <br />
          Military Technical College Cairo 2026
        </div>
      </div>
    </div>
  );
};

export default Reports;