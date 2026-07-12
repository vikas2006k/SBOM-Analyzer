import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auto-inject JWT token header if exists
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sentinel_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle authentication errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('sentinel_token');
      localStorage.removeItem('sentinel_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  register: (username, email, password, role = 'viewer') => api.post('/auth/register', { username, email, password, role }),
  logout: () => {
    localStorage.removeItem('sentinel_token');
    localStorage.removeItem('sentinel_user');
  }
};

export const appAPI = {
  getApplications: () => api.get('/dashboard/summary').then(res => res.data.data.applications_status || []),
  getApplication: (id) => api.get(`/applications/${id}`),
  getApplicationGraph: (id) => api.get(`/applications/${id}/graph`),
  getApplicationDependencies: (id) => api.get(`/applications/${id}/dependencies`),
};

export const sbomAPI = {
  listUploads: () => api.get('/sbom/uploads'),
  uploadSBOM: (applicationId, file) => {
    const formData = new FormData();
    formData.append('application_id', applicationId);
    formData.append('file', file);
    return api.post('/sbom/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  parseSBOM: (uploadId) => api.post(`/sbom/parse/${uploadId}`),
};

export const vulnerabilityAPI = {
  getCatalog: (severity = '', search = '') => {
    let url = '/vulnerabilities';
    const params = [];
    if (severity) params.push(`severity=${severity}`);
    if (search) params.push(`search=${search}`);
    if (params.length) url += `?${params.join('&')}`;
    return api.get(url);
  },
  getCVE: (cveId) => api.get(`/vulnerabilities/${cveId}`),
  getApplicationVulnerabilities: (appId) => api.get(`/vulnerabilities/application/${appId}`),
  addCVE: (cveData) => api.post('/vulnerabilities', cveData),
};

export const licenseAPI = {
  auditApplication: (appId) => api.get(`/licenses/application/${appId}`),
  getRules: () => api.get('/licenses/rules'),
  updateRule: (ruleData) => api.post('/licenses/rules', ruleData),
};

export const maintenanceAPI = {
  auditApplication: (appId) => api.get(`/maintenance/application/${appId}`),
};

export const riskAPI = {
  getRiskReport: (appId) => api.get(`/risk/application/${appId}`),
  recalculateRisk: (appId) => api.post(`/risk/application/${appId}/calculate`),
};

export const attackPathAPI = {
  getAttackPaths: (appId) => api.get(`/attack-paths/application/${appId}`),
};

export const copilotAPI = {
  chat: (applicationId, message) => api.post('/copilot/chat', { application_id: applicationId, message }),
  getHistory: (appId) => api.get(`/copilot/history/${appId}`),
};

export const dashboardAPI = {
  getSummary: (appId = '') => api.get(appId ? `/dashboard/summary?application_id=${appId}` : '/dashboard/summary'),
  search: (query) => api.get(`/dashboard/search?query=${query}`),
};

export const notificationAPI = {
  getNotifications: (unreadOnly = false) => api.get(`/notifications?unread_only=${unreadOnly}`),
  markRead: (id) => api.post(`/notifications/${id}/read`),
  markAllRead: () => api.post('/notifications/read-all'),
};

export const reportAPI = {
  getPDFUrl: (appId) => `${API_BASE_URL}/reports/pdf/${appId}?token=${localStorage.getItem('sentinel_token')}`,
  getCSVUrl: (appId) => `${API_BASE_URL}/reports/csv/${appId}?token=${localStorage.getItem('sentinel_token')}`,
};

export default api;
