import React, { useState, useEffect, Suspense, lazy } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, BedDouble, Users, MessageCircle, CheckSquare,
  Calendar, Sparkles, BookOpen, UtensilsCrossed, Menu, ChevronLeft,
  CalendarCheck, UserCog, Mail, MapPin, Settings, Star, TrendingUp, Heart, LogOut, QrCode, Share2,
  Globe, Bell
} from 'lucide-react';

import { setAuthToken, getMe } from './api';
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

const NAV_CONFIG = [
  {
    labelKey: 'general',
    items: [
      { id: 'dashboard', nameKey: 'dashboard', icon: LayoutDashboard },
      { id: 'reservations', nameKey: 'reservations', icon: CalendarCheck },
      { id: 'rooms', nameKey: 'rooms', icon: BedDouble },
      { id: 'guests', nameKey: 'guests', icon: Users },
      { id: 'pricing', nameKey: 'pricing', icon: TrendingUp },
      { id: 'revenue', nameKey: 'revenue', icon: TrendingUp },
      { id: 'analytics', nameKey: 'analytics', icon: LayoutDashboard },
    ],
  },
  {
    labelKey: 'communication',
    items: [
      { id: 'chatbot', nameKey: 'chatbot', icon: Sparkles },
      { id: 'messages', nameKey: 'messages', icon: MessageCircle },
      { id: 'whatsapp', nameKey: 'whatsapp', icon: MessageCircle },
      { id: 'campaigns', nameKey: 'campaigns', icon: Mail },
      { id: 'reviews', nameKey: 'reviews', icon: Star },
      { id: 'lifecycle', nameKey: 'lifecycle', icon: Heart },
      { id: 'social', nameKey: 'social', icon: Share2 },
    ],
  },
  {
    labelKey: 'operations',
    items: [
      { id: 'tasks', nameKey: 'tasks', icon: CheckSquare },
      { id: 'events', nameKey: 'events', icon: Calendar },
      { id: 'housekeeping', nameKey: 'housekeeping', icon: BedDouble },
      { id: 'staff', nameKey: 'staff', icon: UserCog },
      { id: 'table_reservations', nameKey: 'table_reservations', icon: UtensilsCrossed },
      { id: 'kitchen', nameKey: 'kitchen', icon: UtensilsCrossed },
    ],
  },
  {
    labelKey: 'integrations',
    items: [
      { id: 'hotelrunner', nameKey: 'hotelrunner', icon: Globe },
    ],
  },
  {
    labelKey: 'information',
    items: [
      { id: 'knowledge', nameKey: 'knowledge', icon: BookOpen },
      { id: 'menu', nameKey: 'menu', icon: QrCode },
      { id: 'guide', nameKey: 'guide', icon: MapPin },
    ],
  },
  {
    labelKey: 'system',
    items: [
      { id: 'automation', nameKey: 'automation', icon: Settings },
      { id: 'audit', nameKey: 'audit', icon: Settings },
      { id: 'settings', nameKey: 'settings', icon: Settings },
    ],
  },
];

const PAGES = {
  dashboard: Dashboard,
  rooms: RoomsPage,
  guests: GuestsPage,
  chatbot: ChatbotPage,
  messages: MessagesPage,
  tasks: TasksPage,
  events: EventsPage,
  housekeeping: HousekeepingPage,
  knowledge: KnowledgePage,
  menu: MenuPage,
  reservations: ReservationsPage,
  staff: StaffPage,
  campaigns: CampaignsPage,
  reviews: ReviewsPage,
  pricing: PricingPage,
  table_reservations: TableReservationsPage,
  lifecycle: LifecyclePage,
  automation: AutomationPage,
  social: SocialMediaPage,
  kitchen: KitchenPage,
  whatsapp: WhatsAppPage,
  guide: FocaGuidePage,
  settings: SettingsPage,
  revenue: RevenueManagementPage,
  analytics: AnalyticsPage,
  audit: AuditSecurityPage,
  hotelrunner: HotelRunnerPage,
};

export default function App() {
  if (window.location.pathname === '/menu') {
    return <PublicMenuPage />;
  }
  return (
    <LanguageProvider>
      <AdminApp />
    </LanguageProvider>
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

function AdminApp() {
  const [page, setPage] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const { t } = useLanguage();

  useEffect(() => {
    const saved = localStorage.getItem('kozbeyli_user');
    const token = localStorage.getItem('kozbeyli_token');
    if (saved && token) {
      setUser(JSON.parse(saved));
      getMe().then(r => {
        const u = r.data;
        setUser(u);
        localStorage.setItem('kozbeyli_user', JSON.stringify(u));
      }).catch(() => {
        setAuthToken(null);
        setUser(null);
      });
    }
    setAuthLoading(false);
  }, []);

  const handleLogin = (userData) => setUser(userData);
  const handleLogout = () => { setAuthToken(null); setUser(null); };

  if (authLoading) return <div className="min-h-screen bg-[#0a0a0f]" />;
  if (!user) return <LoginPage onLogin={handleLogin} />;

  const hasPermission = (pageId) => {
    if (!user) return false;
    if (user.role === 'admin') return true;
    const perms = user.permissions || [];
    return perms.includes('*') || perms.includes(pageId);
  };

  const filteredSections = NAV_CONFIG.map(section => ({
    ...section,
    items: section.items.filter(item => hasPermission(item.id)),
  })).filter(section => section.items.length > 0);

  const PageComponent = PAGES[page] || Dashboard;

  return (
    <div className="flex h-screen bg-[#0a0a0f]" data-testid="app-root">
      <motion.aside
        animate={{ width: sidebarOpen ? 260 : 72 }}
        className="bg-[#0f0f14] border-r border-[#C4972A]/10 flex flex-col relative z-20 overflow-hidden"
        data-testid="sidebar"
      >
        {/* Logo */}
        <div className="p-4 border-b border-[#C4972A]/10">
          <div className="flex items-center gap-3">
            <img src="/logo.jpeg" alt="Kozbeyli Konagi"
              className="w-10 h-10 rounded-lg flex-shrink-0 object-cover" data-testid="sidebar-logo" />
            <AnimatePresence>
              {sidebarOpen && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <h1 className="text-base font-bold text-[#C4972A]" style={{ fontFamily: 'var(--font-heading)' }}>
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
                  const active = page === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setPage(item.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 ${
                        active
                          ? 'bg-[#C4972A]/15 text-[#C4972A] gold-glow'
                          : 'text-[#a9a9b2] hover:bg-white/5 hover:text-[#e5e5e8]'
                      }`}
                      data-testid={`nav-${item.id}`}
                    >
                      <Icon className="w-4.5 h-4.5 flex-shrink-0" style={{ width: 18, height: 18 }} />
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
          {/* Language Selector */}
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
            key={page}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.2 }}
            className="h-full"
          >
            <PageComponent onNavigate={setPage} />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
