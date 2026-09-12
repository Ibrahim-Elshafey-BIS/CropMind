import React, { useState, useEffect } from 'react';
import { FiPlus, FiEdit, FiTrash2, FiSearch, FiX } from 'react-icons/fi';
import { FaSeedling } from 'react-icons/fa';
import useFarmStore from '../store/farmStore';
import { crops as cropsApi } from '../services/api';

const Crops = () => {
  const { currentFarm } = useFarmStore();
  const [crops, setCrops] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    variety: '',
    area: 1,
    planting_date: '',
    expected_harvest_date: '',
    status: 'growing',
  });

  const farmId = currentFarm?.id;

  // Fetch crops
  const fetchCrops = async () => {
    if (!farmId) {
      setCrops([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await cropsApi.getCrops({ farm_id: farmId });
      setCrops(data || []);
    } catch (err) {
      console.error('Error fetching crops:', err);
      setError('Failed to load crops. Please refresh.');
      setCrops([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCrops();
  }, [farmId]);

  // Filter crops by search
  const filteredCrops = crops.filter((crop) =>
    crop.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    crop.variety?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Get status badge
  const getStatusBadge = (status) => {
    const statusMap = {
      growing: { color: 'bg-green-100 text-green-700', label: 'Growing' },
      harvested: { color: 'bg-gray-100 text-gray-700', label: 'Harvested' },
      failed: { color: 'bg-red-100 text-red-700', label: 'Failed' },
    };
    return statusMap[status] || { color: 'bg-gray-100 text-gray-700', label: status };
  };

  // Get health score color
  const getHealthColor = (score) => {
    if (score === null || score === undefined) return 'text-gray-400';
    if (score >= 70) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Handle form change
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      variety: '',
      area: 1,
      planting_date: '',
      expected_harvest_date: '',
      status: 'growing',
    });
    setSelectedCrop(null);
  };

  // Open create modal
  const openCreateModal = () => {
    resetForm();
    setIsModalOpen(true);
  };

  // Open edit modal
  const openEditModal = (crop) => {
    setSelectedCrop(crop);
    setFormData({
      name: crop.name || '',
      variety: crop.variety || '',
      area: crop.area || 1,
      planting_date: crop.planting_date || '',
      expected_harvest_date: crop.expected_harvest_date || '',
      status: crop.status || 'growing',
    });
    setIsModalOpen(true);
  };

  // Open delete modal
  const openDeleteModal = (crop) => {
    setSelectedCrop(crop);
    setIsDeleteModalOpen(true);
  };

  // Handle create/update crop
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const payload = {
        ...formData,
        farm_id: farmId,
        area: parseFloat(formData.area),
      };

      if (selectedCrop) {
        // Update
        await cropsApi.updateCrop(selectedCrop.id, payload);
      } else {
        // Create
        await cropsApi.createCrop(payload);
      }

      setIsModalOpen(false);
      resetForm();
      await fetchCrops();
    } catch (err) {
      console.error('Error saving crop:', err);
      setError(err.response?.data?.detail || 'Failed to save crop');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    if (!selectedCrop) return;

    setIsLoading(true);
    setError(null);

    try {
      await cropsApi.deleteCrop(selectedCrop.id);
      setIsDeleteModalOpen(false);
      setSelectedCrop(null);
      await fetchCrops();
    } catch (err) {
      console.error('Error deleting crop:', err);
      setError(err.response?.data?.detail || 'Failed to delete crop');
    } finally {
      setIsLoading(false);
    }
  };

  // Skeleton loader
  const SkeletonRow = () => (
    <div className="p-4 border-b border-gray-100 animate-pulse">
      <div className="flex items-center gap-4">
        <div className="h-10 w-10 bg-gray-200 rounded-lg"></div>
        <div className="flex-1">
          <div className="h-4 bg-gray-200 rounded w-32 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-24"></div>
        </div>
        <div className="h-6 bg-gray-200 rounded w-20"></div>
        <div className="h-4 bg-gray-200 rounded w-16"></div>
        <div className="h-4 bg-gray-200 rounded w-16"></div>
        <div className="flex gap-2">
          <div className="h-8 w-8 bg-gray-200 rounded"></div>
          <div className="h-8 w-8 bg-gray-200 rounded"></div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-4 lg:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Crops</h1>
            <p className="text-sm text-gray-400">
              {farmId ? `Managing crops for ${currentFarm?.name || 'Farm'}` : 'Select a farm to view crops'}
            </p>
          </div>
          <button
            onClick={openCreateModal}
            disabled={!farmId || isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FiPlus />
            Add Crop
          </button>
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="relative max-w-md">
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search crops..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38] focus:border-transparent"
            />
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Crops List */}
        {isLoading && !crops.length ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            {[1, 2, 3, 4, 5].map((i) => (
              <SkeletonRow key={i} />
            ))}
          </div>
        ) : filteredCrops.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 border border-gray-100 text-center">
            <FaSeedling className="text-6xl text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-600">No Crops Found</h3>
            <p className="text-sm text-gray-400 mt-1">
              {searchTerm ? 'Try a different search term' : 'Start by adding your first crop'}
            </p>
            {!searchTerm && (
              <button
                onClick={openCreateModal}
                className="mt-4 px-4 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors"
              >
                <FiPlus className="inline mr-2" />
                Add Crop
              </button>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Crop</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Variety</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Planting Date</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Harvest Date</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Health</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filteredCrops.map((crop) => {
                    const status = getStatusBadge(crop.status);
                    return (
                      <tr key={crop.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <FaSeedling className="text-[#1a5c38]" />
                            <span className="font-medium text-gray-800">{crop.name}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-gray-600">{crop.variety || '—'}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.color}`}>
                            {status.label}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {crop.planting_date ? new Date(crop.planting_date).toLocaleDateString() : '—'}
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {crop.expected_harvest_date ? new Date(crop.expected_harvest_date).toLocaleDateString() : '—'}
                        </td>
                        <td className="px-4 py-3">
                          {crop.health_score !== null && crop.health_score !== undefined ? (
                            <span className={`font-semibold ${getHealthColor(crop.health_score)}`}>
                              {crop.health_score.toFixed(1)}%
                            </span>
                          ) : (
                            <span className="text-gray-400">—</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => openEditModal(crop)}
                            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                              title="Edit"
                            >
                              <FiEdit />
                            </button>
                            <button
                              onClick={() => openDeleteModal(crop)}
                            className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              title="Delete"
                            >
                              <FiTrash2 />
                            </button>
                          </div>
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

      {/* Create/Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-800">
                {selectedCrop ? 'Edit Crop' : 'Add New Crop'}
              </h2>
              <button
                onClick={() => { setIsModalOpen(false); resetForm(); }}
                className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <FiX className="text-gray-500" />
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Crop Name *</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleFormChange}
                    required
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Variety</label>
                  <input
                    type="text"
                    name="variety"
                    value={formData.variety}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Area (feddans) *</label>
                  <input
                    type="number"
                    name="area"
                    value={formData.area}
                    onChange={handleFormChange}
                    min="0.1"
                    step="0.1"
                    required
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Planting Date *</label>
                  <input
                    type="date"
                    name="planting_date"
                    value={formData.planting_date}
                    onChange={handleFormChange}
                    required
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Expected Harvest Date</label>
                  <input
                    type="date"
                    name="expected_harvest_date"
                    value={formData.expected_harvest_date}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  >
                    <option value="growing">Growing</option>
                    <option value="harvested">Harvested</option>
                    <option value="failed">Failed</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => { setIsModalOpen(false); resetForm(); }}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="px-4 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors disabled:opacity-50"
                >
                  {isLoading ? 'Saving...' : selectedCrop ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Modal */}
      {isDeleteModalOpen && selectedCrop && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FiTrash2 className="text-2xl text-red-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">Delete Crop</h2>
              <p className="text-gray-600">
                Are you sure you want to delete <span className="font-semibold">{selectedCrop.name}</span>?
                This action cannot be undone.
              </p>
              <div className="flex justify-center gap-3 mt-6 pt-4 border-t border-gray-100">
                <button
                  onClick={() => { setIsDeleteModalOpen(false); setSelectedCrop(null); }}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
                  disabled={isLoading}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                >
                  {isLoading ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Crops;