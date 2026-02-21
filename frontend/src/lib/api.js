import axios from 'axios';
import { ensureProtocol } from '@/utils/url';

// If REACT_APP_BACKEND_URL is empty, use relative URLs (nginx will proxy to backend)
const backendUrlEnv = process.env.REACT_APP_BACKEND_URL || '';
const BACKEND_URL = backendUrlEnv.trim() ? ensureProtocol(backendUrlEnv) : '';
const API_BASE = BACKEND_URL ? `${BACKEND_URL}/api` : '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' }
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('educando_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('educando_token');
      localStorage.removeItem('educando_user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export default api;
