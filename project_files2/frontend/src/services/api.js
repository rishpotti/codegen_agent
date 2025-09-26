
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token (example)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token'); // Assuming token is stored in localStorage
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors globally (example)
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Example: handle 401 unauthorized errors
    if (error.response && error.response.status === 401) {
      console.log('Unauthorized, redirecting to login...');
      // window.location.href = '/login'; // Example redirect
    }
    return Promise.reject(error);
  }
);

const request = {
  get: (url, params = {}) => api.get(url, { params }),
  post: (url, data = {}) => api.post(url, data),
  put: (url, data = {}) => api.put(url, data),
  delete: (url, params = {}) => api.delete(url, { params }),
};

export default request;
