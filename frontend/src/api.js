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
export const updateRoomStatus = (id, data) => api.patch(`/rooms/${id}/status`, data);
export const updateRoomPrice = (id, data) => api.patch(`/rooms/${id}/price`, data);
export const getRoomAvailability = () => api.get('/rooms/availability/summary');

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
export const runBreakfastNotification = () => api.post('/automation/breakfast-notification');
export const runMorningReminders = () => api.post('/automation/morning-reminders');
export const runCleaningNotification = () => api.post('/automation/cleaning-notification');
export const runEveningRoomCheck = () => api.post('/automation/evening-room-check');
export const getScheduledJobs = () => api.get('/automation/scheduled-jobs');
export const getGroupNotifications = (params) => api.get('/automation/group-notifications', { params });
export const seedSampleEvents = () => api.post('/events/seed-samples');

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
export const checkDuplicateMedia = (url) => api.post('/social/check-duplicate-media', { url });
export const aiGenerateContent = (data) => api.post('/social/ai-generate', data);
export const getAITopics = () => api.get('/social/ai-topics');
export const getAutoPublishSettings = () => api.get('/social/auto-publish/settings');
export const updateAutoPublishSettings = (data) => api.put('/social/auto-publish/settings', data);
export const triggerAutoPublish = () => api.post('/social/auto-publish/trigger');
export const getAutoPublishHistory = (limit) => api.get('/social/auto-publish/history', { params: { limit } });
export const getContentCalendar = (days) => api.get('/social/content-calendar', { params: { days } });
export const batchDriveImport = (data) => api.post('/social/batch-drive', data);
export const publishToPlatforms = (postId, platforms) => api.post(`/social/posts/${postId}/publish-to-platforms`, { post_id: postId, platforms });
export const getPlatformStatus = () => api.get('/social/platform-status');

// Content Queue & Smart Scheduling
export const getContentQueue = () => api.get('/social/queue');
export const addToQueue = (postId) => api.post(`/social/queue/${postId}`);
export const removeFromQueue = (postId) => api.delete(`/social/queue/${postId}`);
export const getOptimalTime = (platforms, topic) => api.get('/social/optimal-time', { params: { platforms, topic } });
export const getRecyclablePosts = () => api.get('/social/recyclable');
export const recyclePost = (postId) => api.post(`/social/recycle/${postId}`);
export const getWeeklyPlan = (startDate) => api.get('/social/weekly-plan', { params: startDate ? { start_date: startDate } : {} });
export const getPostScore = (postId) => api.get(`/social/post-score/${postId}`);
export const publishScheduledPosts = () => api.post('/social/publish-scheduled');

// Escalation Management
export const getEscalations = (params) => api.get('/escalations', { params });
export const resolveEscalation = (id, notes) => api.patch(`/escalations/${id}/resolve`, null, { params: { notes } });
export const getEscalationStats = () => api.get('/escalations/stats');

// Marketing & AI Copywriter
export const generateAICopy = (data) => api.post('/marketing/ai-copy', data);
export const optimizeCTA = (data) => api.post('/marketing/optimize-cta', data);
export const rewriteCopy = (data) => api.post('/marketing/rewrite', data);
export const generateWASequence = (data) => api.post('/marketing/whatsapp-sequence', data);
export const generatePinterestPins = (data) => api.post('/marketing/pinterest-pins', data);
export const generateContentStrategy = (data) => api.post('/marketing/content-strategy', data);
export const getPsychologyTips = (data) => api.post('/marketing/psychology-tips', data);
export const getMarketingPlatforms = () => api.get('/marketing/platforms');
export const getPsychologyTriggers = () => api.get('/marketing/psychology-triggers');
export const getSequenceTypes = () => api.get('/marketing/sequence-types');
export const getPinterestBoards = () => api.get('/marketing/pinterest-boards');

// Meta Ads Manager
export const generateAdCopy = (data) => api.post('/meta-ads/generate-copy', data);
export const getAdAudiences = () => api.get('/meta-ads/audiences');
export const getAdTemplates = () => api.get('/meta-ads/templates');
export const getAdPerformance = (campaignId) => api.get('/meta-ads/performance', { params: campaignId ? { campaign_id: campaignId } : {} });
export const createAdCampaign = (data) => api.post('/meta-ads/campaigns', data);
export const getAdCampaigns = (params) => api.get('/meta-ads/campaigns', { params });
export const updateAdCampaignStatus = (data) => api.put('/meta-ads/campaigns/status', data);
export const getBudgetSuggestions = () => api.get('/meta-ads/budget-suggestions');

// Reputation Management
export const getReputationOverview = () => api.get('/reputation/overview');
export const getReputationPlatforms = () => api.get('/reputation/platforms');
export const analyzeReview = (data) => api.post('/reputation/analyze', data);
export const addReputationReview = (data) => api.post('/reputation/reviews', data);
export const getReputationReviews = (params) => api.get('/reputation/reviews', { params });
export const getCompetitorComparison = () => api.get('/reputation/competitors');
export const getSentimentKeywords = () => api.get('/reputation/sentiment-keywords');
export const quickSentiment = (data) => api.post('/reputation/quick-sentiment', data);

// Marketing Analytics
export const getMarketingOverview = () => api.get('/marketing-analytics/overview');
export const getChannelPerformance = (period) => api.get('/marketing-analytics/channel-performance', { params: { period } });
export const getConversionFunnel = () => api.get('/marketing-analytics/conversion-funnel');
export const getROIReport = () => api.get('/marketing-analytics/roi-report');

// Google Ads Manager
export const getGoogleKeywordPlans = () => api.get('/google-ads/keyword-plans');
export const getGoogleAdFormats = () => api.get('/google-ads/ad-formats');
export const createGoogleCampaign = (data) => api.post('/google-ads/campaigns', data);
export const getGoogleCampaigns = (params) => api.get('/google-ads/campaigns', { params });
export const updateGoogleCampaign = (data) => api.put('/google-ads/campaigns', data);
export const addGoogleAd = (data) => api.post('/google-ads/campaigns/ads', data);
export const updateGoogleKeywords = (data) => api.put('/google-ads/campaigns/keywords', data);
export const getGooglePerformance = (campaignId) => api.get('/google-ads/performance', { params: campaignId ? { campaign_id: campaignId } : {} });
export const deleteGoogleCampaign = (id) => api.delete(`/google-ads/campaigns/${id}`);

// AI Providers
export const getAIProviders = () => api.get('/ai/providers');
export const getAIRouting = () => api.get('/ai/routing');
export const testAI = (data) => api.post('/ai/test', data);
export const smartAIRequest = (data) => api.post('/ai/smart-request', data);
export const getMarketingReports = (limit) => api.get('/ai/marketing-reports', { params: { limit } });
export const getLatestMarketingReport = () => api.get('/ai/marketing-reports/latest');
export const getAIUsageStats = (days) => api.get('/ai/usage-stats', { params: { days } });

// Event Leads & Outreach
export const getEventIdeas = (category) => api.get('/event-leads/ideas', { params: category ? { category } : {} });
export const getTargetGroups = () => api.get('/event-leads/target-groups');
export const getEventLeads = (params) => api.get('/event-leads/leads', { params });
export const createEventLead = (data) => api.post('/event-leads/leads', data);
export const updateEventLead = (id, data) => api.patch(`/event-leads/leads/${id}`, data);
export const deleteEventLead = (id) => api.delete(`/event-leads/leads/${id}`);
export const generateOutreachMessage = (data) => api.post('/event-leads/generate-message', data);
export const logLeadContact = (id) => api.post(`/event-leads/leads/${id}/log-contact`);
export const getEventLeadStats = () => api.get('/event-leads/stats');
export const getEventSuggestions = () => api.get('/event-leads/suggestions');

// Kitchen Dashboard
export const getKitchenOrders = (params) => api.get('/kitchen/orders', { params });
export const createKitchenOrder = (data) => api.post('/kitchen/orders', data);
export const getKitchenOrder = (id) => api.get(`/kitchen/orders/${id}`);
export const updateKitchenOrderStatus = (id, data) => api.put(`/kitchen/orders/${id}/status`, data);
export const cancelKitchenOrder = (id) => api.delete(`/kitchen/orders/${id}`);
export const getKitchenSummary = () => api.get('/kitchen/summary');
export const getKitchenNotifications = () => api.get('/kitchen/notifications');

// Auth
export const login = (data) => api.post('/auth/login', data);
export const getMe = () => api.get('/auth/me');
export const setupAdmin = () => api.post('/auth/setup');
export const registerUser = (data) => api.post('/auth/register', data);
export const listUsers = () => api.get('/auth/users');
export const deleteUser = (id) => api.delete(`/auth/users/${id}`);
export const getRoles = () => api.get('/auth/roles');

// Loyalty / Sadakat
export const getLoyaltyLevels = () => api.get('/loyalty/levels');
export const getLoyaltyGuests = (params) => api.get('/loyalty/guests', { params });
export const getGuestLoyalty = (id) => api.get(`/loyalty/guest/${id}`);
export const updateGuestLoyalty = (id) => api.post(`/loyalty/update-guest/${id}`);
export const matchReturningGuest = (params) => api.post('/loyalty/match-guest', null, { params });
export const getLoyaltyStats = () => api.get('/loyalty/stats');

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

// Global error interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;

    if (status === 401) {
      // Token expired or invalid - redirect to login
      localStorage.removeItem('kozbeyli_token');
      localStorage.removeItem('kozbeyli_user');
      delete api.defaults.headers.common['Authorization'];
      if (window.location.pathname.startsWith('/admin')) {
        window.location.reload();
      }
    }

    if (status >= 500) {
      console.error('Server error:', error.response?.data?.detail || error.message);
    }

    return Promise.reject(error);
  }
);

// Revenue Management
export const getRevenueRoomTypes = () => api.get('/revenue/room-types');
export const calculateDynamicPrice = (roomType, targetDate, basePrice) => api.get('/revenue/pricing/calculate', { params: { room_type: roomType, target_date: targetDate, base_price: basePrice } });
export const getPricingCalendar = (roomType, dateFrom, dateTo) => api.get('/revenue/pricing/calendar', { params: { room_type: roomType, date_from: dateFrom, date_to: dateTo } });
export const updateAllPrices = (daysAhead) => api.post(`/revenue/pricing/update-all?days_ahead=${daysAhead || 90}`);
export const getRevenueForecast = (dateFrom, dateTo) => api.get('/revenue/forecast', { params: { date_from: dateFrom, date_to: dateTo } });
export const getRevenueKPI = (dateFrom, dateTo) => api.get('/revenue/kpi', { params: { date_from: dateFrom, date_to: dateTo } });
export const getPricingRules = () => api.get('/revenue/pricing/rules');

// Analytics
export const getAnalyticsKPI = (dateFrom, dateTo) => api.get('/analytics/dashboard/kpi', { params: { date_from: dateFrom, date_to: dateTo } });
export const getRevenueTrend = (period) => api.get(`/analytics/revenue/trend?period=${period || '30d'}`);
export const getBookingSources = (dateFrom, dateTo) => api.get('/analytics/bookings/sources', { params: { date_from: dateFrom, date_to: dateTo } });
export const getOccupancyHeatmap = (year) => api.get('/analytics/occupancy/heatmap', { params: { year } });
export const getRoomPerformance = (dateFrom, dateTo) => api.get('/analytics/rooms/performance', { params: { date_from: dateFrom, date_to: dateTo } });
export const getGuestSatisfaction = (period) => api.get(`/analytics/guests/satisfaction?period=${period || '30d'}`);

// Audit & Security
export const getAuditLogs = (params) => api.get('/audit/logs', { params });
export const getAuditStats = (dateFrom, dateTo) => api.get('/audit/stats', { params: { date_from: dateFrom, date_to: dateTo } });
export const getSecurityAlerts = (params) => api.get('/audit/alerts', { params });
export const resolveSecurityAlert = (id) => api.post(`/audit/alerts/${id}/resolve`);
export const runSecurityCheck = () => api.post('/audit/check-security');

// HotelRunner
export const getHotelRunnerStatus = () => api.get('/hotelrunner/status');
export const syncHotelRunnerReservations = () => api.post('/hotelrunner/sync/reservations');
export const syncHotelRunnerAvailability = () => api.post('/hotelrunner/sync/availability');
export const syncHotelRunnerRates = () => api.post('/hotelrunner/sync/rates');
export const syncHotelRunnerFull = () => api.post('/hotelrunner/sync/full');
export const getHotelRunnerSyncLogs = (params) => api.get('/hotelrunner/sync-logs', { params });
export const getHotelRunnerConfig = () => api.get('/hotelrunner/config');

// Cache
export const getCacheStats = () => api.get('/cache/stats');
export const clearCache = () => api.post('/cache/clear');

// Notifications
export const subscribePush = (subscription, userId) => api.post('/notifications/subscribe', { subscription, user_id: userId });
export const unsubscribePush = (endpoint) => api.post('/notifications/unsubscribe', { endpoint });
export const getTodayNotifications = () => api.get('/notifications/today');
export const sendTestNotification = () => api.post('/notifications/send-test');
export const getVapidKey = () => api.get('/notifications/vapid-key');
export const sendPushNotification = (title, body, tag) => api.post('/notifications/send-push', { title, body, tag });
export const getSubscriberCount = () => api.get('/notifications/subscribers');
export const getNotificationHistory = (params) => api.get('/notifications/history', { params });
export const createInAppNotification = (data) => api.post('/notifications/in-app', data);
export const markNotificationRead = (id) => api.patch(`/notifications/${id}/read`);
export const markAllNotificationsRead = () => api.post('/notifications/mark-all-read');
export const deleteNotification = (id) => api.delete(`/notifications/${id}`);
export const clearNotificationHistory = () => api.delete('/notifications/history/clear');

// Financials
export const getFinancialCategories = () => api.get('/financials/categories');
export const addIncome = (data) => api.post('/financials/income', data);
export const addExpense = (data) => api.post('/financials/expense', data);
export const getIncomeList = (params) => api.get('/financials/income', { params });
export const getExpenseList = (params) => api.get('/financials/expense', { params });
export const deleteFinancialRecord = (id) => api.delete(`/financials/${id}`);
export const getDailySummary = (dateStr) => api.get(`/financials/daily/${dateStr}`);
export const getMonthlySummary = (year, month) => api.get('/financials/monthly', { params: { year, month } });

export default api;
