import React, { useState, useEffect } from 'react';
import { getEvents, createEvent, deleteEvent, seedSampleEvents, getAIEventPlan } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Calendar, Plus, Trash2, Users, Clock, Music, Heart, Utensils, Download, Sparkles, Loader2, Check } from 'lucide-react';

export default function EventsPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', event_type: 'general', event_date: '', start_time: '', capacity: '', price_per_person: '' });

  // AI Planner State
  const [aiOpen, setAiOpen] = useState(false);
  const [aiForm, setAiForm] = useState({ event_type: 'Kurumsal Toplanti', headcount: 50, budget_level: 'medium', special_requests: '' });
  const [aiLoading, setAiLoading] = useState(false);
  const [aiPlan, setAiPlan] = useState(null);

  const load = () => {
    getEvents().then(r => setEvents(r.data.events)).catch(console.error).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    if (!form.title || !form.event_date) return;
    await createEvent({
      ...form,
      capacity: form.capacity ? parseInt(form.capacity) : null,
      price_per_person: form.price_per_person ? parseFloat(form.price_per_person) : null,
    });
    setForm({ title: '', description: '', event_type: 'general', event_date: '', start_time: '', capacity: '', price_per_person: '' });
    setOpen(false);
    load();
  };

  const handleSeedEvents = async () => {
    setSeeding(true);
    try {
      await seedSampleEvents();
      load();
    } catch (err) {
      console.error(err);
    }
    setSeeding(false);
  };

  const handleRunAIPlanner = async () => {
    setAiLoading(true);
    setAiPlan(null);
    try {
      const { data } = await getAIEventPlan(aiForm);
      if (data.success) {
        setAiPlan(data.plan);
      }
    } catch(e) { console.error(e); }
    setAiLoading(false);
  };

  const handleAcceptAIPlan = () => {
     if(!aiPlan) return;
     setForm({
         ...form,
         title: aiPlan.event_title,
         description: `${aiPlan.theme_concept}\n\nKonsept: ${aiPlan.theme_concept}\nPersonel İhtiyacı: ${aiPlan.staff_requirements}\nTahmini Maliyet: ${aiPlan.estimated_cost_try} TL`,
         event_type: 'general',
         capacity: aiForm.headcount,
         price_per_person: Math.round(aiPlan.estimated_cost_try / aiForm.headcount)
     });
     setAiOpen(false);
     setAiPlan(null);
     setOpen(true);
  };

  const EVENT_TYPES = {
    special_dinner: { label: 'Ozel Aksam Yemegi', icon: Heart, color: 'text-rose-400' },
    live_music: { label: 'Canli Muzik', icon: Music, color: 'text-purple-400' },
    workshop: { label: 'Atolye', icon: Utensils, color: 'text-blue-400' },
    wedding: { label: 'Dugun', icon: Heart, color: 'text-pink-400' },
    corporate: { label: 'Kurumsal', icon: Users, color: 'text-slate-400' },
    cultural: { label: 'Kulturel', icon: Calendar, color: 'text-indigo-400' },
    promotion: { label: 'Promosyon', icon: Download, color: 'text-orange-400' },
    general: { label: 'Genel', icon: Calendar, color: 'text-[#C4972A]' },
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const months = ['Ocak','Subat','Mart','Nisan','Mayis','Haziran','Temmuz','Agustos','Eylul','Ekim','Kasim','Aralik'];
    const days = ['Pazar','Pazartesi','Sali','Carsamba','Persembe','Cuma','Cumartesi'];
    try {
      const d = new Date(dateStr + 'T00:00:00');
      return `${d.getDate()} ${months[d.getMonth()]} ${days[d.getDay()]}`;
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="events-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Etkinlikler</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">{events.length} etkinlik</p>
        </div>
        <div className="flex gap-2">
          {events.length === 0 && (
            <Button onClick={handleSeedEvents} disabled={seeding}
              className="bg-white/5 hover:bg-white/10 text-[#C4972A] border border-[#C4972A]/20"
              data-testid="seed-events-btn">
              {seeding ? 'Yukleniyor...' : 'Ornek Etkinlikleri Yukle'}
            </Button>
          )}

          {/* AI PLANNER DIALOG */}
          <Dialog open={aiOpen} onOpenChange={setAiOpen}>
             <DialogTrigger asChild>
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white border border-indigo-400/30 shadow-[0_0_15px_rgba(79,70,229,0.3)]">
                   <Sparkles className="w-4 h-4 mr-2" /> AI ile Etkinlik Planla
                </Button>
             </DialogTrigger>
             <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20 sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
                <DialogHeader><DialogTitle className="text-indigo-400 flex items-center gap-2"><Sparkles className="w-5 h-5"/> AI Ziyafet & Etkinlik Planlayıcı</DialogTitle></DialogHeader>
                
                {!aiPlan ? (
                   <div className="space-y-4 py-2">
                      <div>
                         <label className="text-xs text-[#7e7e8a] mb-1 block">Etkinlik Tipi</label>
                         <Input value={aiForm.event_type} onChange={e => setAiForm({ ...aiForm, event_type: e.target.value })} placeholder="Örn: Yoga Kampı, Kır Düğünü, Lansman" className="bg-white/5 border-white/10" />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                         <div>
                            <label className="text-xs text-[#7e7e8a] mb-1 block">Kişi Sayısı</label>
                            <Input type="number" value={aiForm.headcount} onChange={e => setAiForm({ ...aiForm, headcount: e.target.value })} className="bg-white/5 border-white/10" />
                         </div>
                         <div>
                            <label className="text-xs text-[#7e7e8a] mb-1 block">Bütçe Seviyesi</label>
                            <select value={aiForm.budget_level} onChange={e => setAiForm({ ...aiForm, budget_level: e.target.value })} className="w-full bg-white/5 border border-white/10 rounded-md p-2 text-sm text-white focus:outline-none">
                               <option value="low" className="bg-[#1a1a22]">Ekonomik</option>
                               <option value="medium" className="bg-[#1a1a22]">Standart</option>
                               <option value="high" className="bg-[#1a1a22]">Premium / Lüks</option>
                            </select>
                         </div>
                      </div>
                      <div>
                         <label className="text-xs text-[#7e7e8a] mb-1 block">Özel İstekler (Opsiyonel)</label>
                         <Input value={aiForm.special_requests} onChange={e => setAiForm({ ...aiForm, special_requests: e.target.value })} placeholder="Örn: Vegan ağırlıklı menü, DJ performansı" className="bg-white/5 border-white/10" />
                      </div>
                      <Button onClick={handleRunAIPlanner} disabled={aiLoading} className="w-full bg-indigo-600 hover:bg-indigo-700 mt-2">
                         {aiLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
                         Sihirli Planı Oluştur
                      </Button>
                   </div>
                ) : (
                   <div className="space-y-5 py-2">
                      <div className="bg-white/5 p-4 rounded-xl border border-white/10">
                         <h3 className="text-xl font-bold text-[#C4972A]">{aiPlan.event_title}</h3>
                         <p className="text-sm text-indigo-300 italic mt-1">"{aiPlan.theme_concept}"</p>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                         <div className="bg-[#1a1a22] p-4 rounded-xl border border-white/5">
                            <h4 className="text-sm font-semibold text-white mb-2 flex items-center gap-1"><Clock className="w-4 h-4 text-[#C4972A]"/> Etkinlik Akışı</h4>
                            <ul className="space-y-2">
                               {aiPlan.schedule?.map((item, i) => (
                                  <li key={i} className="text-xs text-[#a9a9b2]">
                                     <span className="text-white font-medium w-10 inline-block">{item.time}</span> {item.activity}
                                  </li>
                               ))}
                            </ul>
                         </div>
                         <div className="bg-[#1a1a22] p-4 rounded-xl border border-white/5">
                            <h4 className="text-sm font-semibold text-white mb-2 flex items-center gap-1"><Utensils className="w-4 h-4 text-[#C4972A]"/> Önerilen Menü</h4>
                            <ul className="space-y-2">
                               {aiPlan.recommended_menu?.map((item, i) => (
                                  <li key={i} className="text-xs text-[#a9a9b2]">
                                     <span className="text-[#C4972A]">{item.course}:</span> {item.item}
                                  </li>
                               ))}
                            </ul>
                         </div>
                      </div>

                      <div className="bg-indigo-500/10 p-4 rounded-xl border border-indigo-500/20">
                         <h4 className="text-sm font-semibold text-indigo-400 mb-1 flex items-center gap-1"><Sparkles className="w-4 h-4"/> AI Satış Kancası</h4>
                         <p className="text-xs text-indigo-200">{aiPlan.ai_advice}</p>
                      </div>

                      <div className="flex items-center justify-between text-xs text-[#7e7e8a] px-1">
                         <span>Maliyet: <strong className="text-white">{aiPlan.estimated_cost_try?.toLocaleString()} TL</strong></span>
                         <span>Personel: <strong className="text-white">{aiPlan.staff_requirements}</strong></span>
                      </div>

                      <div className="flex gap-2">
                         <Button variant="outline" onClick={() => setAiPlan(null)} className="flex-1 border-white/10 hover:bg-white/5">Geri Dön</Button>
                         <Button onClick={handleAcceptAIPlan} className="flex-1 bg-green-600 hover:bg-green-700 text-white"><Check className="w-4 h-4 mr-2"/> Taslağa Çevir</Button>
                      </div>
                   </div>
                )}
             </DialogContent>
          </Dialog>

          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-event-btn">
                <Plus className="w-4 h-4 mr-2" /> Etkinlik Ekle
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
              <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Etkinlik</DialogTitle></DialogHeader>
              <div className="space-y-3">
                <Input placeholder="Etkinlik adi *" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })}
                  className="bg-white/5 border-white/10" data-testid="event-title-input" />
                <Input placeholder="Aciklama" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
                  className="bg-white/5 border-white/10" />
                <select value={form.event_type} onChange={e => setForm({ ...form, event_type: e.target.value })}
                  className="w-full bg-white/5 border border-white/10 rounded-md p-2 text-sm text-white">
                  {Object.entries(EVENT_TYPES).map(([key, val]) => (
                    <option key={key} value={key} className="bg-[#1a1a22]">{val.label}</option>
                  ))}
                </select>
                <Input type="date" value={form.event_date} onChange={e => setForm({ ...form, event_date: e.target.value })}
                  className="bg-white/5 border-white/10" data-testid="event-date-input" />
                <Input type="time" value={form.start_time} onChange={e => setForm({ ...form, start_time: e.target.value })}
                  className="bg-white/5 border-white/10" />
                <Input type="number" placeholder="Kapasite" value={form.capacity} onChange={e => setForm({ ...form, capacity: e.target.value })}
                  className="bg-white/5 border-white/10" />
                <Input type="number" placeholder="Kisi basi fiyat (TL)" value={form.price_per_person} onChange={e => setForm({ ...form, price_per_person: e.target.value })}
                  className="bg-white/5 border-white/10" />
                <Button onClick={handleCreate} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-event-btn">Kaydet</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {events.map(event => {
          const typeInfo = EVENT_TYPES[event.event_type] || EVENT_TYPES.general;
          const TypeIcon = typeInfo.icon;
          return (
            <div key={event.id} className="glass rounded-xl overflow-hidden hover:gold-glow transition-all" data-testid={`event-${event.id}`}>
              {/* Cover Image */}
              {event.cover_image && (
                <div className="relative h-48 overflow-hidden">
                  <img src={event.cover_image} alt={event.title}
                    className="w-full h-full object-cover" />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0f] via-transparent to-transparent" />
                  <div className="absolute bottom-3 left-4">
                    <Badge className={`${event.event_type === 'special_dinner' ? 'bg-rose-500/20 text-rose-300' : 'bg-purple-500/20 text-purple-300'} text-xs`}>
                      <TypeIcon className="w-3 h-3 mr-1" /> {typeInfo.label}
                    </Badge>
                  </div>
                </div>
              )}

              <div className="p-5 space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-[#C4972A]">{event.title}</h3>
                    {event.artist && (
                      <p className="text-sm text-white/80 mt-0.5 flex items-center gap-1">
                        <Music className="w-3 h-3" /> {event.artist}
                      </p>
                    )}
                  </div>
                  <button onClick={() => { deleteEvent(event.id).then(load); }}
                    className="text-[#7e7e8a] hover:text-red-400 p-1" data-testid={`delete-event-${event.id}`}>
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                {event.description && (
                  <p className="text-sm text-[#a9a9b2] leading-relaxed line-clamp-3">{event.description}</p>
                )}

                {/* Date/Time/Capacity Row */}
                <div className="flex flex-wrap items-center gap-3 text-xs text-[#7e7e8a]">
                  <span className="flex items-center gap-1 text-white/90">
                    <Calendar className="w-3.5 h-3.5 text-[#C4972A]" /> {formatDate(event.event_date)}
                  </span>
                  {event.start_time && (
                    <span className="flex items-center gap-1 text-white/90">
                      <Clock className="w-3.5 h-3.5 text-[#C4972A]" /> {event.start_time}
                    </span>
                  )}
                  {event.capacity && (
                    <span className="flex items-center gap-1">
                      <Users className="w-3.5 h-3.5" /> {event.capacity} kisi
                    </span>
                  )}
                </div>

                {/* Pricing */}
                {(event.pricing || event.price_per_person) && (
                  <div className="bg-white/3 rounded-lg p-3 space-y-1">
                    {event.pricing ? (
                      <div className="flex flex-wrap gap-3">
                        <div>
                          <p className="text-[10px] text-[#7e7e8a] uppercase">Alkolu Menu</p>
                          <p className="text-base font-bold text-[#C4972A]">{event.pricing.alkolu_menu?.toLocaleString()} TL<span className="text-xs font-normal text-[#7e7e8a]">/kisi</span></p>
                        </div>
                        <div>
                          <p className="text-[10px] text-[#7e7e8a] uppercase">Sinirsiz Alkolu</p>
                          <p className="text-base font-bold text-[#C4972A]">{event.pricing.sinirsiz_alkolu_menu?.toLocaleString()} TL<span className="text-xs font-normal text-[#7e7e8a]">/kisi</span></p>
                        </div>
                      </div>
                    ) : (
                      <p className="text-base font-bold text-[#C4972A]">{event.price_per_person?.toLocaleString()} TL<span className="text-xs font-normal text-[#7e7e8a]">/kisi</span></p>
                    )}
                  </div>
                )}

                {/* Menu Details */}
                {event.menu_details && (
                  <details className="group">
                    <summary className="text-xs text-[#C4972A] cursor-pointer hover:text-[#dbb44d] flex items-center gap-1">
                      <Utensils className="w-3 h-3" /> Menu Detaylari
                    </summary>
                    <div className="mt-2 bg-white/3 rounded-lg p-3 text-xs text-[#a9a9b2] space-y-1.5">
                      {event.menu_details.baslangiclar && (
                        <div><span className="text-[#C4972A] font-medium">Baslangiclar:</span> {event.menu_details.baslangiclar.join(', ')}</div>
                      )}
                      {event.menu_details.mezeler && (
                        <div><span className="text-[#C4972A] font-medium">Mezeler:</span> {event.menu_details.mezeler.join(', ')}</div>
                      )}
                      {event.menu_details.salata && (
                        <div><span className="text-[#C4972A] font-medium">Salata:</span> {event.menu_details.salata}</div>
                      )}
                      {event.menu_details.ara_sicak && (
                        <div><span className="text-[#C4972A] font-medium">Ara Sicak:</span> {event.menu_details.ara_sicak}</div>
                      )}
                      {event.menu_details.ana_yemek && (
                        <div><span className="text-[#C4972A] font-medium">Ana Yemek:</span> {event.menu_details.ana_yemek}</div>
                      )}
                      {event.menu_details.tatli && (
                        <div><span className="text-[#C4972A] font-medium">Tatli:</span> {event.menu_details.tatli}</div>
                      )}
                    </div>
                  </details>
                )}

                {/* Tags */}
                {!event.cover_image && (
                  <div className="flex items-center gap-2">
                    <Badge className="bg-[#C4972A]/20 text-[#C4972A] text-xs">{typeInfo.label}</Badge>
                    {event.is_active && <Badge className="bg-green-500/20 text-green-400 text-xs">Aktif</Badge>}
                  </div>
                )}
              </div>
            </div>
          );
        })}
        {events.length === 0 && !loading && (
          <div className="col-span-2 text-center py-12 text-[#7e7e8a]">
            <Calendar className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Henuz etkinlik yok</p>
            <p className="text-xs mt-1">Ornek etkinlikleri yukle butonuna tiklayabilirsiniz</p>
          </div>
        )}
      </div>
    </div>
  );
}
