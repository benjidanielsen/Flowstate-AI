import axios from 'axios';
import { Customer, Interaction, PipelineStatus, PipelineStats } from '../types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const customerApi = {
  getAll: async (status?: PipelineStatus): Promise<Customer[]> => {
    const params = status ? { status } : {};
    const response = await api.get('/customers', { params });
    return response.data;
  },

  getById: async (id: string): Promise<Customer> => {
    const response = await api.get(`/customers/${id}`);
    return response.data;
  },

  create: async (customerData: Omit<Customer, 'id' | 'created_at' | 'updated_at'>): Promise<Customer> => {
    const response = await api.post('/customers', customerData);
    return response.data;
  },

  update: async (id: string, updates: Partial<Customer>): Promise<Customer> => {
    const response = await api.put(`/customers/${id}`, updates);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/customers/${id}`);
  },

  moveToNextStage: async (id: string): Promise<Customer> => {
    const response = await api.post(`/customers/${id}/next-stage`);
    return response.data;
  },

  getStats: async (): Promise<PipelineStats> => {
    const response = await api.get('/customers/stats');
    return response.data;
  },
};

export const interactionApi = {
  getByCustomer: async (customerId: string): Promise<Interaction[]> => {
    const response = await api.get(`/interactions/customer/${customerId}`);
    return response.data;
  },

  create: async (interactionData: Omit<Interaction, 'id' | 'created_at'>): Promise<Interaction> => {
    const response = await api.post('/interactions', interactionData);
    return response.data;
  },

  update: async (id: string, updates: Partial<Interaction>): Promise<Interaction> => {
    const response = await api.put(`/interactions/${id}`, updates);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/interactions/${id}`);
  },

  getUpcoming: async (limit?: number): Promise<Interaction[]> => {
    const params = limit ? { limit } : {};
    const response = await api.get('/interactions/upcoming', { params });
    return response.data;
  },
};

export const healthApi = {
  check: async (): Promise<{ status: string; timestamp: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;