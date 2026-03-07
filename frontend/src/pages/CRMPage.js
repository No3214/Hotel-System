import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Building2, Plus, Phone, Mail, MoreVertical, Search, Zap, Loader2,
  Trash2, MailPlus, AlertCircle, CheckCircle, ArrowRight, DollarSign, GripVertical
} from 'lucide-react';
import { 
  getDeals, createDeal, updateDealStatus, deleteDeal, 
  simulateAILeadDiscovery, getAIPitch 
} from '../api';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';

const STAGES = [
  { id: 'lead', title: 'Aday Şirketler', color: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' },
  { id: 'contacted', title: 'İletişim Kuruldu', color: 'bg-amber-500/10 text-amber-400 border-amber-500/20' },
  { id: 'proposal', title: 'Teklif Verildi', color: 'bg-blue-500/10 text-blue-400 border-blue-500/20' },
  { id: 'won', title: 'Anlaşma Sağlandı', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' },
  { id: 'lost', title: 'Kaybedildi', color: 'bg-red-500/10 text-red-400 border-red-500/20' }
];

export default function CRMPage() {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [discoveryLoading, setDiscoveryLoading] = useState(false);
  const [search, setSearch] = useState('');
  
  // Custom Deal Modal
  const [openNewDeal, setOpenNewDeal] = useState(false);
  const [formData, setFormData] = useState({ 
    company_name: '', contact_person: '', email: '', phone: '', sector: '', estimated_value: '', notes: '' 
  });

  // AI Pitch Modal
  const [pitchDeal, setPitchDeal] = useState(null);
  const [pitchContent, setPitchContent] = useState('');
  const [pitchLoading, setPitchLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getDeals();
      setDeals(res.data?.deals || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const handleCreateDeal = async () => {
    if (!formData.company_name) return;
    try {
      await createDeal({ ...formData, estimated_value: parseFloat(formData.estimated_value || 0) });
      setOpenNewDeal(false);
      setFormData({ company_name: '', contact_person: '', email: '', phone: '', sector: '', estimated_value: '', notes: '' });
      loadData();
    } catch (e) { console.error(e); }
  };

  const handleUpdateStatus = async (dealId, newStatus) => {
    // Optimistic UI Update
    setDeals(prev => prev.map(d => d.id === dealId ? { ...d, status: newStatus } : d));
    try {
      await updateDealStatus(dealId, newStatus);
    } catch (e) {
      console.error(e);
      loadData(); // Revert on failure
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Bu sirket kaydini kalici olarak silmek istediginize emin misiniz?")) return;
    try {
      await deleteDeal(id);
      loadData();
    } catch(e) { console.error(e); }
  };

  const handleAILiscovery = async () => {
    setDiscoveryLoading(true);
    try {
      const res = await simulateAILeadDiscovery();
      if (res.data?.success) {
        alert(`${res.data.deals.length} yeni bolgesel kurumsal sirket adayi bulundu ve eklendi!`);
        loadData();
      }
    } catch (e) { console.error(e); alert("AI Lead kesfi sirasinda hata olustu."); }
    setDiscoveryLoading(false);
  };

  const handleGeneratePitch = async (deal) => {
    setPitchDeal(deal);
    setPitchContent('');
    setPitchLoading(true);
    try {
      const res = await getAIPitch(deal.id);
      if (res.data?.success) {
        setPitchContent(res.data.pitch);
      }
    } catch (e) { console.error(e); alert("AI Pitch olusturulamadi."); }
    setPitchLoading(false);
  };
  
  const copyPitch = () => {
    navigator.clipboard.writeText(pitchContent);
    alert('E-posta metni kopyalandı.');
  }

  // Drag and Drop handlers (Simple React Dnd implementation over native HTML5)
  const onDragStart = (e, dealId) => {
    e.dataTransfer.setData("dealId", dealId);
  };
  const onDragOver = (e) => { e.preventDefault(); };
  const onDrop = (e, targetStatus) => {
    e.preventDefault();
    const dealId = e.dataTransfer.getData("dealId");
    if (dealId) {
      handleUpdateStatus(dealId, targetStatus);
    }
  };

  const filteredDeals = deals.filter(d => 
    d.company_name.toLowerCase().includes(search.toLowerCase()) || 
    d.contact_person.toLowerCase().includes(search.toLowerCase()) ||
    d.sector.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full bg-[#0a0a0f] text-white p-6 space-y-6 overflow-hidden">
      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Building2 className="w-6 h-6 text-indigo-400" /> B2B Kurumsal Satış (CRM)
          </h1>
          <p className="text-sm text-[#a9a9b2] mt-1">Bölgesel sanayi, liman ve şirket konaklamalarını yönetin.</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-[#7e7e8a] absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              type="text" placeholder="Şirket, kişi veya sektör ara..."
              value={search} onChange={e => setSearch(e.target.value)}
              className="bg-[#12121a] border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white w-64 focus:border-indigo-500/50 focus:outline-none"
            />
          </div>
          
          <Button 
            onClick={handleAILiscovery} disabled={discoveryLoading}
            className="bg-indigo-600 hover:bg-indigo-500 text-white shadow-[0_0_15px_rgba(79,70,229,0.3)] transition-all"
          >
            {discoveryLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Zap className="w-4 h-4 mr-2" />}
            AI Firmaları Keşfet
          </Button>

          <Dialog open={openNewDeal} onOpenChange={setOpenNewDeal}>
            <DialogTrigger asChild>
              <Button className="bg-emerald-600 hover:bg-emerald-500 text-white">
                <Plus className="w-4 h-4 mr-2" /> Şirket Ekle
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#1a1a22] border-white/10 text-white md:max-w-lg">
              <DialogHeader><DialogTitle>Yeni Kurumsal Fırsat Ekle</DialogTitle></DialogHeader>
              <div className="space-y-4 py-2">
                <div className="grid grid-cols-2 gap-4">
                   <Input placeholder="Şirket Adı *" value={formData.company_name} onChange={e => setFormData(p => ({...p, company_name: e.target.value}))} className="bg-white/5 border-white/10" />
                   <Input placeholder="Sektör (Örn: Lojistik)" value={formData.sector} onChange={e => setFormData(p => ({...p, sector: e.target.value}))} className="bg-white/5 border-white/10" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                   <Input placeholder="İletişim Kişisi" value={formData.contact_person} onChange={e => setFormData(p => ({...p, contact_person: e.target.value}))} className="bg-white/5 border-white/10" />
                   <Input placeholder="E-posta" type="email" value={formData.email} onChange={e => setFormData(p => ({...p, email: e.target.value}))} className="bg-white/5 border-white/10" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                   <Input placeholder="Telefon" value={formData.phone} onChange={e => setFormData(p => ({...p, phone: e.target.value}))} className="bg-white/5 border-white/10" />
                   <Input placeholder="Beklenen Ciro (TL)" type="number" value={formData.estimated_value} onChange={e => setFormData(p => ({...p, estimated_value: e.target.value}))} className="bg-white/5 border-white/10" />
                </div>
                <textarea 
                  placeholder="Satış Notları..." value={formData.notes} onChange={e => setFormData(p => ({...p, notes: e.target.value}))}
                  className="w-full bg-white/5 border border-white/10 rounded-md p-3 text-sm resize-none focus:outline-none focus:border-indigo-500/50" rows={3}
                />
                <Button className="w-full bg-emerald-600 hover:bg-emerald-500" onClick={handleCreateDeal}>Kaydet</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* KANBAN BOARD */}
      {loading ? (
        <div className="flex-1 flex items-center justify-center"><Loader2 className="w-8 h-8 text-indigo-400 animate-spin" /></div>
      ) : (
        <div className="flex-1 overflow-x-auto pb-4 custom-scrollbar">
          <div className="flex gap-4 h-full min-w-max">
            {STAGES.map(stage => {
              const stageDeals = filteredDeals.filter(d => d.status === stage.id);
              const stageValue = stageDeals.reduce((sum, d) => sum + d.estimated_value, 0);

              return (
                <div 
                  key={stage.id} 
                  className="w-80 flex flex-col bg-[#12121a] border border-white/5 rounded-xl overflow-hidden"
                  onDragOver={onDragOver}
                  onDrop={(e) => onDrop(e, stage.id)}
                >
                  {/* Stage Header */}
                  <div className={`p-3 border-b flex items-center justify-between ${stage.color} bg-opacity-20`}>
                    <div className="font-semibold text-sm flex items-center gap-2">
                       {stage.title} 
                       <span className="bg-white/10 text-xs px-2 py-0.5 rounded-full">{stageDeals.length}</span>
                    </div>
                    <span className="text-xs font-medium opacity-80" title="Beklenen B2B Ciro">
                      {new Intl.NumberFormat('tr-TR', { notation: "compact", maximumFractionDigits: 1 }).format(stageValue)}₺
                    </span>
                  </div>

                  {/* Stage Body (Cards) */}
                  <div className="flex-1 p-3 overflow-y-auto custom-scrollbar space-y-3">
                    {stageDeals.map(deal => (
                      <div 
                        key={deal.id} 
                        draggable 
                        onDragStart={(e) => onDragStart(e, deal.id)}
                        className="bg-[#1a1a22] border border-white/10 hover:border-indigo-500/50 rounded-lg p-3 cursor-grab active:cursor-grabbing group transition-all"
                      >
                         <div className="flex justify-between items-start mb-2">
                            <h4 className="font-semibold text-[13px] text-white flex-1">{deal.company_name}</h4>
                            <div className="flex gap-1 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                               <button onClick={() => handleDelete(deal.id)} className="text-red-400/60 hover:text-red-400"><Trash2 className="w-3.5 h-3.5" /></button>
                            </div>
                         </div>
                         
                         <div className="text-[11px] text-[#a9a9b2] space-y-1 mb-3">
                            {deal.sector && <div className="flex items-center gap-1"><Building2 className="w-3 h-3" /> {deal.sector}</div>}
                            {deal.contact_person && <div className="flex items-center gap-1"><AlertCircle className="w-3 h-3" /> Yetkili: {deal.contact_person}</div>}
                            {deal.email && <div className="flex items-center gap-1 text-blue-300/80"><Mail className="w-3 h-3" /> {deal.email}</div>}
                         </div>

                         <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/5">
                            <div className="text-xs font-medium text-emerald-400 flex items-center gap-1">
                               <DollarSign className="w-3.5 h-3.5" /> 
                               {new Intl.NumberFormat('tr-TR').format(deal.estimated_value)} ₺
                            </div>
                            
                            {/* AI PITCH BUTTON */}
                            <Button size="sm" variant="ghost" className="h-6 px-2 text-[10px] bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 rounded" onClick={() => handleGeneratePitch(deal)}>
                               <Sparkles className="w-3 h-3 mr-1" /> Satış E-postası
                            </Button>
                         </div>
                      </div>
                    ))}
                    {stageDeals.length === 0 && (
                      <div className="text-center p-4 border-2 border-dashed border-white/5 rounded-lg text-xs text-[#5a5a65]">
                        Sürükle bırak
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* AI PITCH MODAL */}
      <Dialog open={!!pitchDeal} onOpenChange={(open) => !open && setPitchDeal(null)}>
        <DialogContent className="bg-[#1a1a22] border-indigo-500/30 text-white max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-indigo-400">
              <Sparkles className="w-5 h-5" /> 
              {pitchDeal?.company_name} - AI Satış Formülü
            </DialogTitle>
          </DialogHeader>
          
          <div className="py-2">
             {pitchLoading ? (
                <div className="flex flex-col items-center justify-center py-10 text-indigo-300">
                   <Loader2 className="w-10 h-10 animate-spin mb-4" />
                   <p className="text-sm">Şirket sektörü analiz ediliyor ve ikna edici B2B e-postası yazılıyor...</p>
                </div>
             ) : (
                <div className="space-y-4">
                   <p className="text-xs text-[#a9a9b2]">Bu e-posta taslağı doğrudan <strong>{pitchDeal?.contact_person || 'Şirket Yetkilisine'}</strong> gönderilmek üzere yapay zeka tarafından özelleştirildi.</p>
                   
                   <div className="bg-[#0f0f14] border border-white/10 rounded-lg p-4 text-sm whitespace-pre-wrap text-[#e5e5e8] font-mono h-96 overflow-y-auto">
                     {pitchContent}
                   </div>

                   <div className="flex justify-end gap-3">
                      <Button variant="outline" onClick={() => setPitchDeal(null)} className="border-white/10 text-[#a9a9b2]">Kapat</Button>
                      <Button className="bg-indigo-600 hover:bg-indigo-500 text-white" onClick={copyPitch}>
                         E-postayı Kopyala
                      </Button>
                   </div>
                </div>
             )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
