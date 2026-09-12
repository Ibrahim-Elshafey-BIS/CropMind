/**
 * CropMind - Main Application
 * Root component with authentication, routing, and layout
 * 
 * Author: CropMind Team
 * Date: 2026
 */

import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { FiMail, FiLock, FiLoader, FiFeather } from 'react-icons/fi';

import useAuthStore from './store/authStore';
import useFarmStore from './store/farmStore';

// Pages
import Dashboard from './pages/Dashboard';
import Crops from './pages/Crops';
import Finance from './pages/Finance';
import Inventory from './pages/Inventory';
import Irrigation from './pages/Irrigation';
import Market from './pages/Market';
import Workforce from './pages/Workforce';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import FarmMap from './pages/FarmMap';
import WorkerDashboard from './pages/WorkerDashboard';

// Shared Components
import Navbar from './components/shared/Navbar';
import Sidebar from './components/shared/Sidebar';
import CopilotWidget from './components/copilot/CopilotWidget';

export default function App() {
  const { user, isAuthenticated, isLoading, login, checkAuth } = useAuthStore();
  const { fetchFarms, loadCurrentFarm } = useFarmStore();

  // Local state for login form
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loginError, setLoginError] = useState('');

  // Check authentication on mount
  useEffect(() => {
    checkAuth();
  }, []);

  // Fetch farms and load current farm when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const loadFarms = async () => {
        await fetchFarms();
        loadCurrentFarm();
      };
      loadFarms();
    }
  }, [isAuthenticated]);

  // Handle login form submission
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    setIsSubmitting(true);

    try {
      const result = await login(email, password);
      if (!result.success) {
        setLoginError(result.error || 'فشل تسجيل الدخول');
      }
    } catch (error) {
      setLoginError('حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Loading screen
  if (isLoading) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <FiLoader className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-neutral-500">جاري التحميل...</p>
        </div>
      </div>
    );
  }

  // Login screen
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-neutral-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-card shadow-xl p-8 max-w-md w-full">
          {/* Logo / Brand */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FiFeather className="w-8 h-8 text-primary-600" />
            </div>
            <h1 className="text-3xl font-bold text-neutral-800">CropMind</h1>
            <p className="text-sm text-neutral-500 mt-1">نظام إدارة المزارع الذكي</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleLogin}>
            <div className="space-y-4">
              {/* Email Field */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-neutral-700 mb-1">
                  البريد الإلكتروني
                </label>
                <div className="relative">
                  <FiMail className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400" />
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="example@cropmind.com"
                    required
                    disabled={isSubmitting}
                    className="w-full pr-10 pl-4 py-2.5 border border-neutral-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-colors bg-white text-neutral-800 disabled:opacity-60 disabled:cursor-not-allowed"
                  />
                </div>
              </div>

              {/* Password Field */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-neutral-700 mb-1">
                  كلمة المرور
                </label>
                <div className="relative">
                  <FiLock className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400" />
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    minLength={8}
                    disabled={isSubmitting}
                    className="w-full pr-10 pl-4 py-2.5 border border-neutral-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-colors bg-white text-neutral-800 disabled:opacity-60 disabled:cursor-not-allowed"
                  />
                </div>
              </div>

              {/* Error Message */}
              {loginError && (
                <div className="bg-danger-50 text-danger-700 rounded-lg p-3 text-sm">
                  {loginError}
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2.5 rounded-lg transition-colors disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <FiLoader className="w-5 h-5 animate-spin" />
                    جاري الدخول...
                  </>
                ) : (
                  'تسجيل الدخول'
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Toaster */}
        <Toaster position="top-center" />
      </div>
    );
  }

  // Main App Layout (Authenticated)
  if (user?.role === 'worker') {
    return <WorkerDashboard />;
  }

  return (
    <div className="flex min-h-screen bg-neutral-50">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="flex-1 overflow-y-auto p-6 scrollbar-thin">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/crops" element={<Crops />} />
            <Route path="/finance" element={<Finance />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/irrigation" element={<Irrigation />} />
            <Route path="/market" element={<Market />} />
            <Route path="/workforce" element={<Workforce />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/farm-map" element={<FarmMap />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>

      {/* Copilot Widget */}
      <CopilotWidget />

      {/* Toaster */}
      <Toaster position="top-center" />
    </div>
  );
}