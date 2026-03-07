import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Crown, Star, HeartCrash, CalendarDays, Loader2, Sparkles, Send, Copy, AlertCircle
} from 'lucide-react';
import { getLoyaltySegments, generateLoyaltyAICampaign } from '../api';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Button } from '../components/ui/button';

const SEGMENTS = [
  { id: 'vip', title: 'VIP Misafirler', icon: Crown, color: 'text-yellow-400', bg: 'bg-yellow-400/10' },
  { id: 'repeat', title: 'Sadık Misafirler (2+)', icon: Star, color: 'text-blue-400', bg: 'bg-blue-400/10' },
  { id: 'upcoming', title: 'Yakında Gelecekler', icon: CalendarDays, color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
  { id: 'churn_risk', title: 'Eski Dostlar (>1 Yıl)', icon: HeartCrash, color: 'text-red-400', bg: 'bg-red-400/10' }
];

export default function LoyaltyPage() {
  const [segments, setSegments] = useState({ vip: [], repeat: [], upcoming: [], churn_risk: [] });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('vip');
  
  // AI Campaign Modal
  const [targetGuest, setTargetGuest] = useState(null);
  const [aiDraft, setAiDraft] = useState(null);
  const [draftLoading, setDraftLoading] = useState(false);

  const loadSegments = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getLoyaltySegments();
      if(res.data?.success) {
        setSegments(res.data.segments);
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { loadSegments(); }, [loadSegments]);

  const handleGenerateCampaign = async (guest, type) => {
    setTargetGuest(guest);
    setAiDraft(null);
    setDraftLoading(true);
    try {
      const payload = {
        guest_name: guest.name || guest.full_name || guest.email || "Değerli Misafirimiz",
        segment: type,
        last_visit_info: typeof guest.last_visit_days_ago === 'number' ? `${guest.last_visit_days_ago} gün önce kalmış` : "",
        special_note: guest.notes || ""
      };
      const res = await generateLoyaltyAICampaign(payload);
      if (res.data?.success) {
        setAiDraft(res.data.campaign);
      }
    } catch (e) {
      console.error(e);
      alert("AI Kampanya taslağı oluşturulamadı.");
    }
    setDraftLoading(false);
  };

  const currentTabGuests = segments[activeTab] || [];

  return (
    <div className="flex flex-col h-full bg-[#0a0a0f] text-white p-6 space-y-6 overflow-hidden">
      {/* HEADER */}
      <div className="flex justify-between items-center shrink-0">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Crown className="w-7 h-7 text-yellow-500" /> AI Sadakat & VIP Yönetimi
          </h1>
          <p className="text-sm text-[#a9a9b2] mt-1">Geçmiş misafirleri segmente edin ve onlara hiper-kişiselleştirilmiş mesajlar gönderin.</p>
        </div>
      </div>

      {/* TABS */}
      <div className="flex gap-4 shrink-0 overflow-x-auto pb-2 custom-scrollbar">
        {SEGMENTS.map(s => {
          const count = segments[s.id]?.length || 0;
          return (
            <button
               key={s.id}
               onClick={() => setActiveTab(s.id)}
               className={`flex-1 min-w-[200px] flex items-center gap-4 p-4 rounded-xl border transition-all ${
                 activeTab === s.id 
                   ? `border-${s.color.split('-')[1]}-500/50 ${s.bg} shadow-[0_0_15px_rgba(250,204,21,0.1)]` 
                   : 'border-white/5 bg-[#12121a] hover:bg-white/5'
               }`}
            >
               <div className={`p-3 rounded-lg bg-[#0a0a0f] border border-white/5 ${s.color}`}>
                  <s.icon className="w-5 h-5" />
               </div>
               <div className="text-left">
                  <div className="text-sm font-semibold">{s.title}</div>
                  <div className="text-2xl font-bold mt-1">{count} <span className="text-xs font-normal text-[#7e7e8a]">Misafir</span></div>
               </div>
            </button>
          )
        })}
      </div>

      {/* CONTENT LIST */}
      <div className="flex-1 bg-[#12121a] border border-white/5 rounded-xl overflow-hidden flex flex-col">
        <div className="p-4 border-b border-white/5 bg-white/5 font-semibold">
           {SEGMENTS.find(s=>s.id === activeTab)?.title} Listesi
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
          {loading ? (
             <div className="h-full flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-yellow-500" /></div>
          ) : currentTabGuests.length === 0 ? (
             <div className="h-full flex flex-col items-center justify-center text-[#7e7e8a] opacity-50">
               <AlertCircle className="w-12 h-12 mb-3" />
               <p>Bu segmentte misafir bulunamadı.</p>
             </div>
          ) : (
             currentTabGuests.map((guest, idx) => (
                <div key={idx} className="flex flex-col md:flex-row md:items-center justify-between p-4 bg-[#1a1a22] border border-white/5 rounded-lg hover:border-yellow-500/30 transition-colors gap-4">
                   <div className="flex-1 flex flex-col gap-1">
                      <div className="font-semibold text-[15px] flex items-center gap-2">
                         {guest.name || guest.full_name || "İsimsiz Misafir"}
                         {guest.vip && <Crown className="w-3.5 h-3.5 text-yellow-500" />}
                      </div>
                      <div className="text-xs text-[#a9a9b2] flex gap-3">
                         {guest.email && <span>{guest.email}</span>}
                         {guest.phone && <span>{guest.phone}</span>}
                      </div>
                      <div className="text-[11px] text-[#7e7e8a] mt-1 space-x-3">
                         {guest.total_stays > 0 && <span>Konaklama: <b>{guest.total_stays} Kez</b></span>}
                         {guest.total_spent > 0 && <span>Harcama: <b>{guest.total_spent} ₺</b></span>}
                         {guest.last_visit_days_ago && <span className="text-red-300">Son Ziyaret: {guest.last_visit_days_ago} Gün Önce</span>}
                      </div>
                   </div>
                   
                   <Button onClick={() => handleGenerateCampaign(guest, activeTab)} className="bg-gradient-to-r from-yellow-600 to-amber-600 hover:from-yellow-500 hover:to-amber-500 text-white shadow-lg shrink-0">
                      <Sparkles className="w-4 h-4 mr-2" /> AI Kampanya Oluştur
                   </Button>
                </div>
             ))
          )}
        </div>
      </div>

      {/* AI DRAFT MODAL */}
      <Dialog open={!!targetGuest} onOpenChange={(open) => !open && setTargetGuest(null)}>
        <DialogContent className="bg-[#1a1a22] border-yellow-500/30 text-white max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-yellow-500">
              <Sparkles className="w-5 h-5" /> 
              {targetGuest?.name || targetGuest?.full_name} - AI İletişim Formülü
            </DialogTitle>
          </DialogHeader>
          
          <div className="py-2">
             {draftLoading ? (
                <div className="flex flex-col items-center justify-center py-12 text-yellow-400">
                   <Loader2 className="w-12 h-12 animate-spin mb-4" />
                   <p className="text-sm">Misafirin geçmişi analiz ediliyor ve ona özel samimi bir metin yazılıyor...</p>
                </div>
             ) : aiDraft ? (
                <div className="space-y-6">
                   <p className="text-xs text-[#a9a9b2]">Bu içerik tamamen tek misafire özel yazılmıştır. Mesajı kopyalayıp WhatsApp veya E-Posta üzerinden misafire anında gönderebilirsiniz.</p>
                   
                   {/* SMS / WHATSAPP */}
                   <div className="space-y-2">
                      <div className="text-xs font-bold text-emerald-400">📱 Kısa Mesaj (WhatsApp / SMS)</div>
                      <div className="relative group">
                        <div className="bg-[#0f0f14] border border-white/10 rounded-lg p-4 text-sm whitespace-pre-wrap text-[#e5e5e8]">
                           {aiDraft.sms}
                        </div>
                        <Button size="sm" variant="ghost" className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 bg-white/10 hover:bg-white/20 h-7" onClick={() => { navigator.clipboard.writeText(aiDraft.sms); alert('Kopyalandı!'); }}>
                           <Copy className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                   </div>

                   {/* EMAIL */}
                   <div className="space-y-2">
                      <div className="text-xs font-bold text-blue-400">✉️ Kurumsal E-Posta</div>
                      <div className="relative group bg-[#0f0f14] border border-white/10 rounded-lg overflow-hidden">
                        <div className="border-b border-white/5 p-3 flex items-center gap-2 text-sm">
                           <span className="text-[#7e7e8a]">Konu:</span>
                           <span className="font-semibold">{aiDraft.email_subject}</span>
                        </div>
                        <div className="p-4 text-sm whitespace-pre-wrap text-[#e5e5e8] font-mono">
                           {aiDraft.email_body}
                        </div>
                        <Button size="sm" variant="ghost" className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 bg-white/10 hover:bg-white/20 h-7" onClick={() => { navigator.clipboard.writeText(`${aiDraft.email_subject}\n\n${aiDraft.email_body}`); alert('E-Posta Kopyalandı!'); }}>
                           <Copy className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                   </div>

                   <div className="flex justify-end gap-3 pt-4">
                      <Button variant="outline" onClick={() => setTargetGuest(null)} className="border-white/10 text-[#a9a9b2]">Kapat</Button>
                      <Button className="bg-yellow-600 hover:bg-yellow-500 text-black font-semibold" onClick={() => alert('Gerçek sistemde doğrudan SendGrid veya Twilio/WhatsApp webhooklarına tetikleyebilirsiniz.')}>
                         <Send className="w-4 h-4 mr-2" /> Gönderimi Başlat
                      </Button>
                   </div>
                </div>
             ) : null}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
