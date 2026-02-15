import React, { useState, useEffect } from 'react';
import { getCampaigns, createCampaign, updateCampaignStatus, deleteCampaign } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Mail, Plus, Trash2, Send, Eye, MousePointer, Users } from 'lucide-react';

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

  const load = () => {
    getCampaigns().then(r => setCampaigns(r.data.campaigns)).catch(console.error).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

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
