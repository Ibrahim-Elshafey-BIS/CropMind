// === FILE: frontend/src/services/api.js ===

import axios from 'axios';
import { toast } from 'react-hot-toast';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      toast.error('Session expired. Please login again.');
    }
    return Promise.reject(error);
  }
);

// ============================================
// Auth
// ============================================

export const auth = {
  login: async (email, password) => {
    const response = await api.post('/api/auth/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },
  register: async (data) => {
    const response = await api.post('/api/auth/register', data);
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },
  getCurrentUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
};

// ============================================
// Farms
// ============================================

export const farms = {
  getFarms: async (params) => {
    const response = await api.get('/api/farms', { params });
    return response.data;
  },
  createFarm: async (data) => {
    const response = await api.post('/api/farms', data);
    return response.data;
  },
  getFarm: async (id) => {
    const response = await api.get(`/api/farms/${id}`);
    return response.data;
  },
  updateFarm: async (id, data) => {
    const response = await api.put(`/api/farms/${id}`, data);
    return response.data;
  },
  deleteFarm: async (id) => {
    await api.delete(`/api/farms/${id}`);
  },
};

// ============================================
// Crops
// ============================================

export const crops = {
  getCrops: async (params) => {
    const response = await api.get('/api/crops', { params });
    return response.data;
  },
  createCrop: async (data) => {
    const response = await api.post('/api/crops', data);
    return response.data;
  },
  getCrop: async (id) => {
    const response = await api.get(`/api/crops/${id}`);
    return response.data;
  },
  updateCrop: async (id, data) => {
    const response = await api.put(`/api/crops/${id}`, data);
    return response.data;
  },
  deleteCrop: async (id) => {
    await api.delete(`/api/crops/${id}`);
  },
};

// ============================================
// Finance
// ============================================

export const finance = {
  getTransactions: async (params) => {
    const response = await api.get('/api/finance', { params });
    return response.data;
  },
  createTransaction: async (data) => {
    const response = await api.post('/api/finance', data);
    return response.data;
  },
  getTransaction: async (id) => {
    const response = await api.get(`/api/finance/${id}`);
    return response.data;
  },
  updateTransaction: async (id, data) => {
    const response = await api.put(`/api/finance/${id}`, data);
    return response.data;
  },
  deleteTransaction: async (id) => {
    await api.delete(`/api/finance/${id}`);
  },
  getFinanceSummary: async (farmId) => {
    const response = await api.get(`/api/finance/farms/${farmId}/summary`);
    return response.data;
  },
};

// ============================================
// Inventory
// ============================================

export const inventory = {
  getInventory: async (params) => {
    const response = await api.get('/api/inventory', { params });
    return response.data;
  },
  createInventoryItem: async (data) => {
    const response = await api.post('/api/inventory', data);
    return response.data;
  },
  getInventoryItem: async (id) => {
    const response = await api.get(`/api/inventory/${id}`);
    return response.data;
  },
  updateInventoryItem: async (id, data) => {
    const response = await api.put(`/api/inventory/${id}`, data);
    return response.data;
  },
  deleteInventoryItem: async (id) => {
    await api.delete(`/api/inventory/${id}`);
  },
  getLowStock: async (farmId) => {
    const response = await api.get(`/api/inventory/farms/${farmId}/low-stock`);
    return response.data;
  },
};

// ============================================
// Workforce
// ============================================

export const workforce = {
  getWorkers: async (params) => {
    const response = await api.get('/api/workforce', { params });
    return response.data;
  },
  createWorker: async (data) => {
    const response = await api.post('/api/workforce', data);
    return response.data;
  },
  getWorker: async (id) => {
    const response = await api.get(`/api/workforce/${id}`);
    return response.data;
  },
  updateWorker: async (id, data) => {
    const response = await api.put(`/api/workforce/${id}`, data);
    return response.data;
  },
  deleteWorker: async (id) => {
    await api.delete(`/api/workforce/${id}`);
  },
  getActiveWorkers: async (farmId) => {
    const response = await api.get(`/api/workforce/farms/${farmId}/active`);
    return response.data;
  },
};

// ============================================
// Irrigation / Sensors
// ============================================

export const irrigation = {
  getSensorReadings: async (farmId, params) => {
    const response = await api.get(`/api/irrigation/farms/${farmId}/readings`, { params });
    return response.data;
  },
  createSensorReading: async (data) => {
    const response = await api.post('/api/irrigation/readings', data);
    return response.data;
  },
  getAnomalies: async (farmId) => {
    const response = await api.get(`/api/irrigation/farms/${farmId}/anomalies`);
    return response.data;
  },
  getLatestReadings: async (farmId) => {
    const response = await api.get(`/api/irrigation/farms/${farmId}/latest`);
    return response.data;
  },
  getSchedules: async (farmId, isActive) => {
    const params = {};
    if (isActive !== undefined) {
      params.is_active = isActive;
    }
    const response = await api.get(`/api/irrigation/schedules/farms/${farmId}`, { params });
    return response.data;
  },
  createSchedule: async (data) => {
    const response = await api.post('/api/irrigation/schedules', data);
    return response.data;
  },
  updateSchedule: async (scheduleId, data) => {
    const response = await api.put(`/api/irrigation/schedules/${scheduleId}`, data);
    return response.data;
  },
  deleteSchedule: async (scheduleId) => {
    await api.delete(`/api/irrigation/schedules/${scheduleId}`);
  },
  getTodaySchedules: async (farmId) => {
    const response = await api.get(`/api/irrigation/schedules/farms/${farmId}/today`);
    return response.data;
  },
};

// ============================================
// Market
// ============================================

export const market = {
  getMarketPrices: async (params) => {
    const response = await api.get('/api/market/prices', { params });
    return response.data;
  },
  createMarketPrice: async (data) => {
    const response = await api.post('/api/market/prices', data);
    return response.data;
  },
  getLatestPrices: async () => {
    const response = await api.get('/api/market/prices/latest');
    return response.data;
  },
  getCommodityPrices: async (commodity, params) => {
    const response = await api.get(`/api/market/prices/${commodity}`, { params });
    return response.data;
  },
};

// ============================================
// Alerts
// ============================================

export const alerts = {
  getFarmAlerts: async (farmId, params) => {
    const response = await api.get(`/api/alerts/farms/${farmId}`, { params });
    return response.data;
  },
};

// ============================================
// Agents
// ============================================

export const agents = {
  chatCopilot: async (message, farmId, conversationId) => {
    const response = await api.post('/api/agents/copilot', {
      message,
      farm_id: farmId,
      conversation_id: conversationId,
    });
    return response.data;
  },
  analyzeFarm: async (farmId) => {
    const response = await api.post(`/api/agents/analyze/${farmId}`);
    return response.data;
  },
  getMarketIntel: async (farmId) => {
    const response = await api.post(`/api/agents/market-intel/${farmId}`);
    return response.data;
  },
  getOptimization: async (farmId) => {
    const response = await api.post(`/api/agents/optimize/${farmId}`);
    return response.data;
  },
  getAgentsStatus: async () => {
    const response = await api.get('/api/agents/status');
    return response.data;
  },
};

export default api;