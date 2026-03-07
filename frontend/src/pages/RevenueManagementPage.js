import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, DollarSign, Calendar, BarChart3, RefreshCw, ChevronLeft, ChevronRight, Loader2, Sparkles, MapPin, Target, Zap } from 'lucide-react';
import { getRevenueRoomTypes, calculateDynamicPrice, getPricingCalendar, getRevenueKPI, getRevenueForecast, updateAllPrices, getRevenueAIInsights, simulateRevenueStrategy } from '../api';

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
  const [aiInsights, setAiInsights] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  
  // Simulator State
  const [simLoading, setSimLoading] = useState(false);
  const [simPercent, setSimPercent] = useState(0);
  const [simResult, setSimResult] = useState(null);

  // Market Intel State
  const [intelLoading, setIntelLoading] = useState(false);
  const [marketIntel, setMarketIntel] = useState(null);

  const loadMarketIntel = async () => {
    setIntelLoading(true);
    try {
      const { getAIMarketIntel } = require('../api');
      const res = await getAIMarketIntel();
      if (res.data?.success) {
        setMarketIntel(res.data);
      }
    } catch (e) {
      console.error(e);
      alert("Pazar analizi alinamadi.");
    }
    setIntelLoading(false);
  };

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

  const loadAiInsights = async () => {
    setAiLoading(true);
    try {
      const res = await getRevenueAIInsights();
      setAiInsights(res.data.insights);
    } catch (e) {
      console.error(e);
      setAiInsights("Yapay zeka analizine su an ulasilamiyor.");
    }
    setAiLoading(false);
  };

  const handleSimulate = async () => {
    if (simPercent === 0) return;
    setSimLoading(true);
    setSimResult(null);
    try {
      const res = await simulateRevenueStrategy(simPercent);
      if (res.data.simulation) {
        setSimResult(res.data.simulation);
      }
    } catch (e) {
      console.error(e);
      alert("AI Simulasyon hatasi.");
    }
    setSimLoading(false);
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

      {/* AI Features Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* AI Insights Section */}
        <div className="bg-[#12121a] border border-[#2A9D8F]/20 rounded-xl p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-[#2A9D8F]/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
          <div className="flex items-center justify-between mb-4 relative z-10">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-[#2A9D8F]/20 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-[#2A9D8F]" />
              </div>
              <h2 className="text-lg font-semibold text-[#2A9D8F]">Gemini AI Fiyatlandirma Onerileri</h2>
            </div>
            <button
              onClick={loadAiInsights}
              disabled={aiLoading}
              className="text-sm px-4 py-1.5 rounded-lg bg-[#2A9D8F]/10 text-[#2A9D8F] hover:bg-[#2A9D8F]/20 transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              {aiLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              {aiInsights ? 'Yeniden Analiz Et' : 'Analizi Baslat'}
            </button>
          </div>
          
          <div className="relative z-10 text-sm">
            {aiLoading ? (
              <div className="flex items-center gap-3 text-[#7e7e8a] py-4">
                <span className="flex gap-1">
                  <span className="w-2 h-2 bg-[#2A9D8F] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-[#2A9D8F] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-[#2A9D8F] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </span>
                Gemini verilerinizi inceliyor ve stratejik oneriler uretiyor...
              </div>
            ) : aiInsights ? (
              <div className="p-4 bg-[#1a1a22] rounded-lg border border-[#2A9D8F]/10 text-[#e5e5e8] whitespace-pre-wrap leading-relaxed">
                {aiInsights}
              </div>
            ) : (
              <p className="text-[#7e7e8a] italic">Satislarinizi maksimize etmek icin 'Analizi Baslat' butonuna basin.</p>
            )}
          </div>
        </div>

        {/* AI Simulator Section */}
        <div className="bg-[#12121a] border border-blue-500/20 rounded-xl p-6 relative overflow-hidden flex flex-col">
          <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
          <div className="flex items-center gap-2 mb-4 relative z-10">
            <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
              <BarChart3 className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-blue-400">Yapay Zeka Strateji Simülatörü</h2>
              <p className="text-xs text-gray-400">Oda fiyatlarini degistirirseniz ne olur?</p>
            </div>
          </div>

          <div className="flex-1 relative z-10 flex flex-col gap-4">
            <div className="flex items-center gap-4 bg-[#1a1a22] p-4 rounded-lg border border-white/5">
              <div className="flex-1">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-400">Indirim Yap</span>
                  <span className="text-white font-bold">{simPercent > 0 ? '+' : ''}{simPercent}%</span>
                  <span className="text-gray-400">Zam Yap</span>
                </div>
                <input 
                  type="range" 
                  min="-50" max="50" step="5"
                  value={simPercent}
                  onChange={(e) => setSimPercent(parseInt(e.target.value))}
                  className="w-full accent-blue-500"
                />
              </div>
              <button 
                onClick={handleSimulate}
                disabled={simLoading || simPercent === 0}
                className="px-4 py-2 bg-blue-500/20 text-blue-400 font-medium rounded hover:bg-blue-500/30 disabled:opacity-50 transition-colors whitespace-nowrap"
              >
                {simLoading ? 'Hesaplaniyor...' : 'Simüle Et'}
              </button>
            </div>

            {simResult && (
              <div className="flex-1 bg-blue-500/5 border border-blue-500/20 rounded-lg p-4 grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-blue-300 mb-1">Yeni Tahmini Gelir</p>
                  <p className="text-xl font-bold text-white">{fmt(simResult.new_predicted_revenue)} TL</p>
                  <p className={`text-xs ${simResult.revenue_delta_percent.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
                    Fark: {simResult.revenue_delta_percent}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-blue-300 mb-1">Doluluk Etkisi</p>
                  <p className="text-lg font-semibold text-white">{simResult.predicted_occupancy_delta}</p>
                  <div className="mt-1 flex items-center gap-1">
                    <span className="text-[10px] uppercase text-gray-400 border border-white/10 px-1.5 py-0.5 rounded">
                      Risk: {simResult.risk_level}
                    </span>
                  </div>
                </div>
                <div className="col-span-2 text-sm text-gray-300 py-2 border-t border-blue-500/10 italic">
                  "{simResult.ai_advice}"
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI Market Intelligence Section (Phase 26) */}
      <div className="bg-[#12121a] border border-[#C4972A]/20 rounded-xl p-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-[#C4972A]/5 to-[#1a1a22] pointer-events-none" />
        <div className="flex items-center justify-between mb-4 relative z-10">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[#C4972A]/20 flex items-center justify-center">
              <Target className="w-4 h-4 text-[#C4972A]" />
            </div>
            <h2 className="text-lg font-semibold text-[#C4972A]">AI Pazar İZ & Rakip Analizi</h2>
          </div>
          <button
            onClick={loadMarketIntel}
            disabled={intelLoading}
            className="text-sm px-4 py-2 rounded-lg bg-[#C4972A] text-black font-semibold hover:bg-[#d4a73a] transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            {intelLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <MapPin className="w-4 h-4" />}
            {marketIntel ? 'Pazar Guncelle' : 'Pazar Analizi Yap'}
          </button>
        </div>

        {marketIntel && (
          <div className="relative z-10 grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            <div className="col-span-1 border-r border-white/5 pr-6 space-y-4">
              <h3 className="text-sm font-semibold text-white/80">Simüle Rakipler</h3>
              <div className="space-y-3">
                {marketIntel.competitors_data.map((comp, idx) => (
                  <div key={idx} className="bg-white/5 p-3 rounded-lg border border-white/5 flex justify-between items-center">
                    <div>
                      <p className="text-sm font-medium text-white">{comp.name}</p>
                      <p className="text-[10px] text-gray-400">{comp.distance_km} km - Doluluk: {comp.occupancy_est}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-[#C4972A]">{comp.current_rate} TL</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="col-span-2 space-y-4">
               <div className="grid grid-cols-2 gap-4">
                 <div className="bg-[#1a1a22] p-4 rounded-lg border border-white/5">
                   <p className="text-xs text-gray-400 mb-1">Pazar Konumlandırması (Positioning)</p>
                   <p className="text-emerald-400 font-medium text-sm">{marketIntel.intelligence.market_position}</p>
                 </div>
                 <div className="bg-[#1a1a22] p-4 rounded-lg border border-white/5">
                   <p className="text-xs text-gray-400 mb-1">Aksiyon Önerisi</p>
                   <p className="text-[#C4972A] font-bold text-lg">{marketIntel.intelligence.rate_adjustment_suggestion}</p>
                 </div>
               </div>
               
               <div className="bg-emerald-900/10 p-4 rounded-lg border border-emerald-500/20 mt-4">
                 <h4 className="text-xs font-semibold text-emerald-400 flex items-center gap-1 mb-2">
                   <Zap className="w-3 h-3"/> Strateji Özeti
                 </h4>
                 <p className="text-sm text-gray-300 leading-relaxed mb-4">{marketIntel.intelligence.recommended_strategy}</p>
                 
                 <h4 className="text-xs font-semibold text-emerald-400 flex items-center gap-1 mb-2">
                   <Target className="w-3 h-3"/> Alınabilir Aksiyonlar
                 </h4>
                 <ul className="list-disc list-inside text-sm text-gray-300 space-y-1">
                   {marketIntel.intelligence.actionable_insights.map((insight, idx) => (
                     <li key={idx}>{insight}</li>
                   ))}
                 </ul>
               </div>
            </div>
          </div>
        )}
      </div>

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
