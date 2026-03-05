import React, { useState, useEffect } from 'react';
import { getReservations, createReservation, updateReservation, deleteReservation, getGuests, getRooms } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Calendar, Plus, Trash2, User, ArrowRight, Check } from 'lucide-react';
import { reservationSchema, validateForm } from '../lib/validations';

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
  const [errors, setErrors] = useState({});

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
    const { success, errors: validationErrors, data } = validateForm(reservationSchema, form);
    if (!success) {
      setErrors(validationErrors);
      return;
    }
    setErrors({});
    try {
      await createReservation({
        ...data,
        guests_count: parseInt(data.guests_count) || 1,
        total_price: data.total_price ? parseFloat(data.total_price) : null,
      });
      setForm({ guest_id: '', room_type: '', check_in: '', check_out: '', guests_count: 1, notes: '', total_price: '' });
      setOpen(false);
      load();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Rezervasyon olusturulamadi';
      alert(msg);
    }
  };

  const handleStatusChange = async (id, newStatus) => {
    try {
      await updateReservation(id, { status: newStatus });
      load();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Durum guncellenemedi';
      alert(msg);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteReservation(id);
      load();
    } catch (err) {
      alert('Rezervasyon silinemedi');
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
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-reservation-btn">
              <Plus className="w-4 h-4 mr-2" /> Yeni Rezervasyon
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
            <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Rezervasyon</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <div>
                <Select value={form.guest_id} onValueChange={v => setForm({ ...form, guest_id: v })}>
                  <SelectTrigger className={`bg-white/5 ${errors.guest_id ? 'border-red-500' : 'border-white/10'}`}><SelectValue placeholder="Misafir secin *" /></SelectTrigger>
                  <SelectContent className="bg-[#1a1a22] border-[#C4972A]/20 max-h-48">
                    {guests.map(g => <SelectItem key={g.id} value={g.id}>{g.name}</SelectItem>)}
                  </SelectContent>
                </Select>
                {errors.guest_id && <p className="text-red-400 text-xs mt-1">{errors.guest_id}</p>}
              </div>
              <div>
                <Select value={form.room_type} onValueChange={v => setForm({ ...form, room_type: v })}>
                  <SelectTrigger className={`bg-white/5 ${errors.room_type ? 'border-red-500' : 'border-white/10'}`}><SelectValue placeholder="Oda tipi *" /></SelectTrigger>
                  <SelectContent className="bg-[#1a1a22] border-[#C4972A]/20">
                    {rooms.map(r => <SelectItem key={r.room_id} value={r.room_id}>{r.name_tr} - {r.base_price_try} TL</SelectItem>)}
                  </SelectContent>
                </Select>
                {errors.room_type && <p className="text-red-400 text-xs mt-1">{errors.room_type}</p>}
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-[#7e7e8a] mb-1 block">Giris *</label>
                  <Input type="date" value={form.check_in} onChange={e => setForm({ ...form, check_in: e.target.value })} className={`bg-white/5 ${errors.check_in ? 'border-red-500' : 'border-white/10'}`} data-testid="res-checkin" />
                  {errors.check_in && <p className="text-red-400 text-xs mt-1">{errors.check_in}</p>}
                </div>
                <div>
                  <label className="text-xs text-[#7e7e8a] mb-1 block">Cikis *</label>
                  <Input type="date" value={form.check_out} onChange={e => setForm({ ...form, check_out: e.target.value })} className={`bg-white/5 ${errors.check_out ? 'border-red-500' : 'border-white/10'}`} data-testid="res-checkout" />
                  {errors.check_out && <p className="text-red-400 text-xs mt-1">{errors.check_out}</p>}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <Input type="number" min="1" placeholder="Kisi sayisi" value={form.guests_count} onChange={e => setForm({ ...form, guests_count: e.target.value })} className={`bg-white/5 ${errors.guests_count ? 'border-red-500' : 'border-white/10'}`} />
                  {errors.guests_count && <p className="text-red-400 text-xs mt-1">{errors.guests_count}</p>}
                </div>
                <Input type="number" placeholder="Toplam fiyat (TL)" value={form.total_price} onChange={e => setForm({ ...form, total_price: e.target.value })} className="bg-white/5 border-white/10" />
              </div>
              <Input placeholder="Notlar" value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} className="bg-white/5 border-white/10" />
              <Button onClick={handleCreate} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-reservation-btn">Kaydet</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

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
                    <span className="font-medium">{guestMap[res.guest_id] || 'Misafir'}</span>
                    <Badge className={cfg.color + ' text-xs'}>{cfg.label}</Badge>
                    <span className="text-xs text-[#C4972A]">{res.room_type}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-[#7e7e8a] mt-1">
                    <span>{res.check_in}</span>
                    <ArrowRight className="w-3 h-3" />
                    <span>{res.check_out}</span>
                    {res.guests_count && <span>| {res.guests_count} kisi</span>}
                    {res.total_price && <span className="text-[#C4972A]">| {res.total_price} TL</span>}
                  </div>
                  {res.notes && <p className="text-xs text-[#a9a9b2] mt-1">{res.notes}</p>}
                </div>
                <div className="flex gap-1.5">
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
                  <button onClick={() => handleDelete(res.id)} className="text-[#7e7e8a] hover:text-red-400">
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
