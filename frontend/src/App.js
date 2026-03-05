import React, { useState, useEffect, Suspense, lazy, useCallback } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation, Navigate, Outlet } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, BedDouble, Users, MessageCircle, CheckSquare,
  Calendar, Sparkles, BookOpen, UtensilsCrossed, Menu, ChevronLeft,
  CalendarCheck, UserCog, Mail, MapPin, Settings, Star, TrendingUp, Heart, LogOut, QrCode, Share2,
  Globe, Bell, DollarSign, PartyPopper, FileText
} from 'lucide-react';

import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ErrorBoundary, NetworkStatusMonitor } from './components/ErrorBoundary';
import { LanguageProvider, useLanguage } from './hooks/useLanguage';
import LoginPage from './pages/LoginPage';
import PublicMenuPage from './pages/PublicMenuPage';
import Dashboard from './pages/Dashboard';

// Lazy load all non-critical pages
const RoomsPage = lazy(() => import('./pages/RoomsPage'));
const GuestsPage = lazy(() => import('./pages/GuestsPage'));
const ChatbotPage = lazy(() => import('./pages/ChatbotPage'));
const TasksPage = lazy(() => import('./pages/TasksPage'));
const EventsPage = lazy(() => import('./pages/EventsPage'));
const HousekeepingPage = lazy(() => import('./pages/HousekeepingPage'));
const KnowledgePage = lazy(() => import('./pages/KnowledgeBasePage'));
const MenuPage = lazy(() => import('./pages/MenuPage'));
const MessagesPage = lazy(() => import('./pages/MessagesPage'));
const ReservationsPage = lazy(() => import('./pages/ReservationsPage'));
const StaffPage = lazy(() => import('./pages/StaffPage'));
const CampaignsPage = lazy(() => import('./pages/CampaignsPage'));
const FocaGuidePage = lazy(() => import('./pages/FocaGuidePage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const ReviewsPage = lazy(() => import('./pages/ReviewsPage'));
const PricingPage = lazy(() => import('./pages/PricingPage'));
const TableReservationsPage = lazy(() => import('./pages/TableReservationsPage'));
const LifecyclePage = lazy(() => import('./pages/LifecyclePage'));
const AutomationPage = lazy(() => import('./pages/AutomationPage'));
const SocialMediaPage = lazy(() => import('./pages/SocialMediaPage'));
const KitchenPage = lazy(() => import('./pages/KitchenPage'));
const WhatsAppPage = lazy(() => import('./pages/WhatsAppPage'));
const RevenueManagementPage = lazy(() => import('./pages/RevenueManagementPage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));
const AuditSecurityPage = lazy(() => import('./pages/AuditSecurityPage'));
const HotelRunnerPage = lazy(() => import('./pages/HotelRunnerPage'));
const FinancialsPage = lazy(() => import('./pages/FinancialsPage'));
const OrganizationPage = lazy(() => import('./pages/OrganizationPage'));
const ProposalsPage = lazy(() => import('./pages/ProposalsPage'));

const NAV_CONFIG = [
  {
    labelKey: 'general',
    items: [
      { id: 'dashboard', path: '/admin', nameKey: 'dashboard', icon: LayoutDashboard },
      { id: 'reservations', path: '/admin/reservations', nameKey: 'reservations', icon: CalendarCheck },
      { id: 'rooms', path: '/admin/rooms', nameKey: 'rooms', icon: BedDouble },
      { id: 'guests', path: '/admin/guests', nameKey: 'guests', icon: Users },
      { id: 'pricing', path: '/admin/pricing', nameKey: 'pricing', icon: TrendingUp },
      { id: 'revenue', path: '/admin/revenue', nameKey: 'revenue', icon: TrendingUp },
      { id: 'analytics', path: '/admin/analytics', nameKey: 'analytics', icon: LayoutDashboard },
      { id: 'financials', path: '/admin/financials', nameKey: 'financials', icon: DollarSign },
    ],
  },
  {
    labelKey: 'communication',
    items: [
      { id: 'chatbot', path: '/admin/chatbot', nameKey: 'chatbot', icon: Sparkles },
      { id: 'messages', path: '/admin/messages', nameKey: 'messages', icon: MessageCircle },
      { id: 'whatsapp', path: '/admin/whatsapp', nameKey: 'whatsapp', icon: MessageCircle },
      { id: 'campaigns', path: '/admin/campaigns', nameKey: 'campaigns', icon: Mail },
      { id: 'reviews', path: '/admin/reviews', nameKey: 'reviews', icon: Star },
      { id: 'lifecycle', path: '/admin/lifecycle', nameKey: 'lifecycle', icon: Heart },
      { id: 'social', path: '/admin/social', nameKey: 'social', icon: Share2 },
    ],
  },
  {
    labelKey: 'operations',
    items: [
      { id: 'tasks', path: '/admin/tasks', nameKey: 'tasks', icon: CheckSquare },
      { id: 'events', path: '/admin/events', nameKey: 'events', icon: Calendar },
      { id: 'organization', path: '/admin/organization', nameKey: 'organization', icon: PartyPopper },
      { id: 'proposals', path: '/admin/proposals', nameKey: 'proposals', icon: FileText },
      { id: 'housekeeping', path: '/admin/housekeeping', nameKey: 'housekeeping', icon: BedDouble },
      { id: 'staff', path: '/admin/staff', nameKey: 'staff', icon: UserCog },
      { id: 'table_reservations', path: '/admin/table-reservations', nameKey: 'table_reservations', icon: UtensilsCrossed },
      { id: 'kitchen', path: '/admin/kitchen', nameKey: 'kitchen', icon: UtensilsCrossed },
    ],
  },
  {
    labelKey: 'integrations',
    items: [
      { id: 'hotelrunner', path: '/admin/hotelrunner', nameKey: 'hotelrunner', icon: Globe },
    ],
  },
  {
    labelKey: 'information',
    items: [
      { id: 'knowledge', path: '/admin/knowledge', nameKey: 'knowledge', icon: BookOpen },
      { id: 'menu', path: '/admin/menu', nameKey: 'menu', icon: QrCode },
      { id: 'guide', path: '/admin/guide', nameKey: 'guide', icon: MapPin },
    ],
  },
  {
    labelKey: 'system',
    items: [
      { id: 'automation', path: '/admin/automation', nameKey: 'automation', icon: Settings },
      { id: 'audit', path: '/admin/audit', nameKey: 'audit', icon: Settings },
      { id: 'settings', path: '/admin/settings', nameKey: 'settings', icon: Settings },
    ],
  },
];

export default function App() {
  return (
    <ErrorBoundary>
      <NetworkStatusMonitor />
      <BrowserRouter>
        <AuthProvider>
          <LanguageProvider>
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<PublicMenuPage />} />
              <Route path="/menu" element={<PublicMenuPage />} />
              <Route path="/login" element={<LoginRoute />} />

              {/* Admin routes */}
              <Route path="/admin" element={<ProtectedRoute><AdminLayout /></ProtectedRoute>}>
                <Route index element={<Dashboard />} />
                <Route path="reservations" element={<PageWrapper><ReservationsPage /></PageWrapper>} />
                <Route path="rooms" element={<PageWrapper><RoomsPage /></PageWrapper>} />
                <Route path="guests" element={<PageWrapper><GuestsPage /></PageWrapper>} />
                <Route path="pricing" element={<PageWrapper><PricingPage /></PageWrapper>} />
                <Route path="revenue" element={<PageWrapper><RevenueManagementPage /></PageWrapper>} />
                <Route path="analytics" element={<PageWrapper><AnalyticsPage /></PageWrapper>} />
                <Route path="financials" element={<PageWrapper><FinancialsPage /></PageWrapper>} />
                <Route path="chatbot" element={<PageWrapper><ChatbotPage /></PageWrapper>} />
                <Route path="messages" element={<PageWrapper><MessagesPage /></PageWrapper>} />
                <Route path="whatsapp" element={<PageWrapper><WhatsAppPage /></PageWrapper>} />
                <Route path="campaigns" element={<PageWrapper><CampaignsPage /></PageWrapper>} />
                <Route path="reviews" element={<PageWrapper><ReviewsPage /></PageWrapper>} />
                <Route path="lifecycle" element={<PageWrapper><LifecyclePage /></PageWrapper>} />
                <Route path="social" element={<PageWrapper><SocialMediaPage /></PageWrapper>} />
                <Route path="tasks" element={<PageWrapper><TasksPage /></PageWrapper>} />
                <Route path="events" element={<PageWrapper><EventsPage /></PageWrapper>} />
                <Route path="housekeeping" element={<PageWrapper><HousekeepingPage /></PageWrapper>} />
                <Route path="staff" element={<PageWrapper><StaffPage /></PageWrapper>} />
                <Route path="table-reservations" element={<PageWrapper><TableReservationsPage /></PageWrapper>} />
                <Route path="kitchen" element={<PageWrapper><KitchenPage /></PageWrapper>} />
                <Route path="organization" element={<PageWrapper><OrganizationPage /></PageWrapper>} />
                <Route path="proposals" element={<PageWrapper><ProposalsPage /></PageWrapper>} />
                <Route path="hotelrunner" element={<PageWrapper><HotelRunnerPage /></PageWrapper>} />
                <Route path="knowledge" element={<PageWrapper><KnowledgePage /></PageWrapper>} />
                <Route path="menu" element={<PageWrapper><MenuPage /></PageWrapper>} />
                <Route path="guide" element={<PageWrapper><FocaGuidePage /></PageWrapper>} />
                <Route path="automation" element={<PageWrapper><AutomationPage /></PageWrapper>} />
                <Route path="audit" element={<PageWrapper><AuditSecurityPage /></PageWrapper>} />
                <Route path="settings" element={<PageWrapper><SettingsPage /></PageWrapper>} />
              </Route>

              {/* Catch-all: redirect to public menu */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </LanguageProvider>
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

function LoginRoute() {
  const { user } = useAuth();
  if (user) return <Navigate to="/admin" replace />;
  return <LoginPage />;
}

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="min-h-screen bg-[#0a0a0f]" />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function PageWrapper({ children }) {
  return (
    <ErrorBoundary>
      <Suspense fallback={
        <div className="flex items-center justify-center h-full">
          <div className="w-8 h-8 border-2 border-[#C4972A] border-t-transparent rounded-full animate-spin" />
        </div>
      }>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
}

const FLAG_MAP = { TR: 'TR', GB: 'GB', DE: 'DE', FR: 'FR', RU: 'RU' };

function LanguageSelector({ compact }) {
  const { lang, setLang, languages } = useLanguage();
  const [open, setOpen] = useState(false);

  const current = languages.find(l => l.code === lang) || { code: 'tr', name: 'Turkce', flag: 'TR' };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-white/5 hover:bg-[#C4972A]/10 transition-all text-[#a9a9b2] hover:text-[#C4972A] w-full"
        data-testid="language-selector"
      >
        <Globe className="w-4 h-4 flex-shrink-0" />
        {!compact && <span className="text-xs">{current.name}</span>}
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute bottom-full left-0 mb-1 bg-[#1a1a22] border border-[#C4972A]/15 rounded-lg shadow-xl z-50 min-w-[140px] overflow-hidden"
            data-testid="language-dropdown">
            {languages.map(l => (
              <button
                key={l.code}
                onClick={() => { setLang(l.code); setOpen(false); }}
                className={`w-full text-left px-3 py-2 text-xs hover:bg-[#C4972A]/10 transition-colors flex items-center gap-2 ${
                  lang === l.code ? 'text-[#C4972A] bg-[#C4972A]/5' : 'text-[#a9a9b2]'
                }`}
                data-testid={`lang-option-${l.code}`}
              >
                <span className="text-[10px] font-bold w-5">{l.flag}</span>
                <span>{l.name}</span>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function NotificationBell({ compact }) {
  const [permission, setPermission] = useState(Notification?.permission || 'default');
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (typeof Notification !== 'undefined') {
      setPermission(Notification.permission);
    }
    import('./api').then(({ getTodayNotifications }) => {
      getTodayNotifications().then(r => setCount(r.data?.total || 0)).catch(() => {});
    });
  }, []);

  const requestPermission = async () => {
    if (typeof Notification === 'undefined') return;
    const result = await Notification.requestPermission();
    setPermission(result);
    if (result === 'granted') {
      new Notification('Kozbeyli Konagi', {
        body: 'Bildirimler aktif edildi!',
        icon: '/logo.jpeg',
      });
    }
  };

  return (
    <button
      onClick={requestPermission}
      className={`flex items-center gap-2 px-2.5 py-1.5 rounded-lg transition-all w-full ${
        permission === 'granted'
          ? 'bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20'
          : 'bg-white/5 hover:bg-[#C4972A]/10 text-[#a9a9b2] hover:text-[#C4972A]'
      }`}
      data-testid="notification-bell"
    >
      <Bell className="w-4 h-4 flex-shrink-0" />
      {!compact && (
        <span className="text-xs flex-1 text-left">
          {permission === 'granted' ? 'Bildirimler Aktif' : 'Bildirimleri Ac'}
        </span>
      )}
      {count > 0 && (
        <span className="bg-[#C4972A] text-[#0a0a0f] text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[18px] text-center">
          {count}
        </span>
      )}
    </button>
  );
}

function AdminLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { user, logout, hasPermission } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const location = useLocation();

  // Listen for auth:logout event from API interceptor
  useEffect(() => {
    const handleLogout = () => {
      logout();
      navigate('/login');
    };
    window.addEventListener('auth:logout', handleLogout);
    return () => window.removeEventListener('auth:logout', handleLogout);
  }, [logout, navigate]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const filteredSections = NAV_CONFIG.map(section => ({
    ...section,
    items: section.items.filter(item => hasPermission(item.id)),
  })).filter(section => section.items.length > 0);

  const isActive = (item) => {
    if (item.path === '/admin') {
      return location.pathname === '/admin';
    }
    return location.pathname.startsWith(item.path);
  };

  return (
    <div className="flex h-screen bg-[#0a0a0f]" data-testid="app-root">
      <motion.aside
        animate={{ width: sidebarOpen ? 260 : 72 }}
        transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
        className="bg-[#0f0f14]/95 backdrop-blur-xl border-r border-[#C4972A]/10 flex flex-col relative z-20 overflow-hidden"
        data-testid="sidebar"
      >
        {/* Logo */}
        <div className="p-4 border-b border-[#C4972A]/10">
          <div className="flex items-center gap-3">
            <div className="relative group">
              <div className="absolute -inset-1 bg-[#C4972A]/15 rounded-xl blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <img src="/logo.jpeg" alt="Kozbeyli Konagi"
                className="w-10 h-10 rounded-lg flex-shrink-0 object-cover cursor-pointer relative z-10 transition-transform duration-300 group-hover:scale-105"
                onClick={() => navigate('/admin')}
                data-testid="sidebar-logo" />
            </div>
            <AnimatePresence>
              {sidebarOpen && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <h1 className="text-base font-bold text-[#C4972A] cursor-pointer"
                    onClick={() => navigate('/admin')}
                    style={{ fontFamily: 'var(--font-heading)' }}>
                    Kozbeyli Konagi
                  </h1>
                  <p className="text-xs text-[#7e7e8a]">{t('hotel_management')}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-3 overflow-y-auto space-y-4">
          {filteredSections.map((section) => (
            <div key={section.labelKey}>
              <AnimatePresence>
                {sidebarOpen && (
                  <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    className="text-[10px] uppercase tracking-wider text-[#7e7e8a]/60 px-3 mb-1.5">
                    {t(section.labelKey)}
                  </motion.p>
                )}
              </AnimatePresence>
              <div className="space-y-0.5">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item);
                  return (
                    <button
                      key={item.id}
                      onClick={() => navigate(item.path)}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl transition-all duration-300 relative group ${
                        active
                          ? 'bg-[#C4972A]/15 text-[#C4972A] gold-glow'
                          : 'text-[#a9a9b2] hover:bg-white/5 hover:text-[#e5e5e8]'
                      }`}
                      data-testid={`nav-${item.id}`}
                    >
                      {active && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-[#C4972A] rounded-r-full" />}
                      <Icon className={`w-4.5 h-4.5 flex-shrink-0 transition-transform duration-300 ${active ? '' : 'group-hover:scale-110'}`} style={{ width: 18, height: 18 }} />
                      <AnimatePresence>
                        {sidebarOpen && (
                          <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                            className="text-sm truncate">
                            {t(item.nameKey)}
                          </motion.span>
                        )}
                      </AnimatePresence>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-3 border-t border-[#C4972A]/10 space-y-2">
          <NotificationBell compact={!sidebarOpen} />
          <LanguageSelector compact={!sidebarOpen} />
          {sidebarOpen && user && (
            <div className="flex items-center justify-between px-2 py-1">
              <div>
                <p className="text-xs font-medium text-[#e5e5e8] truncate">{user.name}</p>
                <p className="text-[10px] text-[#C4972A]">
                  {user.role === 'admin' ? t('admin') : user.role === 'reception' ? t('reception') : user.role}
                </p>
              </div>
              <button onClick={handleLogout} className="text-[#7e7e8a] hover:text-red-400 transition-colors" data-testid="logout-btn">
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-full flex items-center justify-center p-2.5 rounded-lg bg-white/5 hover:bg-[#C4972A]/10 transition-all text-[#a9a9b2] hover:text-[#C4972A]"
            data-testid="sidebar-toggle"
          >
            {sidebarOpen ? <ChevronLeft className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </motion.aside>

      <main className="flex-1 overflow-y-auto">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.2 }}
            className="h-full"
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}

// Renders the matched child route from the Routes definition
function AdminContent() {
  return <Outlet />;
}
