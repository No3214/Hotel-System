import React, { useState, useEffect, useRef } from 'react';
import { getDashboardStats } from '../api';
import { Badge } from '../components/ui/badge';
import { useLanguage } from '../hooks/useLanguage';
import {
  BedDouble, Users, CheckSquare, Calendar, Star, TrendingUp,
  Clock, ArrowDownRight, ArrowUpRight, RefreshCw, Activity,
  DoorOpen, DoorClosed, Zap
} from 'lucide-react';

const ROOM_STATUS_COLORS = {
  available: { bg: 'bg-emerald-500/15', text: 'text-emerald-400', dot: 'bg-emerald-400' },
  occupied: { bg: 'bg-blue-500/15', text: 'text-blue-400', dot: 'bg-blue-400' },
  maintenance: { bg: 'bg-amber-500/15', text: 'text-amber-400', dot: 'bg-amber-400' },
  cleaning: { bg: 'bg-purple-500/15', text: 'text-purple-400', dot: 'bg-purple-400' },
};

export default function Dashboard({ onNavigate }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const intervalRef = useRef(null);
  const { t } = useLanguage();

  const fetchStats = async (isManual = false) => {
    if (isManual) setRefreshing(true);
    try {
      const r = await getDashboardStats();
      setStats(r.data);
      setLastUpdate(new Date());
    } catch (e) { console.error(e); }
    setLoading(false);
    if (isManual) setTimeout(() => setRefreshing(false), 500);
  };

  useEffect(() => {
    fetchStats();
    intervalRef.current = setInterval(() => fetchStats(), 30000);
    return () => clearInterval(intervalRef.current);
  }, []);

  if (loading) {
    return (
      <div className="p-8 space-y-6">
        <div className="h-8 w-64 bg-white/5 rounded animate-pulse" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-24 bg-white/5 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const ratings = stats?.ratings || {};
  const weeklyTrend = stats?.weekly_trend || [];
  const maxOccupancy = Math.max(...weeklyTrend.map(d => d.rate), 1);

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="dashboard-page">
      {/* Header */}
      <div className="flex items-start justify-between animate-fade-in-up">
        <div>
          <h1 className="text-3xl lg:text-4xl font-bold text-[#C4972A]">Kozbeyli Konagi</h1>
          <p className="text-[#7e7e8a] mt-1">{t('hotel_management')}</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[10px] font-medium text-emerald-400 uppercase tracking-wider">{t('live')}</span>
          </div>
          <button
            onClick={() => fetchStats(true)}
            className="p-2 rounded-lg bg-white/5 hover:bg-[#C4972A]/10 transition-all text-[#7e7e8a] hover:text-[#C4972A]"
            data-testid="refresh-dashboard"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Top KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 animate-fade-in-up" style={{ animationDelay: '0.05s' }}>
        <KPICard icon={BedDouble} label={t('occupancy_rate')} value={`${stats?.occupancy_rate || 0}%`}
          sub={`${stats?.occupied_rooms || 0}/${stats?.total_rooms || 0}`} color="#C4972A" onClick={() => onNavigate?.('rooms')} />
        <KPICard icon={DoorOpen} label={t('todays_checkins')} value={stats?.todays_checkins || 0}
          sub={t('today')} color="#22c55e" onClick={() => onNavigate?.('reservations')} />
        <KPICard icon={DoorClosed} label={t('todays_checkouts')} value={stats?.todays_checkouts || 0}
          sub={t('today')} color="#f59e0b" onClick={() => onNavigate?.('reservations')} />
        <KPICard icon={TrendingUp} label={t('monthly_revenue')} value={`${(stats?.monthly_revenue || 0).toLocaleString('tr-TR')} TL`}
          sub={t('this_month')} color="#6366f1" />
      </div>

      {/* Occupancy Bar */}
      <div className="glass rounded-xl p-5 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-[#a9a9b2]">{t('occupancy_rate')}</span>
          <span className="text-2xl font-bold text-[#C4972A]">{stats?.occupancy_rate || 0}%</span>
        </div>
        <div className="w-full bg-[#1a1a22] rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-[#C4972A] to-[#dfa04e] h-3 rounded-full transition-all duration-1000"
            style={{ width: `${stats?.occupancy_rate || 0}%` }}
          />
        </div>
        <div className="flex justify-between mt-2 text-xs text-[#7e7e8a]">
          <span>{stats?.occupied_rooms || 0} {t('occupied').toLowerCase()}</span>
          <span>{stats?.available_rooms || 0} {t('available').toLowerCase()}</span>
          <span>{stats?.total_rooms || 16} {t('total').toLowerCase()}</span>
        </div>
      </div>

      {/* Middle Grid: Stats + Weekly Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stats */}
        <div className="grid grid-cols-2 gap-3 lg:col-span-1">
          <MiniStat icon={Users} label={t('guests')} value={stats?.total_guests || 0} color="#6366f1" onClick={() => onNavigate?.('guests')} />
          <MiniStat icon={Calendar} label={t('reservations')} value={stats?.total_reservations || 0} color="#ec4899" onClick={() => onNavigate?.('reservations')} />
          <MiniStat icon={CheckSquare} label={t('pending')} value={stats?.pending_tasks || 0} color="#f59e0b" onClick={() => onNavigate?.('tasks')} />
          <MiniStat icon={Calendar} label={t('events')} value={stats?.active_events || 0} color="#14b8a6" onClick={() => onNavigate?.('events')} />
          <MiniStat icon={BedDouble} label={t('cleaning')} value={stats?.housekeeping_pending || 0} color="#8b5cf6" onClick={() => onNavigate?.('housekeeping')} />
          <MiniStat icon={TrendingUp} label={t('revenue')} value={`${((stats?.total_revenue || 0) / 1000).toFixed(0)}K`} color="#C4972A" />
        </div>

        {/* Weekly Trend Chart */}
        <div className="glass rounded-xl p-5 lg:col-span-2">
          <h3 className="text-sm font-semibold text-[#C4972A] mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4" /> {t('weekly_trend')}
          </h3>
          <div className="flex items-end gap-2 h-40">
            {weeklyTrend.map((day, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <span className="text-[10px] text-[#C4972A] font-medium">{day.rate}%</span>
                <div className="w-full bg-[#1a1a22] rounded-t-md relative" style={{ height: '120px' }}>
                  <div
                    className="absolute bottom-0 left-0 right-0 rounded-t-md transition-all duration-700"
                    style={{
                      height: `${Math.max((day.rate / Math.max(maxOccupancy, 1)) * 100, 4)}%`,
                      background: day.rate > 70
                        ? 'linear-gradient(to top, #C4972A, #dfa04e)'
                        : day.rate > 40
                          ? 'linear-gradient(to top, #6366f1, #818cf8)'
                          : 'linear-gradient(to top, #3b3b4f, #5a5a6f)',
                    }}
                  />
                </div>
                <span className="text-[10px] text-[#7e7e8a]">{day.day}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Grid: Room Map + Ratings + Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Room Status Grid */}
        <div className="glass rounded-xl p-5 lg:col-span-1">
          <h3 className="text-sm font-semibold text-[#C4972A] mb-3 flex items-center gap-2">
            <BedDouble className="w-4 h-4" /> {t('room_status')}
          </h3>
          <div className="grid grid-cols-4 gap-1.5 mb-3">
            {(stats?.rooms_list || []).map((room) => {
              const st = room.status || 'available';
              const colors = ROOM_STATUS_COLORS[st] || ROOM_STATUS_COLORS.available;
              return (
                <div
                  key={room.room_id}
                  className={`${colors.bg} rounded-md p-1.5 text-center cursor-pointer hover:scale-105 transition-transform`}
                  title={`${room.name_tr || room.room_id} - ${st}`}
                  data-testid={`room-cell-${room.room_id}`}
                >
                  <span className={`text-[10px] font-bold ${colors.text}`}>
                    {(room.name_tr || room.room_id || '').substring(0, 12)}
                  </span>
                </div>
              );
            })}
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(ROOM_STATUS_COLORS).map(([key, colors]) => (
              <div key={key} className="flex items-center gap-1">
                <div className={`w-2 h-2 rounded-full ${colors.dot}`} />
                <span className="text-[9px] text-[#7e7e8a] capitalize">{t(key) || key}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Platform Ratings */}
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-semibold text-[#C4972A] mb-3 flex items-center gap-2">
            <Star className="w-4 h-4" /> {t('platform_ratings')}
          </h3>
          <div className="space-y-2">
            {Object.entries(ratings).map(([platform, data]) => (
              <div key={platform} className="flex items-center justify-between p-2.5 bg-white/5 rounded-lg">
                <span className="text-xs capitalize text-[#a9a9b2]">{platform.replace('_', '.')}</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 bg-[#1a1a22] rounded-full h-1.5">
                    <div
                      className="bg-[#C4972A] h-1.5 rounded-full"
                      style={{ width: `${((data.score || 0) / (data.max || 10)) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-bold text-[#C4972A] w-8 text-right">{data.score}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-semibold text-[#C4972A] mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4" /> {t('recent_activity')}
          </h3>
          <div className="space-y-2">
            {(stats?.recent_reservations || []).slice(0, 4).map((res) => (
              <div key={res.id} className="flex items-center gap-2 p-2 bg-white/5 rounded-lg">
                <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                  res.status === 'checked_in' ? 'bg-green-400' :
                  res.status === 'confirmed' ? 'bg-blue-400' :
                  res.status === 'checked_out' ? 'bg-amber-400' : 'bg-gray-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-[#e5e5e8] truncate">{res.guest_name || 'Misafir'}</p>
                  <p className="text-[10px] text-[#5a5a65]">{res.room_id} | {res.check_in}</p>
                </div>
                <Badge className="text-[9px] bg-white/5 text-[#7e7e8a]">
                  {t(res.status) || res.status}
                </Badge>
              </div>
            ))}
            {(stats?.recent_tasks || []).slice(0, 3).map((task) => (
              <div key={task.id} className="flex items-center gap-2 p-2 bg-white/5 rounded-lg">
                <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                  task.priority === 'urgent' ? 'bg-red-500' :
                  task.priority === 'high' ? 'bg-orange-500' : 'bg-blue-500'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-[#e5e5e8] truncate">{task.title}</p>
                  <p className="text-[10px] text-[#5a5a65]">{task.source || 'gorev'}</p>
                </div>
                <Badge className="text-[9px] bg-white/5 text-[#7e7e8a]">{task.status}</Badge>
              </div>
            ))}
            {(!stats?.recent_reservations?.length && !stats?.recent_tasks?.length) && (
              <p className="text-xs text-[#7e7e8a] text-center py-4">{t('no_data')}</p>
            )}
          </div>
        </div>
      </div>

      {/* Footer timestamp */}
      {lastUpdate && (
        <div className="flex items-center justify-end gap-1.5 text-[10px] text-[#5a5a65]">
          <Clock className="w-3 h-3" />
          <span>Son guncelleme: {lastUpdate.toLocaleTimeString('tr-TR')} (30s otomatik)</span>
        </div>
      )}
    </div>
  );
}

function KPICard({ icon: Icon, label, value, sub, color, onClick }) {
  return (
    <div
      className="glass rounded-xl p-4 hover:gold-glow transition-all duration-300 cursor-pointer group"
      onClick={onClick}
      data-testid={`kpi-${label}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-[10px] text-[#7e7e8a] uppercase tracking-wider mb-1">{label}</p>
          <p className="text-2xl font-bold" style={{ color }}>{value}</p>
          {sub && <p className="text-[10px] text-[#5a5a65] mt-0.5">{sub}</p>}
        </div>
        <div className="w-9 h-9 rounded-lg flex items-center justify-center opacity-60 group-hover:opacity-100 transition-opacity"
          style={{ background: `${color}15` }}>
          <Icon className="w-4 h-4" style={{ color }} />
        </div>
      </div>
    </div>
  );
}

function MiniStat({ icon: Icon, label, value, color, onClick }) {
  return (
    <div className="glass rounded-lg p-3 cursor-pointer hover:bg-white/5 transition-all" onClick={onClick}
      data-testid={`mini-stat-${label}`}>
      <div className="flex items-center gap-2">
        <Icon className="w-3.5 h-3.5" style={{ color }} />
        <span className="text-[10px] text-[#7e7e8a]">{label}</span>
      </div>
      <p className="text-lg font-bold mt-1" style={{ color }}>{value}</p>
    </div>
  );
}
