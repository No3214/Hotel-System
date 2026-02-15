import React, { useState, useEffect } from 'react';
import { getDashboardStats } from '../api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import {
  BedDouble, Users, CheckSquare, Calendar, Star, TrendingUp,
  Sparkles, Clock, AlertCircle
} from 'lucide-react';

const STAT_CARDS = [
  { key: 'total_rooms', label: 'Toplam Oda', icon: BedDouble, color: '#C4972A' },
  { key: 'occupied_rooms', label: 'Dolu Oda', icon: BedDouble, color: '#22c55e' },
  { key: 'total_guests', label: 'Misafirler', icon: Users, color: '#6366f1' },
  { key: 'total_reservations', label: 'Rezervasyonlar', icon: Calendar, color: '#ec4899' },
  { key: 'pending_tasks', label: 'Bekleyen Gorevler', icon: CheckSquare, color: '#f59e0b' },
  { key: 'active_events', label: 'Aktif Etkinlikler', icon: Calendar, color: '#14b8a6' },
];

export default function Dashboard({ onNavigate }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardStats()
      .then(r => setStats(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8 space-y-6">
        <div className="h-8 w-64 bg-white/5 rounded animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-28 bg-white/5 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const ratings = stats?.ratings || {};

  return (
    <div className="p-6 lg:p-8 space-y-8 max-w-[1400px]" data-testid="dashboard-page">
      {/* Header */}
      <div className="animate-fade-in-up">
        <h1 className="text-3xl lg:text-4xl font-bold text-[#C4972A]">
          Kozbeyli Konagi
        </h1>
        <p className="text-[#7e7e8a] mt-1">Otel Yonetim Paneli</p>
      </div>

      {/* Occupancy Bar */}
      <div className="glass rounded-xl p-5 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-[#a9a9b2]">Doluluk Orani</span>
          <span className="text-2xl font-bold text-[#C4972A]">{stats?.occupancy_rate || 0}%</span>
        </div>
        <div className="w-full bg-[#1a1a22] rounded-full h-3">
          <div
            className="bg-gradient-to-r from-[#C4972A] to-[#dfa04e] h-3 rounded-full transition-all duration-1000"
            style={{ width: `${stats?.occupancy_rate || 0}%` }}
          />
        </div>
        <div className="flex justify-between mt-2 text-xs text-[#7e7e8a]">
          <span>{stats?.occupied_rooms || 0} dolu</span>
          <span>{stats?.available_rooms || 0} bos</span>
          <span>{stats?.total_rooms || 16} toplam</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {STAT_CARDS.map((card, i) => {
          const Icon = card.icon;
          const value = stats?.[card.key] ?? 0;
          return (
            <div
              key={card.key}
              className="glass rounded-xl p-5 hover:gold-glow transition-all duration-300 animate-fade-in-up cursor-pointer"
              style={{ animationDelay: `${0.1 + i * 0.05}s` }}
              onClick={() => {
                if (card.key === 'pending_tasks') onNavigate?.('tasks');
                if (card.key === 'total_guests') onNavigate?.('guests');
                if (card.key === 'active_events') onNavigate?.('events');
              }}
              data-testid={`stat-${card.key}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-[#7e7e8a] mb-1">{card.label}</p>
                  <p className="text-2xl font-bold" style={{ color: card.color }}>{value}</p>
                </div>
                <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `${card.color}20` }}>
                  <Icon className="w-5 h-5" style={{ color: card.color }} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Ratings & Recent Tasks */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Platform Ratings */}
        <div className="glass rounded-xl p-5">
          <h3 className="text-lg font-semibold text-[#C4972A] mb-4 flex items-center gap-2">
            <Star className="w-5 h-5" /> Platform Puanlari
          </h3>
          <div className="space-y-3">
            {Object.entries(ratings).map(([platform, data]) => (
              <div key={platform} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-sm capitalize">{platform.replace('_', '.')}</span>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold text-[#C4972A]">{data.score}</span>
                  <span className="text-xs text-[#7e7e8a]">/ {data.max || 10}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Tasks */}
        <div className="glass rounded-xl p-5">
          <h3 className="text-lg font-semibold text-[#C4972A] mb-4 flex items-center gap-2">
            <CheckSquare className="w-5 h-5" /> Son Gorevler
          </h3>
          <div className="space-y-2">
            {(stats?.recent_tasks || []).slice(0, 5).map((task) => (
              <div key={task.id} className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
                <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  task.priority === 'urgent' ? 'bg-red-500' :
                  task.priority === 'high' ? 'bg-orange-500' :
                  task.priority === 'normal' ? 'bg-blue-500' : 'bg-gray-500'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm truncate">{task.title}</p>
                  <p className="text-xs text-[#7e7e8a]">{task.source}</p>
                </div>
                <Badge variant="outline" className="text-xs border-[#C4972A]/30 text-[#C4972A]">
                  {task.status}
                </Badge>
              </div>
            ))}
            {(!stats?.recent_tasks || stats.recent_tasks.length === 0) && (
              <p className="text-sm text-[#7e7e8a] text-center py-4">Henuz gorev yok</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
