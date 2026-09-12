// === FILE: frontend/src/pages/Irrigation.jsx ===

import React, { useState, useEffect } from 'react';
import { FiThermometer, FiDroplet, FiSun, FiActivity, FiAlertTriangle, FiRefreshCw, FiTrash2, FiPlus } from 'react-icons/fi';
import { FaTint } from 'react-icons/fa';
import { toast } from 'react-hot-toast';
import useFarmStore from '../store/farmStore';
import { irrigation as irrigationApi, agents } from '../services/api';

const Irrigation = () => {
  const { currentFarm } = useFarmStore();
  const [readings, setReadings] = useState([]);
  const [latestReadings, setLatestReadings] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [filterType, setFilterType] = useState('all');
  const [error, setError] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [isLoadingRec, setIsLoadingRec] = useState(false);
  const [schedules, setSchedules] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newSchedule, setNewSchedule] = useState({
    day_of_week: 0,
    start_time: '06:00:00',
    duration_minutes: 30,
    is_active: true,
    notes: '',
  });

  const farmId = currentFarm?.id;

  // Sensor types configuration
  const sensorTypes = [
    { id: 'temperature', label: 'Temperature', icon: FiThermometer, unit: '°C', normalRange: '15–40', color: 'text-red-500' },
    { id: 'humidity', label: 'Humidity', icon: FiDroplet, unit: '%', normalRange: '30–80', color: 'text-blue-500' },
    { id: 'soil_moisture', label: 'Soil Moisture', icon: FaTint, unit: '%', normalRange: '20–70', color: 'text-green-600' },
    { id: 'light', label: 'Light Intensity', icon: FiSun, unit: 'lux', normalRange: '100–900', color: 'text-yellow-500' },
    { id: 'ph', label: 'pH Level', icon: FiActivity, unit: '', normalRange: '5.5–7.5', color: 'text-purple-500' },
  ];

  // Fetch readings
  const fetchReadings = async () => {
    if (!farmId) {
      setReadings([]);
      setLatestReadings({});
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await irrigationApi.getSensorReadings(farmId);
      setReadings(data || []);

      // Get latest reading per sensor type
      const latest = {};
      sensorTypes.forEach(type => {
        const typeReadings = (data || []).filter(r => r.type === type.id);
        if (typeReadings.length > 0) {
          latest[type.id] = typeReadings[0];
        }
      });
      setLatestReadings(latest);
    } catch (err) {
      console.error('Error fetching sensor readings:', err);
      setError('Failed to load sensor data. Please refresh.');
      setReadings([]);
      setLatestReadings({});
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch schedules
  const fetchSchedules = async () => {
    if (!farmId) {
      setSchedules([]);
      return;
    }

    try {
      const data = await irrigationApi.getSchedules(farmId);
      setSchedules(data || []);
    } catch (err) {
      console.error('Error fetching schedules:', err);
      setSchedules([]);
    }
  };

  useEffect(() => {
    fetchReadings();
    fetchSchedules();
  }, [farmId]);

  // Filter readings by type
  const filteredReadings = readings.filter((r) =>
    filterType === 'all' || r.type === filterType
  );

  // Format timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return '—';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  // Check if value is normal
  const getNormalRange = (type) => {
    const ranges = {
      temperature: { min: 15, max: 40 },
      humidity: { min: 30, max: 80 },
      soil_moisture: { min: 20, max: 70 },
      light: { min: 100, max: 900 },
      ph: { min: 5.5, max: 7.5 },
    };
    return ranges[type] || { min: 0, max: 100 };
  };

  const isValueNormal = (type, value) => {
    const range = getNormalRange(type);
    return value >= range.min && value <= range.max;
  };

  // Get recommendation
  const getRecommendation = async () => {
    if (!farmId) {
      toast.error('Please select a farm first');
      return;
    }

    setIsLoadingRec(true);
    try {
      const data = await agents.getOptimization(farmId);
      setRecommendation(data);
      toast.success('Recommendation loaded successfully');
    } catch (err) {
      console.error('Error fetching recommendation:', err);
      toast.error(err.response?.data?.detail || 'Failed to get recommendation');
    } finally {
      setIsLoadingRec(false);
    }
  };

  // Handle create schedule
  const handleCreateSchedule = async (e) => {
    e.preventDefault();
    try {
      await irrigationApi.createSchedule({
        ...newSchedule,
        farm_id: farmId,
      });
      toast.success('Schedule created successfully');
      setShowAddForm(false);
      setNewSchedule({
        day_of_week: 0,
        start_time: '06:00:00',
        duration_minutes: 30,
        is_active: true,
        notes: '',
      });
      await fetchSchedules();
    } catch (err) {
      console.error('Error creating schedule:', err);
      toast.error(err.response?.data?.detail || 'Failed to create schedule');
    }
  };

  // Handle delete schedule
  const handleDeleteSchedule = async (scheduleId) => {
    if (!window.confirm('Are you sure you want to delete this schedule?')) return;
    try {
      await irrigationApi.deleteSchedule(scheduleId);
      toast.success('Schedule deleted successfully');
      await fetchSchedules();
    } catch (err) {
      console.error('Error deleting schedule:', err);
      toast.error(err.response?.data?.detail || 'Failed to delete schedule');
    }
  };

  // Get day name
  const getDayName = (dayOfWeek) => {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    return days[dayOfWeek] || 'Unknown';
  };

  // Skeleton loader
  const SkeletonCard = () => (
    <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 bg-gray-200 rounded-lg"></div>
          <div className="h-5 bg-gray-200 rounded w-24"></div>
        </div>
        <div className="h-6 bg-gray-200 rounded w-16"></div>
      </div>
      <div className="mt-2 h-8 bg-gray-200 rounded w-20"></div>
      <div className="mt-1 h-4 bg-gray-200 rounded w-32"></div>
    </div>
  );

  const SkeletonRow = () => (
    <div className="p-4 border-b border-gray-100 animate-pulse">
      <div className="flex items-center gap-4">
        <div className="h-4 bg-gray-200 rounded w-24"></div>
        <div className="h-4 bg-gray-200 rounded w-16"></div>
        <div className="h-4 bg-gray-200 rounded w-20"></div>
        <div className="h-4 bg-gray-200 rounded w-24"></div>
        <div className="h-6 bg-gray-200 rounded w-16"></div>
      </div>
    </div>
  );

  return (
    <div className="p-4 lg:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Irrigation & Sensors</h1>
            <p className="text-sm text-gray-400">
              {farmId ? `Monitoring sensors for ${currentFarm?.name || 'Farm'}` : 'Select a farm to view sensor data'}
            </p>
          </div>
          <button
            onClick={fetchReadings}
            disabled={!farmId || isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FiRefreshCw className={isLoading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Sensor Cards */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Sensor Overview</h2>
          {isLoading && !Object.keys(latestReadings).length ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : Object.keys(latestReadings).length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
              <FiActivity className="text-4xl text-gray-300 mx-auto mb-3" />
              <h4 className="text-gray-600 font-medium">No Sensor Data Available</h4>
              <p className="text-sm text-gray-400 mt-1">Sensor readings will appear here once available</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              {sensorTypes.map((type) => {
                const reading = latestReadings[type.id];
                const Icon = type.icon;
                const isNormal = reading ? isValueNormal(type.id, reading.value) : true;
                const value = reading ? reading.value : '—';
                const unit = reading ? reading.unit : type.unit;

                return (
                  <div
                    key={type.id}
                    className={`bg-white rounded-xl shadow-sm p-4 border ${
                      reading?.is_anomaly ? 'border-red-300 bg-red-50' : 'border-gray-100'
                    } hover:shadow-md transition-shadow`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Icon className={`text-lg ${type.color}`} />
                        <span className="text-sm font-medium text-gray-700">{type.label}</span>
                      </div>
                      {reading?.is_anomaly && (
                        <FiAlertTriangle className="text-red-500 animate-pulse" />
                      )}
                    </div>
                    <div className={`text-2xl font-bold ${reading?.is_anomaly ? 'text-red-600' : 'text-gray-800'}`}>
                      {typeof value === 'number' ? value.toFixed(1) : value}
                      {unit && <span className="text-sm font-normal text-gray-400 ml-1">{unit}</span>}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      {reading ? `Normal: ${type.normalRange}` : 'No data'}
                    </div>
                    {reading && (
                      <div className="text-xs text-gray-400 mt-0.5 truncate">
                        {formatTime(reading.timestamp)}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Smart Recommendation */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-800">Smart Recommendation</h2>
            <button
              onClick={getRecommendation}
              disabled={!farmId || isLoadingRec}
              className="flex items-center gap-2 px-4 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoadingRec ? (
                <FiRefreshCw className="animate-spin" />
              ) : (
                <FiDroplet />
              )}
              {isLoadingRec ? 'Loading...' : 'Get Smart Recommendation'}
            </button>
          </div>

          {recommendation && (
            <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-[#1a5c38]/10 rounded-lg">
                  <FiDroplet className="text-xl text-[#1a5c38]" />
                </div>
                <h3 className="font-semibold text-gray-800">Water Optimization</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-sm text-gray-500">Additional Water Needed</div>
                  <div className="text-xl font-bold text-[#1a5c38]">
                    {recommendation.data?.water_optimization?.additional_water_needed_mm?.toFixed(1) || '—'} mm
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-sm text-gray-500">Frequency</div>
                  <div className="text-lg font-semibold text-gray-800">
                    {recommendation.data?.water_optimization?.frequency || '—'}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-sm text-gray-500">Recommendation</div>
                  <div className="text-md font-medium text-gray-800">
                    {recommendation.data?.water_optimization?.recommendation || '—'}
                  </div>
                </div>
              </div>
              {recommendation.data?.report && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600 whitespace-pre-wrap">
                    {recommendation.data.report}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Weekly Schedule */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-800">Weekly Schedule</h2>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              disabled={!farmId}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FiPlus />
              Add Schedule
            </button>
          </div>

          {/* Add Schedule Form */}
          {showAddForm && (
            <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100 mb-4">
              <h4 className="font-semibold text-gray-800 mb-3">New Schedule</h4>
              <form onSubmit={handleCreateSchedule} className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Day</label>
                  <select
                    value={newSchedule.day_of_week}
                    onChange={(e) => setNewSchedule({ ...newSchedule, day_of_week: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  >
                    <option value={0}>Monday</option>
                    <option value={1}>Tuesday</option>
                    <option value={2}>Wednesday</option>
                    <option value={3}>Thursday</option>
                    <option value={4}>Friday</option>
                    <option value={5}>Saturday</option>
                    <option value={6}>Sunday</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
                  <input
                    type="time"
                    value={newSchedule.start_time}
                    onChange={(e) => setNewSchedule({ ...newSchedule, start_time: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Duration (min)</label>
                  <input
                    type="number"
                    value={newSchedule.duration_minutes}
                    onChange={(e) => setNewSchedule({ ...newSchedule, duration_minutes: parseInt(e.target.value) })}
                    min={1}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>
                <div className="flex items-end gap-2">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Schedules Table */}
          {schedules.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
              <p className="text-gray-500">No irrigation schedules set</p>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Day</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Start Time</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {schedules.map((schedule) => (
                      <tr key={schedule.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 text-gray-800">{getDayName(schedule.day_of_week)}</td>
                        <td className="px-4 py-3 text-gray-600">{schedule.start_time}</td>
                        <td className="px-4 py-3 text-gray-600">{schedule.duration_minutes} min</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            schedule.is_active
                              ? 'bg-green-100 text-green-700'
                              : 'bg-gray-100 text-gray-500'
                          }`}>
                            {schedule.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => handleDeleteSchedule(schedule.id)}
                            className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete"
                          >
                            <FiTrash2 />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* History Table */}
        <div>
          <div className="flex flex-wrap items-center justify-between gap-4 mb-3">
            <h2 className="text-lg font-semibold text-gray-800">Reading History</h2>
            <div className="flex gap-2">
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-3 py-1.5 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-[#1a5c38] focus:border-transparent"
              >
                <option value="all">All Types</option>
                {sensorTypes.map((type) => (
                  <option key={type.id} value={type.id}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {isLoading && !readings.length ? (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              {[1, 2, 3, 4, 5].map((i) => (
                <SkeletonRow key={i} />
              ))}
            </div>
          ) : filteredReadings.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
              <p className="text-gray-500">No sensor readings found</p>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {filteredReadings.map((reading) => {
                      const isNormal = isValueNormal(reading.type, reading.value);
                      return (
                        <tr
                          key={reading.id}
                          className={`hover:bg-gray-50 transition-colors ${
                            reading.is_anomaly ? 'bg-red-50' : ''
                          }`}
                        >
                          <td className="px-4 py-3">
                            <span className="text-sm font-medium text-gray-700">
                              {sensorTypes.find(t => t.id === reading.type)?.label || reading.type}
                            </span>
                          </td>
                          <td className={`px-4 py-3 font-semibold ${reading.is_anomaly ? 'text-red-600' : 'text-gray-800'}`}>
                            {typeof reading.value === 'number' ? reading.value.toFixed(2) : reading.value}
                          </td>
                          <td className="px-4 py-3 text-gray-500">{reading.unit || '—'}</td>
                          <td className="px-4 py-3 text-gray-500">{formatTime(reading.timestamp)}</td>
                          <td className="px-4 py-3">
                            {reading.is_anomaly ? (
                              <span className="flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
                                <FiAlertTriangle className="text-xs" />
                                Anomaly
                              </span>
                            ) : isNormal ? (
                              <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                                Normal
                              </span>
                            ) : (
                              <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-medium">
                                Abnormal
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Irrigation;