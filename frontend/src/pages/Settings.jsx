import React, { useState, useEffect } from 'react';
import { FiSave, FiCheckCircle, FiAlertCircle, FiUser, FiMail, FiShield, FiInfo, FiHome, FiMapPin, FiMaximize2, FiPackage } from 'react-icons/fi';
import { FaSeedling } from 'react-icons/fa';
import useAuthStore from '../store/authStore';
import useFarmStore from '../store/farmStore';
import { farms as farmsApi } from '../services/api';

const Settings = () => {
  const { user } = useAuthStore();
  const { currentFarm, farms, fetchFarms, setCurrentFarm } = useFarmStore();
  const [isLoading, setIsLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    area: '',
    crop_type: '',
  });

  // Load current farm data into form
  useEffect(() => {
    if (currentFarm) {
      setFormData({
        name: currentFarm.name || '',
        location: currentFarm.location || '',
        area: currentFarm.area || '',
        crop_type: currentFarm.crop_type || '',
      });
    }
  }, [currentFarm]);

  // Handle form change
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear save message when user makes changes
    if (saveMessage) setSaveMessage(null);
  };

  // Handle farm update
  const handleUpdateFarm = async (e) => {
    e.preventDefault();
    if (!currentFarm) return;

    setIsLoading(true);
    setSaveMessage(null);

    try {
      const payload = {
        ...formData,
        area: parseFloat(formData.area) || 0,
      };

      await farmsApi.updateFarm(currentFarm.id, payload);
      
      // Refresh farms data
      await fetchFarms();
      
      // Update current farm with new data
      const updatedFarm = farms.find(f => f.id === currentFarm.id);
      if (updatedFarm) {
        setCurrentFarm(updatedFarm);
        // Update form data with fresh values
        setFormData({
          name: updatedFarm.name || '',
          location: updatedFarm.location || '',
          area: updatedFarm.area || '',
          crop_type: updatedFarm.crop_type || '',
        });
      }

      setSaveMessage({ type: 'success', text: 'Farm settings updated successfully!' });
    } catch (err) {
      console.error('Error updating farm:', err);
      setSaveMessage({ 
        type: 'error', 
        text: err.response?.data?.detail || 'Failed to update farm settings' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle farm switch
  const handleSwitchFarm = (farm) => {
    setCurrentFarm(farm);
    // Form will update via useEffect
  };

  // Get role display
  const getRoleDisplay = (role) => {
    const roleMap = {
      manager: 'Farm Manager',
      worker: 'Worker',
      superuser: 'Administrator',
    };
    return roleMap[role] || role || 'User';
  };

  return (
    <div className="p-4 lg:p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Settings</h1>
          <p className="text-sm text-gray-400">Manage your farm and account settings</p>
        </div>

        <div className="space-y-6">
          {/* Section 1: Farm Settings */}
          <section className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <FaSeedling className="text-[#1a5c38]" />
              Farm Settings
            </h2>

            {currentFarm ? (
              <form onSubmit={handleUpdateFarm}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Farm Name *</label>
                    <div className="relative">
                      <FiHome className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                      <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleFormChange}
                        required
                        className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38] focus:border-transparent"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                    <div className="relative">
                      <FiMapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                      <input
                        type="text"
                        name="location"
                        value={formData.location}
                        onChange={handleFormChange}
                        className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38] focus:border-transparent"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Area (feddans)</label>
                    <div className="relative">
                      <FiMaximize2 className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                      <input
                        type="number"
                        name="area"
                        value={formData.area}
                        onChange={handleFormChange}
                        min="0"
                        step="0.1"
                        className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38] focus:border-transparent"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Crop Type</label>
                    <div className="relative">
                      <FiPackage className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                      <input
                        type="text"
                        name="crop_type"
                        value={formData.crop_type}
                        onChange={handleFormChange}
                        placeholder="e.g., Wheat, Corn, Tomatoes"
                        className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38] focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>

                {/* Save Message */}
                {saveMessage && (
                  <div className={`mt-4 p-3 rounded-lg flex items-center gap-2 ${
                    saveMessage.type === 'success' 
                      ? 'bg-green-50 text-green-700 border border-green-200' 
                      : 'bg-red-50 text-red-700 border border-red-200'
                  }`}>
                    {saveMessage.type === 'success' ? (
                      <FiCheckCircle className="text-green-500" />
                    ) : (
                      <FiAlertCircle className="text-red-500" />
                    )}
                    {saveMessage.text}
                  </div>
                )}

                <div className="mt-4 flex justify-end">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="flex items-center gap-2 px-6 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <FiSave className={isLoading ? 'animate-spin' : ''} />
                    {isLoading ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </form>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No farm selected. Please select a farm from the list below.</p>
              </div>
            )}
          </section>

          {/* Section 2: Farm Selector */}
          <section className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <FiHome className="text-[#1a5c38]" />
              Switch Farm
            </h2>

            {farms.length === 0 ? (
              <p className="text-gray-500 text-sm">No farms available. Create a farm to get started.</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {farms.map((farm) => (
                  <button
                    key={farm.id}
                    onClick={() => handleSwitchFarm(farm)}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      currentFarm?.id === farm.id
                        ? 'border-[#1a5c38] bg-green-50'
                        : 'border-gray-200 hover:border-[#1a5c38] hover:bg-gray-50'
                    }`}
                  >
                    <div className="font-medium text-gray-800">{farm.name}</div>
                    <div className="text-sm text-gray-500">{farm.location || 'No location set'}</div>
                    {currentFarm?.id === farm.id && (
                      <div className="mt-1 text-xs text-[#1a5c38] font-medium">✓ Currently selected</div>
                    )}
                  </button>
                ))}
              </div>
            )}
          </section>

          {/* Section 3: Account Info */}
          <section className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <FiUser className="text-[#1a5c38]" />
              Account Information
            </h2>

            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <FiUser className="text-gray-400" />
                <div>
                  <div className="text-xs text-gray-400">Full Name</div>
                  <div className="font-medium text-gray-800">{user?.full_name || '—'}</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <FiMail className="text-gray-400" />
                <div>
                  <div className="text-xs text-gray-400">Email</div>
                  <div className="font-medium text-gray-800">{user?.email || '—'}</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <FiShield className="text-gray-400" />
                <div>
                  <div className="text-xs text-gray-400">Role</div>
                  <div className="font-medium text-gray-800">{getRoleDisplay(user?.role)}</div>
                </div>
              </div>
            </div>
          </section>

          {/* Section 4: App Info */}
          <section className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <FiInfo className="text-[#1a5c38]" />
              Application Information
            </h2>

            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between py-2 border-b border-gray-100">
                <span className="text-gray-500">Application</span>
                <span className="font-medium text-gray-800">CropMind</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-gray-100">
                <span className="text-gray-500">Version</span>
                <span className="font-medium text-gray-800">v1.0.0</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-gray-100">
                <span className="text-gray-500">Institution</span>
                <span className="font-medium text-gray-800">Military Technical College Cairo</span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-gray-500">Year</span>
                <span className="font-medium text-gray-800">2026</span>
              </div>
            </div>

            <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
              <p className="text-sm text-green-700">
                🌱 AI-Powered Farm Management System — Egypt Vision 2030
              </p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Settings;