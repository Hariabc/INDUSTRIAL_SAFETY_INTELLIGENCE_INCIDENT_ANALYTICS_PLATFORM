import axios from 'axios';
import {
  Plant, Machine, MachineDetail, AlarmEvent, Incident,
  IncidentDetail, CorrectiveAction, SafetyAnomaly, OverviewStats,
  EvaluationResponse, PaginatedResult
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const dashboardApi = {
  getOverview: async () => {
    const res = await api.get<{
      stats: OverviewStats;
      recent_critical_alarms: any[];
      recent_incidents: any[];
    }>('/dashboard/overview');
    return res.data;
  },
};

export const plantsApi = {
  getAll: async () => {
    const res = await api.get<Plant[]>('/plants');
    return res.data;
  },
  getById: async (id: string) => {
    const res = await api.get<any>(`/plants/${id}`);
    return res.data;
  },
};

export const machinesApi = {
  getAll: async (params?: {
    plant_id?: string;
    state?: string;
    criticality?: string;
    search?: string;
    page?: number;
    page_size?: number;
    sort_by?: string;
    sort_order?: string;
  }) => {
    const res = await api.get<PaginatedResult<Machine>>('/machines', { params });
    return res.data;
  },
  getById: async (id: string) => {
    const res = await api.get<MachineDetail>(`/machines/${id}`);
    return res.data;
  },
  getHistory: async (id: string) => {
    const res = await api.get<{
      machine_id: string;
      state_transitions: any[];
      recent_alarms: any[];
    }>(`/machines/${id}/history`);
    return res.data;
  },
};

export const alarmsApi = {
  getAll: async (params?: {
    plant_id?: string;
    machine_id?: string;
    severity?: string;
    status?: string;
    is_nuisance?: boolean;
    start_date?: string;
    end_date?: string;
    search?: string;
    page?: number;
    page_size?: number;
    sort_by?: string;
    sort_order?: string;
  }) => {
    const res = await api.get<PaginatedResult<AlarmEvent>>('/alarms', { params });
    return res.data;
  },
  getById: async (id: string) => {
    const res = await api.get<any>(`/alarms/${id}`);
    return res.data;
  },
};

export const incidentsApi = {
  getAll: async (params?: {
    plant_id?: string;
    machine_id?: string;
    severity?: string;
    status?: string;
    incident_type?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }) => {
    const res = await api.get<PaginatedResult<Incident>>('/incidents', { params });
    return res.data;
  },
  getById: async (id: string) => {
    const res = await api.get<IncidentDetail>(`/incidents/${id}`);
    return res.data;
  },
  acknowledge: async (id: string, status: string, investigator?: string) => {
    const res = await api.post(`/incidents/${id}/acknowledge`, { status, investigator });
    return res.data;
  },
};

export const correctiveActionsApi = {
  getAll: async (params?: {
    incident_id?: string;
    status?: string;
    priority?: string;
    is_verified?: boolean;
    search?: string;
    page?: number;
    page_size?: number;
  }) => {
    const res = await api.get<PaginatedResult<CorrectiveAction>>('/corrective-actions', { params });
    return res.data;
  },
  create: async (data: {
    incident_id: string;
    title: string;
    description?: string;
    assigned_to: string;
    priority: string;
    due_date: string;
  }) => {
    const res = await api.post('/corrective-actions', data);
    return res.data;
  },
  verify: async (actionId: string, payload: { verified_by: string; verification_notes: string }) => {
    const res = await api.post(`/corrective-actions/${actionId}/verify`, payload);
    return res.data;
  },
  updateStatus: async (actionId: string, payload: { status: string; actor?: string }) => {
    const res = await api.put(`/corrective-actions/${actionId}/status`, payload);
    return res.data;
  },
};

export const anomaliesApi = {
  getAll: async (params?: {
    anomaly_type?: string;
    severity?: string;
    plant_id?: string;
    machine_id?: string;
    status?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }) => {
    const res = await api.get<PaginatedResult<SafetyAnomaly>>('/anomalies', { params });
    return res.data;
  },
  getById: async (id: string) => {
    const res = await api.get<SafetyAnomaly>(`/anomalies/${id}`);
    return res.data;
  },
  runDetection: async () => {
    const res = await api.post<{
      message: string;
      detections_count: number;
      evaluation: EvaluationResponse;
    }>('/detection/run');
    return res.data;
  },
};

export const analyticsApi = {
  getAlarmTrends: async (params?: { plant_id?: string; machine_id?: string; days?: number }) => {
    const res = await api.get<any[]>('/analytics/alarm-trends', { params });
    return res.data;
  },
  getSeverityDistribution: async (params?: { plant_id?: string; machine_id?: string }) => {
    const res = await api.get<any[]>('/analytics/severity-distribution', { params });
    return res.data;
  },
  getUnsafeMachines: async (limit: number = 10) => {
    const res = await api.get<any[]>('/analytics/unsafe-machines', { params: { limit } });
    return res.data;
  },
  getAcknowledgementPerformance: async (plant_id?: string) => {
    const res = await api.get<any>('/analytics/acknowledgement-performance', { params: { plant_id } });
    return res.data;
  },
  getModelEvaluation: async () => {
    const res = await api.get<EvaluationResponse>('/analytics/model-evaluation');
    return res.data;
  },
};

export const dataQualityApi = {
  getReport: async () => {
    const res = await api.get<{
      summary: any;
      sample_findings: any[];
    }>('/data-quality');
    return res.data;
  },
  runValidation: async () => {
    const res = await api.post<{
      message: string;
      summary: any;
      total_findings: number;
    }>('/data-quality/validate');
    return res.data;
  },
};

export const settingsApi = {
  getSettings: async () => {
    const res = await api.get<{
      settings: any;
      audit_logs: any[];
    }>('/settings');
    return res.data;
  },
  updateSettings: async (payload: any) => {
    const res = await api.post('/settings', payload);
    return res.data;
  },
};

export const exportApi = {
  getDownloadUrl: (entity: string, format: 'csv' | 'json' = 'csv') => {
    return `${API_BASE_URL}/export/${entity}?format=${format}`;
  },
};

export default api;
