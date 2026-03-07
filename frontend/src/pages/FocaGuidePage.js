import React, { useState, useEffect } from 'react';
import { getLocalGuide, getHotelHistory, getAILocalGuideItinerary } from '../api';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { MapPin, Clock, Waves, Landmark, Bike, Heart, History, Sparkles, Loader2, Calendar } from 'lucide-react';

export default function FocaGuidePage() {
  const [guide, setGuide] = useState(null);
  const [history, setHistory] = useState(null);
  const [tab, setTab] = useState('beaches');
  const [loading, setLoading] = useState(true);

  // AI Itinerary State
  const [aiForm, setAiForm] = useState({ guest_type: 'Cift', days: 2, interests: 'Tarih, lezzet, dinlenme' });
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);

  useEffect(() => {
    Promise.all([
      getLocalGuide().then(r => setGuide(r.data)),
      getHotelHistory().then(r => setHistory(r.data)),
    ]).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading || !guide) return <div className="p-8"><div className="h-8 w-48 bg-white/5 rounded animate-pulse" /></div>;

  const TABS = [
    { id: 'beaches', label: 'Plajlar', icon: Waves, data: guide.beaches },
    { id: 'historical', label: 'Tarihi Yerler', icon: Landmark, data: guide.historical },
    { id: 'family', label: 'Aile Aktiviteleri', icon: Bike, data: guide.activities_family },
    { id: 'couple', label: 'Ciftler Icin', icon: Heart, data: guide.activities_couple },
    { id: 'history', label: 'Koy Tarihi', icon: History, data: null },
    { id: 'ai_itinerary', label: 'AI Rota Planlayici', icon: Sparkles, data: null },
  ];

  const activeTab = TABS.find(t => t.id === tab);

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="foca-guide-page">
      <div className="text-center">
        <h1 className="text-3xl lg:text-4xl font-bold text-[#C4972A]">Foca & Cevre Rehberi</h1>
        <p className="text-[#7e7e8a] mt-2">Antik Phokaia - Akdeniz Foklari Diyari</p>
        <div className="w-24 h-0.5 bg-[#C4972A]/50 mx-auto mt-4" />
      </div>

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2 justify-center flex-wrap">
        {TABS.map(t => {
          const Icon = t.icon;
          return (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm transition-all whitespace-nowrap ${
                tab === t.id ? 'bg-[#C4972A] text-white' : 'bg-white/5 text-[#7e7e8a] hover:bg-white/10'
              }`}
              data-testid={`guide-tab-${t.id}`}>
              <Icon className="w-4 h-4" /> {t.label}
            </button>
          );
        })}
      </div>

      {/* Content */}
      {tab !== 'history' && tab !== 'ai_itinerary' && activeTab?.data && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {activeTab.data.map((item, i) => (
            <div key={i} className="glass rounded-xl p-5 hover:gold-glow transition-all" data-testid={`guide-item-${i}`}>
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-[#C4972A]/10 flex items-center justify-center flex-shrink-0">
                  {React.createElement(activeTab.icon, { className: "w-5 h-5 text-[#C4972A]" })}
                </div>
                <div>
                  <h3 className="font-semibold text-[#e5e5e8]">{item.name}</h3>
                  <p className="text-sm text-[#a9a9b2] mt-1">{item.desc}</p>
                  <div className="flex items-center gap-3 mt-2">
                    {item.distance && (
                      <span className="flex items-center gap-1 text-xs text-[#C4972A]">
                        <MapPin className="w-3 h-3" /> {item.distance}
                      </span>
                    )}
                    {item.duration && (
                      <span className="flex items-center gap-1 text-xs text-[#7e7e8a]">
                        <Clock className="w-3 h-3" /> {item.duration}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* History Tab */}
      {tab === 'history' && history && (
        <div className="space-y-6">
          <div className="glass rounded-xl p-6">
            <h3 className="text-xl font-semibold text-[#C4972A] mb-3">Kozbeyli Koyu Tarihi</h3>
            <p className="text-[#a9a9b2] leading-relaxed">{history.history_tr}</p>
            <div className="mt-4 flex items-center gap-3">
              <Badge className="bg-[#C4972A]/20 text-[#C4972A]">{history.village_age_years} yillik tarih</Badge>
              <Badge className="bg-white/5 text-[#7e7e8a]">Kurucu: {history.village_founder}</Badge>
            </div>
          </div>
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-[#C4972A]">Zaman Cizelgesi</h3>
            {(history.timeline || []).map((item, i) => (
              <div key={i} className="flex items-center gap-4">
                <div className="w-20 text-right text-xs font-mono text-[#C4972A] flex-shrink-0">{item.period}</div>
                <div className="w-3 h-3 rounded-full bg-[#C4972A]/40 flex-shrink-0 relative">
                  {i < history.timeline.length - 1 && (
                    <div className="absolute top-3 left-1/2 -translate-x-1/2 w-px h-8 bg-[#C4972A]/20" />
                  )}
                </div>
                <p className="text-sm text-[#a9a9b2]">{item.event}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Itinerary Tab */}
      {tab === 'ai_itinerary' && (
        <div className="space-y-6 animate-in fade-in duration-500">
           <div className="glass rounded-xl p-6 border border-[#C4972A]/30 relative overflow-hidden">
               <div className="absolute top-0 right-0 w-64 h-64 bg-[#C4972A]/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
               <h2 className="text-xl font-bold text-[#C4972A] flex items-center gap-2 mb-2 relative z-10">
                  <Sparkles className="w-5 h-5" /> Gemini AI Konsiyerj
               </h2>
               <p className="text-sm text-[#a9a9b2] mb-6 relative z-10">
                  Size ve sevdiklerinize ozel, Foca tatilinizi unutulmaz kilacak mukemmel rotayi saniyeler icinde planlayalim.
               </p>

               <div className="flex flex-col md:flex-row gap-4 relative z-10">
                  <div className="flex-1 space-y-2">
                     <label className="text-xs text-[#7e7e8a]">Kimlerle seyahat ediyorsunuz?</label>
                     <select value={aiForm.guest_type} onChange={e => setAiForm(p => ({ ...p, guest_type: e.target.value }))}
                        className="w-full bg-[#1a1a22] border border-white/10 rounded-md p-2.5 text-sm text-[#e5e5e8]">
                        <option value="Tek Kisi">Tek Kisi</option>
                        <option value="Cift">Cift / Romantik</option>
                        <option value="Kucuk Cocuklu Aile">Kucuk Cocuklu Aile</option>
                        <option value="Gencler / Arkadas Grubu">Gencler / Arkadas Grubu</option>
                        <option value="Ileri Yas">Ileri Yas / Yavas Tempoda</option>
                     </select>
                  </div>
                  <div className="w-full md:w-32 space-y-2">
                     <label className="text-xs text-[#7e7e8a]">Kac Gun?</label>
                     <Input type="number" min={1} max={7} value={aiForm.days} onChange={e => setAiForm(p => ({ ...p, days: parseInt(e.target.value)||1 }))}
                        className="bg-[#1a1a22] border-white/10" />
                  </div>
                  <div className="flex-[2] space-y-2">
                     <label className="text-xs text-[#7e7e8a]">Ilgi Alanlariniz veya Notlariniz</label>
                     <Input placeholder="Orn: Doga yuruyusu, sarap tadimi, sessizlik..." value={aiForm.interests} onChange={e => setAiForm(p => ({ ...p, interests: e.target.value }))}
                        className="bg-[#1a1a22] border-white/10" />
                  </div>
               </div>

               <div className="mt-4 flex justify-end relative z-10">
                  <Button 
                     onClick={async () => {
                        setAiLoading(true); setAiResult(null);
                        try {
                           const res = await getAILocalGuideItinerary(aiForm);
                           if (res.data?.success) setAiResult(res.data.data);
                           else alert(res.data?.error || 'Hata olustu');
                        } catch (e) { alert("Istek basarisiz oldu."); }
                        setAiLoading(false);
                     }} 
                     disabled={aiLoading}
                     className="bg-[#C4972A] hover:bg-[#a87a1f] text-white min-w-[150px]"
                  >
                     {aiLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Sparkles className="w-4 h-4 mr-2" />}
                     {aiLoading ? 'Hesaplaniyor...' : 'Rotami Olustur'}
                  </Button>
               </div>
           </div>

           {/* AI Result Display */}
           {aiResult && !aiLoading && (
              <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
                 <div className="text-center mt-8 mb-6">
                    <h3 className="text-2xl font-bold text-white mb-2">{aiResult.title}</h3>
                    <p className="text-[#a9a9b2] max-w-2xl mx-auto">{aiResult.summary}</p>
                 </div>

                 <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {(aiResult.itinerary || []).map((day, idx) => (
                       <div key={idx} className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-5 relative">
                          <div className="absolute -top-3 left-5 bg-[#C4972A] text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
                             {day.day}. GUN
                          </div>
                          <div className="mt-4 space-y-5">
                             {(day.activities || []).map((act, actIdx) => (
                                <div key={actIdx} className="flex gap-4">
                                   <div className="flex flex-col items-center">
                                      <div className="w-12 text-xs font-mono text-[#C4972A] font-bold tracking-tight text-right pt-0.5">
                                         {act.time}
                                      </div>
                                      {actIdx !== day.activities.length - 1 && (
                                         <div className="w-px h-full bg-gradient-to-b from-[#C4972A]/30 to-transparent mt-2 mb-1" />
                                      )}
                                   </div>
                                   <div className="flex-1 pb-4">
                                      <h4 className="text-[#e5e5e8] font-medium leading-tight">{act.title}</h4>
                                      <p className="text-sm text-[#7e7e8a] mt-1.5 leading-relaxed">{act.description}</p>
                                   </div>
                                </div>
                             ))}
                          </div>
                       </div>
                    ))}
                 </div>
              </div>
           )}
        </div>
      )}
    </div>
  );
}
