import type { AxiosRequestConfig } from 'axios';
import axiosInstance from '../api/axiosInstance';
import { Customer, Interaction, PipelineStatus, Reminder, EventLog, PipelineStats, Stats } from '../types';

type HttpMethod = 'get' | 'post' | 'put' | 'patch' | 'delete';

const request = async <T>(
  method: HttpMethod,
  url: string,
  payload?: unknown,
  config?: AxiosRequestConfig
): Promise<T> => {
  switch (method) {
    case 'get':
    case 'delete': {
      const response = await axiosInstance[method]<T>(url, config);
      return response.data;
    }
    case 'post':
    case 'put':
    case 'patch': {
      const response = await axiosInstance[method]<T>(url, payload, config);
      return response.data;
    }
    default:
      throw new Error(`Unsupported HTTP method: ${method satisfies never}`);
  }
};

// Customer API
export const aiDecisionLogApi = {
  getAIDecisionLogs: async () => {
    const response = await axiosInstance.get('/ai/decision-logs');
    return response.data;
  },
  updateDecisionStatus: async (id: number, newStatus: string, humanReviewer?: string) => {
    const response = await axiosInstance.put(`/ai/decision-logs/${id}/status`, { newStatus, humanReviewer });
    return response.data;
  },
};

export const customerApi = {
  getAll: async (filters?: { 
    status?: PipelineStatus; 
    search?: string; 
    source?: string; 
    country?: string; 
    language?: string; 
    next_action?: string; 
    sortBy?: string; 
    sortOrder?: 'ASC' | 'DESC'; 
  }): Promise<Customer[]> => {
    const response = await axiosInstance.get('/customers', { params: filters });
    return response.data;
  },
  getById: async (id: string): Promise<Customer> => {
    const response = await axiosInstance.get(`/customers/${id}`);
    return response.data;
  },
  create: async (customerData: Omit<Customer, 'id' | 'created_at' | 'updated_at'>): Promise<Customer> => {
    const response = await axiosInstance.post('/customers', customerData);
    return response.data;
  },
  update: async (id: string, updates: Partial<Customer>): Promise<Customer> => {
    const response = await axiosInstance.put(`/customers/${id}`, updates);
    return response.data;
  },
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/customers/${id}`);
  },
  moveToNextStage: async (id: string): Promise<Customer> => {
    const response = await axiosInstance.post(`/customers/${id}/move-next-stage`);
    return response.data;
  },
  getStats: async (): Promise<PipelineStats> => {
    const response = await axiosInstance.get('/customers/stats');
    return response.data;
  },
};

// Interaction API
export const interactionApi = {
  getAll: async (customerId: string): Promise<Interaction[]> => {
    const response = await axiosInstance.get(`/customers/${customerId}/interactions`);
    return response.data;
  },
  create: async (customerId: string, interactionData: Omit<Interaction, 'id' | 'created_at'>): Promise<Interaction> => {
    const response = await axiosInstance.post(`/customers/${customerId}/interactions`, interactionData);
    return response.data;
  },
  update: async (customerId: string, id: string, updates: Partial<Interaction>): Promise<Interaction> => {
    const response = await axiosInstance.put(`/customers/${customerId}/interactions/${id}`, updates);
    return response.data;
  },
  delete: async (customerId: string, id: string): Promise<void> => {
    await axiosInstance.delete(`/customers/${customerId}/interactions/${id}`);
  },
  getUpcoming: async (limit: number = 5): Promise<Interaction[]> => {
    const response = await axiosInstance.get(`/interactions/upcoming?limit=${limit}`);
    return response.data;
  },
  complete: async (id: string): Promise<Interaction> => {
    const response = await axiosInstance.post(`/interactions/${id}/complete`);
    return response.data;
  },
};

// Reminder API
export const reminderApi = {
  getAll: async (customerId: string): Promise<Reminder[]> => {
    const response = await axiosInstance.get(`/customers/${customerId}/reminders`);
    return response.data;
  },
  create: async (customerId: string, reminderData: Omit<Reminder, 'id' | 'created_at'>): Promise<Reminder> => {
    const response = await axiosInstance.post(`/customers/${customerId}/reminders`, reminderData);
    return response.data;
  },
  update: async (customerId: string, id: string, updates: Partial<Reminder>): Promise<Reminder> => {
    const response = await axiosInstance.put(`/customers/${customerId}/reminders/${id}`, updates);
    return response.data;
  },
  delete: async (customerId: string, id: string): Promise<void> => {
    await axiosInstance.delete(`/customers/${customerId}/reminders/${id}`);
  },
};

// EventLog API
export const eventLogApi = {
  getAll: async (customerId: string): Promise<EventLog[]> => {
    const response = await axiosInstance.get(`/customers/${customerId}/event-logs`);
    return response.data;
  },
};

// Stats API
export const statsApi = {
  getStats: async (): Promise<Stats> => {
    const response = await axiosInstance.get('/stats');
    return response.data;
  },
  getPipelineStats: async (): Promise<PipelineStats> => {
    const response = await axiosInstance.get('/stats/pipeline');
    return response.data;
  },
};

// AI Coordination API
export const aiCoordinationApi = {
  getDecisionLogs: async (status?: string): Promise<any> => {
    const response = await axiosInstance.get("/ai/decision-logs", { params: { status } });
    return response.data;
  },
  updateDecisionStatus: async (id: number, newStatus: string, humanReviewer?: string): Promise<any> => {
    const response = await axiosInstance.put(`/ai/decision-logs/${id}/status`, { newStatus, humanReviewer });
    return response.data;
  },
  sendTask: async (taskType: string, payload: any): Promise<any> => {
    const response = await axiosInstance.post("/ai/ai-task", { taskType, payload });
    return response.data;
  },
  getAIStatus: async (): Promise<any> => {
    const response = await axiosInstance.get("/ai/ai-status");
    return response.data;
  },
};

export const api = {
  get: <T>(url: string, config?: AxiosRequestConfig) => request<T>('get', url, undefined, config),
  post: <T, P = unknown>(url: string, payload?: P, config?: AxiosRequestConfig) => request<T>('post', url, payload, config),
  put: <T, P = unknown>(url: string, payload?: P, config?: AxiosRequestConfig) => request<T>('put', url, payload, config),
  patch: <T, P = unknown>(url: string, payload?: P, config?: AxiosRequestConfig) => request<T>('patch', url, payload, config),
  delete: <T>(url: string, config?: AxiosRequestConfig) => request<T>('delete', url, undefined, config),
};

