import { create } from 'zustand';
import { farms } from '../services/api';

const useFarmStore = create((set, get) => ({
  farms: [],
  currentFarm: null,
  isLoading: false,
  error: null,

  fetchFarms: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await farms.getFarms();
      set({
        farms: data,
        isLoading: false,
        // If no current farm is selected but we have farms, select the first one
        currentFarm: get().currentFarm === null && data.length > 0 ? data[0] : get().currentFarm,
      });
      return { success: true, data };
    } catch (error) {
      set({
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to fetch farms',
      });
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to fetch farms',
      };
    }
  },

  setCurrentFarm: (farm) => {
    set({ currentFarm: farm });
    // Update URL or persist if needed
    if (farm) {
      localStorage.setItem('currentFarmId', String(farm.id));
    } else {
      localStorage.removeItem('currentFarmId');
    }
  },

  // Load current farm from localStorage on app init
  loadCurrentFarm: () => {
    const farmId = localStorage.getItem('currentFarmId');
    const { farms } = get();
    if (farmId && farms.length > 0) {
      const farm = farms.find((f) => String(f.id) === farmId);
      if (farm) {
        set({ currentFarm: farm });
        return farm;
      }
    }
    if (farms.length > 0) {
      set({ currentFarm: farms[0] });
      return farms[0];
    }
    return null;
  },

  createFarm: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const newFarm = await farms.createFarm(data);
      set((state) => ({
        farms: [...state.farms, newFarm],
        currentFarm: state.currentFarm || newFarm,
        isLoading: false,
      }));
      return { success: true, data: newFarm };
    } catch (error) {
      set({
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to create farm',
      });
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to create farm',
      };
    }
  },

  updateFarm: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const updatedFarm = await farms.updateFarm(id, data);
      set((state) => ({
        farms: state.farms.map((farm) =>
          farm.id === id ? updatedFarm : farm
        ),
        currentFarm: state.currentFarm?.id === id ? updatedFarm : state.currentFarm,
        isLoading: false,
      }));
      return { success: true, data: updatedFarm };
    } catch (error) {
      set({
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to update farm',
      });
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to update farm',
      };
    }
  },

  deleteFarm: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await farms.deleteFarm(id);
      set((state) => {
        const newFarms = state.farms.filter((farm) => farm.id !== id);
        const newCurrentFarm =
          state.currentFarm?.id === id
            ? newFarms.length > 0
              ? newFarms[0]
              : null
            : state.currentFarm;
        return {
          farms: newFarms,
          currentFarm: newCurrentFarm,
          isLoading: false,
        };
      });
      return { success: true };
    } catch (error) {
      set({
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to delete farm',
      });
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to delete farm',
      };
    }
  },

  // Reset store
  reset: () => {
    set({
      farms: [],
      currentFarm: null,
      isLoading: false,
      error: null,
    });
    localStorage.removeItem('currentFarmId');
  },
}));

export default useFarmStore;
