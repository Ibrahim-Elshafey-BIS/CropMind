import React, { useState, useEffect } from 'react';
import { FiPlus, FiEdit, FiTrash2, FiSearch, FiX, FiPackage, FiAlertTriangle } from 'react-icons/fi';
import { FaSeedling } from 'react-icons/fa';
import useFarmStore from '../store/farmStore';
import { inventory as inventoryApi } from '../services/api';

const Inventory = () => {
  const { currentFarm } = useFarmStore();
  const [items, setItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    category: 'other',
    quantity: '',
    min_quantity: '',
    unit: 'piece',
    price_per_unit: '',
    notes: '',
  });

  const farmId = currentFarm?.id;

  // Fetch inventory items
  const fetchItems = async () => {
    if (!farmId) {
      setItems([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await inventoryApi.getInventory({ farm_id: farmId });
      setItems(data || []);
    } catch (err) {
      console.error('Error fetching inventory:', err);
      setError('Failed to load inventory. Please refresh.');
      setItems([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, [farmId]);

  // Categories
  const categories = ['All', 'Seeds', 'Fertilizer', 'Pesticide', 'Equipment', 'Other'];

  // Filter items
  const filteredItems = items.filter((item) => {
    const matchesCategory = categoryFilter === 'All' || item.category === categoryFilter.toLowerCase();
    const matchesSearch =
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.category.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  // Get category display name
  const getCategoryDisplay = (cat) => {
    return cat.charAt(0).toUpperCase() + cat.slice(1);
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-EG', {
      style: 'currency',
      currency: 'EGP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      category: 'other',
      quantity: '',
      min_quantity: '',
      unit: 'piece',
      price_per_unit: '',
      notes: '',
    });
    setSelectedItem(null);
  };

  // Open create modal
  const openCreateModal = () => {
    resetForm();
    setIsModalOpen(true);
  };

  // Open edit modal
  const openEditModal = (item) => {
    setSelectedItem(item);
    setFormData({
      name: item.name || '',
      category: item.category || 'other',
      quantity: item.quantity?.toString() || '',
      min_quantity: item.min_quantity?.toString() || '',
      unit: item.unit || 'piece',
      price_per_unit: item.price_per_unit?.toString() || '',
      notes: item.notes || '',
    });
    setIsModalOpen(true);
  };

  // Open delete modal
  const openDeleteModal = (item) => {
    setSelectedItem(item);
    setIsDeleteModalOpen(true);
  };

  // Handle form change
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
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
        quantity: parseFloat(formData.quantity) || 0,
        min_quantity: parseFloat(formData.min_quantity) || 0,
        price_per_unit: parseFloat(formData.price_per_unit) || 0,
      };

      if (selectedItem) {
        await inventoryApi.updateInventoryItem(selectedItem.id, payload);
      } else {
        await inventoryApi.createInventoryItem(payload);
      }

      setIsModalOpen(false);
      resetForm();
      await fetchItems();
    } catch (err) {
      console.error('Error saving item:', err);
      setError(err.response?.data?.detail || 'Failed to save item');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    if (!selectedItem) return;

    setIsLoading(true);
    setError(null);

    try {
      await inventoryApi.deleteInventoryItem(selectedItem.id);
      setIsDeleteModalOpen(false);
      setSelectedItem(null);
      await fetchItems();
    } catch (err) {
      console.error('Error deleting item:', err);
      setError(err.response?.data?.detail || 'Failed to delete item');
    } finally {
      setIsLoading(false);
    }
  };

  // Skeleton loader
  const SkeletonItem = () => (
    <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100 animate-pulse">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="h-5 bg-gray-200 rounded w-32 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-24"></div>
        </div>
        <div className="h-6 bg-gray-200 rounded w-16"></div>
      </div>
      <div className="mt-3 flex items-center gap-4">
        <div className="h-4 bg-gray-200 rounded w-20"></div>
        <div className="h-4 bg-gray-200 rounded w-24"></div>
      </div>
      <div className="mt-2 flex items-center gap-4">
        <div className="h-4 bg-gray-200 rounded w-16"></div>
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
            <h1 className="text-2xl font-bold text-gray-800">Inventory</h1>
            <p className="text-sm text-gray-400">
              {farmId ? `Managing inventory for ${currentFarm?.name || 'Farm'}` : 'Select a farm to view inventory'}
            </p>
          </div>
          <button
            onClick={openCreateModal}
            disabled={!farmId || isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FiPlus />
            Add Item
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-4 mb-6">
          <div className="flex flex-wrap gap-2 bg-white rounded-lg border border-gray-200 p-1">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setCategoryFilter(cat)}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  categoryFilter === cat
                    ? cat === 'All' ? 'bg-[#1a5c38] text-white' : 'bg-[#1a5c38] text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="relative flex-1 max-w-sm">
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search by name or category..."
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

        {/* Items Grid */}
        {isLoading && !items.length ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <SkeletonItem key={i} />
            ))}
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 border border-gray-100 text-center">
            <FiPackage className="text-6xl text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-600">No Items Found</h3>
            <p className="text-sm text-gray-400 mt-1">
              {searchTerm ? 'Try a different search term' : 'Start by adding your first inventory item'}
            </p>
            {!searchTerm && categoryFilter === 'All' && (
              <button
                onClick={openCreateModal}
                className="mt-4 px-4 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors"
              >
                <FiPlus className="inline mr-2" />
                Add Item
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredItems.map((item) => {
              const isLowStock = item.quantity < item.min_quantity;
              return (
                <div
                  key={item.id}
                  className="bg-white rounded-xl shadow-sm p-4 border border-gray-100 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-800">{item.name}</h4>
                      <p className="text-xs text-gray-400">{getCategoryDisplay(item.category)}</p>
                    </div>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        isLowStock
                          ? 'bg-red-100 text-red-700'
                          : 'bg-green-100 text-green-700'
                      }`}
                    >
                      {isLowStock ? (
                        <span className="flex items-center gap-1">
                          <FiAlertTriangle className="text-xs" />
                          Low
                        </span>
                      ) : (
                        'OK'
                      )}
                    </span>
                  </div>

                  <div className="mt-3 flex flex-wrap items-center gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Qty:</span>
                      <span className="ml-1 font-medium text-gray-700">
                        {item.quantity} {item.unit}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-400">Min:</span>
                      <span className="ml-1 text-gray-600">
                        {item.min_quantity} {item.unit}
                      </span>
                    </div>
                  </div>

                  <div className="mt-1 flex flex-wrap items-center gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Price:</span>
                      <span className="ml-1 font-medium text-[#1a5c38]">
                        {formatCurrency(item.price_per_unit)} / {item.unit}
                      </span>
                    </div>
                  </div>

                  <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-end gap-2">
                    <button
                      onClick={() => openEditModal(item)}
                      className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="Edit"
                    >
                      <FiEdit />
                    </button>
                    <button
                      onClick={() => openDeleteModal(item)}
                      className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Delete"
                    >
                      <FiTrash2 />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-800">
                {selectedItem ? 'Edit Item' : 'Add New Item'}
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">Item Name *</label>
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select
                    name="category"
                    value={formData.category}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  >
                    <option value="seeds">Seeds</option>
                    <option value="fertilizer">Fertilizer</option>
                    <option value="pesticide">Pesticide</option>
                    <option value="equipment">Equipment</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Quantity *</label>
                  <input
                    type="number"
                    name="quantity"
                    value={formData.quantity}
                    onChange={handleFormChange}
                    min="0"
                    step="0.01"
                    required
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Minimum Quantity</label>
                  <input
                    type="number"
                    name="min_quantity"
                    value={formData.min_quantity}
                    onChange={handleFormChange}
                    min="0"
                    step="0.01"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Unit</label>
                  <select
                    name="unit"
                    value={formData.unit}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  >
                    <option value="piece">Piece</option>
                    <option value="kg">Kilogram (kg)</option>
                    <option value="g">Gram (g)</option>
                    <option value="liter">Liter (L)</option>
                    <option value="ml">Milliliter (mL)</option>
                    <option value="box">Box</option>
                    <option value="bag">Bag</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Price per Unit</label>
                  <input
                    type="number"
                    name="price_per_unit"
                    value={formData.price_per_unit}
                    onChange={handleFormChange}
                    min="0"
                    step="0.01"
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
                  {isLoading ? 'Saving...' : selectedItem ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Modal */}
      {isDeleteModalOpen && selectedItem && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FiTrash2 className="text-2xl text-red-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">Delete Item</h2>
              <p className="text-gray-600">
                Are you sure you want to delete <span className="font-semibold">{selectedItem.name}</span>?
                This action cannot be undone.
              </p>
              <div className="flex justify-center gap-3 mt-6 pt-4 border-t border-gray-100">
                <button
                  onClick={() => { setIsDeleteModalOpen(false); setSelectedItem(null); }}
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

export default Inventory;