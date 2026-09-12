/**
 * CropMind - Farm Map Page
 * Interactive overview of farm fields with health monitoring
 * 
 * Author: CropMind Team
 * Date: 2026
 */

import React, { useState } from 'react';
import { FiMap, FiActivity, FiDroplet, FiThermometer, FiWind, FiCamera, FiFileText, FiCpu, FiCheckCircle, FiAlertCircle, FiAlertTriangle, FiMaximize } from 'react-icons/fi';
import { FaSeedling } from 'react-icons/fa';
import useFarmStore from '../store/farmStore';

const FarmMap = () => {
  const { currentFarm } = useFarmStore();

  // Static field data
  const fields = [
    { id: 'A', crop: 'Tomato', cropAr: 'طماطم', area: 5, health: 91, status: 'healthy', lastReading: '2026-08-22 14:30' },
    { id: 'B', crop: 'Potato', cropAr: 'بطاطس', area: 3, health: 78, status: 'warning', lastReading: '2026-08-22 13:15' },
    { id: 'C', crop: 'Corn', cropAr: 'ذرة', area: 7, health: 65, status: 'warning', lastReading: '2026-08-22 12:45' },
    { id: 'D', crop: 'Pepper', cropAr: 'فلفل', area: 4, health: 45, status: 'critical', lastReading: '2026-08-22 11:30' },
    { id: 'E', crop: 'Grape', cropAr: 'عنب', area: 6, health: 88, status: 'healthy', lastReading: '2026-08-22 10:00' },
  ];

  // Sensor readings data
  const sensorReadings = [
    { field: 'A', moisture: 62, temperature: 28, humidity: 65, ph: 6.8, status: 'normal' },
    { field: 'B', moisture: 45, temperature: 31, humidity: 58, ph: 7.2, status: 'warning' },
    { field: 'C', moisture: 32, temperature: 34, humidity: 42, ph: 7.8, status: 'critical' },
    { field: 'D', moisture: 28, temperature: 35, humidity: 38, ph: 8.1, status: 'critical' },
    { field: 'E', moisture: 55, temperature: 26, humidity: 72, ph: 6.5, status: 'normal' },
  ];

  // Stats
  const totalFields = fields.length;
  const totalArea = fields.reduce((sum, f) => sum + f.area, 0);
  const activeCrops = fields.filter(f => f.status !== 'critical').length;
  const avgHealth = Math.round(fields.reduce((sum, f) => sum + f.health, 0) / fields.length);

  const getStatusBadge = (status) => {
    const statusMap = {
      healthy: { label: 'سليم', color: 'bg-success-50 text-success-700 border-success-200', icon: FiCheckCircle },
      warning: { label: 'تحذير', color: 'bg-warning-50 text-warning-700 border-warning-200', icon: FiAlertCircle },
      critical: { label: 'حرج', color: 'bg-danger-50 text-danger-700 border-danger-200', icon: FiAlertTriangle },
    };
    return statusMap[status] || statusMap.healthy;
  };

  const getSensorStatus = (status) => {
    const statusMap = {
      normal: { label: 'طبيعي', color: 'text-success-600 bg-success-50' },
      warning: { label: 'تحذير', color: 'text-warning-600 bg-warning-50' },
      critical: { label: 'حرج', color: 'text-danger-600 bg-danger-50' },
    };
    return statusMap[status] || statusMap.normal;
  };

  const getHealthColor = (score) => {
    if (score >= 80) return 'bg-success-500';
    if (score >= 60) return 'bg-warning-500';
    return 'bg-danger-500';
  };

  const getStatusEmoji = (status) => {
    const emojiMap = {
      healthy: '🟢',
      warning: '🟡',
      critical: '🟠',
    };
    return emojiMap[status] || '⚪';
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-800">Farm Map</h1>
        <p className="text-sm text-neutral-400 mt-1">Interactive overview of your farm fields</p>
        {currentFarm && (
          <p className="text-sm text-primary-600 mt-1">🌾 {currentFarm.name}</p>
        )}
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-card shadow-sm p-4 border border-neutral-100">
          <div className="flex items-center gap-2 text-primary-600 mb-1">
            <FiMap className="text-lg" />
            <span className="text-sm font-medium">Total Fields</span>
          </div>
          <div className="text-2xl font-bold text-neutral-800">{totalFields}</div>
        </div>
        <div className="bg-white rounded-card shadow-sm p-4 border border-neutral-100">
          <div className="flex items-center gap-2 text-accent-600 mb-1">
            <FiMaximize className="text-lg" />
            <span className="text-sm font-medium">Total Area</span>
          </div>
          <div className="text-2xl font-bold text-neutral-800">{totalArea} Feddan</div>
        </div>
        <div className="bg-white rounded-card shadow-sm p-4 border border-neutral-100">
          <div className="flex items-center gap-2 text-primary-600 mb-1">
            <FaSeedling className="text-lg" />
            <span className="text-sm font-medium">Active Crops</span>
          </div>
          <div className="text-2xl font-bold text-neutral-800">{activeCrops}</div>
        </div>
        <div className="bg-white rounded-card shadow-sm p-4 border border-neutral-100">
          <div className="flex items-center gap-2 text-primary-600 mb-1">
            <FiActivity className="text-lg" />
            <span className="text-sm font-medium">Health Score</span>
          </div>
          <div className="text-2xl font-bold text-neutral-800">{avgHealth}%</div>
        </div>
      </div>

      {/* Fields Grid */}
      <div>
        <h2 className="text-lg font-semibold text-neutral-800 mb-3">Fields Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {fields.map((field) => {
            const status = getStatusBadge(field.status);
            const StatusIcon = status.icon;
            const healthColor = getHealthColor(field.health);
            
            return (
              <div key={field.id} className="bg-white rounded-card shadow-sm p-5 border border-neutral-100 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="text-xs text-neutral-400 font-medium">Field {field.id}</div>
                    <div className="text-lg font-bold text-neutral-800">{field.cropAr}</div>
                    <div className="text-sm text-neutral-500">{field.crop}</div>
                  </div>
                  <span className="text-2xl">{getStatusEmoji(field.status)}</span>
                </div>
                
                <div className="text-sm text-neutral-500 mb-2">
                  {field.area} Feddan
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-neutral-500">Health</span>
                    <span className="font-semibold text-neutral-800">{field.health}%</span>
                  </div>
                  <div className="w-full h-2 bg-neutral-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${healthColor}`}
                      style={{ width: `${field.health}%` }}
                    />
                  </div>
                </div>
                
                <div className="mt-3 flex items-center justify-between">
                  <span className={`text-xs px-2 py-1 rounded-full border ${status.color} flex items-center gap-1`}>
                    <StatusIcon className="text-xs" />
                    {status.label}
                  </span>
                  <span className="text-xs text-neutral-400">
                    {field.lastReading}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Sensor Readings Table */}
      <div>
        <h2 className="text-lg font-semibold text-neutral-800 mb-3">Sensor Readings</h2>
        <div className="bg-white rounded-card shadow-sm border border-neutral-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-neutral-50 border-b border-neutral-200">
                <tr>
                  <th className="px-4 py-3 text-right text-xs font-medium text-neutral-500 uppercase">Field</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-neutral-500 uppercase">Soil Moisture</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-neutral-500 uppercase">Temperature</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-neutral-500 uppercase">Humidity</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-neutral-500 uppercase">pH</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-neutral-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {sensorReadings.map((reading) => {
                  const sensorStatus = getSensorStatus(reading.status);
                  return (
                    <tr key={reading.field} className="hover:bg-neutral-50 transition-colors">
                      <td className="px-4 py-3 font-medium text-neutral-800">Field {reading.field}</td>
                      <td className="px-4 py-3 text-neutral-600">
                        <span className="flex items-center gap-1">
                          <FiDroplet className="text-blue-500" />
                          {reading.moisture}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-neutral-600">
                        <span className="flex items-center gap-1">
                          <FiThermometer className="text-red-500" />
                          {reading.temperature}°C
                        </span>
                      </td>
                      <td className="px-4 py-3 text-neutral-600">
                        <span className="flex items-center gap-1">
                          <FiWind className="text-cyan-500" />
                          {reading.humidity}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-neutral-600">{reading.ph}</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-1 rounded-full ${sensorStatus.color}`}>
                          {sensorStatus.label}
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

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-neutral-800 mb-3">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <button className="flex items-center gap-3 px-5 py-4 bg-primary-50 hover:bg-primary-100 rounded-card border border-primary-200 transition-colors text-primary-700">
            <FiCamera className="text-xl" />
            <div className="text-right">
              <div className="font-semibold">Scan Field</div>
              <div className="text-sm text-primary-500">Open CV Scanner</div>
            </div>
          </button>
          <button className="flex items-center gap-3 px-5 py-4 bg-accent-50 hover:bg-accent-100 rounded-card border border-accent-200 transition-colors text-accent-700">
            <FiFileText className="text-xl" />
            <div className="text-right">
              <div className="font-semibold">View Reports</div>
              <div className="text-sm text-accent-500">Detailed Analysis</div>
            </div>
          </button>
          <button className="flex items-center gap-3 px-5 py-4 bg-primary-50 hover:bg-primary-100 rounded-card border border-primary-200 transition-colors text-primary-700">
            <FiCpu className="text-xl" />
            <div className="text-right">
              <div className="font-semibold">Run Agent</div>
              <div className="text-sm text-primary-500">AI Farm Intelligence</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default FarmMap;