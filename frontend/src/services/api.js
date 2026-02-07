import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data) => api.put('/auth/profile', data),
  refresh: () => api.post('/auth/refresh'),
};

// X-ray APIs
export const xrayAPI = {
  upload: (formData) => api.post('/xray/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  getReports: () => api.get('/xray/reports'),
  getReport: (id) => api.get(`/xray/report/${id}`),
  updateReport: (id, data) => api.put(`/xray/report/${id}`, data),
  deleteReport: (id) => api.delete(`/xray/report/${id}`),
  getImage: (filename) => `${API_URL}/xray/image/${filename}`,
};

// Symptom APIs
export const symptomAPI = {
  check: (symptoms) => api.post('/symptoms/check', symptoms),
  checkV2: (payload) => api.post('/symptoms/check/v2', payload),
  getHistory: () => api.get('/symptoms/history'),
  getCheck: (id) => api.get(`/symptoms/check/${id}`),
  updateCheck: (id, data) => api.put(`/symptoms/check/${id}`, data),
  deleteCheck: (id) => api.delete(`/symptoms/check/${id}`),
  getDiseases: () => api.get('/symptoms/diseases'),
};

// Dashboard APIs
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getPatients: (params) => api.get('/dashboard/patients', { params }),
  getPatientDetails: (id) => api.get(`/dashboard/patient/${id}`),
  getAlerts: () => api.get('/dashboard/alerts'),
  markAlertRead: (id) => api.put(`/dashboard/alert/${id}/read`),
  getTrends: (params) => api.get('/dashboard/analytics/trends', { params }),
};

export default api;


