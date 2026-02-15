import React, { useState, useEffect, useCallback } from 'react';
import { getTableReservations, createTableReservation, updateTableReservationStatus, deleteTableReservation, getTableAvailability } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { UtensilsCrossed, Plus, Trash2, Check, Clock, Users, Calendar, Coffee, Sun, Moon, MapPin, RefreshCw } from 'lucide-react';
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

const FLOW = { pending: 'confirmed', confirmed: 'seated', seated: 'completed' };
const OCCASIONS = ['', 'birthday', 'anniversary', 'business', 'date_night', 'celebration', 'other'];
const OCCASION_LABELS = { birthday: 'Dogum Gunu', anniversary: 'Yildonumu', business: 'Is Yemegi', date_night: 'Romantik', celebration: 'Kutlama', other: 'Diger' };

export default function TableReservationsPage() {
  const [reservations, setReservations] = useState([]);
  const [availability, setAvailability] = useState(null);
  const [dailyView, setDailyView] = useState(null);
  const [tables, setTables] = useState([]);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [view, setView] = useState('list'); // list, daily
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    guest_name: '', phone: '', date: '', time: '', party_size: 2,
    meal_type: 'dinner', notes: '', occasion: '', is_hotel_guest: false,
    preferred_table_id: ''
  });
  const [availableTables, setAvailableTables] = useState([]);

  const load = useCallback(async () => {
    try {
      const params = filter !== 'all' ? { status: filter } : {};
      if (selectedDate) params.date = selectedDate;
      const res = await getTableReservations(params);
      setReservations(res.data.reservations);
      if (res.data.config) {
        setConfig(res.data.config);
        setTables(res.data.config.tables || []);
      }
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  }, [filter, selectedDate]);

  const loadAvailability = useCallback(async () => {
    if (!selectedDate) return;
    try {
      const res = await getTableAvailability(selectedDate);
      setAvailability(res.data);
    } catch (err) {
      console.error(err);
    }
  }, [selectedDate]);

  const loadDailyView = useCallback(async () => {
    if (!selectedDate) return;
    try {
      const res = await api.get(`/table-reservations/daily-view?date=${selectedDate}`);
      setDailyView(res.data);
    } catch (err) {
      console.error(err);
    }
  }, [selectedDate]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => { loadAvailability(); }, [loadAvailability]);
  useEffect(() => { if (view === 'daily') loadDailyView(); }, [view, loadDailyView]);

  // Update available times when meal type changes
  const getMealTimes = (mealType) => {
    if (!config?.meal_time_slots) return [];
    return config.meal_time_slots[mealType] || [];
  };

  // Check availability when form changes
  useEffect(() => {
    if (form.date && form.time && form.meal_type && form.party_size) {
      api.get(`/table-reservations/availability?date=${form.date}&meal_type=${form.meal_type}&party_size=${form.party_size}`)
        .then(res => {
          const slots = res.data.availability?.[form.meal_type] || [];
          const slot = slots.find(s => s.time === form.time);
          if (slot) {
            const availTables = tables.filter(t => slot.available_table_ids?.includes(t.id));
            setAvailableTables(availTables);
          }
        })
        .catch(() => setAvailableTables([]));
    }
  }, [form.date, form.time, form.meal_type, form.party_size, tables]);

  const handleCreate = async () => {
    if (!form.guest_name || !form.phone || !form.date || !form.time || !form.meal_type) return;
    try {
      await createTableReservation({ ...form, party_size: parseInt(form.party_size) || 2 });
      setForm({
        guest_name: '', phone: '', date: '', time: '', party_size: 2,
        meal_type: 'dinner', notes: '', occasion: '', is_hotel_guest: false,
        preferred_table_id: ''
      });
      setOpen(false);
      load();
      loadAvailability();
    } catch (err) {
      alert(err.response?.data?.detail || 'Hata olustu');
    }
  };

  const handleStatus = async (id, status, tableId = null) => {
    await updateTableReservationStatus(id, status, tableId);
    load();
    if (view === 'daily') loadDailyView();
  };

  const times = getMealTimes(form.meal_type);

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1600px]" data-testid="table-reservations-page">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]" data-testid="table-title">Masa Rezervasyonlari</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">
            Antakya Sofrasi - {config?.total_tables || 19} Masa ({config?.small_tables || 13} kucuk, {config?.medium_tables || 6} buyuk)
          </p>
        </div>
        <div className="flex gap-2">
          <div className="flex rounded-lg overflow-hidden border border-white/10">
            <button
              onClick={() => setView('list')}
              className={`px-3 py-1.5 text-xs ${view === 'list' ? 'bg-[#C4972A]/20 text-[#C4972A]' : 'text-[#7e7e8a]'}`}
            >
              Liste
            </button>
            <button
              onClick={() => setView('daily')}
              className={`px-3 py-1.5 text-xs ${view === 'daily' ? 'bg-[#C4972A]/20 text-[#C4972A]' : 'text-[#7e7e8a]'}`}
            >
              Gunluk Goruntule
            </button>
          </div>
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-table-res-btn">
                <Plus className="w-4 h-4 mr-2" /> Masa Ayirt
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20 max-w-lg">
              <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Masa Rezervasyonu</DialogTitle></DialogHeader>
              <div className="space-y-4">
                <Input placeholder="Misafir Adi *" value={form.guest_name} onChange={e => setForm({ ...form, guest_name: e.target.value })}
                  className="bg-white/5 border-white/10 text-white" data-testid="table-guest-name" />
                <Input placeholder="Telefon *" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })}
                  className="bg-white/5 border-white/10 text-white" data-testid="table-phone" />

                {/* Meal Type */}
                <div>
                  <label className="text-xs text-[#7e7e8a] block mb-2">Ogun *</label>
                  <div className="grid grid-cols-3 gap-2">
                    {Object.entries(MEAL_CONFIG).map(([key, cfg]) => {
                      const Icon = cfg.icon;
                      const isSelected = form.meal_type === key;
                      return (
                        <button
                          key={key}
                          onClick={() => setForm({ ...form, meal_type: key, time: '' })}
                          className={`p-3 rounded-lg border text-center transition-all ${isSelected ? 'border-[#C4972A] bg-[#C4972A]/10' : 'border-white/10 hover:border-white/20'}`}
                          data-testid={`meal-${key}`}
                        >
                          <Icon className={`w-5 h-5 mx-auto mb-1 ${isSelected ? 'text-[#C4972A]' : 'text-[#7e7e8a]'}`} />
                          <p className={`text-xs font-medium ${isSelected ? 'text-[#C4972A]' : 'text-white'}`}>{cfg.label}</p>
                          <p className="text-[10px] text-[#7e7e8a]">{cfg.duration}</p>
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-[#7e7e8a] block mb-1">Tarih *</label>
                    <Input type="date" value={form.date} onChange={e => setForm({ ...form, date: e.target.value })}
                      className="bg-white/5 border-white/10" data-testid="table-date" />
                  </div>
                  <div>
                    <label className="text-xs text-[#7e7e8a] block mb-1">Saat *</label>
                    <select value={form.time} onChange={e => setForm({ ...form, time: e.target.value })}
                      className="w-full h-9 bg-[#0f0f14] border border-white/10 rounded-md text-sm text-white px-3" data-testid="table-time">
                      <option value="">Saat secin</option>
                      {times.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-[#7e7e8a] block mb-1">Kisi Sayisi</label>
                    <Input type="number" min="1" max="12" value={form.party_size} onChange={e => setForm({ ...form, party_size: e.target.value })}
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

                {/* Available Tables */}
                {form.date && form.time && availableTables.length > 0 && (
                  <div>
                    <label className="text-xs text-[#7e7e8a] block mb-2">Musait Masalar ({availableTables.length})</label>
                    <div className="flex gap-2 flex-wrap">
                      {availableTables.map(table => (
                        <button
                          key={table.id}
                          onClick={() => setForm({ ...form, preferred_table_id: table.id })}
                          className={`px-3 py-2 rounded-lg text-xs border transition-all ${form.preferred_table_id === table.id ? 'border-[#C4972A] bg-[#C4972A]/10 text-[#C4972A]' : 'border-white/10 text-white hover:border-white/20'}`}
                        >
                          <span className="font-medium">{table.name}</span>
                          <span className="text-[#7e7e8a] ml-1">({table.capacity} kisi)</span>
                          <span className={`ml-1 text-[10px] ${table.location === 'indoor' ? 'text-blue-400' : 'text-green-400'}`}>
                            {table.location === 'indoor' ? 'Ic' : 'Dis'}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {form.date && form.time && availableTables.length === 0 && (
                  <p className="text-xs text-red-400 text-center py-2">Bu saat icin musait masa bulunmuyor</p>
                )}

                <div className="flex items-center gap-2">
                  <input type="checkbox" checked={form.is_hotel_guest} onChange={e => setForm({ ...form, is_hotel_guest: e.target.checked })}
                    className="rounded" data-testid="table-hotel-guest" />
                  <label className="text-sm text-[#a9a9b2]">Otel misafiri</label>
                </div>

                <Input placeholder="Notlar" value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })}
                  className="bg-white/5 border-white/10 text-white" />

                <Button onClick={handleCreate} disabled={!form.guest_name || !form.phone || !form.date || !form.time}
                  className="w-full bg-[#C4972A] hover:bg-[#a87a1f] disabled:opacity-50" data-testid="save-table-res-btn">
                  Kaydet
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Date Picker & Availability */}
      <div className="glass rounded-xl p-5">
        <div className="flex items-center gap-4 mb-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-[#C4972A]" />
            <Input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)}
              className="w-40 h-8 bg-white/5 border-white/10 text-sm" data-testid="avail-date" />
          </div>
          <button onClick={() => { load(); loadAvailability(); if (view === 'daily') loadDailyView(); }}
            className="text-[#7e7e8a] hover:text-[#C4972A]">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {/* Availability by meal type */}
        {availability?.availability && (
          <div className="space-y-4">
            {Object.entries(availability.availability).map(([mealType, slots]) => {
              const mealCfg = MEAL_CONFIG[mealType];
              if (!mealCfg) return null;
              const Icon = mealCfg.icon;
              return (
                <div key={mealType}>
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className="w-4 h-4 text-[#C4972A]" />
                    <span className="text-sm font-medium text-white">{mealCfg.label}</span>
                    <span className="text-xs text-[#7e7e8a]">({mealCfg.duration})</span>
                  </div>
                  <div className="flex gap-2 flex-wrap">
                    {slots.map(slot => (
                      <div key={slot.time}
                        className={`px-3 py-2 rounded-lg text-center text-xs ${slot.is_available ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
                        <p className="font-medium text-white">{slot.time}</p>
                        <p className={slot.is_available ? 'text-green-400' : 'text-red-400'}>
                          {slot.available_tables} masa
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Filters */}
      {view === 'list' && (
        <div className="flex gap-2 flex-wrap">
          {['all', 'pending', 'confirmed', 'seated', 'completed', 'cancelled'].map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-full text-xs transition-all ${filter === f ? 'bg-[#C4972A]/20 text-[#C4972A]' : 'bg-white/5 text-[#7e7e8a] hover:bg-white/10'}`}
              data-testid={`table-filter-${f}`}>
              {f === 'all' ? 'Tumu' : STATUS_CONFIG[f]?.label || f}
            </button>
          ))}
        </div>
      )}

      {/* Daily View */}
      {view === 'daily' && dailyView && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-[#C4972A]">
            {selectedDate} - {dailyView.total_reservations} Rezervasyon
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
            {dailyView.tables.map(({ table, reservations: tableRes }) => (
              <div key={table.id} className="glass rounded-xl p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <span className="font-medium text-white">{table.name}</span>
                    <span className="text-xs text-[#7e7e8a] ml-2">{table.capacity} kisi</span>
                  </div>
                  <span className={`text-[10px] px-2 py-0.5 rounded ${table.location === 'indoor' ? 'bg-blue-500/20 text-blue-400' : 'bg-green-500/20 text-green-400'}`}>
                    {table.location === 'indoor' ? 'Ic Mekan' : 'Dis Mekan'}
                  </span>
                </div>
                {tableRes.length === 0 ? (
                  <p className="text-xs text-[#5a5a65] text-center py-3">Rezervasyon yok</p>
                ) : (
                  <div className="space-y-2">
                    {tableRes.map(res => {
                      const mealCfg = MEAL_CONFIG[res.meal_type] || MEAL_CONFIG.dinner;
                      return (
                        <div key={res.id} className="bg-white/5 rounded-lg p-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-medium text-white">{res.guest_name}</span>
                            <Badge className={STATUS_CONFIG[res.status]?.color + ' text-[10px]'}>
                              {STATUS_CONFIG[res.status]?.label}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-2 mt-1 text-[10px] text-[#7e7e8a]">
                            <span>{res.time} - {res.end_time}</span>
                            <span>{res.party_size} kisi</span>
                            <Badge className={mealCfg.color + ' text-[10px]'}>{mealCfg.label}</Badge>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* List View */}
      {view === 'list' && (
        <div className="space-y-3">
          {reservations.map(res => {
            const cfg = STATUS_CONFIG[res.status] || STATUS_CONFIG.pending;
            const mealCfg = MEAL_CONFIG[res.meal_type] || MEAL_CONFIG.dinner;
            const MealIcon = mealCfg.icon;
            const next = FLOW[res.status];
            return (
              <div key={res.id} className="glass rounded-xl p-4 hover:gold-glow transition-all" data-testid={`table-res-${res.id}`}>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-lg bg-[#C4972A]/10 flex items-center justify-center">
                    <MealIcon className="w-5 h-5 text-[#C4972A]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-white">{res.guest_name}</span>
                      <Badge className={cfg.color + ' text-xs'}>{cfg.label}</Badge>
                      <Badge className={mealCfg.color + ' text-xs'}>{mealCfg.label}</Badge>
                      {res.is_hotel_guest && <Badge className="bg-[#C4972A]/10 text-[#C4972A] text-[10px]">Otel Misafiri</Badge>}
                      {res.occasion && <Badge className="bg-purple-500/10 text-purple-400 text-[10px]">{OCCASION_LABELS[res.occasion] || res.occasion}</Badge>}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-[#7e7e8a] mt-1 flex-wrap">
                      <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {res.date}</span>
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {res.time} - {res.end_time}</span>
                      <span className="flex items-center gap-1"><Users className="w-3 h-3" /> {res.party_size} kisi</span>
                      <span>{res.phone}</span>
                      {res.table_name && (
                        <span className="flex items-center gap-1 text-[#C4972A]">
                          <MapPin className="w-3 h-3" /> {res.table_name}
                        </span>
                      )}
                    </div>
                    {res.notes && <p className="text-xs text-[#a9a9b2] mt-1">{res.notes}</p>}
                  </div>
                  <div className="flex gap-1.5 flex-wrap">
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
      )}
    </div>
  );
}
