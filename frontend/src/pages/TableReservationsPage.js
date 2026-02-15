import React, { useState, useEffect, useCallback } from 'react';
import { getTableReservations, createTableReservation, updateTableReservationStatus, deleteTableReservation, getTableAvailability } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { UtensilsCrossed, Plus, Trash2, Check, Clock, Users, Calendar } from 'lucide-react';

const STATUS_CONFIG = {
  pending: { label: 'Bekliyor', color: 'bg-yellow-500/20 text-yellow-400' },
  confirmed: { label: 'Onaylandi', color: 'bg-blue-500/20 text-blue-400' },
  seated: { label: 'Oturdu', color: 'bg-green-500/20 text-green-400' },
  completed: { label: 'Tamamlandi', color: 'bg-gray-500/20 text-gray-400' },
  cancelled: { label: 'Iptal', color: 'bg-red-500/20 text-red-400' },
  no_show: { label: 'Gelmedi', color: 'bg-red-700/20 text-red-500' },
};

const FLOW = { pending: 'confirmed', confirmed: 'seated', seated: 'completed' };
const OCCASIONS = ['', 'birthday', 'anniversary', 'business', 'date_night', 'celebration', 'other'];
const OCCASION_LABELS = { birthday: 'Dogum Gunu', anniversary: 'Yildonumu', business: 'Is Yemegi', date_night: 'Romantik', celebration: 'Kutlama', other: 'Diger' };

export default function TableReservationsPage() {
  const [reservations, setReservations] = useState([]);
  const [availability, setAvailability] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ guest_name: '', phone: '', date: '', time: '19:00', party_size: 2, notes: '', occasion: '', is_hotel_guest: false });

  const load = useCallback(() => {
    const params = filter !== 'all' ? { status: filter } : {};
    if (selectedDate) params.date = selectedDate;
    getTableReservations(params).then(r => setReservations(r.data.reservations)).catch(console.error).finally(() => setLoading(false));
  }, [filter, selectedDate]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    if (selectedDate) getTableAvailability(selectedDate).then(r => setAvailability(r.data)).catch(() => {});
  }, [selectedDate]);

  const handleCreate = async () => {
    if (!form.guest_name || !form.phone || !form.date || !form.time) return;
    await createTableReservation({ ...form, party_size: parseInt(form.party_size) || 2 });
    setForm({ guest_name: '', phone: '', date: '', time: '19:00', party_size: 2, notes: '', occasion: '', is_hotel_guest: false });
    setOpen(false);
    load();
    if (selectedDate) getTableAvailability(selectedDate).then(r => setAvailability(r.data)).catch(() => {});
  };

  const handleStatus = async (id, status) => {
    await updateTableReservationStatus(id, status);
    load();
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="table-reservations-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]" data-testid="table-title">Masa Rezervasyonlari</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">Antakya Sofrasi - Restoran Yonetimi</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-table-res-btn">
              <Plus className="w-4 h-4 mr-2" /> Masa Ayirt
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
            <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Masa Rezervasyonu</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <Input placeholder="Misafir Adi *" value={form.guest_name} onChange={e => setForm({ ...form, guest_name: e.target.value })}
                className="bg-white/5 border-white/10 text-white" data-testid="table-guest-name" />
              <Input placeholder="Telefon *" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })}
                className="bg-white/5 border-white/10 text-white" data-testid="table-phone" />
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-[#7e7e8a] block mb-1">Tarih *</label>
                  <Input type="date" value={form.date} onChange={e => setForm({ ...form, date: e.target.value })}
                    className="bg-white/5 border-white/10" data-testid="table-date" />
                </div>
                <div>
                  <label className="text-xs text-[#7e7e8a] block mb-1">Saat *</label>
                  <select value={form.time} onChange={e => setForm({ ...form, time: e.target.value })}
                    className="w-full h-9 bg-[#0f0f14] border border-white/10 rounded-md text-sm text-white px-3" data-testid="table-time">
                    {['12:00','12:30','13:00','13:30','19:00','19:30','20:00','20:30','21:00'].map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-[#7e7e8a] block mb-1">Kisi Sayisi</label>
                  <Input type="number" min="1" max="20" value={form.party_size} onChange={e => setForm({ ...form, party_size: e.target.value })}
                    className="bg-white/5 border-white/10" data-testid="table-size" />
                </div>
                <div>
                  <label className="text-xs text-[#7e7e8a] block mb-1">Ozel Gun</label>
                  <select value={form.occasion} onChange={e => setForm({ ...form, occasion: e.target.value })}
                    className="w-full h-9 bg-[#0f0f14] border border-white/10 rounded-md text-sm text-white px-3">
                    <option value="">Yok</option>
                    {OCCASIONS.filter(o => o).map(o => <option key={o} value={o}>{OCCASION_LABELS[o]}</option>)}
                  </select>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" checked={form.is_hotel_guest} onChange={e => setForm({ ...form, is_hotel_guest: e.target.checked })}
                  className="rounded" data-testid="table-hotel-guest" />
                <label className="text-sm text-[#a9a9b2]">Otel misafiri</label>
              </div>
              <Input placeholder="Notlar" value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })}
                className="bg-white/5 border-white/10 text-white" />
              <Button onClick={handleCreate} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-table-res-btn">Kaydet</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Availability */}
      <div className="glass rounded-xl p-5">
        <div className="flex items-center gap-3 mb-3">
          <h3 className="text-sm font-semibold text-[#C4972A]">Musaitlik</h3>
          <Input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)}
            className="w-40 h-8 bg-white/5 border-white/10 text-sm" data-testid="avail-date" />
        </div>
        {availability && (
          <div className="flex gap-2 flex-wrap" data-testid="availability-slots">
            {availability.slots.map(slot => (
              <div key={slot.time} className={`px-3 py-2 rounded-lg text-center text-xs ${slot.is_available ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
                <p className="font-medium text-white">{slot.time}</p>
                <p className={slot.is_available ? 'text-green-400' : 'text-red-400'}>{slot.available}/{slot.total}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        {['all', 'pending', 'confirmed', 'seated', 'completed', 'cancelled'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-full text-xs transition-all ${filter === f ? 'bg-[#C4972A]/20 text-[#C4972A]' : 'bg-white/5 text-[#7e7e8a] hover:bg-white/10'}`}
            data-testid={`table-filter-${f}`}>
            {f === 'all' ? 'Tumu' : STATUS_CONFIG[f]?.label || f}
          </button>
        ))}
      </div>

      {/* List */}
      <div className="space-y-3">
        {reservations.map(res => {
          const cfg = STATUS_CONFIG[res.status] || STATUS_CONFIG.pending;
          const next = FLOW[res.status];
          return (
            <div key={res.id} className="glass rounded-xl p-4 hover:gold-glow transition-all" data-testid={`table-res-${res.id}`}>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-[#C4972A]/10 flex items-center justify-center">
                  <UtensilsCrossed className="w-5 h-5 text-[#C4972A]" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium text-white">{res.guest_name}</span>
                    <Badge className={cfg.color + ' text-xs'}>{cfg.label}</Badge>
                    {res.is_hotel_guest && <Badge className="bg-[#C4972A]/10 text-[#C4972A] text-[10px]">Otel Misafiri</Badge>}
                    {res.occasion && <Badge className="bg-purple-500/10 text-purple-400 text-[10px]">{OCCASION_LABELS[res.occasion] || res.occasion}</Badge>}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-[#7e7e8a] mt-1">
                    <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {res.date}</span>
                    <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {res.time}</span>
                    <span className="flex items-center gap-1"><Users className="w-3 h-3" /> {res.party_size} kisi</span>
                    <span>{res.phone}</span>
                    {res.table_number && <span className="text-[#C4972A]">Masa #{res.table_number}</span>}
                  </div>
                  {res.notes && <p className="text-xs text-[#a9a9b2] mt-1">{res.notes}</p>}
                </div>
                <div className="flex gap-1.5">
                  {next && (
                    <Button size="sm" variant="outline" onClick={() => handleStatus(res.id, next)}
                      className="text-xs border-[#C4972A]/30 text-[#C4972A] hover:bg-[#C4972A]/10">
                      <Check className="w-3 h-3 mr-1" />{STATUS_CONFIG[next]?.label}
                    </Button>
                  )}
                  {res.status === 'pending' && (
                    <Button size="sm" variant="outline" onClick={() => handleStatus(res.id, 'cancelled')}
                      className="text-xs border-red-500/30 text-red-400 hover:bg-red-500/10">Iptal</Button>
                  )}
                  <button onClick={() => { deleteTableReservation(res.id).then(load); }} className="text-[#7e7e8a] hover:text-red-400">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
        {reservations.length === 0 && !loading && (
          <div className="text-center py-12 text-[#7e7e8a]">
            <UtensilsCrossed className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Bu tarihte masa rezervasyonu yok</p>
          </div>
        )}
      </div>
    </div>
  );
}
