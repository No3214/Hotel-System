import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, BedDouble, Users, MessageCircle, CheckSquare,
  Calendar, Sparkles, BookOpen, UtensilsCrossed, Menu, X, ChevronLeft
} from 'lucide-react';

import Dashboard from './pages/Dashboard';
import RoomsPage from './pages/RoomsPage';
import GuestsPage from './pages/GuestsPage';
import ChatbotPage from './pages/ChatbotPage';
import TasksPage from './pages/TasksPage';
import EventsPage from './pages/EventsPage';
import HousekeepingPage from './pages/HousekeepingPage';
import KnowledgePage from './pages/KnowledgeBasePage';
import MenuPage from './pages/MenuPage';
import MessagesPage from './pages/MessagesPage';

const NAV_ITEMS = [
  { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard },
  { id: 'rooms', name: 'Odalar', icon: BedDouble },
  { id: 'guests', name: 'Misafirler', icon: Users },
  { id: 'chatbot', name: 'AI Asistan', icon: Sparkles },
  { id: 'messages', name: 'Mesajlar', icon: MessageCircle },
  { id: 'tasks', name: 'Gorevler', icon: CheckSquare },
  { id: 'events', name: 'Etkinlikler', icon: Calendar },
  { id: 'housekeeping', name: 'Kat Hizmetleri', icon: BedDouble },
  { id: 'knowledge', name: 'Bilgi Bankasi', icon: BookOpen },
  { id: 'menu', name: 'Restoran Menu', icon: UtensilsCrossed },
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
};

export default function App() {
  const [page, setPage] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const PageComponent = PAGES[page] || Dashboard;

  return (
    <div className="flex h-screen bg-[#0a0a0f]" data-testid="app-root">
      {/* Sidebar */}
      <motion.aside
        animate={{ width: sidebarOpen ? 260 : 72 }}
        className="bg-[#0f0f14] border-r border-[#C4972A]/10 flex flex-col relative z-20"
        data-testid="sidebar"
      >
        {/* Logo */}
        <div className="p-4 border-b border-[#C4972A]/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#C4972A] to-[#8a5f1a] flex items-center justify-center flex-shrink-0 animate-pulse-gold">
              <span className="text-white font-bold text-lg" style={{fontFamily: 'var(--font-heading)'}}>K</span>
            </div>
            <AnimatePresence>
              {sidebarOpen && (
                <motion.div
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                >
                  <h1 className="text-base font-bold text-[#C4972A]" style={{fontFamily: 'var(--font-heading)'}}>
                    Kozbeyli Konagi
                  </h1>
                  <p className="text-xs text-[#7e7e8a]">Otel Yonetim Sistemi</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = page === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setPage(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                  active
                    ? 'bg-[#C4972A]/15 text-[#C4972A] gold-glow'
                    : 'text-[#a9a9b2] hover:bg-white/5 hover:text-[#e5e5e8]'
                }`}
                data-testid={`nav-${item.id}`}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                <AnimatePresence>
                  {sidebarOpen && (
                    <motion.span
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                      className="text-sm font-medium truncate"
                    >
                      {item.name}
                    </motion.span>
                  )}
                </AnimatePresence>
              </button>
            );
          })}
        </nav>

        {/* Toggle */}
        <div className="p-3 border-t border-[#C4972A]/10">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-full flex items-center justify-center p-2.5 rounded-lg bg-white/5 hover:bg-[#C4972A]/10 transition-all text-[#a9a9b2] hover:text-[#C4972A]"
            data-testid="sidebar-toggle"
          >
            {sidebarOpen ? <ChevronLeft className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </motion.aside>

      {/* Main */}
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
