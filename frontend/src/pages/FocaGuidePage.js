import React, { useState, useEffect } from 'react';
import { getLocalGuide, getHotelHistory } from '../api';
import { Badge } from '../components/ui/badge';
import { MapPin, Clock, Waves, Landmark, Bike, Heart, History } from 'lucide-react';

export default function FocaGuidePage() {
  const [guide, setGuide] = useState(null);
  const [history, setHistory] = useState(null);
  const [tab, setTab] = useState('beaches');
  const [loading, setLoading] = useState(true);

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
      {tab !== 'history' && activeTab?.data && (
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
    </div>
  );
}
