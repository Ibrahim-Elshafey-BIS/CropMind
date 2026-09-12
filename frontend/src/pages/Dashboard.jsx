import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FarmDNAScore from '../components/shared/FarmDNAScore';
import KPICards from '../components/dashboard/KPICards';
import FarmHealthChart from '../components/dashboard/FarmHealthChart';
import AIInsightsFeed from '../components/dashboard/AIInsightsFeed';
import RevenueChart from '../components/dashboard/RevenueChart';
import ProductionForecast from '../components/dashboard/ProductionForecast';
import useAuthStore from '../store/authStore';
import useFarmStore from '../store/farmStore';
import useAgentStore from '../store/agentStore';
import { finance, crops, workforce, irrigation, alerts } from '../services/api';

const Dashboard = () => {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading, user } = useAuthStore();
  const { currentFarm, farms, fetchFarms, loadCurrentFarm } = useFarmStore();
  const { agentsStatus, fetchAgentsStatus } = useAgentStore();

  // State for dashboard data
  const [financeSummary, setFinanceSummary] = useState(null);
  const [cropsCount, setCropsCount] = useState(0);
  const [workersCount, setWorkersCount] = useState(0);
  const [healthData, setHealthData] = useState([]);
  const [insights, setInsights] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const farmId = currentFarm?.id;

  // Check authentication
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [authLoading, isAuthenticated, navigate]);

  // Load farms and current farm
  useEffect(() => {
    if (isAuthenticated) {
      fetchFarms();
    }
  }, [isAuthenticated]);

  // Load current farm from localStorage after farms are loaded
  useEffect(() => {
    if (farms.length > 0) {
      loadCurrentFarm();
    }
  }, [farms]);

  // Fetch dashboard data when farm changes
  useEffect(() => {
    if (!farmId) {
      setIsLoading(false);
      return;
    }

    const fetchDashboardData = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Fetch all data in parallel
        const [
          summaryRes,
          cropsRes,
          workersRes,
          healthRes,
          insightsRes,
          agentsStatusRes,
        ] = await Promise.allSettled([
          finance.getFinanceSummary(farmId),
          crops.getCrops({ farm_id: farmId, limit: 1000 }),
          workforce.getWorkers({ farm_id: farmId, limit: 1000 }),
          irrigation.getLatestReadings(farmId),
          alerts.getFarmAlerts(farmId),
          fetchAgentsStatus(),
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
          const cropsData = cropsRes.value || [];
          setCropsCount(cropsData.length);
        } else {
          console.error('Failed to fetch crops:', cropsRes.reason);
          setCropsCount(0);
        }

        // Process workers
        if (workersRes.status === 'fulfilled') {
          const workersData = workersRes.value || [];
          setWorkersCount(workersData.filter(w => w.is_active !== false).length);
        } else {
          console.error('Failed to fetch workers:', workersRes.reason);
          setWorkersCount(0);
        }

        // Process health data (sensor readings)
        if (healthRes.status === 'fulfilled') {
          const readings = healthRes.value || [];
          // Transform sensor readings into health data format
          const transformedHealthData = readings.map(reading => ({
            date: new Date(reading.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            score: reading.type === 'soil_moisture' ? reading.value : 75 + Math.random() * 15,
            crop_health: reading.type === 'temperature' ? Math.min(reading.value, 100) : 70 + Math.random() * 20,
            water_efficiency: reading.type === 'humidity' ? Math.min(reading.value, 100) : 65 + Math.random() * 25,
            soil_health: reading.type === 'ph' ? Math.min(reading.value * 10, 100) : 60 + Math.random() * 30,
          }));
          setHealthData(transformedHealthData);
        } else {
          console.error('Failed to fetch health data:', healthRes.reason);
          setHealthData([]);
        }

        // Process insights (alerts)
        if (insightsRes.status === 'fulfilled') {
          const alertsData = insightsRes.value || { alerts: [] };
          const transformedInsights = (alertsData.alerts || []).map((alert, index) => ({
            id: index + 1,
            agent: alert.type === 'low_stock' ? 'Inventory Agent' :
                   alert.type === 'sensor_anomaly' ? 'Resource Optimization' :
                   alert.type === 'crop_health' ? 'Farm Intelligence' : 'Farm Copilot',
            message: alert.message,
            type: alert.severity === 'critical' ? 'danger' :
                   alert.severity === 'high' ? 'warning' :
                   alert.severity === 'medium' ? 'info' : 'success',
            timestamp: new Date().toISOString(),
          }));
          setInsights(transformedInsights);
        } else {
          console.error('Failed to fetch insights:', insightsRes.reason);
          setInsights([]);
        }

        // Process agents status
        if (agentsStatusRes.status === 'fulfilled') {
          // Agents status is already stored in agentStore
          console.log('Agents status updated');
        }

        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError('Failed to load dashboard data. Please refresh.');
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [farmId, fetchAgentsStatus]);

  // Show loading state while checking auth
  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1a5c38] mx-auto mb-4"></div>
          <p className="text-gray-500">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="p-4 lg:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Page Title */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
          <p className="text-sm text-gray-400">
            Welcome back, {user?.full_name || 'User'}!
            {currentFarm && ` 🌾 ${currentFarm.name}`}
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Top: KPICards */}
        <div className="mb-6">
          <KPICards
            financeSummary={financeSummary}
            cropsCount={cropsCount}
            workersCount={workersCount}
            dnaScore={84}
            isLoading={isLoading}
          />
        </div>

        {/* Middle: FarmHealthChart + AIInsightsFeed */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <FarmHealthChart
            healthData={healthData}
            isLoading={isLoading}
          />
          <AIInsightsFeed
            insights={insights}
            isLoading={isLoading}
          />
        </div>

        {/* Bottom: RevenueChart + ProductionForecast */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RevenueChart
            revenueData={[]}
            isLoading={isLoading}
          />
          <ProductionForecast
            forecastData={[]}
            isLoading={isLoading}
          />
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-xs text-gray-400 border-t border-gray-200 pt-4">
          CropMind — AI-Powered Farm Management System
          <br />
          Military Technical College Cairo 2026
        </div>
      </div>
    </div>
  );
};

export default Dashboard;