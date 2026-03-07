import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, DollarSign, Calendar, BarChart3, RefreshCw, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { getRevenueRoomTypes, calculateDynamicPrice, getPricingCalendar, getRevenueKPI, getRevenueForecast, updateAllPrices } from '../api';

const ROOM_TYPE_LABELS = {
  standart_deniz: 'Standart (Deniz)',
  standart_kara: 'Standart (Kara)',
  superior: 'Superior',
  uc_kisilik: '3 Kisilik',
  dort_kisilik: '4 Kisilik',
};

function fmt(n) { return n?.toLocaleString('tr-TR') ?? '0'; }

export default function RevenueManagementPage() {
  const [roomTypes, setRoomTypes] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState('standart_deniz');
  const [calendarData, setCalendarData] = useState(null);
  const [kpi, setKPI] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [calMonth, setCalMonth] = useState(() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
  });

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    loadCalendar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedRoom, calMonth]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [rtRes, kpiRes, fcRes] = await Promise.all([
        getRevenueRoomTypes(),
        getRevenueKPI(),
        getRevenueForecast(),
      ]);
      setRoomTypes(rtRes.data.room_types || []);
      setKPI(kpiRes.data);
      setForecast(fcRes.data);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const loadCalendar = async () => {
    try {
      const [year, month] = calMonth.split('-').map(Number);
      const from = `${year}-${String(month).padStart(2, '0')}-01`;
      const lastDay = new Date(year, month, 0).getDate();
      const to = `${year}-${String(month).padStart(2, '0')}-${lastDay}`;
      const res = await getPricingCalendar(selectedRoom, from, to);
      setCalendarData(res.data);
    } catch (e) { console.error(e); }
  };

  const handleUpdateAll = async () => {
    setUpdating(true);
    try {
      await updateAllPrices(90);
      await loadCalendar();
    } catch (e) { console.error(e); }
    setUpdating(false);
  };

  const shiftMonth = (dir) => {
    const [y, m] = calMonth.split('-').map(Number);
    const d = new Date(y, m - 1 + dir, 1);
    setCalMonth(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`);
  };

  const MONTH_TR = ['', 'Ocak', 'Subat', 'Mart', 'Nisan', 'Mayis', 'Haziran', 'Temmuz', 'Agustos', 'Eylul', 'Ekim', 'Kasim', 'Aralik'];
  const [calYear, calMon] = calMonth.split('-').map(Number);

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <Loader2 className="w-8 h-8 animate-spin text-[#C4972A]" />
    </div>
  );

  return (
    <div className="p-6 space-y-6" data-testid="revenue-management-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Gelir Yonetimi</h1>
          <p className="text-sm text-[#7e7e8a] mt-1">Dinamik fiyatlandirma ve gelir tahmini</p>
        </div>
        <button onClick={handleUpdateAll} disabled={updating}
          className="flex items-center gap-2 px-4 py-2 bg-[#C4972A] text-black rounded-lg font-medium hover:bg-[#d4a73a] transition-colors disabled:opacity-50"
          data-testid="update-all-prices-btn">
          <RefreshCw className={`w-4 h-4 ${updating ? 'animate-spin' : ''}`} />
          {updating ? 'Guncelleniyor...' : '90 Gun Fiyat Guncelle'}
        </button>
      </div>

      {/* KPI Cards */}
      {kpi && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" data-testid="revenue-kpi-cards">
          <KPICard title="Toplam Gelir" value={`${fmt(kpi.total_revenue)} TL`} change={kpi.revenue_change_percent} icon={DollarSign} />
          <KPICard title="Doluluk Orani" value={`%${kpi.occupancy_rate}`} change={0} icon={BarChart3} />
          <KPICard title="ADR" value={`${fmt(kpi.adr)} TL`} change={0} icon={TrendingUp} />
          <KPICard title="RevPAR" value={`${fmt(kpi.revpar)} TL`} change={0} icon={Calendar} />
        </div>
      )}

      {/* Room Type Selector */}
      <div className="flex flex-wrap gap-2" data-testid="room-type-selector">
        {roomTypes.map(rt => (
          <button key={rt.key} onClick={() => setSelectedRoom(rt.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedRoom === rt.key
                ? 'bg-[#C4972A] text-black'
                : 'bg-[#1a1a22] text-[#a9a9b2] border border-[#C4972A]/10 hover:border-[#C4972A]/30'
            }`}
            data-testid={`room-type-${rt.key}`}>
            {ROOM_TYPE_LABELS[rt.key] || rt.key} ({fmt(rt.base_price)} TL)
          </button>
        ))}
      </div>

      {/* Calendar Navigation */}
      <div className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-6" data-testid="pricing-calendar">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Fiyat Takvimi</h2>
          <div className="flex items-center gap-3">
            <button onClick={() => shiftMonth(-1)} className="p-1.5 rounded-lg bg-white/5 hover:bg-[#C4972A]/10 text-[#a9a9b2]">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-white font-medium min-w-[120px] text-center">{MONTH_TR[calMon]} {calYear}</span>
            <button onClick={() => shiftMonth(1)} className="p-1.5 rounded-lg bg-white/5 hover:bg-[#C4972A]/10 text-[#a9a9b2]">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {calendarData && calendarData.summary && (
          <div className="flex gap-6 mb-4 text-xs text-[#7e7e8a]">
            <span>Min: <span className="text-emerald-400 font-medium">{fmt(calendarData.summary.min_price)} TL</span></span>
            <span>Maks: <span className="text-red-400 font-medium">{fmt(calendarData.summary.max_price)} TL</span></span>
            <span>Ort: <span className="text-[#C4972A] font-medium">{fmt(calendarData.summary.avg_price)} TL</span></span>
          </div>
        )}

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-1">
          {['Pzt', 'Sal', 'Car', 'Per', 'Cum', 'Cmt', 'Paz'].map(d => (
            <div key={d} className="text-center text-xs text-[#7e7e8a] py-1 font-medium">{d}</div>
          ))}
          {calendarData?.prices && (() => {
            const firstDay = new Date(calYear, calMon - 1, 1).getDay();
            const offset = firstDay === 0 ? 6 : firstDay - 1;
            const cells = [];
            for (let i = 0; i < offset; i++) cells.push(<div key={`e-${i}`} />);
            calendarData.prices.forEach((p) => {
              const day = parseInt(p.date.split('-')[2]);
              const mult = p.total_multiplier;
              let bg = 'bg-[#1a1a22]';
              if (mult >= 1.5) bg = 'bg-red-900/40 border-red-500/30';
              else if (mult >= 1.2) bg = 'bg-orange-900/30 border-orange-500/20';
              else if (mult >= 1.0) bg = 'bg-[#1a1a22] border-[#C4972A]/10';
              else bg = 'bg-emerald-900/20 border-emerald-500/20';

              cells.push(
                <div key={p.date} className={`${bg} border rounded-lg p-1.5 text-center cursor-default hover:border-[#C4972A]/40 transition-colors`}
                  title={`${p.date}\nBaz: ${p.base_price} TL\nDinamik: ${p.dynamic_price} TL\nCarpan: ${mult}x`}>
                  <div className="text-xs text-[#7e7e8a]">{day}</div>
                  <div className="text-xs font-bold text-white">{fmt(p.dynamic_price)}</div>
                  <div className={`text-[10px] ${mult >= 1.0 ? 'text-[#C4972A]' : 'text-emerald-400'}`}>
                    {mult >= 1.0 ? '+' : ''}{Math.round((mult - 1) * 100)}%
                  </div>
                </div>
              );
            });
            return cells;
          })()}
        </div>
      </div>

      {/* Forecast */}
      {forecast && (
        <div className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-6" data-testid="revenue-forecast">
          <h2 className="text-lg font-semibold text-white mb-4">30 Gunluk Gelir Tahmini</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="bg-[#1a1a22] rounded-lg p-3">
              <p className="text-xs text-[#7e7e8a]">Tahmini Toplam Gelir</p>
              <p className="text-lg font-bold text-[#C4972A]">{fmt(forecast.total_predicted_revenue)} TL</p>
            </div>
            <div className="bg-[#1a1a22] rounded-lg p-3">
              <p className="text-xs text-[#7e7e8a]">Gunluk Ortalama</p>
              <p className="text-lg font-bold text-white">{fmt(forecast.average_daily_revenue)} TL</p>
            </div>
          </div>
          {/* Mini chart - daily bars */}
          <div className="flex items-end gap-0.5 h-24 mt-2" data-testid="forecast-chart">
            {(forecast.daily_forecasts || []).slice(0, 30).map((d, i) => {
              const maxRev = Math.max(...forecast.daily_forecasts.map(f => f.predicted_revenue), 1);
              const h = Math.max(4, (d.predicted_revenue / maxRev) * 100);
              return (
                <div key={i} className="flex-1 flex flex-col items-center justify-end" title={`${d.date}: ${fmt(d.predicted_revenue)} TL`}>
                  <div className="w-full bg-[#C4972A]/60 rounded-t hover:bg-[#C4972A] transition-colors" style={{ height: `${h}%` }} />
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function KPICard({ title, value, change, icon: Icon }) {
  const isUp = change >= 0;
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-4 hover:border-[#C4972A]/30 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <div className="p-2 bg-[#C4972A]/10 rounded-lg">
          <Icon className="w-5 h-5 text-[#C4972A]" />
        </div>
        {change !== 0 && (
          <div className={`flex items-center gap-1 text-xs font-medium ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>
            {isUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            <span>{change > 0 ? '+' : ''}{change}%</span>
          </div>
        )}
      </div>
      <p className="text-xs text-[#7e7e8a]">{title}</p>
      <p className="text-lg font-bold text-white mt-0.5">{value}</p>
    </motion.div>
  );
}
