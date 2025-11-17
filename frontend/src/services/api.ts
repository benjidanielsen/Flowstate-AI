import axiosInstance from '../api/axiosInstance';
import { Customer, Interaction, PipelineStatus, Reminder, EventLog, PipelineStats, Stats } from '../types';

const toIsoString = (value?: Date | string | null) => {
  if (!value) return undefined;
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return undefined;
  return date.toISOString();
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
    return response.data.counts_by_status ?? {};
  },
};

// Interaction API
export const interactionApi = {
  getAll: async (customerId: string): Promise<Interaction[]> => {
    const response = await axiosInstance.get(`/customers/${customerId}/interactions`);
    return response.data;
  },
  create: async (
    customerId: string,
    interactionData: Omit<Interaction, 'id' | 'created_at' | 'updated_at'>
  ): Promise<Interaction> => {
    const payload: Record<string, unknown> = {
      type: interactionData.type,
      summary: interactionData.summary,
      notes: interactionData.notes,
      completed: interactionData.completed ?? false,
    };

    const interactionDate = toIsoString(interactionData.interaction_date as Date | string | undefined);
    if (interactionDate) {
      payload.interaction_date = interactionDate;
    }

    const scheduledFor = interactionData.scheduled_for === null
      ? null
      : toIsoString(interactionData.scheduled_for as Date | string | undefined);
    if (scheduledFor !== undefined) {
      payload.scheduled_for = scheduledFor;
    }

    const response = await axiosInstance.post(`/customers/${customerId}/interactions`, payload);
    return response.data;
  },
  update: async (customerId: string, id: string, updates: Partial<Interaction>): Promise<Interaction> => {
    const payload: Record<string, unknown> = {};

    if (updates.type !== undefined) payload.type = updates.type;
    if (updates.summary !== undefined) payload.summary = updates.summary;
    if (updates.notes !== undefined) payload.notes = updates.notes;
    if (updates.completed !== undefined) payload.completed = updates.completed;

    if (updates.interaction_date) {
      const iso = toIsoString(updates.interaction_date as Date | string | undefined);
      if (iso) payload.interaction_date = iso;
    }

    if (updates.scheduled_for !== undefined) {
      if (updates.scheduled_for === null) {
        payload.scheduled_for = null;
      } else {
        const iso = toIsoString(updates.scheduled_for as Date | string | undefined);
        if (iso) payload.scheduled_for = iso;
      }
    }

    const response = await axiosInstance.put(`/customers/${customerId}/interactions/${id}`, payload);
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
    const payload: Record<string, unknown> = {
      type: reminderData.type,
      message: reminderData.message,
      repeat_interval: reminderData.repeat_interval,
    };

    const scheduled = toIsoString(reminderData.scheduled_for as Date | string | undefined);
    if (scheduled) {
      payload.scheduled_for = scheduled;
    }

    const response = await axiosInstance.post(`/customers/${customerId}/reminders`, payload);
    return response.data;
  },
  update: async (customerId: string, id: string, updates: Partial<Reminder>): Promise<Reminder> => {
    const payload: Record<string, unknown> = {};
    if (updates.type !== undefined) payload.type = updates.type;
    if (updates.message !== undefined) payload.message = updates.message;
    if (updates.repeat_interval !== undefined) payload.repeat_interval = updates.repeat_interval;
    if (updates.completed !== undefined) payload.completed = updates.completed;

    if (updates.scheduled_for !== undefined) {
      const iso = toIsoString(updates.scheduled_for as Date | string | undefined);
      if (iso) {
        payload.scheduled_for = iso;
      }
    }

    const response = await axiosInstance.put(`/customers/${customerId}/reminders/${id}`, payload);
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
    const response = await axiosInstance.get('/stats');
    return response.data.countsByStatus ?? {};
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

