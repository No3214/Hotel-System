import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileText, CheckCircle, Clock, AlertCircle, TrendingUp, Upload } from 'lucide-react';
import { getDashboardStats } from '../api';

const StatCard = ({ icon: Icon, label, value, trend, color }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-bg-surface border border-white/5 rounded-xl p-6 card-hover"
    data-testid={`stat-${label.toLowerCase().replace(/\s/g, '-')}`}
  >
    <div className="flex items-center justify-between mb-4">
      <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${color} flex items-center justify-center`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      {trend && (
        <div className="flex items-center text-sm text-emerald-400">
          <TrendingUp className="w-4 h-4 mr-1" />
          <span>{trend}</span>
        </div>
      )}
    </div>
    <div className="text-3xl font-bold font-heading mb-1">{value}</div>
    <div className="text-sm text-gray-400">{label}</div>
  </motion.div>
);

const RecentActivity = ({ activities }) => (
  <div className="bg-bg-surface border border-white/5 rounded-xl p-6" data-testid="recent-activities">
    <h3 className="text-lg font-heading font-bold mb-4">Son Aktiviteler</h3>
    <div className="space-y-3">
      {activities.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>Henüz doküman yüklenmedi</p>
        </div>
      ) : (
        activities.map((activity, index) => (
          <motion.div
            key={activity.id || index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="flex items-center justify-between py-3 border-b border-white/5 last:border-0"
            data-testid="activity-item"
          >
            <div className="flex items-center space-x-3">
              <FileText className="w-5 h-5 text-indigo-400" />
              <div>
                <p className="text-sm font-medium">{activity.filename}</p>
                <p className="text-xs text-gray-500">
                  {new Date(activity.created_at).toLocaleString('tr-TR')}
                </p>
              </div>
            </div>
            <span className={`status-badge status-${activity.status}`}>
              {activity.status === 'completed' ? 'Tamamlandı' :
               activity.status === 'processing' ? 'İşleniyor' :
               activity.status === 'failed' ? 'Hata' : 'Bekliyor'}
            </span>
          </motion.div>
        ))
      )}
    </div>
  </div>
);

const Dashboard = ({ onNavigate }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getDashboardStats();
        setStats(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchStats();
    // Refresh every 10 seconds
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-red-400">Hata: {error}</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto" data-testid="dashboard-page">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-heading font-bold mb-2">
          Hoş Geldiniz 👋
        </h1>
        <p className="text-gray-400">Otel yönetim sisteminizin genel durumu</p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={FileText}
          label="Toplam Doküman"
          value={stats.total_documents}
          color="from-indigo-600 to-purple-600"
        />
        <StatCard
          icon={CheckCircle}
          label="İşlenen Doküman"
          value={stats.documents_processed}
          trend="+12%"
          color="from-emerald-600 to-teal-600"
        />
        <StatCard
          icon={Clock}
          label="Bekleyen Görev"
          value={stats.pending_tasks}
          color="from-amber-600 to-orange-600"
        />
        <StatCard
          icon={TrendingUp}
          label="Kalite Skoru"
          value={`${(stats.quality_score * 100).toFixed(0)}%`}
          color="from-blue-600 to-cyan-600"
        />
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activities */}
        <div className="lg:col-span-2">
          <RecentActivity activities={stats.recent_activities || []} />
        </div>

        {/* Quick Actions */}
        <div className="bg-bg-surface border border-white/5 rounded-xl p-6" data-testid="quick-actions">
          <h3 className="text-lg font-heading font-bold mb-4">Hızlı İşlemler</h3>
          <div className="space-y-3">
            <button
              onClick={() => onNavigate('upload')}
              className="w-full py-3 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 rounded-lg font-medium transition-all hover:scale-[1.02] flex items-center justify-center space-x-2"
              data-testid="btn-upload-document"
            >
              <Upload className="w-5 h-5" />
              <span>Doküman Yükle</span>
            </button>
            <button
              onClick={() => onNavigate('knowledge')}
              className="w-full py-3 px-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg font-medium transition-all"
              data-testid="btn-view-knowledge"
            >
              Bilgi Tabanı
            </button>
            <button
              onClick={() => onNavigate('tasks')}
              className="w-full py-3 px-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg font-medium transition-all"
              data-testid="btn-view-tasks"
            >
              Görevler
            </button>
          </div>

          {/* System Status */}
          <div className="mt-6 pt-6 border-t border-white/5">
            <h4 className="text-sm font-semibold mb-3">Sistem Durumu</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">API</span>
                <div className="flex items-center text-emerald-400">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 mr-2 animate-pulse"></div>
                  Aktif
                </div>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Database</span>
                <div className="flex items-center text-emerald-400">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 mr-2 animate-pulse"></div>
                  Bağlı
                </div>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">LLM Council</span>
                <div className="flex items-center text-emerald-400">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 mr-2 animate-pulse"></div>
                  Hazır
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
