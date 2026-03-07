import React, { useState, useEffect } from 'react';
import { getCampaigns, createCampaign, updateCampaignStatus, deleteCampaign, getAILoyaltyCampaigns, getAIB2BLeads } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Mail, Plus, Trash2, Send, Eye, MousePointer, Users, Sparkles, Check, Briefcase, Building2, Linkedin, Loader2 } from 'lucide-react';

const STATUS_CONFIG = {
  draft: { label: 'Taslak', color: 'bg-gray-500/20 text-gray-400' },
  scheduled: { label: 'Planlanmis', color: 'bg-blue-500/20 text-blue-400' },
  sent: { label: 'Gonderildi', color: 'bg-green-500/20 text-green-400' },
  cancelled: { label: 'Iptal', color: 'bg-red-500/20 text-red-400' },
};

const SEGMENTS = {
  all: 'Tum Misafirler',
  vip: 'VIP Misafirler',
  recent: 'Son 30 Gun',
  returning: 'Tekrar Gelen',
  international: 'Uluslararasi',
};

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ title: '', subject: '', content: '', target_segment: 'all', channel: 'email', scheduled_at: '' });
  
  // Tabs
  const [tab, setTab] = useState('campaigns'); // 'campaigns' | 'b2b'

  // AI CRM State
  const [aiLoading, setAiLoading] = useState(false);
  const [aiCampaigns, setAiCampaigns] = useState([]);

  // B2B State
  const [b2bLeads, setB2bLeads] = useState([]);
  const [b2bLoading, setB2bLoading] = useState(false);
  const [b2bIndustry, setB2bIndustry] = useState('Sanayi (OSB)');

  const load = () => {
    getCampaigns().then(r => setCampaigns(r.data.campaigns)).catch(console.error).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);
  
  const fetchAILoyalty = async () => {
    setAiLoading(true);
    try {
      const { data } = await getAILoyaltyCampaigns();
      if (data.campaigns) setAiCampaigns(data.campaigns);
    } catch (error) {
       console.error(error);
    } finally {
      setAiLoading(false);
    }
  };
  
  const handleApproveAICampaign = async (aiComp) => {
      await createCampaign({
          title: `AI Sadakat: ${aiComp.guest_name}`,
          subject: aiComp.subject,
          content: aiComp.message,
          target_segment: 'returning',
          channel: 'email',
          status: 'draft'
      });
      // Remove from list
      setAiCampaigns(prev => prev.filter(c => c.id !== aiComp.id));
      load();
  };

  const handleCreate = async () => {
    if (!form.title || !form.subject || !form.content) return;
    await createCampaign(form);
    setForm({ title: '', subject: '', content: '', target_segment: 'all', channel: 'email', scheduled_at: '' });
    setOpen(false);
    load();
  };

  const handleSend = async (id) => {
    await updateCampaignStatus(id, 'sent');
    load();
  };

  const handleRunB2B = async () => {
    setB2bLoading(true);
    try {
      const { data } = await getAIB2BLeads(b2bIndustry);
      if (data.success) setB2bLeads(data.leads || []);
    } catch(e) { console.error("B2B err", e); }
    setB2bLoading(false);
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="campaigns-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">E-posta Kampanyalari</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">{campaigns.length} kampanya</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={fetchAILoyalty} disabled={aiLoading} className="bg-indigo-600 hover:bg-indigo-700 text-white">
            <Sparkles className="w-4 h-4 mr-2" /> 
            {aiLoading ? 'Analiz Ediliyor...' : 'AI Sadakat Fırsatları'}
          </Button>
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-campaign-btn">
                <Plus className="w-4 h-4 mr-2" /> Yeni Kampanya
              </Button>
            </DialogTrigger>
          <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
            <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Kampanya</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <Input placeholder="Kampanya adi *" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} className="bg-white/5 border-white/10" data-testid="campaign-title-input" />
              <Input placeholder="E-posta konusu *" value={form.subject} onChange={e => setForm({ ...form, subject: e.target.value })} className="bg-white/5 border-white/10" />
              <textarea placeholder="Icerik *" value={form.content} onChange={e => setForm({ ...form, content: e.target.value })}
                className="w-full min-h-[100px] p-3 rounded-md bg-white/5 border border-white/10 text-sm resize-none focus:border-[#C4972A]/50 focus:outline-none" data-testid="campaign-content" />
              <Select value={form.target_segment} onValueChange={v => setForm({ ...form, target_segment: v })}>
                <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                <SelectContent className="bg-[#1a1a22] border-[#C4972A]/20">
                  {Object.entries(SEGMENTS).map(([k, v]) => <SelectItem key={k} value={k}>{v}</SelectItem>)}
                </SelectContent>
              </Select>
              <Select value={form.channel} onValueChange={v => setForm({ ...form, channel: v })}>
                <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                <SelectContent className="bg-[#1a1a22] border-[#C4972A]/20">
                  <SelectItem value="email">E-posta</SelectItem>
                  <SelectItem value="whatsapp">WhatsApp</SelectItem>
                  <SelectItem value="sms">SMS</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={handleCreate} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-campaign-btn">Olustur</Button>
            </div>
          </DialogContent>
        </Dialog>
        </div>
      </div>
      
      <div className="flex gap-2 mb-6">
        <Button 
          variant={tab === 'campaigns' ? 'default' : 'ghost'} 
          onClick={() => setTab('campaigns')}
          className={tab === 'campaigns' ? 'bg-[#C4972A] text-white' : 'text-[#7e7e8a]'}
        >
          <Mail className="w-4 h-4 mr-2" /> E-posta Kampanyaları
        </Button>
        <Button 
          variant={tab === 'b2b' ? 'default' : 'ghost'} 
          onClick={() => setTab('b2b')}
          className={tab === 'b2b' ? 'bg-[#1a1a22] border border-[#C4972A]/50 text-[#C4972A]' : 'text-[#7e7e8a]'}
        >
          <Briefcase className="w-4 h-4 mr-2 text-[#C4972A]" /> B2B Kurumsal Satış (AI)
        </Button>
      </div>

      {tab === 'campaigns' ? (
        <>
          {aiCampaigns.length > 0 && (
            <div className="mb-8 p-6 bg-indigo-500/10 border border-indigo-500/30 rounded-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10"><Sparkles className="w-24 h-24" /></div>
                <h2 className="text-xl font-semibold text-indigo-400 flex items-center gap-2 mb-4">
                   <Sparkles className="w-5 h-5" /> Gemini CRM: Yaklaşan Yıldönümleri / Bekleyen Fırsatlar
                </h2>
                <div className="grid md:grid-cols-2 gap-4">
                    {aiCampaigns.map(ac => (
                        <div key={ac.id} className="bg-[#1a1a22] p-4 rounded-lg border border-indigo-500/20">
                            <div className="flex justify-between items-start mb-2">
                                <div>
                                    <h3 className="font-medium text-white">{ac.guest_name}</h3>
                                    <span className="text-xs text-indigo-300">{ac.reason}</span>
                                </div>
                                <Button size="sm" onClick={() => handleApproveAICampaign(ac)} className="bg-green-600 hover:bg-green-700 h-8">
                                    <Check className="w-3 h-3 mr-1" /> Onayla & Taslağa Ekle
                                </Button>
                            </div>
                            <div className="bg-white/5 p-3 rounded text-sm text-[#a9a9b2]">
                                <p className="font-medium text-white mb-1">Konu: {ac.subject}</p>
                                <p className="line-clamp-2">{ac.message}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
          )}

          <div className="space-y-4">
        {campaigns.map(c => {
          const cfg = STATUS_CONFIG[c.status] || STATUS_CONFIG.draft;
          return (
            <div key={c.id} className="glass rounded-xl p-5 hover:gold-glow transition-all" data-testid={`campaign-${c.id}`}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">{c.title}</h3>
                    <Badge className={cfg.color + ' text-xs'}>{cfg.label}</Badge>
                    <Badge className="bg-white/5 text-[#7e7e8a] text-xs">{SEGMENTS[c.target_segment] || c.target_segment}</Badge>
                  </div>
                  <p className="text-sm text-[#a9a9b2] mt-1">{c.subject}</p>
                  <p className="text-xs text-[#7e7e8a] mt-2 line-clamp-2">{c.content}</p>
                  {c.status === 'sent' && (
                    <div className="flex items-center gap-4 mt-3">
                      <span className="flex items-center gap-1 text-xs text-[#C4972A]"><Users className="w-3 h-3" />{c.recipients_count} alici</span>
                      <span className="flex items-center gap-1 text-xs text-green-400"><Eye className="w-3 h-3" />{c.opened_count} acilma</span>
                      <span className="flex items-center gap-1 text-xs text-blue-400"><MousePointer className="w-3 h-3" />{c.clicked_count} tiklama</span>
                    </div>
                  )}
                </div>
                <div className="flex gap-1.5 ml-4">
                  {c.status === 'draft' && (
                    <Button size="sm" onClick={() => handleSend(c.id)} className="bg-green-600 hover:bg-green-700 text-white text-xs" data-testid={`send-campaign-${c.id}`}>
                      <Send className="w-3 h-3 mr-1" /> Gonder
                    </Button>
                  )}
                  <button onClick={() => { deleteCampaign(c.id).then(load); }} className="text-[#7e7e8a] hover:text-red-400">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
        {campaigns.length === 0 && !loading && (
          <div className="text-center py-12 text-[#7e7e8a]">
            <Mail className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Henuz kampanya yok</p>
          </div>
        )}
      </div>
      </>
      ) : (
        <div className="space-y-6">
           <div className="glass rounded-xl p-5 border border-[#C4972A]/30 flex flex-col md:flex-row items-center justify-between gap-4 relative overflow-hidden">
               <div className="absolute top-0 right-0 w-64 h-64 bg-[#C4972A]/10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
               <div className="relative z-10 w-full md:w-auto">
                  <h3 className="text-xl font-bold text-[#C4972A] flex items-center gap-2 mb-1">
                     <Building2 className="w-5 h-5" /> B2B Kurumsal Satış Robotu
                  </h3>
                  <p className="text-sm text-[#a9a9b2] max-w-lg">Çevredeki şirketleri sektörel olarak bulur, onlara uygun konaklama paketleri tasarlar ve kilit karar vericilere göndermeniz için çok kanallı (E-posta + LinkedIn) taslaklar sunar.</p>
               </div>
               <div className="relative z-10 flex items-center w-full md:w-auto gap-3">
                  <Select value={b2bIndustry} onValueChange={setB2bIndustry}>
                     <SelectTrigger className="w-[200px] bg-white/5 border-white/10 text-white">
                        <SelectValue placeholder="Sektör Seçin" />
                     </SelectTrigger>
                     <SelectContent className="bg-[#1a1a22] border-[#C4972A]/30 text-white">
                        <SelectItem value="Sanayi (OSB)">Sanayi Bölgesi (OSB)</SelectItem>
                        <SelectItem value="Liman ve Gümrük">Liman ve Gümrük</SelectItem>
                        <SelectItem value="Serbest Bölge">Serbest Bölge</SelectItem>
                        <SelectItem value="Lojistik Şirketleri">Lojistik Şirketleri</SelectItem>
                        <SelectItem value="Yazılım ve Teknoloji">Yazılım ve Teknoloji</SelectItem>
                        <SelectItem value="Sağlık ve İlaç">Sağlık ve İlaç</SelectItem>
                     </SelectContent>
                  </Select>
                  <Button onClick={handleRunB2B} disabled={b2bLoading} className="bg-[#C4972A] hover:bg-[#a87a1f] text-white">
                     {b2bLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
                     Müşteri Bul
                  </Button>
               </div>
           </div>

           {b2bLoading ? (
               <div className="py-20 text-center">
                  <Loader2 className="w-10 h-10 animate-spin text-[#C4972A] mx-auto mb-4" />
                  <p className="text-[#a9a9b2]">Bölgedeki <b>{b2bIndustry}</b> sektörü taranıyor, şirketler analiz ediliyor ve paketler oluşturuluyor...</p>
               </div>
           ) : b2bLeads.length > 0 ? (
               <div className="grid grid-cols-1 gap-6">
                  {b2bLeads.map((lead, i) => (
                     <div key={i} className="glass rounded-xl p-5 border border-white/10 hover:border-[#C4972A]/30 transition-all flex flex-col md:flex-row gap-6">
                        <div className="w-full md:w-1/3 border-b md:border-b-0 md:border-r border-white/10 pb-4 md:pb-0 md:pr-4">
                           <div className="flex items-center gap-3 mb-3">
                              <div className="w-10 h-10 rounded-lg bg-[#C4972A]/10 flex items-center justify-center">
                                 <Building2 className="w-5 h-5 text-[#C4972A]" />
                              </div>
                              <div>
                                 <h4 className="font-bold text-lg text-white">{lead.company_name}</h4>
                                 <Badge className="bg-emerald-500/10 text-emerald-400 border-0 text-[10px] uppercase font-bold tracking-wider">{lead.status_label}</Badge>
                              </div>
                           </div>
                           <div className="space-y-2 mt-4 text-sm">
                              <div>
                                 <span className="text-[#7e7e8a] block text-xs">Karar Verici</span>
                                 <p className="text-[#e5e5e8] font-medium flex items-center gap-1.5"><Users className="w-3.5 h-3.5 text-[#C4972A]" /> {lead.contact_person}</p>
                              </div>
                              <div>
                                 <span className="text-[#7e7e8a] block text-xs">Satış Açısı (Değer Önerisi)</span>
                                 <p className="text-indigo-300 italic">"{lead.angle}"</p>
                              </div>
                           </div>
                        </div>

                        <div className="w-full md:w-2/3 grid grid-cols-1 md:grid-cols-2 gap-4">
                           {/* Email Panel */}
                           <div className="bg-[#1a1a22]/80 p-4 rounded-xl border border-white/5 relative group">
                              <div className="absolute -top-3 left-4 bg-[#1a1a22] px-2 text-xs font-semibold text-blue-400 flex items-center gap-1">
                                 <Mail className="w-3.5 h-3.5" /> Soğuk E-Posta
                              </div>
                              <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                 <Button size="sm" className="h-7 text-[10px] bg-blue-600 hover:bg-blue-700 text-white"><Send className="w-3 h-3 mr-1" /> Kopyala/Gönder</Button>
                              </div>
                              <p className="text-xs text-[#a9a9b2] whitespace-pre-wrap mt-2">{lead.cold_email}</p>
                           </div>

                           {/* LinkedIn Panel */}
                           <div className="bg-[#1a1a22]/80 p-4 rounded-xl border border-white/5 relative group">
                              <div className="absolute -top-3 left-4 bg-[#1a1a22] px-2 text-xs font-semibold text-[#0a66c2] flex items-center gap-1">
                                 <Linkedin className="w-3.5 h-3.5" /> LinkedIn Mesajı
                              </div>
                              <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                 <Button size="sm" className="h-7 text-[10px] bg-[#0a66c2] hover:bg-[#004182] text-white"><Send className="w-3 h-3 mr-1" /> Bağlan</Button>
                              </div>
                              <p className="text-xs text-[#a9a9b2] whitespace-pre-wrap mt-2">{lead.linkedin_dm}</p>
                           </div>
                        </div>
                     </div>
                  ))}
               </div>
           ) : (
              <div className="text-center py-20 text-[#7e7e8a] flex flex-col items-center">
                 <Building2 className="w-16 h-16 opacity-20 mb-4" />
                 <p className="max-w-md">Sol üstten sektör seçip "Müşteri Bul" butonuna bastığınızda, çevredeki hedef şirketler ve onlara gönderilecek otomatik pazarlama mesajları burada listelenecektir.</p>
              </div>
           )}
        </div>
      )}
    </div>
  );
}
