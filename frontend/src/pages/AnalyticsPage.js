import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, DollarSign, Users, BedDouble, BarChart3, Loader2 } from 'lucide-react';
import { getAnalyticsKPI, getRevenueTrend, getBookingSources, getOccupancyHeatmap, getRoomPerformance } from '../api';

function fmt(n) { return n?.toLocaleString('tr-TR') ?? '0'; }

const COLORS = ['#C4972A', '#7A8B6F', '#9CA3AF', '#D1D5DB', '#E5E7EB'];
const HEATMAP_COLORS = { high: 'bg-emerald-500', medium: 'bg-yellow-500', low: 'bg-orange-500', critical: 'bg-red-500/60' };

export default function AnalyticsPage() {
  const [kpi, setKPI] = useState(null);
  const [trend, setTrend] = useState(null);
  const [sources, setSources] = useState(null);
  const [heatmap, setHeatmap] = useState(null);
  const [roomPerf, setRoomPerf] = useState(null);
  const [loading, setLoading] = useState(true);
  const [trendPeriod, setTrendPeriod] = useState('30d');

  useEffect(() => { loadAll(); }, []);
  useEffect(() => { loadTrend(); }, [trendPeriod]);

  const loadAll = async () => {
    setLoading(true);
    try {
      const results = await Promise.allSettled([
        getAnalyticsKPI(),
        getBookingSources(),
        getOccupancyHeatmap(),
        getRoomPerformance(),
      ]);
      if (results[0].status === 'fulfilled') setKPI(results[0].value.data);
      if (results[1].status === 'fulfilled') setSources(results[1].value.data);
      if (results[2].status === 'fulfilled') setHeatmap(results[2].value.data);
      if (results[3].status === 'fulfilled') setRoomPerf(results[3].value.data);
      results.filter(r => r.status === 'rejected').forEach(r => console.error('Analytics load error:', r.reason));
      await loadTrend();
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const loadTrend = async () => {
    try {
      const res = await getRevenueTrend(trendPeriod);
      setTrend(res.data);
    } catch (e) { console.error(e); }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <Loader2 className="w-8 h-8 animate-spin text-[#C4972A]" />
    </div>
  );

  return (
    <div className="p-6 space-y-6" data-testid="analytics-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Analitik & Raporlama</h1>
          <p className="text-sm text-[#7e7e8a] mt-1">KPI'lar, trendler ve performans analizi</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-[#7e7e8a]">
          <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
          <span>Canli</span>
        </div>
      </div>

      {/* KPI Cards */}
      {kpi && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" data-testid="analytics-kpi-cards">
          <KPICard title="Gunluk Gelir" value={kpi.daily_revenue.value} currency="TRY" change={kpi.daily_revenue.change_percent} trend={kpi.daily_revenue.trend} icon={DollarSign} />
          <KPICard title="Doluluk Orani" value={kpi.occupancy_rate.value} suffix="%" change={kpi.occupancy_rate.change_percent} trend={kpi.occupancy_rate.trend} icon={Users} />
          <KPICard title="ADR" value={kpi.adr.value} currency="TRY" change={kpi.adr.change_percent} trend={kpi.adr.trend} icon={BedDouble} />
          <KPICard title="RevPAR" value={kpi.revpar.value} currency="TRY" change={kpi.revpar.change_percent} trend={kpi.revpar.trend} icon={BarChart3} />
        </div>
      )}

      {/* Revenue Trend */}
      {trend && (
        <div className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-6" data-testid="revenue-trend">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Gelir Trendi</h2>
            <div className="flex gap-2">
              {['7d', '30d', '90d'].map(p => (
                <button key={p} onClick={() => setTrendPeriod(p)}
                  className={`px-3 py-1 text-xs rounded-lg ${trendPeriod === p ? 'bg-[#C4972A] text-black' : 'bg-white/5 text-[#a9a9b2] hover:bg-white/10'}`}
                  data-testid={`trend-period-${p}`}>
                  {p === '7d' ? '7 Gun' : p === '30d' ? '30 Gun' : '90 Gun'}
                </button>
              ))}
            </div>
          </div>
          <div className="flex gap-4 mb-3 text-xs text-[#7e7e8a]">
            <span>Toplam: <span className="text-[#C4972A] font-medium">{fmt(trend.total)} TL</span></span>
            <span>Ortalama: <span className="text-white font-medium">{fmt(Math.round(trend.average))} TL</span></span>
          </div>
          <div className="flex items-end gap-px h-32" data-testid="trend-chart">
            {(trend.data || []).map((d, i) => {
              const maxR = Math.max(...trend.data.map(x => x.revenue), 1);
              const h = Math.max(2, (d.revenue / maxR) * 100);
              return (
                <div key={i} className="flex-1 flex flex-col items-center justify-end"
                  title={`${d.date}: ${fmt(d.revenue)} TL`}>
                  <div className="w-full bg-[#C4972A]/50 hover:bg-[#C4972A] rounded-t transition-colors" style={{ height: `${h}%` }} />
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Booking Sources */}
        {sources && (
          <div className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-6" data-testid="booking-sources">
            <h2 className="text-lg font-semibold text-white mb-4">Rezervasyon Kaynaklari</h2>
            <div className="space-y-3">
              {(sources.sources || []).map((s, i) => (
                <div key={s.name} className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                  <div className="flex-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-white capitalize">{s.name}</span>
                      <span className="text-[#7e7e8a]">{s.bookings} rez. ({s.bookings_percent}%)</span>
                    </div>
                    <div className="w-full bg-white/5 rounded-full h-1.5 mt-1">
                      <div className="h-1.5 rounded-full transition-all" style={{ width: `${s.bookings_percent}%`, backgroundColor: COLORS[i % COLORS.length] }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Room Performance */}
        {roomPerf && (
          <div className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-6" data-testid="room-performance">
            <h2 className="text-lg font-semibold text-white mb-4">Oda Performansi</h2>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {(roomPerf.rooms || []).slice(0, 10).map(r => (
                <div key={r.room_id} className="flex items-center justify-between py-2 px-3 bg-white/[0.02] rounded-lg">
                  <div>
                    <span className="text-sm text-white">{r.room_name || r.room_id}</span>
                    <span className="text-xs text-[#7e7e8a] ml-2">{r.room_type}</span>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-[#C4972A]">{fmt(r.total_revenue)} TL</p>
                    <p className="text-xs text-[#7e7e8a]">%{r.occupancy_rate} doluluk</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Occupancy Heatmap */}
      {heatmap && (
        <div className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-6" data-testid="occupancy-heatmap">
          <h2 className="text-lg font-semibold text-white mb-4">Doluluk Isi Haritasi - {heatmap.year}</h2>
          <div className="space-y-1">
            {(heatmap.heatmap || []).map(month => (
              <div key={month.month} className="flex items-center gap-2">
                <span className="w-8 text-xs text-[#7e7e8a] font-medium">{month.month_name}</span>
                <div className="flex gap-0.5 flex-wrap">
                  {(month.days || []).map(day => (
                    <div key={day.day}
                      className={`w-2.5 h-2.5 rounded-sm ${HEATMAP_COLORS[day.level] || 'bg-gray-700'} hover:ring-1 hover:ring-white/30 cursor-default transition-all`}
                      title={`${day.day} ${month.month_name}: %${day.occupancy}`} />
                  ))}
                </div>
              </div>
            ))}
          </div>
          <div className="flex gap-4 mt-3 text-xs text-[#7e7e8a]">
            <div className="flex items-center gap-1"><div className="w-2.5 h-2.5 bg-emerald-500 rounded-sm" /> %80-100</div>
            <div className="flex items-center gap-1"><div className="w-2.5 h-2.5 bg-yellow-500 rounded-sm" /> %60-80</div>
            <div className="flex items-center gap-1"><div className="w-2.5 h-2.5 bg-orange-500 rounded-sm" /> %40-60</div>
            <div className="flex items-center gap-1"><div className="w-2.5 h-2.5 bg-red-500/60 rounded-sm" /> %0-40</div>
          </div>
        </div>
      )}
    </div>
  );
}

function KPICard({ title, value, currency, suffix, change, trend, icon: Icon }) {
  const isUp = trend === 'up';
  const displayValue = currency ? `${fmt(value)} ${currency === 'TRY' ? 'TL' : currency}` : `${suffix || ''}${value}`;
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-4 hover:border-[#C4972A]/30 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <div className="p-2 bg-[#C4972A]/10 rounded-lg"><Icon className="w-5 h-5 text-[#C4972A]" /></div>
        {change !== 0 && (
          <div className={`flex items-center gap-1 text-xs font-medium ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>
            {isUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            <span>{change > 0 ? '+' : ''}{change}%</span>
          </div>
        )}
      </div>
      <p className="text-xs text-[#7e7e8a]">{title}</p>
      <p className="text-lg font-bold text-white mt-0.5">{displayValue}</p>
    </motion.div>
  );
}
