import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getTableReservations, createTableReservation, updateTableReservationStatus, deleteTableReservation, getTableAvailability } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import {
  UtensilsCrossed, Plus, Trash2, Check, Clock, Users, Calendar,
  Coffee, Sun, Moon, MapPin, RefreshCw, Flame, Music, Eye, Wine, ChevronRight
} from 'lucide-react';
import api from '../api';

const STATUS_CONFIG = {
  pending: { label: 'Bekliyor', color: 'bg-yellow-500/20 text-yellow-400' },
  confirmed: { label: 'Onaylandi', color: 'bg-blue-500/20 text-blue-400' },
  seated: { label: 'Oturdu', color: 'bg-green-500/20 text-green-400' },
  completed: { label: 'Tamamlandi', color: 'bg-gray-500/20 text-gray-400' },
  cancelled: { label: 'Iptal', color: 'bg-red-500/20 text-red-400' },
  no_show: { label: 'Gelmedi', color: 'bg-red-700/20 text-red-500' },
};

const MEAL_CONFIG = {
  breakfast: { label: 'Kahvalti', icon: Coffee, duration: '2 saat', color: 'bg-orange-500/20 text-orange-400' },
  lunch: { label: 'Oglen', icon: Sun, duration: '2 saat', color: 'bg-yellow-500/20 text-yellow-400' },
  dinner: { label: 'Aksam', icon: Moon, duration: '4 saat', color: 'bg-indigo-500/20 text-indigo-400' },
};

const ZONE_ICONS = { somine: Flame, sahne: Music, manzara: Eye, ara: UtensilsCrossed, bar: Wine };
const ZONE_COLORS = {
  somine: 'border-orange-500/40 bg-orange-500/5',
  sahne: 'border-purple-500/40 bg-purple-500/5',
  manzara: 'border-blue-500/40 bg-blue-500/5',
  ara: 'border-green-500/40 bg-green-500/5',
  bar: 'border-amber-500/40 bg-amber-500/5',
};
const TABLE_TYPE_STYLE = {
  rectangular: 'rounded-lg w-20 h-12',
  round: 'rounded-full w-16 h-16',
  small: 'rounded-md w-14 h-10',
  bar: 'rounded-sm w-16 h-10',
};

const FLOW = { pending: 'confirmed', confirmed: 'seated', seated: 'completed' };

function TableCard({ table, onClick }) {
  const occupied = table.is_occupied;
  const res = table.reservation;
  const isCurrent = res?.is_current;

  return (
    <button
      onClick={() => onClick(table)}
      className={`relative flex flex-col items-center justify-center transition-all hover:scale-105 border-2
        ${TABLE_TYPE_STYLE[table.type]}
        ${occupied
          ? isCurrent ? 'border-red-500 bg-red-500/20 text-red-300' : 'border-yellow-500 bg-yellow-500/15 text-yellow-300'
          : 'border-green-500/50 bg-green-500/10 text-green-400 hover:bg-green-500/20'
        }`}
      data-testid={`table-${table.id}`}
    >
      <span className="text-xs font-bold">{table.id}</span>
      <span className="text-[10px] opacity-70">{table.capacity}K</span>
      {occupied && (
        <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-red-500 animate-pulse" />
      )}
    </button>
  );
}

export default function TableReservationsPage() {
  const [reservations, setReservations] = useState([]);
  const [floorPlan, setFloorPlan] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('floor');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [open, setOpen] = useState(false);
  const [selectedTable, setSelectedTable] = useState(null);
  const [form, setForm] = useState({
    guest_name: '', phone: '', date: '', time: '', party_size: 2,
    meal_type: 'dinner', notes: '', occasion: '', is_hotel_guest: false, preferred_table_id: ''
  });

  const load = useCallback(async () => {
    try {
      const [resData, floorData] = await Promise.all([
        getTableReservations({ date: selectedDate }),
        api.get(`/table-reservations/floor-plan?date=${selectedDate}`),
      ]);
      setReservations(resData.data.reservations);
      setFloorPlan(floorData.data);
      if (resData.data.config) setConfig(resData.data.config);
    } catch (err) { console.error(err); }
    setLoading(false);
  }, [selectedDate]);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async () => {
    try {
      await createTableReservation({
        ...form,
        date: form.date || selectedDate,
        party_size: parseInt(form.party_size),
      });
      setOpen(false);
      setForm({ guest_name: '', phone: '', date: '', time: '', party_size: 2, meal_type: 'dinner', notes: '', occasion: '', is_hotel_guest: false, preferred_table_id: '' });
      load();
    } catch (err) { alert(err.response?.data?.detail || 'Hata'); }
  };

  const handleStatus = async (id, newStatus) => {
    try {
      await updateTableReservationStatus(id, newStatus);
      load();
    } catch (err) { console.error(err); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Rezervasyonu silmek istediginize emin misiniz?')) return;
    try { await deleteTableReservation(id); load(); } catch (err) { console.error(err); }
  };

  const handleTableClick = (table) => {
    setSelectedTable(table);
    if (!table.is_occupied) {
      setForm(p => ({ ...p, preferred_table_id: table.id, date: selectedDate }));
      setOpen(true);
    }
  };

  const stats = floorPlan ? {
    total: floorPlan.total_tables,
    occupied: floorPlan.occupied_tables,
    available: floorPlan.available_tables,
    capacity: floorPlan.total_capacity,
  } : { total: 0, occupied: 0, available: 0, capacity: 0 };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1600px]" data-testid="table-reservations-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A] flex items-center gap-3">
            <UtensilsCrossed className="w-8 h-8" />
            Masa Yonetimi
          </h1>
          <p className="text-[#7e7e8a] text-sm mt-1">Kozbeyli Konagi - Ic Mekan Yerlesim Plani</p>
        </div>
        <div className="flex items-center gap-3">
          <Input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)}
            className="bg-white/5 border-white/10 w-40" data-testid="date-picker" />
          <div className="flex gap-1 bg-white/5 rounded-lg p-1">
            {['floor', 'list'].map(v => (
              <button key={v} onClick={() => setView(v)}
                className={`px-3 py-1.5 rounded text-sm ${view === v ? 'bg-[#C4972A] text-white' : 'text-[#7e7e8a]'}`}
                data-testid={`view-${v}`}>
                {v === 'floor' ? 'Yerlesim' : 'Liste'}
              </button>
            ))}
          </div>
          <Button onClick={() => { setSelectedTable(null); setOpen(true); }}
            className="bg-[#C4972A] hover:bg-[#d4a73a] text-white" data-testid="new-reservation-btn">
            <Plus className="w-4 h-4 mr-2" /> Yeni Rez.
          </Button>
          <Button variant="outline" onClick={load} className="border-[#C4972A]/30 text-[#C4972A]" data-testid="refresh-btn">
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass rounded-xl p-4"><p className="text-2xl font-bold text-[#e5e5e8]">{stats.total}</p><p className="text-xs text-[#7e7e8a]">Toplam Masa</p></div>
        <div className="glass rounded-xl p-4"><p className="text-2xl font-bold text-green-400">{stats.available}</p><p className="text-xs text-[#7e7e8a]">Musait</p></div>
        <div className="glass rounded-xl p-4"><p className="text-2xl font-bold text-red-400">{stats.occupied}</p><p className="text-xs text-[#7e7e8a]">Dolu</p></div>
        <div className="glass rounded-xl p-4"><p className="text-2xl font-bold text-[#C4972A]">{stats.capacity}</p><p className="text-xs text-[#7e7e8a]">Toplam Kapasite</p></div>
      </div>

      {/* FLOOR PLAN VIEW */}
      {view === 'floor' && floorPlan && (
        <div className="space-y-4" data-testid="floor-plan">
          {/* Legend */}
          <div className="flex gap-4 text-xs text-[#7e7e8a]">
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-green-500/30 border border-green-500" /> Musait</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-yellow-500/30 border border-yellow-500" /> Rezerve</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-red-500/30 border border-red-500 animate-pulse" /> Su An Dolu</span>
          </div>

          {/* Zones */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Şömine - Sol */}
            {floorPlan.zones.filter(z => z.id === 'somine').map(zone => {
              const ZIcon = ZONE_ICONS[zone.id];
              return (
                <div key={zone.id} className={`border rounded-xl p-4 ${ZONE_COLORS[zone.id]}`} data-testid={`zone-${zone.id}`}>
                  <div className="flex items-center gap-2 mb-3">
                    <ZIcon className="w-5 h-5 text-orange-400" />
                    <h3 className="font-semibold text-[#e5e5e8]">{zone.name}</h3>
                    <Badge className="ml-auto bg-white/10 text-[#a9a9b2]">{zone.occupied_count}/{zone.total_count}</Badge>
                  </div>
                  <div className="flex flex-wrap gap-3 justify-center">
                    {zone.tables.map(t => <TableCard key={t.id} table={t} onClick={handleTableClick} />)}
                  </div>
                </div>
              );
            })}

            {/* Sahne - Orta */}
            {floorPlan.zones.filter(z => z.id === 'sahne').map(zone => {
              const ZIcon = ZONE_ICONS[zone.id];
              return (
                <div key={zone.id} className={`border rounded-xl p-4 ${ZONE_COLORS[zone.id]}`} data-testid={`zone-${zone.id}`}>
                  <div className="flex items-center gap-2 mb-3">
                    <ZIcon className="w-5 h-5 text-purple-400" />
                    <h3 className="font-semibold text-[#e5e5e8]">{zone.name}</h3>
                    <Badge className="ml-auto bg-white/10 text-[#a9a9b2]">{zone.occupied_count}/{zone.total_count}</Badge>
                  </div>
                  <div className="bg-purple-500/10 rounded-lg p-2 mb-3 text-center text-xs text-purple-300 font-medium">SAHNE</div>
                  <div className="flex flex-wrap gap-3 justify-center">
                    {zone.tables.map(t => <TableCard key={t.id} table={t} onClick={handleTableClick} />)}
                  </div>
                </div>
              );
            })}

            {/* Manzara - Sağ */}
            {floorPlan.zones.filter(z => z.id === 'manzara').map(zone => {
              const ZIcon = ZONE_ICONS[zone.id];
              return (
                <div key={zone.id} className={`border rounded-xl p-4 ${ZONE_COLORS[zone.id]}`} data-testid={`zone-${zone.id}`}>
                  <div className="flex items-center gap-2 mb-3">
                    <ZIcon className="w-5 h-5 text-blue-400" />
                    <h3 className="font-semibold text-[#e5e5e8]">{zone.name}</h3>
                    <Badge className="ml-auto bg-white/10 text-[#a9a9b2]">{zone.occupied_count}/{zone.total_count}</Badge>
                  </div>
                  <div className="flex flex-wrap gap-3 justify-center">
                    {zone.tables.map(t => <TableCard key={t.id} table={t} onClick={handleTableClick} />)}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Ara + Bar */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {floorPlan.zones.filter(z => ['ara', 'bar'].includes(z.id)).map(zone => {
              const ZIcon = ZONE_ICONS[zone.id];
              return (
                <div key={zone.id} className={`border rounded-xl p-4 ${ZONE_COLORS[zone.id]}`} data-testid={`zone-${zone.id}`}>
                  <div className="flex items-center gap-2 mb-3">
                    <ZIcon className="w-5 h-5" />
                    <h3 className="font-semibold text-[#e5e5e8]">{zone.name}</h3>
                    <Badge className="ml-auto bg-white/10 text-[#a9a9b2]">{zone.occupied_count}/{zone.total_count}</Badge>
                  </div>
                  <div className="flex flex-wrap gap-3 justify-center">
                    {zone.tables.map(t => <TableCard key={t.id} table={t} onClick={handleTableClick} />)}
                  </div>
                </div>
              );
            })}
          </div>

          {/* KAPI indicator */}
          <div className="flex justify-center">
            <div className="bg-white/5 border border-white/10 rounded-lg px-6 py-2 text-xs text-[#7e7e8a] flex items-center gap-2">
              <MapPin className="w-3 h-3" /> KAPI (Ana Giris)
            </div>
          </div>
        </div>
      )}

      {/* LIST VIEW */}
      {view === 'list' && (
        <div className="space-y-3" data-testid="list-view">
          {reservations.length === 0 ? (
            <div className="text-center py-12 text-[#7e7e8a]">
              <Calendar className="w-16 h-16 mx-auto mb-3 opacity-30" />
              <p>Bu tarihte rezervasyon yok</p>
            </div>
          ) : reservations.map(res => {
            const meal = MEAL_CONFIG[res.meal_type] || {};
            const status = STATUS_CONFIG[res.status] || {};
            const MealIcon = meal.icon || Clock;
            const nextStatus = FLOW[res.status];
            return (
              <motion.div key={res.id} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }}
                className="glass rounded-xl p-4" data-testid={`reservation-${res.id}`}>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div className="flex items-center gap-4">
                    <div className="p-2 rounded-lg bg-[#C4972A]/20">
                      <MealIcon className="w-5 h-5 text-[#C4972A]" />
                    </div>
                    <div>
                      <p className="font-semibold text-[#e5e5e8]">{res.guest_name}</p>
                      <p className="text-sm text-[#7e7e8a]">{res.phone}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge className={meal.color}>{meal.label}</Badge>
                    <Badge className="bg-white/10 text-[#a9a9b2]"><Clock className="w-3 h-3 mr-1" />{res.time}-{res.end_time}</Badge>
                    <Badge className="bg-white/10 text-[#a9a9b2]"><Users className="w-3 h-3 mr-1" />{res.party_size}K</Badge>
                    <Badge className="bg-[#C4972A]/20 text-[#C4972A]">{res.table_name || res.table_id}</Badge>
                    <Badge className={status.color}>{status.label}</Badge>
                  </div>
                  <div className="flex gap-2">
                    {nextStatus && (
                      <Button size="sm" onClick={() => handleStatus(res.id, nextStatus)}
                        className="bg-green-500/20 text-green-400 hover:bg-green-500/30">
                        <Check className="w-3 h-3 mr-1" />
                        {STATUS_CONFIG[nextStatus]?.label}
                      </Button>
                    )}
                    {['pending', 'confirmed'].includes(res.status) && (
                      <Button size="sm" variant="ghost" onClick={() => handleStatus(res.id, 'cancelled')} className="text-red-400 hover:bg-red-500/10">
                        Iptal
                      </Button>
                    )}
                    <Button size="sm" variant="ghost" onClick={() => handleDelete(res.id)} className="text-red-400 hover:bg-red-500/10">
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
                {res.notes && <p className="text-sm text-[#7e7e8a] mt-2 pl-14">Not: {res.notes}</p>}
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Selected Table Info Popup */}
      {selectedTable?.is_occupied && (
        <Dialog open={!!selectedTable?.is_occupied} onOpenChange={() => setSelectedTable(null)}>
          <DialogContent className="bg-[#1a1a2e] border-white/10 text-white">
            <DialogHeader>
              <DialogTitle className="text-[#C4972A]">{selectedTable.name} - Detay</DialogTitle>
            </DialogHeader>
            <div className="space-y-3">
              <p><strong>Misafir:</strong> {selectedTable.reservation?.guest_name}</p>
              <p><strong>Kisi:</strong> {selectedTable.reservation?.party_size}</p>
              <p><strong>Saat:</strong> {selectedTable.reservation?.time} - {selectedTable.reservation?.end_time}</p>
              <p><strong>Durum:</strong> {STATUS_CONFIG[selectedTable.reservation?.status]?.label}</p>
              <p><strong>Bolge:</strong> {selectedTable.zone_label}</p>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* New Reservation Dialog */}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="bg-[#1a1a2e] border-white/10 text-white max-w-md">
          <DialogHeader>
            <DialogTitle className="text-[#C4972A]">
              {form.preferred_table_id ? `${form.preferred_table_id} icin Rezervasyon` : 'Yeni Masa Rezervasyonu'}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <Input placeholder="Misafir adi" value={form.guest_name}
              onChange={e => setForm(p => ({ ...p, guest_name: e.target.value }))}
              className="bg-white/5 border-white/10" data-testid="form-guest-name" />
            <Input placeholder="Telefon" value={form.phone}
              onChange={e => setForm(p => ({ ...p, phone: e.target.value }))}
              className="bg-white/5 border-white/10" data-testid="form-phone" />
            <div className="grid grid-cols-2 gap-3">
              <Input type="date" value={form.date || selectedDate}
                onChange={e => setForm(p => ({ ...p, date: e.target.value }))}
                className="bg-white/5 border-white/10" data-testid="form-date" />
              <select value={form.meal_type} onChange={e => setForm(p => ({ ...p, meal_type: e.target.value }))}
                className="bg-white/5 border border-white/10 rounded-md px-3 text-sm" data-testid="form-meal-type">
                <option value="breakfast">Kahvalti</option>
                <option value="lunch">Oglen</option>
                <option value="dinner">Aksam</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <select value={form.time} onChange={e => setForm(p => ({ ...p, time: e.target.value }))}
                className="bg-white/5 border border-white/10 rounded-md px-3 text-sm" data-testid="form-time">
                <option value="">Saat secin</option>
                {(form.meal_type === 'breakfast' ? ['08:00','08:30','09:00','09:30','10:00','10:30'] :
                  form.meal_type === 'lunch' ? ['12:00','12:30','13:00','13:30','14:00'] :
                  ['18:00','18:30','19:00','19:30','20:00','20:30']).map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
              <Input type="number" min="1" max="24" value={form.party_size}
                onChange={e => setForm(p => ({ ...p, party_size: e.target.value }))}
                className="bg-white/5 border-white/10" placeholder="Kisi sayisi" data-testid="form-party-size" />
            </div>
            <Input placeholder="Notlar (opsiyonel)" value={form.notes}
              onChange={e => setForm(p => ({ ...p, notes: e.target.value }))}
              className="bg-white/5 border-white/10" data-testid="form-notes" />
            <Button onClick={handleCreate}
              disabled={!form.guest_name || !form.phone || !form.time}
              className="w-full bg-[#C4972A] hover:bg-[#d4a73a] text-white" data-testid="submit-reservation-btn">
              <Plus className="w-4 h-4 mr-2" /> Rezervasyon Olustur
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
