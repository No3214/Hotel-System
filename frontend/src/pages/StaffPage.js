import React, { useState, useEffect } from 'react';
import { getStaff, createStaff, deleteStaff, getShifts, createShift, deleteShift } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Users, Plus, Trash2, Clock, Calendar } from 'lucide-react';

const DEPARTMENTS = {
  resepsiyon: 'Resepsiyon',
  mutfak: 'Mutfak',
  kat_hizmetleri: 'Kat Hizmetleri',
  bahce: 'Bahce & Havuz',
  guvenlik: 'Guvenlik',
  yonetim: 'Yonetim',
  general: 'Genel',
};

export default function StaffPage() {
  const [staff, setStaff] = useState([]);
  const [shifts, setShifts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('staff');
  const [openStaff, setOpenStaff] = useState(false);
  const [openShift, setOpenShift] = useState(false);
  const [form, setForm] = useState({ name: '', role: '', phone: '', email: '', department: 'general' });
  const [shiftForm, setShiftForm] = useState({ staff_id: '', staff_name: '', date: '', start_time: '08:00', end_time: '17:00', department: 'general', notes: '' });

  const loadStaff = () => { getStaff().then(r => setStaff(r.data.staff)).catch(console.error).finally(() => setLoading(false)); };
  const loadShifts = () => { getShifts().then(r => setShifts(r.data.shifts)).catch(console.error); };

  useEffect(() => { loadStaff(); loadShifts(); }, []);

  const handleCreateStaff = async () => {
    if (!form.name || !form.role) return;
    await createStaff(form);
    setForm({ name: '', role: '', phone: '', email: '', department: 'general' });
    setOpenStaff(false);
    loadStaff();
  };

  const handleCreateShift = async () => {
    if (!shiftForm.staff_id || !shiftForm.date) return;
    await createShift(shiftForm);
    setShiftForm({ staff_id: '', staff_name: '', date: '', start_time: '08:00', end_time: '17:00', department: 'general', notes: '' });
    setOpenShift(false);
    loadShifts();
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="staff-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Personel & Vardiyalar</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">{staff.length} personel, {shifts.length} vardiya</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={openStaff} onOpenChange={setOpenStaff}>
            <DialogTrigger asChild>
              <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-staff-btn">
                <Plus className="w-4 h-4 mr-2" /> Personel Ekle
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
              <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Personel</DialogTitle></DialogHeader>
              <div className="space-y-3">
                <Input placeholder="Ad Soyad *" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} className="bg-white/5 border-white/10" data-testid="staff-name-input" />
                <Input placeholder="Gorev *" value={form.role} onChange={e => setForm({ ...form, role: e.target.value })} className="bg-white/5 border-white/10" />
                <Select value={form.department} onValueChange={v => setForm({ ...form, department: v })}>
                  <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-[#1a1a22] border-[#C4972A]/20">
                    {Object.entries(DEPARTMENTS).map(([k, v]) => <SelectItem key={k} value={k}>{v}</SelectItem>)}
                  </SelectContent>
                </Select>
                <Input placeholder="Telefon" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} className="bg-white/5 border-white/10" />
                <Input placeholder="E-posta" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} className="bg-white/5 border-white/10" />
                <Button onClick={handleCreateStaff} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-staff-btn">Kaydet</Button>
              </div>
            </DialogContent>
          </Dialog>
          <Dialog open={openShift} onOpenChange={setOpenShift}>
            <DialogTrigger asChild>
              <Button variant="outline" className="border-[#C4972A]/30 text-[#C4972A]" data-testid="add-shift-btn">
                <Clock className="w-4 h-4 mr-2" /> Vardiya Ekle
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
              <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Vardiya</DialogTitle></DialogHeader>
              <div className="space-y-3">
                <Select value={shiftForm.staff_id} onValueChange={v => {
                  const s = staff.find(x => x.id === v);
                  setShiftForm({ ...shiftForm, staff_id: v, staff_name: s?.name || '', department: s?.department || 'general' });
                }}>
                  <SelectTrigger className="bg-white/5 border-white/10"><SelectValue placeholder="Personel secin *" /></SelectTrigger>
                  <SelectContent className="bg-[#1a1a22] border-[#C4972A]/20 max-h-48">
                    {staff.map(s => <SelectItem key={s.id} value={s.id}>{s.name} - {s.role}</SelectItem>)}
                  </SelectContent>
                </Select>
                <Input type="date" value={shiftForm.date} onChange={e => setShiftForm({ ...shiftForm, date: e.target.value })} className="bg-white/5 border-white/10" data-testid="shift-date" />
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs text-[#7e7e8a] block mb-1">Baslangic</label>
                    <Input type="time" value={shiftForm.start_time} onChange={e => setShiftForm({ ...shiftForm, start_time: e.target.value })} className="bg-white/5 border-white/10" />
                  </div>
                  <div>
                    <label className="text-xs text-[#7e7e8a] block mb-1">Bitis</label>
                    <Input type="time" value={shiftForm.end_time} onChange={e => setShiftForm({ ...shiftForm, end_time: e.target.value })} className="bg-white/5 border-white/10" />
                  </div>
                </div>
                <Input placeholder="Notlar" value={shiftForm.notes} onChange={e => setShiftForm({ ...shiftForm, notes: e.target.value })} className="bg-white/5 border-white/10" />
                <Button onClick={handleCreateShift} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-shift-btn">Kaydet</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[['staff', 'Personel', Users], ['shifts', 'Vardiyalar', Calendar]].map(([id, label, Icon]) => (
          <button key={id} onClick={() => setTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all ${tab === id ? 'bg-[#C4972A]/20 text-[#C4972A]' : 'bg-white/5 text-[#7e7e8a] hover:bg-white/10'}`}>
            <Icon className="w-4 h-4" /> {label}
          </button>
        ))}
      </div>

      {/* Staff List */}
      {tab === 'staff' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {staff.map(s => (
            <div key={s.id} className="glass rounded-xl p-4 hover:gold-glow transition-all" data-testid={`staff-${s.id}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-[#C4972A]/20 flex items-center justify-center text-[#C4972A] font-bold">
                    {s.name?.[0]}
                  </div>
                  <div>
                    <p className="font-medium">{s.name}</p>
                    <p className="text-xs text-[#C4972A]">{s.role}</p>
                  </div>
                </div>
                <button onClick={() => { deleteStaff(s.id).then(loadStaff); }} className="text-[#7e7e8a] hover:text-red-400">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              <div className="mt-3 flex items-center gap-2">
                <Badge className="bg-white/5 text-[#7e7e8a] text-xs">{DEPARTMENTS[s.department] || s.department}</Badge>
                {s.phone && <span className="text-xs text-[#7e7e8a]">{s.phone}</span>}
              </div>
            </div>
          ))}
          {staff.length === 0 && <div className="col-span-3 text-center py-12 text-[#7e7e8a]"><Users className="w-12 h-12 mx-auto mb-3 opacity-30" /><p>Henuz personel yok</p></div>}
        </div>
      )}

      {/* Shifts List */}
      {tab === 'shifts' && (
        <div className="space-y-3">
          {shifts.map(sh => (
            <div key={sh.id} className="glass rounded-xl p-4 flex items-center gap-4 hover:gold-glow transition-all" data-testid={`shift-${sh.id}`}>
              <div className="w-10 h-10 rounded-lg bg-[#C4972A]/10 flex items-center justify-center">
                <Clock className="w-5 h-5 text-[#C4972A]" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{sh.staff_name}</span>
                  <Badge className="bg-white/5 text-[#7e7e8a] text-xs">{DEPARTMENTS[sh.department] || sh.department}</Badge>
                </div>
                <div className="text-xs text-[#7e7e8a] mt-1">
                  {sh.date} | {sh.start_time} - {sh.end_time}
                  {sh.notes && ` | ${sh.notes}`}
                </div>
              </div>
              <button onClick={() => { deleteShift(sh.id).then(loadShifts); }} className="text-[#7e7e8a] hover:text-red-400">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
          {shifts.length === 0 && <div className="text-center py-12 text-[#7e7e8a]"><Clock className="w-12 h-12 mx-auto mb-3 opacity-30" /><p>Henuz vardiya yok</p></div>}
        </div>
      )}
    </div>
  );
}
