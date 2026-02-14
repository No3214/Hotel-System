import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const api = axios.create({
  baseURL: API,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dashboard
export const getDashboardStats = async () => {
  const response = await api.get('/dashboard/stats');
  return response.data;
};

// Documents
export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const listDocuments = async (params = {}) => {
  const response = await api.get('/documents', { params });
  return response.data;
};

export const getDocument = async (documentId) => {
  const response = await api.get(`/documents/${documentId}`);
  return response.data;
};

// Knowledge Base
export const listKnowledgeItems = async (params = {}) => {
  const response = await api.get('/knowledge', { params });
  return response.data;
};

export const getKnowledgeItem = async (itemId) => {
  const response = await api.get(`/knowledge/${itemId}`);
  return response.data;
};

// Tasks
export const listTasks = async (params = {}) => {
  const response = await api.get('/tasks', { params });
  return response.data;
};

export const updateTaskStatus = async (taskId, status) => {
  const response = await api.patch(`/tasks/${taskId}/status`, null, {
    params: { status }
  });
  return response.data;
};

// Search
export const semanticSearch = async (query, limit = 10) => {
  const response = await api.post('/search/semantic', null, {
    params: { query, limit }
  });
  return response.data;
};
