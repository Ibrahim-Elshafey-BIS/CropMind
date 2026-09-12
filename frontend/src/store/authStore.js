import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { auth } from '../services/api';

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,

      login: async (email, password) => {
        set({ isLoading: true });
        try {
          const data = await auth.login(email, password);
          set({
            user: data.user,
            isAuthenticated: true,
            isLoading: false,
          });
          return { success: true, data };
        } catch (error) {
          set({ isLoading: false });
          return {
            success: false,
            error: error.response?.data?.detail || 'Login failed',
          };
        }
      },

      logout: () => {
        auth.logout();
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },

      checkAuth: () => {
        const token = localStorage.getItem('access_token');
        const user = auth.getCurrentUser();
        
        if (token && user) {
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } else {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      // Reset store (used for testing or hard logout)
      reset: () => {
        auth.logout();
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;
