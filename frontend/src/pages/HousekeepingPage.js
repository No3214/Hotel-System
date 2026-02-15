import React, { useState, useEffect } from 'react';
import { getHousekeeping, createHousekeeping, updateHousekeepingStatus } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { BedDouble, Plus, CheckCircle, Clock, Loader2 } from 'lucide-react';

const STATUS_CONFIG = {
  pending: { label: 'Bekliyor', color: 'bg-yellow-500/20 text-yellow-400', icon: Clock },
  in_progress: { label: 'Devam Ediyor', color: 'bg-blue-500/20 text-blue-400', icon: Loader2 },
  completed: { label: 'Tamamlandi', color: 'bg-green-500/20 text-green-400', icon: CheckCircle },
  inspected: { label: 'Kontrol Edildi', color: 'bg-purple-500/20 text-purple-400', icon: CheckCircle },
};

export default function HousekeepingPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ room_number: '', task_type: 'standard_clean', priority: 'normal', assigned_to: '', notes: '' });

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

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="housekeeping-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Kat Hizmetleri</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">{logs.length} kayit</p>
        </div>
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
