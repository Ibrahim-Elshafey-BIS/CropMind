import React, { useState, useEffect } from 'react';
import { FiPlus, FiEdit, FiTrash2, FiSearch, FiX, FiTrendingUp, FiTrendingDown, FiDollarSign } from 'react-icons/fi';
import useFarmStore from '../store/farmStore';
import { finance as financeApi } from '../services/api';

const Finance = () => {
  const { currentFarm } = useFarmStore();
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    type: 'income',
    amount: '',
    category: '',
    description: '',
    date: '',
  });

  const farmId = currentFarm?.id;

  // Fetch transactions and summary
  const fetchData = async () => {
    if (!farmId) {
      setTransactions([]);
      setSummary(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const params = { farm_id: farmId };
      if (filterType !== 'all') {
        params.type = filterType;
      }

      const [transactionsData, summaryData] = await Promise.all([
        financeApi.getTransactions(params),
        financeApi.getFinanceSummary(farmId),
      ]);

      setTransactions(transactionsData || []);
      setSummary(summaryData);
    } catch (err) {
      console.error('Error fetching finance data:', err);
      setError('Failed to load finance data. Please refresh.');
      setTransactions([]);
      setSummary(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [farmId, filterType]);

  // Filter transactions by search
  const filteredTransactions = transactions.filter((t) =>
    t.category?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
      type: 'income',
      amount: '',
      category: '',
      description: '',
      date: new Date().toISOString().split('T')[0],
    });
    setSelectedTransaction(null);
  };

  // Open create modal
  const openCreateModal = () => {
    resetForm();
    setIsModalOpen(true);
  };

  // Open edit modal
  const openEditModal = (transaction) => {
    setSelectedTransaction(transaction);
    setFormData({
      type: transaction.type,
      amount: transaction.amount.toString(),
      category: transaction.category,
      description: transaction.description || '',
      date: transaction.date,
    });
    setIsModalOpen(true);
  };

  // Open delete modal
  const openDeleteModal = (transaction) => {
    setSelectedTransaction(transaction);
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
        amount: parseFloat(formData.amount),
        date: formData.date,
      };

      if (selectedTransaction) {
        await financeApi.updateTransaction(selectedTransaction.id, payload);
      } else {
        await financeApi.createTransaction(payload);
      }

      setIsModalOpen(false);
      resetForm();
      await fetchData();
    } catch (err) {
      console.error('Error saving transaction:', err);
      setError(err.response?.data?.detail || 'Failed to save transaction');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    if (!selectedTransaction) return;

    setIsLoading(true);
    setError(null);

    try {
      await financeApi.deleteTransaction(selectedTransaction.id);
      setIsDeleteModalOpen(false);
      setSelectedTransaction(null);
      await fetchData();
    } catch (err) {
      console.error('Error deleting transaction:', err);
      setError(err.response?.data?.detail || 'Failed to delete transaction');
    } finally {
      setIsLoading(false);
    }
  };

  // Skeleton loader
  const SkeletonRow = () => (
    <div className="p-4 border-b border-gray-100 animate-pulse">
      <div className="flex items-center gap-4">
        <div className="h-8 w-16 bg-gray-200 rounded"></div>
        <div className="flex-1">
          <div className="h-4 bg-gray-200 rounded w-32 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-24"></div>
        </div>
        <div className="h-4 bg-gray-200 rounded w-24"></div>
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
            <h1 className="text-2xl font-bold text-gray-800">Finance</h1>
            <p className="text-sm text-gray-400">
              {farmId ? `Managing finances for ${currentFarm?.name || 'Farm'}` : 'Select a farm to view finances'}
            </p>
          </div>
          <button
            onClick={openCreateModal}
            disabled={!farmId || isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FiPlus />
            Add Transaction
          </button>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
              <div className="flex items-center gap-2 text-green-600 mb-1">
                <FiTrendingUp />
                <span className="text-sm font-medium">Total Income</span>
              </div>
              <div className="text-2xl font-bold text-gray-800">
                {formatCurrency(summary.total_income || 0)}
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
              <div className="flex items-center gap-2 text-red-600 mb-1">
                <FiTrendingDown />
                <span className="text-sm font-medium">Total Expense</span>
              </div>
              <div className="text-2xl font-bold text-gray-800">
                {formatCurrency(summary.total_expense || 0)}
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
              <div className="flex items-center gap-2 text-[#1a5c38] mb-1">
                <FiDollarSign />
                <span className="text-sm font-medium">Net Profit</span>
              </div>
              <div className={`text-2xl font-bold ${(summary.net_profit || 0) >= 0 ? 'text-[#1a5c38]' : 'text-red-600'}`}>
                {formatCurrency(summary.net_profit || 0)}
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-4 mb-6">
          <div className="flex gap-2 bg-white rounded-lg border border-gray-200 p-1">
            <button
              onClick={() => setFilterType('all')}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                filterType === 'all'
                  ? 'bg-[#1a5c38] text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterType('income')}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                filterType === 'income'
                  ? 'bg-green-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Income
            </button>
            <button
              onClick={() => setFilterType('expense')}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                filterType === 'expense'
                  ? 'bg-red-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Expense
            </button>
          </div>

          <div className="relative flex-1 max-w-sm">
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search by category or description..."
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

        {/* Transactions Table */}
        {isLoading && !transactions.length ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            {[1, 2, 3, 4, 5].map((i) => (
              <SkeletonRow key={i} />
            ))}
          </div>
        ) : filteredTransactions.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 border border-gray-100 text-center">
            <FiDollarSign className="text-6xl text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-600">No Transactions Found</h3>
            <p className="text-sm text-gray-400 mt-1">
              {searchTerm ? 'Try a different search term' : 'Start by adding your first transaction'}
            </p>
            {!searchTerm && (
              <button
                onClick={openCreateModal}
                className="mt-4 px-4 py-2 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors"
              >
                <FiPlus className="inline mr-2" />
                Add Transaction
              </button>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filteredTransactions.map((t) => (
                    <tr key={t.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          t.type === 'income' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                        }`}>
                          {t.type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-600">{t.category}</td>
                      <td className={`px-4 py-3 font-semibold ${t.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(t.amount)}
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {t.date ? new Date(t.date).toLocaleDateString() : '—'}
                      </td>
                      <td className="px-4 py-3 text-gray-600 max-w-xs truncate">
                        {t.description || '—'}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => openEditModal(t)}
                            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Edit"
                          >
                            <FiEdit />
                          </button>
                          <button
                            onClick={() => openDeleteModal(t)}
                            className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete"
                          >
                            <FiTrash2 />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
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
                {selectedTransaction ? 'Edit Transaction' : 'Add Transaction'}
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                  <select
                    name="type"
                    value={formData.type}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  >
                    <option value="income">Income</option>
                    <option value="expense">Expense</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Amount *</label>
                  <input
                    type="number"
                    name="amount"
                    value={formData.amount}
                    onChange={handleFormChange}
                    min="0.01"
                    step="0.01"
                    required
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category *</label>
                  <input
                    type="text"
                    name="category"
                    value={formData.category}
                    onChange={handleFormChange}
                    required
                    placeholder="e.g., Seeds, Labor, Sales"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                  <input
                    type="date"
                    name="date"
                    value={formData.date}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <input
                    type="text"
                    name="description"
                    value={formData.description}
                    onChange={handleFormChange}
                    placeholder="Optional description"
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
                  {isLoading ? 'Saving...' : selectedTransaction ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Modal */}
      {isDeleteModalOpen && selectedTransaction && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FiTrash2 className="text-2xl text-red-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">Delete Transaction</h2>
              <p className="text-gray-600">
                Are you sure you want to delete this transaction?
                This action cannot be undone.
              </p>
              <div className="flex justify-center gap-3 mt-6 pt-4 border-t border-gray-100">
                <button
                  onClick={() => { setIsDeleteModalOpen(false); setSelectedTransaction(null); }}
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

export default Finance;