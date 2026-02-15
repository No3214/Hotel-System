import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
});

// Dashboard
export const getDashboardStats = () => api.get('/dashboard/stats');

// Hotel Info
export const getHotelInfo = () => api.get('/hotel/info');
export const getHotelAwards = () => api.get('/hotel/awards');
export const getHotelPolicies = () => api.get('/hotel/policies');
export const getLocalGuide = () => api.get('/hotel/guide');

// Rooms
export const getRooms = () => api.get('/rooms');
export const getRoom = (id) => api.get(`/rooms/${id}`);

// Menu
export const getMenu = () => api.get('/menu');

// Guests
export const getGuests = (params) => api.get('/guests', { params });
export const createGuest = (data) => api.post('/guests', data);
export const getGuest = (id) => api.get(`/guests/${id}`);
export const updateGuest = (id, data) => api.patch(`/guests/${id}`, data);

// Reservations
export const getReservations = (params) => api.get('/reservations', { params });
export const createReservation = (data) => api.post('/reservations', data);
export const updateReservationStatus = (id, status) => api.patch(`/reservations/${id}/status?status=${status}`);

// Tasks
export const getTasks = (params) => api.get('/tasks', { params });
export const createTask = (data) => api.post('/tasks', data);
export const updateTask = (id, data) => api.patch(`/tasks/${id}`, data);
export const deleteTask = (id) => api.delete(`/tasks/${id}`);

// Events
export const getEvents = (params) => api.get('/events', { params });
export const createEvent = (data) => api.post('/events', data);
export const updateEvent = (id, data) => api.patch(`/events/${id}`, data);
export const deleteEvent = (id) => api.delete(`/events/${id}`);

// Housekeeping
export const getHousekeeping = (params) => api.get('/housekeeping', { params });
export const createHousekeeping = (data) => api.post('/housekeeping', data);
export const updateHousekeepingStatus = (id, status) => api.patch(`/housekeeping/${id}/status?status=${status}`);

// Staff
export const getStaff = () => api.get('/staff');
export const createStaff = (data) => api.post('/staff', data);

// Knowledge Base
export const getKnowledge = (params) => api.get('/knowledge', { params });
export const createKnowledge = (data) => api.post('/knowledge', data);
export const deleteKnowledge = (id) => api.delete(`/knowledge/${id}`);

// Chatbot
export const sendChatMessage = (data) => api.post('/chatbot', data);
export const getChatHistory = (sessionId) => api.get(`/chatbot/history/${sessionId}`);
export const clearChat = (sessionId) => api.delete(`/chatbot/session/${sessionId}`);

// Messages (WhatsApp/Instagram)
export const getMessages = (params) => api.get('/messages', { params });
export const sendWhatsAppWebhook = (data) => api.post('/whatsapp/webhook', data);

// Seed
export const seedDatabase = () => api.post('/seed');

// Campaigns
export const getCampaigns = (params) => api.get('/campaigns', { params });
export const createCampaign = (data) => api.post('/campaigns', data);
export const updateCampaignStatus = (id, status) => api.patch(`/campaigns/${id}/status?status=${status}`);
export const deleteCampaign = (id) => api.delete(`/campaigns/${id}`);

// Shifts
export const getShifts = (params) => api.get('/shifts', { params });
export const createShift = (data) => api.post('/shifts', data);
export const deleteShift = (id) => api.delete(`/shifts/${id}`);

// Staff extended
export const updateStaff = (id, data) => api.patch(`/staff/${id}`, data);
export const deleteStaff = (id) => api.delete(`/staff/${id}`);

// Reservations extended
export const getReservation = (id) => api.get(`/reservations/${id}`);
export const updateReservation = (id, data) => api.patch(`/reservations/${id}`, data);
export const deleteReservation = (id) => api.delete(`/reservations/${id}`);

// Settings
export const getSettings = () => api.get('/settings');
export const updateSettings = (data) => api.patch('/settings', data);

// KVKK
export const getKvkkPolicy = () => api.get('/kvkk/policy');

// i18n
export const getTranslations = (lang) => api.get(`/i18n/${lang}`);
export const getLanguages = () => api.get('/i18n');

// Housekeeping auto
export const autoScheduleHousekeeping = () => api.post('/housekeeping/auto-schedule');

// Hotel
export const getHotelHistory = () => api.get('/hotel/history');

// Reviews
export const getReviews = (params) => api.get('/reviews', { params });
export const createReview = (data) => api.post('/reviews', data);
export const generateReviewResponse = (reviewId, tone) => api.post(`/reviews/${reviewId}/generate-response?tone=${tone}`);
export const updateReview = (id, data) => api.patch(`/reviews/${id}`, data);
export const deleteReview = (id) => api.delete(`/reviews/${id}`);
export const getReviewStats = () => api.get('/reviews/stats');

export default api;
