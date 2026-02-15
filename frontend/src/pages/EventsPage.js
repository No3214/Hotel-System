import React, { useState, useEffect } from 'react';
import { getEvents, createEvent, deleteEvent } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Calendar, Plus, Trash2, Users, Clock } from 'lucide-react';

export default function EventsPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', event_type: 'general', event_date: '', start_time: '', capacity: '', price_per_person: '' });

  const load = () => {
    getEvents().then(r => setEvents(r.data.events)).catch(console.error).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    if (!form.title || !form.event_date) return;
    await createEvent({
      ...form,
      capacity: form.capacity ? parseInt(form.capacity) : null,
      price_per_person: form.price_per_person ? parseFloat(form.price_per_person) : null,
    });
    setForm({ title: '', description: '', event_type: 'general', event_date: '', start_time: '', capacity: '', price_per_person: '' });
    setOpen(false);
    load();
  };

  const EVENT_TYPES = {
    special_dinner: 'Ozel Aksam Yemegi',
    live_music: 'Canli Muzik',
    workshop: 'Atolye',
    wedding: 'Dugun',
    corporate: 'Kurumsal',
    cultural: 'Kulturel',
    promotion: 'Promosyon',
    general: 'Genel',
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="events-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Etkinlikler</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">{events.length} etkinlik</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-event-btn">
              <Plus className="w-4 h-4 mr-2" /> Etkinlik Ekle
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
            <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Etkinlik</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <Input placeholder="Etkinlik adi *" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })}
                className="bg-white/5 border-white/10" data-testid="event-title-input" />
              <Input placeholder="Aciklama" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Input type="date" value={form.event_date} onChange={e => setForm({ ...form, event_date: e.target.value })}
                className="bg-white/5 border-white/10" data-testid="event-date-input" />
              <Input type="time" value={form.start_time} onChange={e => setForm({ ...form, start_time: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Input type="number" placeholder="Kapasite" value={form.capacity} onChange={e => setForm({ ...form, capacity: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Input type="number" placeholder="Kisi basi fiyat (TL)" value={form.price_per_person} onChange={e => setForm({ ...form, price_per_person: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Button onClick={handleCreate} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-event-btn">Kaydet</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {events.map(event => (
          <div key={event.id} className="glass rounded-xl p-5 hover:gold-glow transition-all" data-testid={`event-${event.id}`}>
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-[#C4972A]">{event.title}</h3>
                {event.description && <p className="text-sm text-[#a9a9b2] mt-1">{event.description}</p>}
              </div>
              <button onClick={() => { deleteEvent(event.id).then(load); }} className="text-[#7e7e8a] hover:text-red-400">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center gap-3 mt-3 text-xs text-[#7e7e8a]">
              <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />{event.event_date}</span>
              {event.start_time && <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{event.start_time}</span>}
              {event.capacity && <span className="flex items-center gap-1"><Users className="w-3 h-3" />{event.capacity} kisi</span>}
            </div>
            <div className="flex items-center gap-2 mt-3">
              <Badge className="bg-[#C4972A]/20 text-[#C4972A] text-xs">{EVENT_TYPES[event.event_type] || event.event_type}</Badge>
              {event.price_per_person && <span className="text-sm font-medium text-[#C4972A]">{event.price_per_person} TL/kisi</span>}
              {event.is_active && <Badge className="bg-green-500/20 text-green-400 text-xs">Aktif</Badge>}
            </div>
          </div>
        ))}
        {events.length === 0 && !loading && (
          <div className="col-span-2 text-center py-12 text-[#7e7e8a]">
            <Calendar className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Henuz etkinlik yok</p>
          </div>
        )}
      </div>
    </div>
  );
}
