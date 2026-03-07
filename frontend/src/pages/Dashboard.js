import React, { useState, useEffect, useRef } from 'react';
import { getDashboardStats, getArrivalBriefings, getEnergyAIReport, getAIComplaintRadar } from '../api';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { useLanguage } from '../hooks/useLanguage';
import {
  BedDouble, Users, CheckSquare, Calendar, Star, TrendingUp,
  Clock, ArrowDownRight, ArrowUpRight, RefreshCw, Activity,
  DoorOpen, DoorClosed, Zap, Sparkles, MessageSquareHeart, Loader2, Leaf, Droplet, AlertTriangle
} from 'lucide-react';

const ROOM_STATUS_COLORS = {
  available: { bg: 'bg-emerald-500/15', text: 'text-emerald-400', dot: 'bg-emerald-400' },
  occupied: { bg: 'bg-blue-500/15', text: 'text-blue-400', dot: 'bg-blue-400' },
  maintenance: { bg: 'bg-amber-500/15', text: 'text-amber-400', dot: 'bg-amber-400' },
  cleaning: { bg: 'bg-purple-500/15', text: 'text-purple-400', dot: 'bg-purple-400' },
};

  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  
  // VIP Briefings state
  const [briefings, setBriefings] = useState([]);
  const [briefingsLoading, setBriefingsLoading] = useState(false);
  const [showBriefings, setShowBriefings] = useState(false);

  // Phase 10: Energy AI State
  const [energyReport, setEnergyReport] = useState(null);
  const [energyLoading, setEnergyLoading] = useState(false);
  const [showEnergy, setShowEnergy] = useState(false);

  // Phase 11: AI Complaint Radar State
  const [radarResults, setRadarResults] = useState([]);
  const [radarLoading, setRadarLoading] = useState(false);
  const [showRadar, setShowRadar] = useState(false);

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

  const loadBriefings = async () => {
    setBriefingsLoading(true);
    setShowBriefings(true);
    try {
       const res = await getArrivalBriefings();
       if (res.data?.success) setBriefings(res.data.briefings || []);
    } catch(e) { console.error("VIP Briefing load error", e); }
    setBriefingsLoading(false);
  };

  const loadEnergyReport = async () => {
    setEnergyLoading(true);
    setShowEnergy(true);
    try {
       const res = await getEnergyAIReport();
       if (res.data?.success) setEnergyReport(res.data);
    } catch(e) { console.error("Energy AI load error", e); }
    setEnergyLoading(false);
  };

  const loadComplaintRadar = async () => {
    setRadarLoading(true);
    setShowRadar(true);
    try {
       const res = await getAIComplaintRadar();
       if (res.data?.success) setRadarResults(res.data.radar_results || []);
    } catch(e) { console.error("Complaint Radar load error", e); }
    setRadarLoading(false);
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

      {/* VIP Arrival Briefings Panel (Phase 8) */}
      <div className="glass rounded-xl p-6 border border-[#C4972A]/20 relative overflow-hidden animate-fade-in-up" style={{ animationDelay: '0.15s' }}>
         <div className="absolute top-0 right-0 w-64 h-64 bg-[#C4972A]/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
         <div className="flex items-center justify-between mb-4 relative z-10">
            <div>
               <h3 className="text-lg font-bold text-[#C4972A] flex items-center gap-2">
                  <Sparkles className="w-5 h-5" /> VIP Misafir Karsilama Asistani
               </h3>
               <p className="text-xs text-[#a9a9b2] mt-1">
                  Bugun giris yapacak ({stats?.todays_checkins || 0}) misafir icin AI tarafindan hazirlanmis kisisellestirilmis karsilama brifingleri.
               </p>
            </div>
            <Button 
               onClick={loadBriefings} 
               disabled={briefingsLoading}
               className="bg-[#1a1a22] border border-[#C4972A]/30 hover:bg-[#C4972A]/10 text-[#C4972A] whitespace-nowrap"
            >
               {briefingsLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Sparkles className="w-4 h-4 mr-2" />}
               {briefings.length > 0 ? 'Brifingleri Yenile' : 'AI Brifingleri Getir'}
            </Button>
         </div>

         {showBriefings && (
            <div className="mt-6 space-y-4 relative z-10">
               {briefingsLoading ? (
                  <div className="flex items-center gap-2 text-[#7e7e8a] text-sm py-4">
                     <Loader2 className="w-4 h-4 animate-spin" /> AI gecmis misafir verilerini analiz ediyor (CRM)...
                  </div>
               ) : briefings.length === 0 ? (
                  <p className="text-[#7e7e8a] text-sm py-2">Bugun icin beklenen giris (check-in) basarisiz oldu veya kayit bulunamadi.</p>
               ) : (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                     {briefings.map(b => (
                        <div key={b.id} className="bg-[#12121a] border border-white/5 rounded-xl p-4 hover:border-[#C4972A]/20 transition-all">
                           <div className="flex justify-between items-start mb-3">
                              <div>
                                 <h4 className="text-[#e5e5e8] font-bold">{b.guest_name}</h4>
                                 <div className="flex items-center gap-2 mt-1">
                                    <Badge className="bg-[#C4972A]/10 text-[#C4972A] border-0 text-[10px]">{b.persona}</Badge>
                                    <span className="text-xs text-[#7e7e8a]">Oda: {b.room}</span>
                                 </div>
                              </div>
                           </div>
                           <div className="space-y-3">
                              <div className="bg-[#C4972A]/5 rounded-lg p-3 border-l-2 border-[#C4972A]">
                                 <p className="text-xs text-[#a9a9b2] flex items-center gap-1.5 mb-1.5 font-medium text-[#C4972A]">
                                    <MessageSquareHeart className="w-3.5 h-3.5" /> Nasil Karsilanmali?
                                 </p>
                                 <p className="text-sm text-[#e5e5e8] leading-relaxed">{b.greeting_advice}</p>
                              </div>
                              <div className="bg-emerald-500/5 rounded-lg p-2.5 border-l-2 border-emerald-500/30">
                                 <p className="text-[10px] font-medium text-emerald-400 mb-1 uppercase tracking-wider">AI Upsell Onerisi</p>
                                 <p className="text-xs text-[#a9a9b2]">{b.upsell}</p>
                              </div>
                           </div>
                        </div>
                     ))}
                  </div>
               )}
            </div>
         )}
      </div>

      {/* Phase 10: AI Green Hotel (Sustainability Panel) */}
      <div className="glass rounded-xl p-6 border border-emerald-500/20 relative overflow-hidden animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
         <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
         <div className="flex items-center justify-between mb-4 relative z-10">
            <div>
               <h3 className="text-lg font-bold text-emerald-400 flex items-center gap-2">
                  <Leaf className="w-5 h-5" /> Green Hotel AI: Enerji & Surdurulebilirlik Asistani
               </h3>
               <p className="text-xs text-[#a9a9b2] mt-1">
                  Gemini AI ile otel dolulugunu ve hava durumunu analiz ederek anlik enerji tasarrufu ve karbon emisyonunu azaltma rotalari uretin.
               </p>
            </div>
            <Button 
               onClick={loadEnergyReport} 
               disabled={energyLoading}
               className="bg-[#1a1a22] border border-emerald-500/30 hover:bg-emerald-500/10 text-emerald-400 whitespace-nowrap"
            >
               {energyLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Leaf className="w-4 h-4 mr-2" />}
               Tasarruf Raporu Taramasi Yap
            </Button>
         </div>

         {showEnergy && (
            <div className="mt-6 relative z-10">
               {energyLoading ? (
                  <div className="flex items-center gap-2 text-[#7e7e8a] text-sm py-4">
                     <Loader2 className="w-4 h-4 animate-spin" /> Gemini sensorleri, hava durumu ve rezervasyon haritasini sentezliyor...
                  </div>
               ) : energyReport?.report ? (
                  <div className="space-y-4">
                     <div className="flex items-center justify-between bg-emerald-950/20 border border-emerald-500/10 p-4 rounded-lg">
                       <div className="flex items-center gap-3">
                         <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center">
                           <Droplet className="w-5 h-5 text-emerald-400" />
                         </div>
                         <div>
                           <p className="text-xs text-[#7e7e8a]">Hava Durumu Bileseni</p>
                           <p className="text-sm font-medium text-emerald-100">{energyReport.report.weather_context || 'Sicak, acik hava'}</p>
                         </div>
                       </div>
                       <div className="text-right">
                         <p className="text-xs text-[#7e7e8a]">Olası Karbon Kazanımı</p>
                         <p className="text-xl font-bold text-emerald-400">~{energyReport.report.carbon_saving_estimate_kg} kg CO₂</p>
                       </div>
                     </div>
                     
                     <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                       {energyReport.report.actions?.map((act, i) => (
                         <div key={i} className="bg-[#12121a] border border-white/5 rounded-xl p-4 hover:border-emerald-500/20 transition-all">
                           <h4 className="text-emerald-300 font-bold mb-2 flex items-center gap-2">
                             <Zap className="w-4 h-4" /> {act.title}
                           </h4>
                           <p className="text-xs text-[#e5e5e8] leading-relaxed mb-3 h-12 overflow-y-auto pr-1 custom-scrollbar">
                             {act.description}
                           </p>
                           <Badge className="bg-white/5 text-[#a9a9b2] border-0 text-[10px]">Dep: {act.department?.toUpperCase()}</Badge>
                         </div>
                       ))}
                     </div>
                  </div>
               ) : (
                  <p className="text-[#7e7e8a] text-sm py-2">Henuz bir rapor uretilemedi. Lutfen tekrar deneyin.</p>
               )}
            </div>
         )}
      </div>

      {/* Phase 11: AI Complaint & Churn Radar */}
      <div className="glass rounded-xl p-6 border border-red-500/20 relative overflow-hidden animate-fade-in-up" style={{ animationDelay: '0.25s' }}>
         <div className="absolute top-0 right-0 w-64 h-64 bg-red-500/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
         <div className="flex items-center justify-between mb-4 relative z-10">
            <div>
               <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" /> Çıkış Öncesi Risk Radarı (AI Complaint Predictor)
               </h3>
               <p className="text-xs text-[#a9a9b2] mt-1">
                  Şu an otelde konaklayan misafirlerin şikayet ve görev geçmişlerini analiz ederek memnuniyetsizlik riskini tahmin edin.
               </p>
            </div>
            <Button 
               onClick={loadComplaintRadar} 
               disabled={radarLoading}
               className="bg-[#1a1a22] border border-red-500/30 hover:bg-red-500/10 text-red-400 whitespace-nowrap"
            >
               {radarLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <AlertTriangle className="w-4 h-4 mr-2" />}
               Riski Analiz Et
            </Button>
         </div>

         {showRadar && (
            <div className="mt-6 relative z-10">
               {radarLoading ? (
                  <div className="flex items-center gap-2 text-[#7e7e8a] text-sm py-4">
                     <Loader2 className="w-4 h-4 animate-spin" /> AI, aktif konaklamalardaki görev etkileşimlerini (CX) tarıyor...
                  </div>
               ) : radarResults.length > 0 ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                     {radarResults.map((result, i) => (
                        <div key={i} className="bg-[#12121a] border border-white/5 rounded-xl p-4 hover:border-red-500/20 transition-all">
                           <div className="flex justify-between items-start mb-3">
                              <div>
                                 <h4 className="text-[#e5e5e8] font-bold">{result.guest_name}</h4>
                                 <Badge className={`mt-1 text-[10px] border-0 ${
                                    result.risk_level === 'Yuksek Risk' ? 'bg-red-500/10 text-red-400' : 
                                    result.risk_level === 'Orta Risk' ? 'bg-orange-500/10 text-orange-400' : 
                                    'bg-yellow-500/10 text-yellow-400'
                                 }`}>
                                    {result.risk_level} (%{result.churn_probability_percent})
                                 </Badge>
                              </div>
                           </div>
                           <div className="space-y-3">
                              <div className="bg-red-500/5 rounded-lg p-3 border-l-2 border-red-500">
                                 <p className="text-xs text-red-400 mb-1 font-medium">Tespit Edilen Sorun</p>
                                 <p className="text-sm text-[#e5e5e8] leading-relaxed">{result.reason}</p>
                              </div>
                              <div className="bg-emerald-500/5 rounded-lg p-3 border-l-2 border-emerald-500">
                                 <p className="text-xs text-emerald-400 mb-1 font-medium">AI Telafi Önerisi</p>
                                 <p className="text-sm text-[#e5e5e8] leading-relaxed">{result.compensation_action}</p>
                              </div>
                           </div>
                        </div>
                     ))}
                  </div>
               ) : (
                  <p className="text-emerald-400 text-sm py-2 flex items-center gap-2">
                     <CheckSquare className="w-4 h-4" /> Şu an otelde konaklayan misafirlerde yüksek şikayet riski tespit edilmedi.
                  </p>
               )}
            </div>
         )}
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
