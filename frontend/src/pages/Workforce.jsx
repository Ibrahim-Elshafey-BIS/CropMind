import React, { useState, useEffect } from 'react';
import { FiPlus, FiEdit, FiTrash2, FiSearch, FiX, FiUsers, FiUser, FiUserCheck, FiUserX } from 'react-icons/fi';
import { FaSeedling } from 'react-icons/fa';
import useFarmStore from '../store/farmStore';
import { workforce as workforceApi } from '../services/api';

const Workforce = () => {
  const { currentFarm } = useFarmStore();
  const [workers, setWorkers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedWorker, setSelectedWorker] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    role: 'laborer',
    phone: '',
    daily_wage: '',
    is_active: true,
    hire_date: '',
    notes: '',
  });

  const farmId = currentFarm?.id;

  // Fetch workers
  const fetchWorkers = async () => {
    if (!farmId) {
      setWorkers([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await workforceApi.getWorkers({ farm_id: farmId });
      setWorkers(data || []);
    } catch (err) {
      console.error('Error fetching workers:', err);
      setError('Failed to load workers. Please refresh.');
      setWorkers([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkers();
  }, [farmId]);

  // Filter workers
  const filteredWorkers = workers.filter((worker) => {
    const matchesStatus =
      filterStatus === 'all' ||
      (filterStatus === 'active' && worker.is_active) ||
      (filterStatus === 'inactive' && !worker.is_active);
    const matchesSearch =
      worker.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      worker.role?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      worker.phone?.includes(searchTerm);
    return matchesStatus && matchesSearch;
  });

  // Summary stats
  const totalWorkers = workers.length;
  const activeWorkers = workers.filter((w) => w.is_active).length;

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-EG', {
      style: 'currency',
      currency: 'EGP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Get role display
  const getRoleDisplay = (role) => {
    const roleMap = {
      laborer: 'Laborer',
      supervisor: 'Supervisor',
      irrigation_specialist: 'Irrigation Specialist',
    };
    return roleMap[role] || role;
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      role: 'laborer',
      phone: '',
      daily_wage: '',
      is_active: true,
      hire_date: new Date().toISOString().split('T')[0],
      notes: '',
    });
    setSelectedWorker(null);
  };

  // Open create modal
  const openCreateModal = () => {
    resetForm();
    setIsModalOpen(true);
  };

  // Open edit modal
  const openEditModal = (worker) => {
    setSelectedWorker(worker);
    setFormData({
      name: worker.name || '',
      role: worker.role || 'laborer',
      phone: worker.phone || '',
      daily_wage: worker.daily_wage?.toString() || '',
      is_active: worker.is_active !== undefined ? worker.is_active : true,
      hire_date: worker.hire_date || new Date().toISOString().split('T')[0],
      notes: worker.notes || '',
    });
    setIsModalOpen(true);
  };

  // Open delete modal
  const openDeleteModal = (worker) => {
    setSelectedWorker(worker);
    setIsDeleteModalOpen(true);
  };

  // Handle form change
  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  // Handle submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const payload = {
        ...formData,
        farm_id: farmId,
        daily_wage: parseFloat(formData.daily_wage) || 0,
      };

      if (selectedWorker) {
        await workforceApi.updateWorker(selectedWorker.id, payload);
      } else {
        await workforceApi.createWorker(payload);
      }

      setIsModalOpen(false);
      resetForm();
      await fetchWorkers();
    } catch (err) {
      console.error('Error saving worker:', err);
      setError(err.response?.data?.detail || 'Failed to save worker');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    if (!selectedWorker) return;

    setIsLoading(true);
    setError(null);

    try {
      await workforceApi.deleteWorker(selectedWorker.id);
      setIsDeleteModalOpen(false);
      setSelectedWorker(null);
      await fetchWorkers();
    } catch (err) {
      console.error('Error deleting worker:', err);
      setError(err.response?.data?.detail || 'Failed to delete worker');
    } finally {
      setIsLoading(false);
    }
  };

  // Skeleton loader
  const SkeletonCard = () => (
    <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100 animate-pulse">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="h-5 bg-gray-200 rounded w-32 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-24"></div>
          <div className="mt-2 h-4 bg-gray-200 rounded w-20"></div>
        </div>
        <div className="h-6 bg-gray-200 rounded w-16"></div>
      </div>
      <div className="mt-3 flex items-center gap-4">
        <div className="h-4 bg-gray-200 rounded w-24"></div>
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
            <h1 className="text-2xl font-bold text-gray-800">Workforce</h1>
            <p className="text-sm text-gray-400">
              {farmId ? `Managing workforce for ${currentFarm?.name || 'Farm'}` : 'Select a farm to view workforce'}
            </p>
          </div>
          <button
            onClick={openCreateModal}
            disabled={!farmId || isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FiPlus />
            Add Worker
          </button>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
            <div className="flex items-center gap-2 text-[#1a5c38] mb-1">
              <FiUsers />
              <span className="text-sm font-medium">Total Workers</span>
            </div>
            <div className="text-2xl font-bold text-gray-800">
              {totalWorkers}
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
            <div className="flex items-center gap-2 text-green-600 mb-1">
              <FiUserCheck />
              <span className="text-sm font-medium">Active Workers</span>
            </div>
            <div className="text-2xl font-bold text-gray-800">
              {activeWorkers}
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-4 mb-6">
          <div className="flex gap-2 bg-white rounded-lg border border-gray-200 p-1">
            <button
              onClick={() => setFilterStatus('all')}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                filterStatus === 'all'
                  ? 'bg-[#1a5c38] text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterStatus('active')}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                filterStatus === 'active'
                  ? 'bg-green-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Active
            </button>
            <button
              onClick={() => setFilterStatus('inactive')}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                filterStatus === 'inactive'
                  ? 'bg-gray-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Inactive
            </button>
          </div>

          <div className="relative flex-1 max-w-sm">
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search by name, role, or phone..."
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

        {/* Workers Grid */}
        {isLoading && !workers.length ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        ) : filteredWorkers.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 border border-gray-100 text-center">
            <FiUsers className="text-6xl text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-600">No Workers Found</h3>
            <p className="text-sm text-gray-400 mt-1">
              {searchTerm ? 'Try a different search term' : 'Start by adding your first worker'}
            </p>
            {!searchTerm && filterStatus === 'all' && (
              <button
                onClick={openCreateModal}
                className="mt-4 px-4 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors"
              >
                <FiPlus className="inline mr-2" />
                Add Worker
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredWorkers.map((worker) => (
              <div
                key={worker.id}
                className="bg-white rounded-xl shadow-sm p-4 border border-gray-100 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-800">{worker.name}</h4>
                    <p className="text-sm text-gray-500">{getRoleDisplay(worker.role)}</p>
                  </div>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      worker.is_active
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-500'
                    }`}
                  >
                    {worker.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>

                <div className="mt-3 space-y-1 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400">Phone:</span>
                    <span className="text-gray-700">{worker.phone || '—'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400">Wage:</span>
                    <span className="font-medium text-[#1a5c38]">
                      {formatCurrency(worker.daily_wage)} / day
                    </span>
                  </div>
                  {worker.hire_date && (
                    <div className="flex items-center gap-2">
                      <span className="text-gray-400">Hired:</span>
                      <span className="text-gray-500">
                        {new Date(worker.hire_date).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>

                <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-end gap-2">
                  <button
                    onClick={() => openEditModal(worker)}
                    className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Edit"
                  >
                    <FiEdit />
                  </button>
                  <button
                    onClick={() => openDeleteModal(worker)}
                    className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <FiTrash2 />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-800">
                {selectedWorker ? 'Edit Worker' : 'Add New Worker'}
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                  <select
                    name="role"
                    value={formData.role}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  >
                    <option value="laborer">Laborer</option>
                    <option value="supervisor">Supervisor</option>
                    <option value="irrigation_specialist">Irrigation Specialist</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input
                    type="text"
                    name="phone"
                    value={formData.phone}
                    onChange={handleFormChange}
                    placeholder="e.g., +20 123 456 7890"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Daily Wage (EGP) *</label>
                  <input
                    type="number"
                    name="daily_wage"
                    value={formData.daily_wage}
                    onChange={handleFormChange}
                    min="0"
                    step="1"
                    required
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Hire Date</label>
                  <input
                    type="date"
                    name="hire_date"
                    value={formData.hire_date}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                  <textarea
                    name="notes"
                    value={formData.notes}
                    onChange={handleFormChange}
                    rows="2"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleFormChange}
                    className="w-4 h-4 text-[#1a5c38] rounded focus:ring-[#1a5c38]"
                  />
                  <label className="text-sm text-gray-700">Active Worker</label>
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
                  {isLoading ? 'Saving...' : selectedWorker ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Modal */}
      {isDeleteModalOpen && selectedWorker && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FiTrash2 className="text-2xl text-red-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">Delete Worker</h2>
              <p className="text-gray-600">
                Are you sure you want to delete <span className="font-semibold">{selectedWorker.name}</span>?
                This action cannot be undone.
              </p>
              <div className="flex justify-center gap-3 mt-6 pt-4 border-t border-gray-100">
                <button
                  onClick={() => { setIsDeleteModalOpen(false); setSelectedWorker(null); }}
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

export default Workforce;