import { create } from 'zustand';
import { agents } from '../services/api';

const useAgentStore = create((set, get) => ({
  messages: [],
  isTyping: false,
  agentsStatus: null,
  farmAnalysis: null,
  marketIntel: null,
  isLoading: false,
  error: null,

  sendMessage: async (message, farmId, conversationId = null) => {
    if (!message.trim()) return;
    
    // Fallback to farm 1 if no farmId
    const effectiveFarmId = farmId || 1;

    // Add user message to history
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, userMessage],
      isTyping: true,
      error: null,
    }));

    try {
      const response = await agents.chatCopilot(message, effectiveFarmId, conversationId);

      const botMessage = {
        role: 'assistant',
        content: typeof response.response === 'string' 
          ? response.response 
          : JSON.stringify(response.response),
        timestamp: response.timestamp || new Date().toISOString(),
        conversationId: response.conversation_id,
        suggestions: response.suggestions || [],
      };

      set((state) => ({
        messages: [...state.messages, botMessage],
        isTyping: false,
      }));

      return { success: true, data: response };
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to send message';
      set({
        isTyping: false,
        error: errorMsg,
      });

      // Add error message to chat
      const errorMessage = {
        role: 'assistant',
        content: `⚠️ ${errorMsg}`,
        timestamp: new Date().toISOString(),
        isError: true,
      };
      set((state) => ({
        messages: [...state.messages, errorMessage],
      }));

      return {
        success: false,
        error: errorMsg,
      };
    }
  },

  clearMessages: () => {
    set({ messages: [] });
  },

  fetchAgentsStatus: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await agents.getAgentsStatus();
      set({
        agentsStatus: data,
        isLoading: false,
      });
      return { success: true, data };
    } catch (error) {
      set({
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to fetch agents status',
      });
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to fetch agents status',
      };
    }
  },

  analyzeFarm: async (farmId) => {
    set({ isLoading: true, error: null });
    try {
      const data = await agents.analyzeFarm(farmId);
      set({
        farmAnalysis: data.data,
        isLoading: false,
      });
      return { success: true, data };
    } catch (error) {
      set({
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to analyze farm',
      });
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to analyze farm',
      };
    }
  },

  getMarketIntel: async (farmId) => {
    set({ isLoading: true, error: null });
    try {
      const data = await agents.getMarketIntel(farmId);
      set({
        marketIntel: data.data,
        isLoading: false,
      });
      return { success: true, data };
    } catch (error) {
      set({
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to get market intelligence',
      });
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to get market intelligence',
      };
    }
  },

  optimizeResources: async (farmId) => {
    set({ isLoading: true, error: null });
    try {
      const data = await agents.optimizeResources(farmId);
      set({
        isLoading: false,
      });
      return { success: true, data };
    } catch (error) {
      set({
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to optimize resources',
      });
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to optimize resources',
      };
    }
  },

  // Reset store
  reset: () => {
    set({
      messages: [],
      isTyping: false,
      agentsStatus: null,
      farmAnalysis: null,
      marketIntel: null,
      isLoading: false,
      error: null,
    });
  },
}));

export default useAgentStore;