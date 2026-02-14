import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import '@/App.css';
import '@/index.css';
import { LayoutDashboard, Upload, BookOpen, CheckSquare, MessageSquare, Menu, X } from 'lucide-react';

// Pages
import Dashboard from './pages/Dashboard';
import UploadPage from './pages/UploadPage';
import KnowledgeBasePage from './pages/KnowledgeBasePage';
import TasksPage from './pages/TasksPage';
import WhatsAppPage from './pages/WhatsAppPage';

const App = () => {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navigation = [
    { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload', name: 'Doküman Yükle', icon: Upload },
    { id: 'whatsapp', name: 'WhatsApp', icon: MessageSquare },
    { id: 'knowledge', name: 'Bilgi Tabanı', icon: BookOpen },
    { id: 'tasks', name: 'Görevler', icon: CheckSquare },
  ];

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard onNavigate={setCurrentPage} />;
      case 'upload':
        return <UploadPage />;
      case 'whatsapp':
        return <WhatsAppPage />;
      case 'knowledge':
        return <KnowledgeBasePage />;
      case 'tasks':
        return <TasksPage />;
      default:
        return <Dashboard onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="flex h-screen bg-bg-primary" data-testid="app-root">
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarOpen ? 280 : 80 }}
        className="bg-bg-surface border-r border-white/5 flex flex-col relative"
      >
        {/* Logo */}
        <div className="p-6 border-b border-white/5">
          <motion.div
            className="flex items-center space-x-3"
            animate={{ justifyContent: sidebarOpen ? 'flex-start' : 'center' }}
          >
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center flex-shrink-0">
              <span className="text-xl">📄</span>
            </div>
            <AnimatePresence>
              {sidebarOpen && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex flex-col"
                >
                  <span className="text-xl font-heading font-bold">VeriÇevir</span>
                  <span className="text-xs text-gray-500">Otel Yönetim AI</span>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            
            return (
              <motion.button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg'
                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                }`}
                data-testid={`nav-${item.id}`}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                <AnimatePresence>
                  {sidebarOpen && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="font-medium"
                    >
                      {item.name}
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.button>
            );
          })}
        </nav>

        {/* Toggle Button */}
        <div className="p-4 border-t border-white/5">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-full flex items-center justify-center p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-all"
            data-testid="btn-toggle-sidebar"
          >
            {sidebarOpen ? (
              <X className="w-5 h-5" />
            ) : (
              <Menu className="w-5 h-5" />
            )}
          </button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentPage}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
          >
            {renderPage()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
};

export default App;
