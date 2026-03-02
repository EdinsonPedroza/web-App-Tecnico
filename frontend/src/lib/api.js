import axios from 'axios';
import { ensureProtocol } from '@/utils/url';

// If REACT_APP_BACKEND_URL is empty, use relative URLs (nginx will proxy to backend)
const backendUrlEnv = process.env.REACT_APP_BACKEND_URL || '';
const BACKEND_URL = backendUrlEnv.trim() ? ensureProtocol(backendUrlEnv) : '';
const API_BASE = BACKEND_URL ? `${BACKEND_URL}/api` : '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('educando_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});



const shouldRetry = (error) => {
  const status = error?.response?.status;
  if (!status && (error.code === 'ECONNABORTED' || error.message?.includes('Network Error'))) return true;
  return status >= 500 && status < 600;
};

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalConfig = error.config || {};

    if (error.response?.status === 401 && !originalConfig.__refreshed) {
      const refreshToken = sessionStorage.getItem('educando_refresh_token');
      if (refreshToken) {
        originalConfig.__refreshed = true;
        try {
          const refreshRes = await axios.post(`${API_BASE}/auth/refresh`, { refresh_token: refreshToken });
          sessionStorage.setItem('educando_token', refreshRes.data.token);
          sessionStorage.setItem('educando_refresh_token', refreshRes.data.refresh_token);
          originalConfig.headers = { ...originalConfig.headers, Authorization: `Bearer ${refreshRes.data.token}` };
          return api(originalConfig);
        } catch (_refreshError) {
          // Refresh failed — clear session and redirect
        }
      }
      sessionStorage.removeItem('educando_token');
      sessionStorage.removeItem('educando_refresh_token');
      sessionStorage.removeItem('educando_user');
      window.location.href = '/';
      return Promise.reject(error);
    }

    if ((originalConfig.method || 'get').toLowerCase() === 'get' && !originalConfig.__retried && shouldRetry(error)) {
      originalConfig.__retried = true;
      return api(originalConfig);
    }

    return Promise.reject(error);
  }
);

export default api;
