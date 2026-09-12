/**
 * CropMind - Mobile API Service
 * React Native API client for worker mobile app
 * 
 * Author: CropMind Team
 * Date: 2026
 */

import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// ============================================
// Configuration
// ============================================

const BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api/v1';
const TOKEN_KEY = 'cropmind_auth_token';
const USER_KEY = 'cropmind_user';

// ============================================
// Axios Instance
// ============================================

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    } catch (error) {
      console.error('[API] Interceptor error:', error);
      return config;
    }
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle auth errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      await AsyncStorage.removeItem(TOKEN_KEY);
      await AsyncStorage.removeItem(USER_KEY);
      // Navigate to login will be handled in the app
    }
    return Promise.reject(error);
  }
);

// ============================================
// Auth Functions
// ============================================

/**
 * Login user with email and password
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<Object>} User data and token
 */
export const login = async (email, password) => {
  try {
    const response = await api.post('/auth/login', { email, password });
    const { access_token, user } = response.data;
    
    await AsyncStorage.setItem(TOKEN_KEY, access_token);
    await AsyncStorage.setItem(USER_KEY, JSON.stringify(user));
    
    return { success: true, user, token: access_token };
  } catch (error) {
    console.error('[API] Login error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Login failed',
    };
  }
};

/**
 * Logout user
 */
export const logout = async () => {
  try {
    await AsyncStorage.removeItem(TOKEN_KEY);
    await AsyncStorage.removeItem(USER_KEY);
    return { success: true };
  } catch (error) {
    console.error('[API] Logout error:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Get current user from storage
 * @returns {Promise<Object|null>} User data or null
 */
export const getCurrentUser = async () => {
  try {
    const userJson = await AsyncStorage.getItem(USER_KEY);
    if (userJson) {
      return JSON.parse(userJson);
    }
    return null;
  } catch (error) {
    console.error('[API] Get current user error:', error);
    return null;
  }
};

// ============================================
// Worker Functions
// ============================================

/**
 * Get worker by ID
 * @param {number} workerId - Worker ID
 * @returns {Promise<Object>} Worker data
 */
export const getWorkerProfile = async (workerId) => {
  try {
    const response = await api.get(`/workforce/${workerId}`);
    return { success: true, data: response.data };
  } catch (error) {
    console.error('[API] Get worker profile error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to get worker profile',
    };
  }
};

/**
 * Update worker profile
 * @param {number} workerId - Worker ID
 * @param {Object} data - Updated worker data
 * @returns {Promise<Object>} Updated worker data
 */
export const updateWorkerProfile = async (workerId, data) => {
  try {
    const response = await api.put(`/workforce/${workerId}`, data);
    return { success: true, data: response.data };
  } catch (error) {
    console.error('[API] Update worker profile error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to update profile',
    };
  }
};

/**
 * Get farm details
 * @param {number} farmId - Farm ID
 * @returns {Promise<Object>} Farm data
 */
export const getFarm = async (farmId) => {
  try {
    const response = await api.get(`/farms/${farmId}`);
    return { success: true, data: response.data };
  } catch (error) {
    console.error('[API] Get farm error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to get farm',
    };
  }
};

// ============================================
// Task Functions
// ============================================

/**
 * Get today's tasks for a worker
 * @param {number} farmId - Farm ID
 * @param {number} workerId - Worker ID
 * @returns {Promise<Object>} List of tasks
 */
export const getTodayTasks = async (farmId, workerId) => {
  try {
    // Note: Tasks endpoint may need to be implemented in backend
    // This is a placeholder using workforce agent endpoint
    const response = await api.get(`/workforce/farms/${farmId}/active`);
    const workers = response.data || [];
    
    // Filter tasks for specific worker if workerId provided
    let tasks = [];
    if (workerId) {
      const worker = workers.find(w => w.id === workerId);
      if (worker && worker.tasks) {
        tasks = worker.tasks;
      }
    } else {
      // Collect all tasks from all workers
      workers.forEach(w => {
        if (w.tasks) {
          tasks = tasks.concat(w.tasks);
        }
      });
    }
    
    // Filter for today's tasks
    const today = new Date().toISOString().split('T')[0];
    const todayTasks = tasks.filter(task => {
      if (!task.due_date) return true;
      return task.due_date <= today;
    });
    
    return { success: true, data: todayTasks };
  } catch (error) {
    console.error('[API] Get today tasks error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to get tasks',
    };
  }
};

/**
 * Complete a task
 * @param {string|number} taskId - Task ID
 * @returns {Promise<Object>} Updated task status
 */
export const completeTask = async (taskId) => {
  try {
    // Note: Task completion endpoint may need to be implemented
    // This is a placeholder
    const response = await api.post(`/workforce/tasks/${taskId}/complete`);
    return { success: true, data: response.data };
  } catch (error) {
    console.error('[API] Complete task error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to complete task',
    };
  }
};

// ============================================
// Alert Functions
// ============================================

/**
 * Get alerts for a farm
 * @param {number} farmId - Farm ID
 * @returns {Promise<Object>} List of alerts
 */
export const getAlerts = async (farmId) => {
  try {
    const response = await api.get(`/alerts/farms/${farmId}`);
    return { success: true, data: response.data };
  } catch (error) {
    console.error('[API] Get alerts error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to get alerts',
    };
  }
};

// ============================================
// Crop Scanning Functions
// ============================================

/**
 * Scan a crop image for disease detection
 * @param {string} imageBase64 - Base64 encoded image
 * @param {number} farmId - Farm ID
 * @returns {Promise<Object>} Scan results
 */
export const scanCrop = async (imageBase64, farmId) => {
  try {
    // Convert base64 to blob for upload
    const response = await api.post(
      '/computer-vision/scan',
      {
        image: imageBase64,
        farm_id: farmId,
      },
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return { success: true, data: response.data };
  } catch (error) {
    console.error('[API] Scan crop error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to scan crop',
    };
  }
};

// ============================================
// Issue Reporting Functions
// ============================================

/**
 * Report an issue on the farm
 * @param {number} farmId - Farm ID
 * @param {number} workerId - Worker ID
 * @param {Object} issue - Issue details
 * @param {string} issue.type - Issue type
 * @param {string} issue.description - Issue description
 * @param {string} issue.severity - Issue severity (low, medium, high)
 * @returns {Promise<Object>} Report result
 */
export const reportIssue = async (farmId, workerId, issue) => {
  try {
    const response = await api.post('/alerts/report', {
      farm_id: farmId,
      worker_id: workerId,
      type: issue.type,
      description: issue.description,
      severity: issue.severity || 'medium',
    });
    return { success: true, data: response.data };
  } catch (error) {
    console.error('[API] Report issue error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to report issue',
    };
  }
};

// ============================================
// Farm Crops Functions
// ============================================

/**
 * Get crops for a farm
 * @param {number} farmId - Farm ID
 * @returns {Promise<Object>} List of crops
 */
export const getCrops = async (farmId) => {
  try {
    const response = await api.get('/crops', {
      params: { farm_id: farmId },
    });
    return { success: true, data: response.data };
  } catch (error) {
    console.error('[API] Get crops error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to get crops',
    };
  }
};

// ============================================
// Export Default
// ============================================

export default {
  login,
  logout,
  getCurrentUser,
  getWorkerProfile,
  updateWorkerProfile,
  getFarm,
  getTodayTasks,
  completeTask,
  getAlerts,
  scanCrop,
  reportIssue,
  getCrops,
};
