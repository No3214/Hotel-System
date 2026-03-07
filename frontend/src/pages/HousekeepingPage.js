import React, { useState, useEffect } from 'react';
import { getHousekeeping, createHousekeeping, updateHousekeepingStatus, getHousekeepingAIRouting } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { BedDouble, Plus, CheckCircle, Clock, Loader2, Sparkles, Map, MapPin, Search } from 'lucide-react';
import { getAILostAndFoundMatch } from '../api';

const STATUS_CONFIG = {
  pending: { label: 'Bekliyor', color: 'bg-yellow-500/20 text-yellow-400', icon: Clock },
  in_progress: { label: 'Devam Ediyor', color: 'bg-blue-500/20 text-blue-400', icon: Loader2 },
  completed: { label: 'Tamamlandi', color: 'bg-green-500/20 text-green-400', icon: CheckCircle },
  inspected: { label: 'Kontrol Edildi', color: 'bg-purple-500/20 text-purple-400', icon: CheckCircle },
};

export default function HousekeepingPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ room_number: '', task_type: 'standard_clean', priority: 'normal', assigned_to: '', notes: '' });
  const [aiRouting, setAiRouting] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);

  // Phase 10: Lost & Found
  const [lostFoundMatches, setLostFoundMatches] = useState(null);
  const [matchLoading, setMatchLoading] = useState(false);

  const load = () => {
    getHousekeeping().then(r => setLogs(r.data.logs)).catch(console.error).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    if (!form.room_number) return;
    await createHousekeeping(form);
    setForm({ room_number: '', task_type: 'standard_clean', priority: 'normal', assigned_to: '', notes: '' });
    setOpen(false);
    load();
  };

  const handleStatus = async (id, status) => {
    await updateHousekeepingStatus(id, status);
    load();
  };

  const loadAiRouting = async () => {
    setAiLoading(true);
    try {
      const res = await getHousekeepingAIRouting();
      if (res.data.success) {
        setAiRouting(res.data.routing);
      }
    } catch (e) {
      console.error(e);
      alert('AI Rotalama kullanilamiyor.');
    }
    setAiLoading(false);
  };

  const handleAIMatch = async () => {
    setMatchLoading(true);
    try {
      const res = await getAILostAndFoundMatch();
      if (res.data?.success) {
        setLostFoundMatches(res.data.matches);
        if (res.data.matches.length === 0) alert('Eslesme bulunamadi veya kayit yetersiz.');
      }
    } catch(e) {
      console.error(e);
      alert('Kayip esya AI eslestirmesi sirasinda hata olustu.');
    }
    setMatchLoading(false);
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="housekeeping-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Kat Hizmetleri</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">{logs.length} kayit</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleAIMatch} disabled={matchLoading} className="bg-indigo-600 hover:bg-indigo-500 text-white border-none shadow-md hidden sm:flex">
            {matchLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Search className="w-4 h-4 mr-2" />}
            AI Kayip Esya Eslestir
          </Button>
          <Button onClick={loadAiRouting} disabled={aiLoading} className="bg-sky-600 hover:bg-sky-500 text-white border-none shadow-md" data-testid="ai-routing-btn">
            {aiLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Map className="w-4 h-4 mr-2" />}
            AI Rota Optimizasyonu
          </Button>
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-housekeeping-btn">
                <Plus className="w-4 h-4 mr-2" /> Temizlik Ekle
              </Button>
            </DialogTrigger>
          <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
            <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Temizlik Gorevi</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <Input placeholder="Oda numarasi *" value={form.room_number} onChange={e => setForm({ ...form, room_number: e.target.value })}
                className="bg-white/5 border-white/10" data-testid="room-number-input" />
              <Select value={form.task_type} onValueChange={v => setForm({ ...form, task_type: v })}>
                <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                <SelectContent className="bg-[#1a1a22] border-[#C4972A]/20">
                  <SelectItem value="standard_clean">Standart Temizlik</SelectItem>
                  <SelectItem value="deep_clean">Derin Temizlik</SelectItem>
                  <SelectItem value="checkout_clean">Check-out Temizligi</SelectItem>
                  <SelectItem value="turndown">Yatak Hazirlama</SelectItem>
                </SelectContent>
              </Select>
              <Input placeholder="Gorevli" value={form.assigned_to} onChange={e => setForm({ ...form, assigned_to: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Input placeholder="Notlar" value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Button onClick={handleCreate} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-housekeeping-btn">Kaydet</Button>
            </div>
          </DialogContent>
        </Dialog>
        </div>
      </div>

      {/* AI Routing Panel */}
      {aiRouting && (
        <div className="bg-sky-900/10 border border-sky-500/20 rounded-xl p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-sky-500/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
          <div className="flex items-center justify-between mb-4 relative z-10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-sky-500/10 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-sky-400" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-sky-400">{aiRouting.plan_name || 'Optimize Rota'}</h2>
                <p className="text-sm text-[#c8c8d0] mt-1 pr-4">{aiRouting.summary}</p>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 relative z-10">
            {aiRouting.optimized_route?.map((step, idx) => (
              <div key={idx} className="bg-[#12121a] border border-white/5 rounded-lg p-3 flex gap-4">
                <div className="w-10 flex-shrink-0 flex flex-col items-center">
                  <div className="w-8 h-8 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold text-sm">
                    {idx + 1}
                  </div>
                  {idx < aiRouting.optimized_route.length - 1 && <div className="w-0.5 h-full bg-sky-500/20 mt-2" />}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-lg">{step.room_number?.toUpperCase()}</span>
                    <Badge variant="outline" className="border-sky-500/30 text-sky-400 text-[10px]">{step.task}</Badge>
                    <span className="text-xs text-[#7e7e8a] flex items-center gap-1"><Clock className="w-3 h-3" /> ~{step.estimated_mins} dk</span>
                  </div>
                  <p className="text-xs text-[#a9a9b2] mt-1">{step.reason}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Phase 10: AI Lost & Found Matches */}
      {lostFoundMatches && lostFoundMatches.length > 0 && (
        <div className="bg-indigo-950/20 border border-indigo-500/30 rounded-xl p-6 relative overflow-hidden">
          <div className="flex items-center justify-between mb-4 relative z-10">
            <h2 className="text-lg font-bold text-indigo-400 flex items-center gap-2">
              <Search className="w-5 h-5" /> Gemini NLP: Kayip & Bulunan Eslesmeleri
            </h2>
            <Button variant="ghost" size="sm" onClick={() => setLostFoundMatches(null)} className="text-[#a9a9b2] hover:text-white">Kapat</Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 relative z-10">
            {lostFoundMatches.map((m, i) => (
               <div key={i} className="bg-[#12121a] border border-indigo-500/20 rounded-lg p-4">
                 <div className="flex items-center justify-between mb-2">
                    <Badge variant="outline" className={`${m.match_score > 80 ? 'border-green-500/50 text-green-400' : 'border-yellow-500/50 text-yellow-500'} bg-transparent`}>
                      % {m.match_score} Eslesme
                    </Badge>
                 </div>
                 <p className="text-sm text-[#e5e5e8] leading-relaxed mb-3">
                   <strong>Eslesme Nedeni:</strong> {m.reason}
                 </p>
                 <div className="text-xs text-[#a9a9b2] bg-white/5 p-2 rounded">
                   Lost ID: {m.lost_id} ↔ Found ID: {m.found_id}
                 </div>
               </div>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-3">
        {logs.map(log => {
          const config = STATUS_CONFIG[log.status] || STATUS_CONFIG.pending;
          return (
            <div key={log.id} className="glass rounded-xl p-4 hover:gold-glow transition-all" data-testid={`housekeeping-${log.id}`}>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-[#C4972A]/10 flex items-center justify-center">
                  <BedDouble className="w-6 h-6 text-[#C4972A]" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">Oda {log.room_number}</span>
                    <Badge className={config.color + ' text-xs'}>{config.label}</Badge>
                  </div>
                  <p className="text-xs text-[#7e7e8a] mt-1">
                    {log.task_type?.replace('_', ' ')} {log.assigned_to && `- ${log.assigned_to}`}
                  </p>
                  {log.notes && <p className="text-xs text-[#a9a9b2] mt-1">{log.notes}</p>}
                </div>
                <div className="flex gap-1">
                  {log.status === 'pending' && (
                    <Button size="sm" variant="outline" onClick={() => handleStatus(log.id, 'in_progress')}
                      className="text-xs border-blue-500/30 text-blue-400 hover:bg-blue-500/10">Basla</Button>
                  )}
                  {log.status === 'in_progress' && (
                    <Button size="sm" variant="outline" onClick={() => handleStatus(log.id, 'completed')}
                      className="text-xs border-green-500/30 text-green-400 hover:bg-green-500/10">Tamamla</Button>
                  )}
                  {log.status === 'completed' && (
                    <Button size="sm" variant="outline" onClick={() => handleStatus(log.id, 'inspected')}
                      className="text-xs border-purple-500/30 text-purple-400 hover:bg-purple-500/10">Kontrol Et</Button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
        {logs.length === 0 && !loading && (
          <div className="text-center py-12 text-[#7e7e8a]">
            <BedDouble className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Temizlik kaydi yok</p>
          </div>
        )}
      </div>
    </div>
  );
}
