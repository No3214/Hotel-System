import React, { useState, useEffect } from 'react';
import { getCampaigns, createCampaign, updateCampaignStatus, deleteCampaign, getAILoyaltyCampaigns } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Mail, Plus, Trash2, Send, Eye, MousePointer, Users, Sparkles, Check } from 'lucide-react';

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
  
  // AI CRM State
  const [aiLoading, setAiLoading] = useState(false);
  const [aiCampaigns, setAiCampaigns] = useState([]);

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
    </div>
  );
}
