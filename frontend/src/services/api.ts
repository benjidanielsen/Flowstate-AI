import axios from 'axios';
import { QueryKey, UseQueryOptions, useMutation, useQuery } from '@tanstack/react-query';
import axiosInstance from '../api/axiosInstance';
import { queryClient } from './queryClient';
import {
  ActivityLog,
  AdminTask,
  AgentProfile,
  Customer,
  EventLog,
  EvolutionDashboardPayload,
  Interaction,
  KpiDashboardPayload,
  PipelineStats,
  PipelineStatus,
  Reminder,
  Stats,
} from '../types';

export const api = axiosInstance;
export default api;

export interface ApiError {
  message: string;
  status?: number;
  details?: unknown;
}

const normalizeApiError = (error: unknown): ApiError => {
  if (axios.isAxiosError(error)) {
    return {
      message: error.response?.data?.message || error.message || 'An unexpected error occurred',
      status: error.response?.status,
      details: error.response?.data,
    };
  }

  if (error instanceof Error) {
    return { message: error.message };
  }

  return { message: 'Unknown error' };
};

interface UseApiQueryConfig<TData>
  extends Omit<UseQueryOptions<TData, ApiError, TData, QueryKey>, 'queryKey' | 'queryFn'> {
  key: QueryKey;
  queryFn: () => Promise<TData>;
}

const DEFAULT_QUERY_OPTIONS = {
  staleTime: 60 * 1000,
  retry: 1,
  refetchOnWindowFocus: false,
};

export const useApiQuery = <TData,>({ key, queryFn, ...options }: UseApiQueryConfig<TData>) =>
  useQuery<TData, ApiError>({
    queryKey: key,
    queryFn: async () => {
      try {
        return await queryFn();
      } catch (error) {
        throw normalizeApiError(error);
      }
    },
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });

export interface CustomerFilters {
  status?: PipelineStatus;
  search?: string;
  source?: string;
  country?: string;
  language?: string;
  next_action?: string;
  sortBy?: string;
  sortOrder?: 'ASC' | 'DESC';
}

export const aiDecisionLogApi = {
  getAIDecisionLogs: async () => {
    const response = await api.get('/ai/decision-logs');
    return response.data;
  },
  updateDecisionStatus: async (id: number, newStatus: string, humanReviewer?: string) => {
    const response = await api.put(`/ai/decision-logs/${id}/status`, { newStatus, humanReviewer });
    return response.data;
  },
};

export const customerApi = {
  getAll: async (filters?: CustomerFilters): Promise<Customer[]> => {
    const response = await api.get('/customers', { params: filters });
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
    const response = await api.post(`/customers/${id}/move-next-stage`);
    return response.data;
  },
  getStats: async (): Promise<PipelineStats> => {
    const response = await api.get('/customers/stats');
    return response.data;
  },
};

export const interactionApi = {
  getAll: async (customerId: string): Promise<Interaction[]> => {
    const response = await api.get(`/customers/${customerId}/interactions`);
    return response.data;
  },
  create: async (customerId: string, interactionData: Omit<Interaction, 'id' | 'created_at'>): Promise<Interaction> => {
    const response = await api.post(`/customers/${customerId}/interactions`, interactionData);
    return response.data;
  },
  update: async (customerId: string, id: string, updates: Partial<Interaction>): Promise<Interaction> => {
    const response = await api.put(`/customers/${customerId}/interactions/${id}`, updates);
    return response.data;
  },
  delete: async (customerId: string, id: string): Promise<void> => {
    await api.delete(`/customers/${customerId}/interactions/${id}`);
  },
  getUpcoming: async (limit: number = 5): Promise<Interaction[]> => {
    const response = await api.get(`/interactions/upcoming?limit=${limit}`);
    return response.data;
  },
  complete: async (id: string): Promise<Interaction> => {
    const response = await api.post(`/interactions/${id}/complete`);
    return response.data;
  },
};

export const reminderApi = {
  getAll: async (customerId: string): Promise<Reminder[]> => {
    const response = await api.get(`/customers/${customerId}/reminders`);
    return response.data;
  },
  create: async (customerId: string, reminderData: Omit<Reminder, 'id' | 'created_at'>): Promise<Reminder> => {
    const response = await api.post(`/customers/${customerId}/reminders`, reminderData);
    return response.data;
  },
  update: async (customerId: string, id: string, updates: Partial<Reminder>): Promise<Reminder> => {
    const response = await api.put(`/customers/${customerId}/reminders/${id}`, updates);
    return response.data;
  },
  delete: async (customerId: string, id: string): Promise<void> => {
    await api.delete(`/customers/${customerId}/reminders/${id}`);
  },
};

export const eventLogApi = {
  getAll: async (customerId: string): Promise<EventLog[]> => {
    const response = await api.get(`/customers/${customerId}/event-logs`);
    return response.data;
  },
};

export const statsApi = {
  getStats: async (): Promise<Stats> => {
    const response = await api.get('/stats');
    return response.data;
  },
  getPipelineStats: async (): Promise<PipelineStats> => {
    const response = await api.get('/stats/pipeline');
    return response.data;
  },
};

export const aiCoordinationApi = {
  getDecisionLogs: async (status?: string): Promise<any> => {
    const response = await api.get('/ai/decision-logs', { params: { status } });
    return response.data;
  },
  updateDecisionStatus: async (id: number, newStatus: string, humanReviewer?: string): Promise<any> => {
    const response = await api.put(`/ai/decision-logs/${id}/status`, { newStatus, humanReviewer });
    return response.data;
  },
  sendTask: async (taskType: string, payload: any): Promise<any> => {
    const response = await api.post('/ai/ai-task', { taskType, payload });
    return response.data;
  },
  getAIStatus: async (): Promise<any> => {
    const response = await api.get('/ai/ai-status');
    return response.data;
  },
};

export const kpiApi = {
  getByCategory: async (category: string): Promise<KpiDashboardPayload> => {
    const response = await api.get('/analytics/kpis', { params: { category } });
    return response.data;
  },
};

export const evolutionApi = {
  getDashboard: async (): Promise<EvolutionDashboardPayload> => {
    const response = await api.get('/evolution/dashboard');
    return response.data;
  },
  toggleSafeMode: async (enabled: boolean): Promise<{ safeModeActive: boolean }> => {
    const response = await api.post('/evolution/safe-mode', { enabled });
    return response.data;
  },
};

export const adminApi = {
  getRoster: async (): Promise<AgentProfile[]> => {
    const response = await api.get('/admin/agents');
    return response.data;
  },
  getActivityFeed: async (): Promise<ActivityLog[]> => {
    const response = await api.get('/admin/activity');
    return response.data;
  },
  getTasks: async (): Promise<AdminTask[]> => {
    const response = await api.get('/admin/tasks');
    return response.data;
  },
};

export const useCustomerPipeline = (filters?: CustomerFilters) =>
  useApiQuery<Customer[]>({
    key: ['customers', filters ? JSON.stringify(filters) : 'all'],
    queryFn: () => customerApi.getAll(filters),
    placeholderData: () => [],
  });

export const useKpiDashboard = (category: string) =>
  useApiQuery<KpiDashboardPayload>({
    key: ['kpis', category],
    queryFn: () => kpiApi.getByCategory(category),
    placeholderData: () => ({ category, metrics: [], trend: [], summary: { total: 0, delta: 0 } }),
  });

export const useEvolutionDashboard = () =>
  useApiQuery<EvolutionDashboardPayload>({
    key: ['evolution', 'dashboard'],
    queryFn: () => evolutionApi.getDashboard(),
  });

export const useAdminRoster = () =>
  useApiQuery<AgentProfile[]>({
    key: ['admin', 'roster'],
    queryFn: () => adminApi.getRoster(),
    placeholderData: () => [],
  });

export const useAdminActivity = () =>
  useApiQuery<ActivityLog[]>({
    key: ['admin', 'activity'],
    queryFn: () => adminApi.getActivityFeed(),
    placeholderData: () => [],
  });

export const useAdminTasks = () =>
  useApiQuery<AdminTask[]>({
    key: ['admin', 'tasks'],
    queryFn: () => adminApi.getTasks(),
    placeholderData: () => [],
  });

export const useToggleSafeMode = () =>
  useMutation({
    mutationFn: (enabled: boolean) => evolutionApi.toggleSafeMode(enabled),
    onSuccess: (result, variables) => {
      const nextState = typeof result.safeModeActive === 'boolean' ? result.safeModeActive : variables;
      queryClient.setQueryData<EvolutionDashboardPayload>(['evolution', 'dashboard'], (previous) => {
        if (!previous) return previous;
        return {
          ...previous,
          metrics: { ...previous.metrics, safeModeActive: nextState },
        };
      });
    },
  });
