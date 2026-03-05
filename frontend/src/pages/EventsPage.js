import React, { useState, useEffect, useRef } from 'react';
import { getEvents, createEvent, updateEvent, deleteEvent, seedSampleEvents } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Calendar, Plus, Trash2, Users, Clock, Music, Heart, Utensils, Download, Image, X, Edit2, Eye } from 'lucide-react';

export default function EventsPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  const [viewEvent, setViewEvent] = useState(null);
  const [form, setForm] = useState({
    title: '', description: '', event_type: 'general', event_date: '',
    start_time: '', capacity: '', price_per_person: '', images: []
  });
  const fileInputRef1 = useRef(null);
  const fileInputRef2 = useRef(null);

  const load = () => {
    getEvents().then(r => setEvents(r.data.events)).catch(console.error).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const fileToBase64 = (file) => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });

  const handleImageSelect = async (e, index) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) return;
    if (file.size > 5 * 1024 * 1024) {
      alert('Dosya boyutu 5MB\'dan kucuk olmali');
      return;
    }
    const base64 = await fileToBase64(file);
    const newImages = [...(form.images || [])];
    newImages[index] = base64;
    setForm({ ...form, images: newImages });
  };

  const removeImage = (index) => {
    const newImages = [...(form.images || [])];
    newImages[index] = null;
    setForm({ ...form, images: newImages.filter(Boolean) });
  };

  const resetForm = () => {
    setForm({ title: '', description: '', event_type: 'general', event_date: '', start_time: '', capacity: '', price_per_person: '', images: [] });
    setEditingEvent(null);
  };

  const handleCreate = async () => {
    if (!form.title || !form.event_date) return;
    const payload = {
      ...form,
      capacity: form.capacity ? parseInt(form.capacity) : null,
      price_per_person: form.price_per_person ? parseFloat(form.price_per_person) : null,
      images: (form.images || []).filter(Boolean),
    };
    try {
      if (editingEvent) {
        await updateEvent(editingEvent.id, payload);
      } else {
        await createEvent(payload);
      }
      resetForm();
      setOpen(false);
      load();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Etkinlik kaydedilemedi';
      alert(msg);
    }
  };

  const handleEdit = (event) => {
    setEditingEvent(event);
    setForm({
      title: event.title || '',
      description: event.description || '',
      event_type: event.event_type || 'general',
      event_date: event.event_date || '',
      start_time: event.start_time || '',
      capacity: event.capacity || '',
      price_per_person: event.price_per_person || '',
      images: event.images || [],
    });
    setOpen(true);
  };

  const handleSeedEvents = async () => {
    setSeeding(true);
    try { await seedSampleEvents(); load(); } catch (err) { console.error(err); }
    setSeeding(false);
  };

  const EVENT_TYPES = {
    special_dinner: { label: 'Ozel Aksam Yemegi', icon: Heart, color: 'text-rose-400' },
    live_music: { label: 'Canli Muzik', icon: Music, color: 'text-purple-400' },
    workshop: { label: 'Atolye', icon: Utensils, color: 'text-blue-400' },
    wedding: { label: 'Dugun', icon: Heart, color: 'text-pink-400' },
    corporate: { label: 'Kurumsal', icon: Users, color: 'text-slate-400' },
    cultural: { label: 'Kulturel', icon: Calendar, color: 'text-indigo-400' },
    promotion: { label: 'Promosyon', icon: Download, color: 'text-orange-400' },
    general: { label: 'Genel', icon: Calendar, color: 'text-[#C4972A]' },
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const months = ['Ocak','Subat','Mart','Nisan','Mayis','Haziran','Temmuz','Agustos','Eylul','Ekim','Kasim','Aralik'];
    const days = ['Pazar','Pazartesi','Sali','Carsamba','Persembe','Cuma','Cumartesi'];
    try {
      const d = new Date(dateStr + 'T00:00:00');
      return `${d.getDate()} ${months[d.getMonth()]} ${days[d.getDay()]}`;
    } catch { return dateStr; }
  };

  const getImageUrl = (img) => {
    if (!img) return null;
    if (img.startsWith('data:')) return img;
    if (img.startsWith('http')) return img;
    return img; // relative path like /uploads/events/xxx.jpg
  };

  const allImages = (event) => {
    const imgs = [];
    if (event.images && event.images.length > 0) {
      event.images.forEach(i => { if (i) imgs.push(i); });
    }
    if (event.cover_image && !imgs.includes(event.cover_image)) {
      imgs.unshift(event.cover_image);
    }
    return imgs;
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="events-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Etkinlikler</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">{events.length} etkinlik</p>
        </div>
        <div className="flex gap-2">
          {events.length === 0 && (
            <Button onClick={handleSeedEvents} disabled={seeding}
              className="bg-white/5 hover:bg-white/10 text-[#C4972A] border border-[#C4972A]/20"
              data-testid="seed-events-btn">
              {seeding ? 'Yukleniyor...' : 'Ornek Etkinlikleri Yukle'}
            </Button>
          )}
          <Dialog open={open} onOpenChange={(v) => { setOpen(v); if (!v) resetForm(); }}>
            <DialogTrigger asChild>
              <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-event-btn">
                <Plus className="w-4 h-4 mr-2" /> Etkinlik Ekle
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20 max-w-lg max-h-[90vh] overflow-y-auto">
              <DialogHeader><DialogTitle className="text-[#C4972A]">{editingEvent ? 'Etkinlik Duzenle' : 'Yeni Etkinlik'}</DialogTitle></DialogHeader>
              <div className="space-y-3">
                <Input placeholder="Etkinlik adi *" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })}
                  className="bg-white/5 border-white/10" data-testid="event-title-input" />
                <textarea placeholder="Aciklama" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
                  className="w-full bg-white/5 border border-white/10 rounded-md p-2 text-sm text-white min-h-[80px] resize-y" />
                <select value={form.event_type} onChange={e => setForm({ ...form, event_type: e.target.value })}
                  className="w-full bg-white/5 border border-white/10 rounded-md p-2 text-sm text-white">
                  {Object.entries(EVENT_TYPES).map(([key, val]) => (
                    <option key={key} value={key} className="bg-[#1a1a22]">{val.label}</option>
                  ))}
                </select>
                <Input type="date" value={form.event_date} onChange={e => setForm({ ...form, event_date: e.target.value })}
                  className="bg-white/5 border-white/10" data-testid="event-date-input" />
                <Input type="time" value={form.start_time} onChange={e => setForm({ ...form, start_time: e.target.value })}
                  className="bg-white/5 border-white/10" />
                <Input type="number" placeholder="Kapasite" value={form.capacity} onChange={e => setForm({ ...form, capacity: e.target.value })}
                  className="bg-white/5 border-white/10" />
                <Input type="number" placeholder="Kisi basi fiyat (TL)" value={form.price_per_person} onChange={e => setForm({ ...form, price_per_person: e.target.value })}
                  className="bg-white/5 border-white/10" />

                {/* Image Upload Section */}
                <div className="space-y-2">
                  <label className="text-sm text-[#C4972A] font-medium flex items-center gap-1.5">
                    <Image className="w-4 h-4" /> Afis / Fotograf Yukle (max 2 adet)
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    {/* Image 1 */}
                    <div className="relative">
                      {form.images?.[0] ? (
                        <div className="relative group">
                          <img src={getImageUrl(form.images[0])} alt="Afis 1"
                            className="w-full h-32 object-cover rounded-lg border border-white/10" />
                          <button onClick={() => removeImage(0)}
                            className="absolute top-1 right-1 bg-red-500/80 hover:bg-red-500 rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <X className="w-3 h-3 text-white" />
                          </button>
                        </div>
                      ) : (
                        <button onClick={() => fileInputRef1.current?.click()}
                          className="w-full h-32 border-2 border-dashed border-white/20 rounded-lg flex flex-col items-center justify-center gap-1 hover:border-[#C4972A]/50 transition-colors"
                          data-testid="upload-image-1">
                          <Image className="w-6 h-6 text-[#7e7e8a]" />
                          <span className="text-xs text-[#7e7e8a]">Afis 1</span>
                        </button>
                      )}
                      <input ref={fileInputRef1} type="file" accept="image/*" className="hidden"
                        onChange={(e) => handleImageSelect(e, 0)} />
                    </div>

                    {/* Image 2 */}
                    <div className="relative">
                      {form.images?.[1] ? (
                        <div className="relative group">
                          <img src={getImageUrl(form.images[1])} alt="Afis 2"
                            className="w-full h-32 object-cover rounded-lg border border-white/10" />
                          <button onClick={() => removeImage(1)}
                            className="absolute top-1 right-1 bg-red-500/80 hover:bg-red-500 rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <X className="w-3 h-3 text-white" />
                          </button>
                        </div>
                      ) : (
                        <button onClick={() => fileInputRef2.current?.click()}
                          className="w-full h-32 border-2 border-dashed border-white/20 rounded-lg flex flex-col items-center justify-center gap-1 hover:border-[#C4972A]/50 transition-colors"
                          data-testid="upload-image-2">
                          <Image className="w-6 h-6 text-[#7e7e8a]" />
                          <span className="text-xs text-[#7e7e8a]">Afis 2</span>
                        </button>
                      )}
                      <input ref={fileInputRef2} type="file" accept="image/*" className="hidden"
                        onChange={(e) => handleImageSelect(e, 1)} />
                    </div>
                  </div>
                  <p className="text-[10px] text-[#7e7e8a]">JPG, PNG, WebP - max 5MB</p>
                </div>

                <Button onClick={handleCreate} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-event-btn">
                  {editingEvent ? 'Guncelle' : 'Kaydet'}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* View Event Dialog - Full detail with images */}
      <Dialog open={!!viewEvent} onOpenChange={(v) => { if (!v) setViewEvent(null); }}>
        <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20 max-w-2xl max-h-[90vh] overflow-y-auto">
          {viewEvent && (
            <>
              <DialogHeader>
                <DialogTitle className="text-[#C4972A] text-xl">{viewEvent.title}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                {/* All images gallery */}
                {allImages(viewEvent).length > 0 && (
                  <div className={`grid gap-3 ${allImages(viewEvent).length === 1 ? 'grid-cols-1' : 'grid-cols-2'}`}>
                    {allImages(viewEvent).map((img, idx) => (
                      <img key={idx} src={getImageUrl(img)} alt={`${viewEvent.title} - ${idx + 1}`}
                        className="w-full h-64 object-cover rounded-xl" />
                    ))}
                  </div>
                )}
                {viewEvent.description && (
                  <p className="text-sm text-[#a9a9b2] leading-relaxed">{viewEvent.description}</p>
                )}
                <div className="flex flex-wrap gap-3 text-sm text-[#7e7e8a]">
                  <span className="flex items-center gap-1 text-white/90">
                    <Calendar className="w-4 h-4 text-[#C4972A]" /> {formatDate(viewEvent.event_date)}
                  </span>
                  {viewEvent.start_time && (
                    <span className="flex items-center gap-1 text-white/90">
                      <Clock className="w-4 h-4 text-[#C4972A]" /> {viewEvent.start_time}
                    </span>
                  )}
                  {viewEvent.capacity && (
                    <span className="flex items-center gap-1"><Users className="w-4 h-4" /> {viewEvent.capacity} kisi</span>
                  )}
                </div>
                {viewEvent.menu_details && (
                  <div className="bg-white/3 rounded-lg p-4 text-sm text-[#a9a9b2] space-y-2">
                    <h4 className="text-[#C4972A] font-medium flex items-center gap-1"><Utensils className="w-4 h-4" /> Menu Detaylari</h4>
                    {viewEvent.menu_details.baslangiclar && <div><span className="text-[#C4972A]">Baslangiclar:</span> {viewEvent.menu_details.baslangiclar.join(', ')}</div>}
                    {viewEvent.menu_details.mezeler && <div><span className="text-[#C4972A]">Mezeler:</span> {viewEvent.menu_details.mezeler.join(', ')}</div>}
                    {viewEvent.menu_details.salata && <div><span className="text-[#C4972A]">Salata:</span> {viewEvent.menu_details.salata}</div>}
                    {viewEvent.menu_details.ara_sicak && <div><span className="text-[#C4972A]">Ara Sicak:</span> {viewEvent.menu_details.ara_sicak}</div>}
                    {viewEvent.menu_details.ana_yemek && <div><span className="text-[#C4972A]">Ana Yemek:</span> {viewEvent.menu_details.ana_yemek}</div>}
                    {viewEvent.menu_details.tatli && <div><span className="text-[#C4972A]">Tatli:</span> {viewEvent.menu_details.tatli}</div>}
                  </div>
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {events.map(event => {
          const typeInfo = EVENT_TYPES[event.event_type] || EVENT_TYPES.general;
          const TypeIcon = typeInfo.icon;
          const imgs = allImages(event);
          return (
            <div key={event.id} className="glass rounded-xl overflow-hidden hover:gold-glow transition-all" data-testid={`event-${event.id}`}>
              {/* Images Gallery */}
              {imgs.length > 0 && (
                <div className="relative">
                  {imgs.length === 1 ? (
                    <div className="h-48 overflow-hidden cursor-pointer" onClick={() => setViewEvent(event)}>
                      <img src={getImageUrl(imgs[0])} alt={event.title} className="w-full h-full object-cover" />
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 h-48 cursor-pointer" onClick={() => setViewEvent(event)}>
                      {imgs.slice(0, 2).map((img, idx) => (
                        <div key={idx} className="overflow-hidden">
                          <img src={getImageUrl(img)} alt={`${event.title} ${idx + 1}`} className="w-full h-full object-cover" />
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0f] via-transparent to-transparent pointer-events-none" />
                  <div className="absolute bottom-3 left-4 flex items-center gap-2">
                    <Badge className={`${event.event_type === 'special_dinner' ? 'bg-rose-500/20 text-rose-300' : 'bg-purple-500/20 text-purple-300'} text-xs`}>
                      <TypeIcon className="w-3 h-3 mr-1" /> {typeInfo.label}
                    </Badge>
                    {imgs.length > 1 && (
                      <Badge className="bg-black/40 text-white/80 text-xs">
                        <Image className="w-3 h-3 mr-1" /> {imgs.length} foto
                      </Badge>
                    )}
                  </div>
                </div>
              )}

              <div className="p-5 space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1 cursor-pointer" onClick={() => setViewEvent(event)}>
                    <h3 className="text-lg font-semibold text-[#C4972A]">{event.title}</h3>
                    {event.artist && (
                      <p className="text-sm text-white/80 mt-0.5 flex items-center gap-1">
                        <Music className="w-3 h-3" /> {event.artist}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-1">
                    <button onClick={() => handleEdit(event)}
                      className="text-[#7e7e8a] hover:text-[#C4972A] p-1" title="Duzenle">
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button onClick={() => setViewEvent(event)}
                      className="text-[#7e7e8a] hover:text-blue-400 p-1" title="Goruntule">
                      <Eye className="w-4 h-4" />
                    </button>
                    <button onClick={() => { if (window.confirm('Bu etkinligi silmek istediginize emin misiniz?')) deleteEvent(event.id).then(load); }}
                      className="text-[#7e7e8a] hover:text-red-400 p-1" data-testid={`delete-event-${event.id}`}>
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {event.description && (
                  <p className="text-sm text-[#a9a9b2] leading-relaxed line-clamp-3">{event.description}</p>
                )}

                {/* Date/Time/Capacity Row */}
                <div className="flex flex-wrap items-center gap-3 text-xs text-[#7e7e8a]">
                  <span className="flex items-center gap-1 text-white/90">
                    <Calendar className="w-3.5 h-3.5 text-[#C4972A]" /> {formatDate(event.event_date)}
                  </span>
                  {event.start_time && (
                    <span className="flex items-center gap-1 text-white/90">
                      <Clock className="w-3.5 h-3.5 text-[#C4972A]" /> {event.start_time}
                    </span>
                  )}
                  {event.capacity && (
                    <span className="flex items-center gap-1">
                      <Users className="w-3.5 h-3.5" /> {event.capacity} kisi
                    </span>
                  )}
                </div>

                {/* Pricing */}
                {(event.pricing || event.price_per_person) && (
                  <div className="bg-white/3 rounded-lg p-3 space-y-1">
                    {event.pricing ? (
                      <div className="flex flex-wrap gap-3">
                        <div>
                          <p className="text-[10px] text-[#7e7e8a] uppercase">Alkolu Menu</p>
                          <p className="text-base font-bold text-[#C4972A]">{event.pricing.alkolu_menu?.toLocaleString()} TL<span className="text-xs font-normal text-[#7e7e8a]">/kisi</span></p>
                        </div>
                        <div>
                          <p className="text-[10px] text-[#7e7e8a] uppercase">Sinirsiz Alkolu</p>
                          <p className="text-base font-bold text-[#C4972A]">{event.pricing.sinirsiz_alkolu_menu?.toLocaleString()} TL<span className="text-xs font-normal text-[#7e7e8a]">/kisi</span></p>
                        </div>
                      </div>
                    ) : (
                      <p className="text-base font-bold text-[#C4972A]">{event.price_per_person?.toLocaleString()} TL<span className="text-xs font-normal text-[#7e7e8a]">/kisi</span></p>
                    )}
                  </div>
                )}

                {/* Menu Details */}
                {event.menu_details && (
                  <details className="group">
                    <summary className="text-xs text-[#C4972A] cursor-pointer hover:text-[#dbb44d] flex items-center gap-1">
                      <Utensils className="w-3 h-3" /> Menu Detaylari
                    </summary>
                    <div className="mt-2 bg-white/3 rounded-lg p-3 text-xs text-[#a9a9b2] space-y-1.5">
                      {event.menu_details.baslangiclar && (
                        <div><span className="text-[#C4972A] font-medium">Baslangiclar:</span> {event.menu_details.baslangiclar.join(', ')}</div>
                      )}
                      {event.menu_details.mezeler && (
                        <div><span className="text-[#C4972A] font-medium">Mezeler:</span> {event.menu_details.mezeler.join(', ')}</div>
                      )}
                      {event.menu_details.salata && (
                        <div><span className="text-[#C4972A] font-medium">Salata:</span> {event.menu_details.salata}</div>
                      )}
                      {event.menu_details.ara_sicak && (
                        <div><span className="text-[#C4972A] font-medium">Ara Sicak:</span> {event.menu_details.ara_sicak}</div>
                      )}
                      {event.menu_details.ana_yemek && (
                        <div><span className="text-[#C4972A] font-medium">Ana Yemek:</span> {event.menu_details.ana_yemek}</div>
                      )}
                      {event.menu_details.tatli && (
                        <div><span className="text-[#C4972A] font-medium">Tatli:</span> {event.menu_details.tatli}</div>
                      )}
                    </div>
                  </details>
                )}

                {/* Tags */}
                {imgs.length === 0 && (
                  <div className="flex items-center gap-2">
                    <Badge className="bg-[#C4972A]/20 text-[#C4972A] text-xs">{typeInfo.label}</Badge>
                    {event.is_active && <Badge className="bg-green-500/20 text-green-400 text-xs">Aktif</Badge>}
                  </div>
                )}
              </div>
            </div>
          );
        })}
        {events.length === 0 && !loading && (
          <div className="col-span-2 text-center py-12 text-[#7e7e8a]">
            <Calendar className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Henuz etkinlik yok</p>
            <p className="text-xs mt-1">Ornek etkinlikleri yukle butonuna tiklayabilirsiniz</p>
          </div>
        )}
      </div>
    </div>
  );
}
