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

// Dynamic Pricing
export const calculatePrice = (roomId, date) => api.get(`/pricing/calculate?room_id=${roomId}&date=${date}`);
export const getPriceRange = (roomId, start, end) => api.get(`/pricing/range?room_id=${roomId}&start_date=${start}&end_date=${end}`);
export const getSeasons = () => api.get('/pricing/seasons');
export const getHolidays = () => api.get('/pricing/holidays');

// Table Reservations
export const getTableReservations = (params) => api.get('/table-reservations', { params });
export const createTableReservation = (data) => api.post('/table-reservations', data);
export const updateTableReservationStatus = (id, status, tableNumber) => api.patch(`/table-reservations/${id}/status?status=${status}${tableNumber ? `&table_number=${tableNumber}` : ''}`);
export const deleteTableReservation = (id) => api.delete(`/table-reservations/${id}`);
export const getTableAvailability = (date) => api.get(`/table-reservations/availability?date=${date}`);
export const getTableStats = () => api.get('/table-reservations/stats');

// Guest Lifecycle
export const getLifecycleTemplates = () => api.get('/lifecycle/templates');
export const getLifecycleTemplate = (key) => api.get(`/lifecycle/templates/${key}`);
export const previewLifecycleMessage = (templateKey, reservationId) => api.post(`/lifecycle/preview?template_key=${templateKey}${reservationId ? `&reservation_id=${reservationId}` : ''}`);
export const sendLifecycleMessage = (templateKey, reservationId, channel) => api.post(`/lifecycle/send?template_key=${templateKey}&reservation_id=${reservationId}&channel=${channel}`);
export const getLifecycleHistory = (params) => api.get('/lifecycle/history', { params });

// Automation
export const runPaymentReminder = () => api.post('/automation/payment-reminder');
export const runCancellationCheck = () => api.post('/automation/cancellation-check');
export const getKitchenForecast = (days) => api.get(`/automation/kitchen-forecast?days=${days || 7}`);
export const getAutomationLogs = (params) => api.get('/automation/logs', { params });
export const getAutomationSummary = () => api.get('/automation/summary');

// Public Menu (no auth)
export const getPublicMenu = () => axios.get(`${API_BASE}/api/public/menu`);
export const getPublicTheme = () => axios.get(`${API_BASE}/api/public/theme`);

// Menu Admin
export const getMenuItems = (category) => api.get('/menu-admin/items', { params: category ? { category } : {} });
export const createMenuItem = (data) => api.post('/menu-admin/items', data);
export const updateMenuItem = (id, data) => api.patch(`/menu-admin/items/${id}`, data);
export const deleteMenuItem = (id) => api.delete(`/menu-admin/items/${id}`);
export const getMenuCategories = () => api.get('/menu-admin/categories');
export const createMenuCategory = (data) => api.post('/menu-admin/categories', data);
export const updateMenuCategory = (id, data) => api.patch(`/menu-admin/categories/${id}`, data);
export const deleteMenuCategory = (id) => api.delete(`/menu-admin/categories/${id}`);
export const getMenuTheme = () => api.get('/menu-admin/theme');
export const updateMenuTheme = (data) => api.patch('/menu-admin/theme', data);

// Social Media
export const getSocialPosts = (params) => api.get('/social/posts', { params });
export const createSocialPost = (data) => api.post('/social/posts', data);
export const getSocialPost = (id) => api.get(`/social/posts/${id}`);
export const updateSocialPost = (id, data) => api.patch(`/social/posts/${id}`, data);
export const deleteSocialPost = (id) => api.delete(`/social/posts/${id}`);
export const publishSocialPost = (id) => api.post(`/social/posts/${id}/publish`);
export const getSocialTemplates = () => api.get('/social/templates');
export const getSocialStats = () => api.get('/social/stats');
export const convertImageLink = (url) => api.post('/social/convert-image-link', { url });

// Auth
export const login = (data) => api.post('/auth/login', data);
export const getMe = () => api.get('/auth/me');
export const setupAdmin = () => api.post('/auth/setup');
export const registerUser = (data) => api.post('/auth/register', data);
export const listUsers = () => api.get('/auth/users');
export const deleteUser = (id) => api.delete(`/auth/users/${id}`);
export const getRoles = () => api.get('/auth/roles');

// Set auth token
export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('kozbeyli_token', token);
  } else {
    delete api.defaults.headers.common['Authorization'];
    localStorage.removeItem('kozbeyli_token');
    localStorage.removeItem('kozbeyli_user');
  }
};

// Load token on init
const savedToken = localStorage.getItem('kozbeyli_token');
if (savedToken) {
  api.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
}

export default api;
