import React, { useState, useEffect } from 'react';
import { getReservations, createReservation, updateReservation, deleteReservation, getGuests, getRooms, getAIUpsellOpps } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Calendar, Plus, Trash2, User, ArrowRight, Check, Sparkles, Loader2, TrendingUp, HandCoins, Gift, MessageCircle } from 'lucide-react';

const STATUS_CONFIG = {
  pending: { label: 'Bekliyor', color: 'bg-yellow-500/20 text-yellow-400' },
  confirmed: { label: 'Onaylandi', color: 'bg-blue-500/20 text-blue-400' },
  checked_in: { label: 'Check-in', color: 'bg-green-500/20 text-green-400' },
  checked_out: { label: 'Check-out', color: 'bg-gray-500/20 text-gray-400' },
  cancelled: { label: 'Iptal', color: 'bg-red-500/20 text-red-400' },
  no_show: { label: 'No-Show', color: 'bg-red-700/20 text-red-500' },
};

const FLOW = { pending: 'confirmed', confirmed: 'checked_in', checked_in: 'checked_out' };

export default function ReservationsPage() {
  const [reservations, setReservations] = useState([]);
  const [guests, setGuests] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ guest_id: '', room_type: '', check_in: '', check_out: '', guests_count: 1, notes: '', total_price: '' });

  // Phase 11 AI Actions
  const [allocating, setAllocating] = useState(false);
  const [allocationMsg, setAllocationMsg] = useState("");

  // Phase 14 AI Upsell Actions
  const [upsellLoading, setUpsellLoading] = useState({});
  const [upsellData, setUpsellData] = useState({});

  // Phase 25 AI Guest Journey
  const [journeyLoading, setJourneyLoading] = useState(false);
  const [journeyData, setJourneyData] = useState(null);
  const [openJourney, setOpenJourney] = useState(false);

  const load = () => {
    const params = filter !== 'all' ? { status: filter } : {};
    getReservations(params).then(r => setReservations(r.data.reservations)).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [filter]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    getGuests({ limit: 200 }).then(r => setGuests(r.data.guests)).catch(() => {});
    getRooms().then(r => setRooms(r.data.rooms)).catch(() => {});
  }, []);

  const handleCreate = async () => {
    if (!form.guest_id || !form.room_type || !form.check_in || !form.check_out) return;
    await createReservation({
      ...form,
      guests_count: parseInt(form.guests_count) || 1,
      total_price: form.total_price ? parseFloat(form.total_price) : null,
    });
    setForm({ guest_id: '', room_type: '', check_in: '', check_out: '', guests_count: 1, notes: '', total_price: '' });
    setOpen(false);
    load();
  };

  const handleStatusChange = async (id, newStatus) => {
    await updateReservation(id, { status: newStatus });
    load();
  };

  const handleAIAllocation = async () => {
    setAllocating(true);
    setAllocationMsg("");
    try {
      // Import at top needed if not present (handled below)
      const { getAISmartRoomAllocation } = require('../api'); 
      const res = await getAISmartRoomAllocation();
      if (res.data?.success) {
        setAllocationMsg(`${res.data.applied_count} misafire otomatik oda atandı!`);
        load();
      }
    } catch (e) {
      console.error(e);
      setAllocationMsg("AI Atama hatası.");
    }
    setAllocating(false);
    setTimeout(() => setAllocationMsg(""), 5000);
  };

  const handleFetchUpsell = async (resId) => {
      setUpsellLoading(prev => ({...prev, [resId]: true}));
      try {
          const { data } = await getAIUpsellOpps(resId);
          if(data.success) {
              setUpsellData(prev => ({...prev, [resId]: data.suggestions}));
          }
      } catch(e) { console.error("Upsell err:", e); }
      setUpsellLoading(prev => ({...prev, [resId]: false}));
  };

  const handleFetchJourney = async () => {
    setOpenJourney(true);
    setJourneyLoading(true);
    setJourneyData(null);
    try {
      const { getAIGuestJourney } = require('../api');
      const res = await getAIGuestJourney();
      if (res.data?.data) {
          if (res.data.data.length === 0 && res.data.message) {
              setJourneyData([]);
              alert(res.data.message);
          } else {
              setJourneyData(res.data.data);
          }
      } else if (res.data?.error) alert(res.data.error);
    } catch (e) {
      console.error(e);
      alert('Misafir yolculuğu üretilemedi.');
    } finally {
      setJourneyLoading(false);
    }
  };

  const guestMap = Object.fromEntries(guests.map(g => [g.id, g.name]));

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="reservations-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Rezervasyonlar</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">{reservations.length} rezervasyon</p>
        </div>
        
        <div className="flex items-center gap-2 flex-wrap">
          {allocationMsg && <span className="text-emerald-400 text-sm animate-pulse mr-2">{allocationMsg}</span>}
          <Button 
            onClick={handleAIAllocation} 
            disabled={allocating}
            className="bg-[#1a1a22] border border-[#C4972A]/30 hover:bg-[#C4972A]/10 text-[#C4972A]"
          >
            {allocating ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
            AI Oda Ata
          </Button>

          <Button 
            onClick={handleFetchJourney} 
            className="bg-purple-600 hover:bg-purple-500 text-white shadow-[0_0_15px_rgba(147,51,234,0.3)]"
          >
            <Sparkles className="w-4 h-4 mr-2" /> AI Misafir Yolculuğu
          </Button>

          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-reservation-btn">
                <Plus className="w-4 h-4 mr-2" /> Yeni Rezervasyon
              </Button>
            </DialogTrigger>
          <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
            <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Rezervasyon</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <Select value={form.guest_id} onValueChange={v => setForm({ ...form, guest_id: v })}>
                <SelectTrigger className="bg-white/5 border-white/10"><SelectValue placeholder="Misafir secin *" /></SelectTrigger>
                <SelectContent className="bg-[#1a1a22] border-[#C4972A]/20 max-h-48">
                  {guests.map(g => <SelectItem key={g.id} value={g.id}>{g.name}</SelectItem>)}
                </SelectContent>
              </Select>
              <Select value={form.room_type} onValueChange={v => setForm({ ...form, room_type: v })}>
                <SelectTrigger className="bg-white/5 border-white/10"><SelectValue placeholder="Oda tipi *" /></SelectTrigger>
                <SelectContent className="bg-[#1a1a22] border-[#C4972A]/20">
                  {rooms.map(r => <SelectItem key={r.room_id} value={r.room_id}>{r.name_tr} - {r.base_price_try} TL</SelectItem>)}
                </SelectContent>
              </Select>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-[#7e7e8a] mb-1 block">Giris *</label>
                  <Input type="date" value={form.check_in} onChange={e => setForm({ ...form, check_in: e.target.value })} className="bg-white/5 border-white/10" data-testid="res-checkin" />
                </div>
                <div>
                  <label className="text-xs text-[#7e7e8a] mb-1 block">Cikis *</label>
                  <Input type="date" value={form.check_out} onChange={e => setForm({ ...form, check_out: e.target.value })} className="bg-white/5 border-white/10" data-testid="res-checkout" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <Input type="number" min="1" placeholder="Kisi sayisi" value={form.guests_count} onChange={e => setForm({ ...form, guests_count: e.target.value })} className="bg-white/5 border-white/10" />
                <Input type="number" placeholder="Toplam fiyat (TL)" value={form.total_price} onChange={e => setForm({ ...form, total_price: e.target.value })} className="bg-white/5 border-white/10" />
              </div>
              <Input placeholder="Notlar" value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} className="bg-white/5 border-white/10" />
              <Button onClick={handleCreate} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-reservation-btn">Kaydet</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>

    {/* AI Guest Journey Modal */}
      <Dialog open={openJourney} onOpenChange={setOpenJourney}>
        <DialogContent className="bg-[#1a1a22] border-purple-500/30 max-w-4xl text-white max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-purple-400 flex items-center gap-2 text-xl">
              <Sparkles className="w-6 h-6" /> AI Hiper-Kişiselleştirilmiş Misafir Yolculuğu
            </DialogTitle>
            <p className="text-sm text-gray-400 mt-2">Önümüzdeki 3 gün içinde giriş yapacak misafirler için AI destekli karşılama hediyeleri ve SMS kurguları.</p>
          </DialogHeader>
          <div className="space-y-6 mt-4">
            {journeyLoading ? (
               <div className="text-center py-12">
                 <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                 <p className="text-gray-400 text-sm">Gemini konuk profillerini analiz edip özel senaryolar üretiyor...</p>
               </div>
            ) : journeyData && journeyData.length > 0 ? (
               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 {journeyData.map((jd, idx) => (
                    <div key={idx} className="bg-white/5 border border-purple-500/20 rounded-xl p-5 hover:border-purple-500/50 transition-colors">
                       <h3 className="font-semibold text-lg text-white mb-3 flex justify-between items-center">
                          {jd.guest_name}
                          <Badge className="bg-purple-500/20 text-purple-300 text-[10px]">Rezervasyon: {jd.reservation_id}</Badge>
                       </h3>
                       <div className="space-y-4">
                          <div className="bg-[#1a1a22] p-3 rounded-lg border border-white/5">
                             <h4 className="flex items-center gap-2 text-emerald-400 text-sm font-medium mb-2">
                                <Gift className="w-4 h-4"/> Odaya Bırakılacak Karşılama Hediyesi
                             </h4>
                             <p className="text-sm text-gray-300 leading-relaxed">{jd.welcome_package}</p>
                          </div>
                          <div className="bg-[#1a1a22] p-3 rounded-lg border border-white/5">
                             <h4 className="flex items-center gap-2 text-[#C4972A] text-sm font-medium mb-2">
                                <MessageCircle className="w-4 h-4"/> WhatsApp Karşılama & Upsell Mesajı
                             </h4>
                             <p className="text-sm text-gray-300 leading-relaxed italic">"{jd.sms_text}"</p>
                             <div className="mt-3 flex justify-end">
                                <Button size="sm" variant="outline" className="text-xs bg-white/5 border-white/10 text-white hover:bg-white/10" onClick={() => { navigator.clipboard.writeText(jd.sms_text); alert("Kopyalandı!"); }}>
                                  Metni Kopyala
                                </Button>
                             </div>
                          </div>
                       </div>
                    </div>
                 ))}
               </div>
            ) : journeyData && journeyData.length === 0 ? (
               <div className="text-center py-8 text-gray-400">
                  Şu an için önümüzdeki 3 gün içinde onaylı giriş yapacak misafir bulunmuyor.
               </div>
            ) : null}
          </div>
        </DialogContent>
      </Dialog>

      <div className="flex gap-2 flex-wrap">
        {['all', 'pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-full text-xs transition-all ${filter === f ? 'bg-[#C4972A]/20 text-[#C4972A]' : 'bg-white/5 text-[#7e7e8a] hover:bg-white/10'}`}
            data-testid={`res-filter-${f}`}>
            {f === 'all' ? 'Tumu' : STATUS_CONFIG[f]?.label || f}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {reservations.map(res => {
          const cfg = STATUS_CONFIG[res.status] || STATUS_CONFIG.pending;
          const nextStatus = FLOW[res.status];
          return (
            <div key={res.id} className="glass rounded-xl p-4 hover:gold-glow transition-all" data-testid={`reservation-${res.id}`}>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-[#C4972A]/10 flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-[#C4972A]" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium">{guestMap[res.guest_id] || res.guest_name || 'Misafir'}</span>
                    <Badge className={cfg.color + ' text-xs'}>{cfg.label}</Badge>
                    <span className="text-xs text-[#C4972A]">{res.room_type} {res.room_id ? `(#${res.room_id})` : '(Atanmadı)'}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-[#7e7e8a] mt-1">
                    <span>{res.check_in}</span>
                    <ArrowRight className="w-3 h-3" />
                    <span>{res.check_out}</span>
                    {res.guests_count && <span>| {res.guests_count} kisi</span>}
                    {res.total_price && <span className="text-[#C4972A]">| {res.total_price} TL</span>}
                  </div>
                  {res.notes && <p className="text-xs text-[#a9a9b2] mt-1">{res.notes}</p>}
                  {res.ai_allocation_reason && (
                    <p className="text-[10px] text-emerald-400 mt-1 flex items-center gap-1">
                      <Sparkles className="w-3 h-3" /> AI Tarafından Atandı: {res.ai_allocation_reason}
                    </p>
                  )}
                  
                  {res.ai_guest_profile && !res.ai_guest_profile.error && (
                    <div className="mt-3 p-3 bg-[#1a1a22]/50 border border-[#C4972A]/20 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-semibold text-[#C4972A] bg-[#C4972A]/10 px-2 py-0.5 rounded">
                          AI Profil: {res.ai_guest_profile.persona}
                        </span>
                      </div>
                      <p className="text-xs text-[#a9a9b2]"><strong className="text-gray-300">Ek Satis Önerisi:</strong> {res.ai_guest_profile.upsell_suggestion}</p>
                      <p className="text-xs text-[#a9a9b2] mt-1"><strong className="text-gray-300">Hoşgeldin Mesajı:</strong> {res.ai_guest_profile.welcome_message_draft}</p>
                    </div>
                  )}

                  {/* AI Dynamic Upsell Panel */}
                  <div className="mt-4">
                     {!upsellData[res.id] ? (
                        <Button 
                           size="sm" 
                           onClick={() => handleFetchUpsell(res.id)} 
                           disabled={upsellLoading[res.id]}
                           className="text-[10px] h-7 bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600/40 border border-indigo-500/30"
                        >
                           {upsellLoading[res.id] ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : <TrendingUp className="w-3 h-3 mr-1" />}
                           AI Upsell (Çapraz Satış) Olanaklarını Gör
                        </Button>
                     ) : (
                        <div className="bg-[#1a1a22] border border-indigo-500/30 p-3 rounded-xl mt-2 relative overflow-hidden">
                           <div className="absolute top-0 right-0 p-2 opacity-5"><HandCoins className="w-16 h-16 text-indigo-400" /></div>
                           <h4 className="text-xs font-bold text-indigo-400 flex items-center gap-1 mb-3"><Sparkles className="w-3 h-3"/> AI Upsell Motoru Asistanı</h4>
                           <div className="space-y-3">
                              {upsellData[res.id].map((upsell, idx) => (
                                 <div key={idx} className="bg-white/5 p-2.5 rounded-lg border border-white/5 hover:border-indigo-500/30 transition-colors">
                                    <div className="flex justify-between items-start mb-1">
                                       <span className="text-xs font-semibold text-white">{upsell.item}</span>
                                       <Badge className={`text-[10px] ${upsell.probability_percent > 70 ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                                          %{upsell.probability_percent} İhtimal
                                       </Badge>
                                    </div>
                                    <p className="text-[10px] text-indigo-300 italic">"{upsell.pitch}"</p>
                                    <div className="text-[10px] text-emerald-400 font-medium mt-1.5 flex justify-end">+{upsell.estimated_revenue_try} TL Ek Gelir</div>
                                 </div>
                              ))}
                           </div>
                        </div>
                     )}
                  </div>
                  
                </div>
                <div className="flex gap-1.5 flex-col items-end">
                  {nextStatus && (
                    <Button size="sm" variant="outline" onClick={() => handleStatusChange(res.id, nextStatus)}
                      className="text-xs border-[#C4972A]/30 text-[#C4972A] hover:bg-[#C4972A]/10">
                      <Check className="w-3 h-3 mr-1" />{STATUS_CONFIG[nextStatus]?.label}
                    </Button>
                  )}
                  {res.status === 'pending' && (
                    <Button size="sm" variant="outline" onClick={() => handleStatusChange(res.id, 'cancelled')}
                      className="text-xs border-red-500/30 text-red-400 hover:bg-red-500/10">Iptal</Button>
                  )}
                  <button onClick={() => { deleteReservation(res.id).then(load); }} className="text-[#7e7e8a] hover:text-red-400">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
        {reservations.length === 0 && !loading && (
          <div className="text-center py-12 text-[#7e7e8a]">
            <Calendar className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Henuz rezervasyon yok</p>
          </div>
        )}
      </div>
    </div>
  );
}
