import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  FileText, Plus, Eye, Copy, Trash2, Send, Check, X,
  Calendar, Users, DollarSign, RefreshCw, Clock, Heart,
  ChevronDown, ChevronUp, Building2, Sparkles, Search, Download
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import api from '../api';

const STATUS_MAP = {
  draft: { label: 'Taslak', color: 'bg-gray-500/20 text-gray-400', icon: FileText },
  sent: { label: 'Gonderildi', color: 'bg-blue-500/20 text-blue-400', icon: Send },
  accepted: { label: 'Kabul Edildi', color: 'bg-green-500/20 text-green-400', icon: Check },
  rejected: { label: 'Reddedildi', color: 'bg-red-500/20 text-red-400', icon: X },
  expired: { label: 'Suresi Doldu', color: 'bg-yellow-500/20 text-yellow-400', icon: Clock },
};

const EVENT_TYPES = {
  dugun: 'Dugun', nisan: 'Nisan', soz: 'Soz', kina: 'Kina',
  dogum_gunu: 'Dogum Gunu', yil_donumu: 'Yil Donumu', kurumsal: 'Kurumsal', diger: 'Diger',
};

const ROOM_TYPES = [
  { id: 'double', name: 'Double Oda (2 Kisilik)', defaultPrice: 3500 },
  { id: 'triple', name: 'Triple Oda (3 Kisilik)', defaultPrice: 4000 },
  { id: 'superior', name: 'Superior Oda (3 Kisilik)', defaultPrice: 4250 },
  { id: 'king', name: 'King Oda (4 Kisilik)', defaultPrice: 5000 },
];

const DEFAULT_EXTRAS = [
  { name: 'Dekorasyon', description: 'Masa dekor, yuzuk tepsisi, konsept, ayna, pano, isteme alani', price: 40000 },
  { name: 'Fotograf & Video', description: 'Sinirsiz fotograf, video, klip cekimi, dijital davetiye', price: 35000 },
  { name: 'DJ & Ses Sistemi', description: 'DJ dahil, ses sistemi kirasi', price: 30000 },
  { name: 'Koordinasyon', description: 'Organizasyon koordinasyonu', price: 15000 },
];

function formatPrice(n) { return n ? n.toLocaleString('tr-TR') + ' TL' : '-'; }

export default function ProposalsPage() {
  const [proposals, setProposals] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [creating, setCreating] = useState(false);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [expanded, setExpanded] = useState(null);

  // Form state
  const [form, setForm] = useState({
    customer_name: '', customer_phone: '', customer_email: '', inquiry_id: '',
    event_type: 'dugun', event_date: '', event_date_note: '', guest_count: 70,
    accommodation_items: ROOM_TYPES.map(r => ({ room_type: r.name, room_count: 0, nights: 1, per_room_price: r.defaultPrice, total: 0, note: '' })),
    meal_per_person: 2500, meal_cash_price: 2250,
    extra_services: DEFAULT_EXTRAS.map(e => ({ ...e, enabled: true })),
    discount_amount: 0, discount_note: '', validity_days: 15,
    notes: 'Tum oda fiyatlarina kisi basi gurme serpme kahvalti dahildir.',
    internal_notes: '',
  });

  const [aiLoading, setAiLoading] = useState(false);
  const [aiTheme, setAiTheme] = useState('');
  const [aiDietary, setAiDietary] = useState('');

  const load = useCallback(async () => {
    try {
      const [propRes, statsRes] = await Promise.all([
        api.get('/proposals'),
        api.get('/proposals/stats/summary'),
      ]);
      setProposals(propRes.data.proposals || []);
      setStats(statsRes.data);
    } catch (err) { console.error(err); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const calcTotals = () => {
    const accTotal = form.accommodation_items.reduce((s, i) => s + (i.room_count * i.nights * i.per_room_price), 0);
    const mealTotal = form.guest_count * form.meal_per_person;
    const mealCash = form.guest_count * form.meal_cash_price;
    const extTotal = form.extra_services.filter(e => e.enabled !== false).reduce((s, e) => s + e.price, 0);
    const grand = accTotal + mealTotal + extTotal - form.discount_amount;
    const grandCash = accTotal + mealCash + extTotal - form.discount_amount;
    return { accTotal, mealTotal, mealCash, extTotal, grand, grandCash };
  };

  const handleCreate = async () => {
    const t = calcTotals();
    const payload = {
      customer_name: form.customer_name, customer_phone: form.customer_phone,
      customer_email: form.customer_email, inquiry_id: form.inquiry_id,
      event_type: form.event_type, event_date: form.event_date,
      event_date_note: form.event_date_note, guest_count: form.guest_count,
      accommodation_items: form.accommodation_items.filter(i => i.room_count > 0).map(i => ({
        ...i, total: i.room_count * i.nights * i.per_room_price,
      })),
      accommodation_total: t.accTotal, accommodation_note: form.notes,
      meal_options: [
        { description: 'Kredi Karti ile', per_person_price: form.meal_per_person, guest_count: form.guest_count, payment_method: 'kredi_karti', total: t.mealTotal },
        { description: 'Nakit Odeme', per_person_price: form.meal_cash_price, guest_count: form.guest_count, payment_method: 'nakit', total: t.mealCash },
      ],
      meal_total: t.mealTotal,
      extra_services: form.extra_services.filter(e => e.enabled !== false).map(e => ({ name: e.name, description: e.description, price: e.price })),
      extras_total: t.extTotal,
      grand_total: t.grand,
      discount_amount: form.discount_amount, discount_note: form.discount_note,
      validity_days: form.validity_days,
      notes: form.notes, internal_notes: form.internal_notes,
    };
    try {
      await api.post('/proposals', payload);
      setCreating(false);
      load();
    } catch (err) { alert(err.response?.data?.detail || 'Hata'); }
  };

  const generateAIMenu = async () => {
    setAiLoading(true);
    try {
      const res = await api.post('/proposals/ai-menu-planner', {
         event_type: form.event_type,
         guest_count: form.guest_count,
         budget_per_person: form.meal_per_person,
         dietary_notes: aiDietary,
         theme: aiTheme
      });
      if (res.data.ai_menus && res.data.ai_menus.length > 0) {
         const aiMenu = res.data.ai_menus[0];
         setForm(p => ({
             ...p, 
             meal_per_person: aiMenu.per_person_price,
             meal_cash_price: aiMenu.per_person_price * 0.9,
             notes: p.notes + '\n\n--- AI ZIYAFET MENUSU ---\n' + aiMenu.description
         }));
         alert("AI Menü başarıyla oluşturuldu! Fiyat güncellendi ve menü detayları Notlar kısmına eklendi.");
      } else if (res.data.error) {
         alert(res.data.error);
      }
    } catch (e) {
      alert("Hata olustu.");
    } finally {
      setAiLoading(false);
    }
  };

  const handleStatus = async (id, status) => {
    try { await api.patch(`/proposals/${id}`, { status }); load(); } catch (err) { console.error(err); }
  };

  const handleDuplicate = async (id) => {
    try { await api.post(`/proposals/${id}/duplicate`); load(); } catch (err) { console.error(err); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Teklifi silmek istediginize emin misiniz?')) return;
    try { await api.delete(`/proposals/${id}`); load(); } catch (err) { console.error(err); }
  };

  const handleDownloadPdf = async (id, proposalNumber) => {
    try {
      const res = await api.get(`/proposals/${id}/pdf`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `${proposalNumber || 'teklif'}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) { console.error(err); alert('PDF indirme hatasi'); }
  };

  const filtered = proposals.filter(p => {
    if (filter !== 'all' && p.status !== filter) return false;
    if (search) {
      const q = search.toLowerCase();
      return (p.customer_name || '').toLowerCase().includes(q) ||
        (p.customer_phone || '').includes(q) ||
        (p.proposal_number || '').toLowerCase().includes(q) ||
        (p.customer_email || '').toLowerCase().includes(q);
    }
    return true;
  });
  const t = calcTotals();

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1600px]" data-testid="proposals-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A] flex items-center gap-3">
            <FileText className="w-8 h-8" /> Teklif Yonetimi
          </h1>
          <p className="text-[#7e7e8a] text-sm mt-1">Organizasyon teklifleri, fiyatlar ve arsiv</p>
        </div>
        <div className="flex gap-3">
          <Button onClick={() => setCreating(true)} className="bg-[#C4972A] hover:bg-[#d4a73a] text-white" data-testid="new-proposal-btn">
            <Plus className="w-4 h-4 mr-2" /> Yeni Teklif
          </Button>
          <Button onClick={load} variant="outline" className="border-[#C4972A]/30 text-[#C4972A]">
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {[
          { label: 'Toplam', value: stats.total || 0, color: 'text-[#e5e5e8]' },
          { label: 'Taslak', value: stats.draft || 0, color: 'text-gray-400' },
          { label: 'Gonderildi', value: stats.sent || 0, color: 'text-blue-400' },
          { label: 'Kabul', value: stats.accepted || 0, color: 'text-green-400' },
          { label: 'Toplam Deger', value: formatPrice(stats.total_value || 0), color: 'text-[#C4972A]', small: true },
          { label: 'Donusum', value: `%${stats.conversion_rate || 0}`, color: 'text-purple-400' },
        ].map((s, i) => (
          <div key={i} className="glass rounded-xl p-4 text-center">
            <p className={`${s.small ? 'text-lg' : 'text-2xl'} font-bold ${s.color}`}>{s.value}</p>
            <p className="text-xs text-[#7e7e8a]">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Filter & Search */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex gap-2 overflow-x-auto pb-2 flex-1">
          {['all', ...Object.keys(STATUS_MAP)].map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-all ${
                filter === f ? 'bg-[#C4972A] text-white' : 'bg-white/5 text-[#7e7e8a] hover:bg-white/10'
              }`} data-testid={`filter-${f}`}>
              {f === 'all' ? 'Tumu' : STATUS_MAP[f]?.label}
            </button>
          ))}
        </div>
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#7e7e8a]" />
          <Input placeholder="Musteri adi, telefon, teklif no..." value={search}
            onChange={e => setSearch(e.target.value)}
            className="pl-9 bg-white/5 border-white/10 text-sm" data-testid="search-input" />
        </div>
      </div>

      {/* Proposals List */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="text-center py-12 text-[#7e7e8a]">
            <FileText className="w-16 h-16 mx-auto mb-3 opacity-30" />
            <p>{filter === 'all' ? 'Henuz teklif yok. Yeni teklif olusturun!' : 'Bu filtrede teklif yok'}</p>
          </div>
        ) : filtered.map(p => {
          const status = STATUS_MAP[p.status] || STATUS_MAP.draft;
          const isExpanded = expanded === p.id;
          return (
            <motion.div key={p.id} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }}
              className="glass rounded-xl overflow-hidden" data-testid={`proposal-${p.id}`}>
              {/* Header Row */}
              <div className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 cursor-pointer hover:bg-white/5"
                onClick={() => setExpanded(isExpanded ? null : p.id)}>
                <div className="flex items-center gap-4">
                  <div className="p-2 rounded-lg bg-[#C4972A]/20">
                    <FileText className="w-5 h-5 text-[#C4972A]" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm text-[#C4972A]">{p.proposal_number}</span>
                      <span className="font-semibold text-[#e5e5e8]">{p.customer_name}</span>
                    </div>
                    <p className="text-sm text-[#7e7e8a]">{p.customer_phone} {p.event_date && `| ${p.event_date}`}</p>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge className="bg-pink-500/20 text-pink-400">{EVENT_TYPES[p.event_type] || p.event_type}</Badge>
                  {p.guest_count > 0 && <Badge className="bg-white/10 text-[#a9a9b2]"><Users className="w-3 h-3 mr-1" />{p.guest_count}K</Badge>}
                  <Badge className="bg-[#C4972A]/20 text-[#C4972A] font-mono">{formatPrice(p.grand_total)}</Badge>
                  <Badge className={status.color}>{status.label}</Badge>
                  {isExpanded ? <ChevronUp className="w-4 h-4 text-[#7e7e8a]" /> : <ChevronDown className="w-4 h-4 text-[#7e7e8a]" />}
                </div>
              </div>

              {/* Expanded Detail */}
              {isExpanded && (
                <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                  className="border-t border-white/10 p-4 space-y-4">
                  {/* Konaklama */}
                  {p.accommodation_items?.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-blue-400 mb-2 flex items-center gap-1"><Building2 className="w-4 h-4" /> Konaklama</h4>
                      <div className="bg-blue-500/5 rounded-lg p-3 space-y-1">
                        {p.accommodation_items.map((a, i) => (
                          <div key={i} className="flex justify-between text-sm">
                            <span className="text-[#a9a9b2]">{a.room_type} x{a.room_count} ({a.nights} gece)</span>
                            <span className="text-[#e5e5e8] font-mono">{formatPrice(a.total)}</span>
                          </div>
                        ))}
                        <div className="flex justify-between text-sm font-semibold border-t border-white/10 pt-1 mt-1">
                          <span className="text-blue-400">Konaklama Toplam</span>
                          <span className="text-blue-400 font-mono">{formatPrice(p.accommodation_total)}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Yemek */}
                  {p.meal_options?.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-orange-400 mb-2 flex items-center gap-1"><Users className="w-4 h-4" /> Yemek ({p.guest_count} kisi)</h4>
                      <div className="bg-orange-500/5 rounded-lg p-3 space-y-1">
                        {p.meal_options.map((m, i) => (
                          <div key={i} className="flex justify-between text-sm">
                            <span className="text-[#a9a9b2]">{m.description} ({formatPrice(m.per_person_price)}/kisi)</span>
                            <span className="text-[#e5e5e8] font-mono">{formatPrice(m.total)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Ek Hizmetler */}
                  {p.extra_services?.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-purple-400 mb-2 flex items-center gap-1"><Sparkles className="w-4 h-4" /> Ek Hizmetler</h4>
                      <div className="bg-purple-500/5 rounded-lg p-3 space-y-1">
                        {p.extra_services.map((e, i) => (
                          <div key={i} className="flex justify-between text-sm">
                            <div>
                              <span className="text-[#a9a9b2]">{e.name}</span>
                              {e.description && <span className="text-[#7e7e8a] text-xs ml-2">({e.description})</span>}
                            </div>
                            <span className="text-[#e5e5e8] font-mono">{formatPrice(e.price)}</span>
                          </div>
                        ))}
                        <div className="flex justify-between text-sm font-semibold border-t border-white/10 pt-1 mt-1">
                          <span className="text-purple-400">Ek Hizmetler Toplam</span>
                          <span className="text-purple-400 font-mono">{formatPrice(p.extras_total)}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Genel Toplam */}
                  <div className="bg-[#C4972A]/10 rounded-lg p-4">
                    <div className="flex justify-between items-center">
                      <span className="text-lg font-bold text-[#C4972A]">GENEL TOPLAM</span>
                      <span className="text-2xl font-bold text-[#C4972A] font-mono">{formatPrice(p.grand_total)}</span>
                    </div>
                    {p.discount_amount > 0 && (
                      <p className="text-sm text-green-400 mt-1">Indirim: -{formatPrice(p.discount_amount)} {p.discount_note}</p>
                    )}
                  </div>

                  {/* Notlar */}
                  {p.notes && <p className="text-sm text-[#a9a9b2] italic">{p.notes}</p>}
                  {p.internal_notes && <p className="text-sm text-yellow-400 bg-yellow-500/10 rounded p-2">Dahili Not: {p.internal_notes}</p>}
                  <p className="text-xs text-[#7e7e8a]">Teklif No: {p.proposal_number} | Olusturulma: {new Date(p.created_at).toLocaleDateString('tr-TR')} | Gecerlilik: {p.validity_days} gun</p>

                  {/* Actions */}
                  <div className="flex flex-wrap gap-2 pt-2 border-t border-white/10">
                    <Button size="sm" onClick={() => handleDownloadPdf(p.id, p.proposal_number)}
                      className="bg-[#C4972A]/20 text-[#C4972A] hover:bg-[#C4972A]/30" data-testid={`pdf-btn-${p.id}`}>
                      <Download className="w-3 h-3 mr-1" /> PDF Indir
                    </Button>
                    {p.status === 'draft' && (
                      <Button size="sm" onClick={() => handleStatus(p.id, 'sent')} className="bg-blue-500/20 text-blue-400 hover:bg-blue-500/30">
                        <Send className="w-3 h-3 mr-1" /> Gonderildi
                      </Button>
                    )}
                    {p.status === 'sent' && (
                      <>
                        <Button size="sm" onClick={() => handleStatus(p.id, 'accepted')} className="bg-green-500/20 text-green-400 hover:bg-green-500/30">
                          <Check className="w-3 h-3 mr-1" /> Kabul Edildi
                        </Button>
                        <Button size="sm" onClick={() => handleStatus(p.id, 'rejected')} className="bg-red-500/20 text-red-400 hover:bg-red-500/30">
                          <X className="w-3 h-3 mr-1" /> Reddedildi
                        </Button>
                      </>
                    )}
                    <Button size="sm" variant="outline" onClick={() => handleDuplicate(p.id)} className="border-white/10 text-[#a9a9b2]">
                      <Copy className="w-3 h-3 mr-1" /> Kopyala
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => handleDelete(p.id)} className="text-red-400">
                      <Trash2 className="w-3 h-3 mr-1" /> Sil
                    </Button>
                  </div>
                </motion.div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Create Dialog */}
      <Dialog open={creating} onOpenChange={setCreating}>
        <DialogContent className="bg-[#1a1a2e] border-white/10 text-white max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-[#C4972A]"><Plus className="w-5 h-5 inline mr-2" />Yeni Teklif Olustur</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {/* Musteri */}
            <div className="grid grid-cols-2 gap-3">
              <Input placeholder="Musteri Adi *" value={form.customer_name}
                onChange={e => setForm(p => ({ ...p, customer_name: e.target.value }))}
                className="bg-white/5 border-white/10" data-testid="form-name" />
              <Input placeholder="Telefon" value={form.customer_phone}
                onChange={e => setForm(p => ({ ...p, customer_phone: e.target.value }))}
                className="bg-white/5 border-white/10" />
            </div>
            <div className="grid grid-cols-3 gap-3">
              <select value={form.event_type} onChange={e => setForm(p => ({ ...p, event_type: e.target.value }))}
                className="bg-white/5 border border-white/10 rounded-md px-3 text-sm">
                {Object.entries(EVENT_TYPES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
              <Input type="date" value={form.event_date}
                onChange={e => setForm(p => ({ ...p, event_date: e.target.value }))}
                className="bg-white/5 border-white/10" />
              <Input type="number" placeholder="Kisi sayisi" value={form.guest_count}
                onChange={e => setForm(p => ({ ...p, guest_count: parseInt(e.target.value) || 0 }))}
                className="bg-white/5 border-white/10" />
            </div>

            {/* Konaklama */}
            <div>
              <h4 className="text-sm font-medium text-blue-400 mb-2">Konaklama</h4>
              {form.accommodation_items.map((item, i) => (
                <div key={i} className="grid grid-cols-3 gap-2 mb-2">
                  <span className="text-sm text-[#a9a9b2] self-center">{item.room_type}</span>
                  <Input type="number" placeholder="Adet" value={item.room_count}
                    onChange={e => {
                      const items = [...form.accommodation_items];
                      items[i] = { ...items[i], room_count: parseInt(e.target.value) || 0 };
                      setForm(p => ({ ...p, accommodation_items: items }));
                    }}
                    className="bg-white/5 border-white/10" />
                  <Input type="number" placeholder="Fiyat/gece" value={item.per_room_price}
                    onChange={e => {
                      const items = [...form.accommodation_items];
                      items[i] = { ...items[i], per_room_price: parseFloat(e.target.value) || 0 };
                      setForm(p => ({ ...p, accommodation_items: items }));
                    }}
                    className="bg-white/5 border-white/10" />
                </div>
              ))}
              <p className="text-xs text-[#7e7e8a]">Konaklama Toplam: <strong className="text-blue-400">{formatPrice(t.accTotal)}</strong></p>
            </div>

            {/* Yemek */}
            <div>
              <div className="flex justify-between items-center mb-2">
                 <h4 className="text-sm font-medium text-orange-400">Yemek ({form.guest_count} kisi)</h4>
                 <Dialog>
                    <DialogTrigger asChild>
                       <Button size="sm" variant="outline" className="border-orange-500/30 text-orange-400 h-7 text-xs">
                          <Sparkles className="w-3 h-3 mr-1" /> AI Menü Tasarla
                       </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-[#1a1a2e] border-orange-500/20 max-w-md text-white">
                       <DialogHeader><DialogTitle className="text-orange-400">AI Ziyafet Menüsü Tasarımcısı</DialogTitle></DialogHeader>
                       <div className="space-y-3">
                          <p className="text-xs text-gray-400">Müsşterinin bütçesi, konsepti ve diyet isteklerine göre otomatik vegan/glütensiz veya gösterişli menüler oluşturun.</p>
                          <Input placeholder="Tema/Konsept (Örn: Rustik Kır Düğünü)" value={aiTheme} onChange={e => setAiTheme(e.target.value)} className="bg-white/5 border-white/10" />
                          <Input placeholder="Özel Diyet (Örn: %20 Vegan Menü)" value={aiDietary} onChange={e => setAiDietary(e.target.value)} className="bg-white/5 border-white/10" />
                          <Input type="number" placeholder="Kişi Başı Hedef Bütçe (TL)" value={form.meal_per_person} onChange={e => setForm(p => ({ ...p, meal_per_person: parseFloat(e.target.value) || 0 }))} className="bg-white/5 border-white/10" />
                          <Button onClick={generateAIMenu} disabled={aiLoading} className="w-full bg-orange-600 hover:bg-orange-700 text-white">
                             {aiLoading ? 'Menü Üretiliyor...' : 'Menüyü Oluştur ve Teklife Ekle'}
                          </Button>
                       </div>
                    </DialogContent>
                 </Dialog>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-[#7e7e8a]">Kredi Karti (kisi basi)</label>
                  <Input type="number" value={form.meal_per_person}
                    onChange={e => setForm(p => ({ ...p, meal_per_person: parseFloat(e.target.value) || 0 }))}
                    className="bg-white/5 border-white/10" />
                  <p className="text-xs text-[#7e7e8a] mt-1">Toplam: {formatPrice(t.mealTotal)}</p>
                </div>
                <div>
                  <label className="text-xs text-[#7e7e8a]">Nakit (kisi basi)</label>
                  <Input type="number" value={form.meal_cash_price}
                    onChange={e => setForm(p => ({ ...p, meal_cash_price: parseFloat(e.target.value) || 0 }))}
                    className="bg-white/5 border-white/10" />
                  <p className="text-xs text-[#7e7e8a] mt-1">Toplam: {formatPrice(t.mealCash)}</p>
                </div>
              </div>
            </div>

            {/* Ek Hizmetler */}
            <div>
              <h4 className="text-sm font-medium text-purple-400 mb-2">Ek Hizmetler</h4>
              {form.extra_services.map((s, i) => (
                <div key={i} className="flex items-center gap-3 mb-2">
                  <input type="checkbox" checked={s.enabled !== false}
                    onChange={e => {
                      const svcs = [...form.extra_services];
                      svcs[i] = { ...svcs[i], enabled: e.target.checked };
                      setForm(p => ({ ...p, extra_services: svcs }));
                    }} className="rounded" />
                  <span className="text-sm text-[#a9a9b2] flex-1">{s.name}</span>
                  <Input type="number" value={s.price}
                    onChange={e => {
                      const svcs = [...form.extra_services];
                      svcs[i] = { ...svcs[i], price: parseFloat(e.target.value) || 0 };
                      setForm(p => ({ ...p, extra_services: svcs }));
                    }}
                    className="bg-white/5 border-white/10 w-32" />
                </div>
              ))}
              <p className="text-xs text-[#7e7e8a]">Ek Toplam: <strong className="text-purple-400">{formatPrice(t.extTotal)}</strong></p>
            </div>

            {/* Toplam */}
            <div className="bg-[#C4972A]/10 rounded-lg p-4 text-center">
              <p className="text-sm text-[#7e7e8a]">GENEL TOPLAM (Kredi Karti)</p>
              <p className="text-3xl font-bold text-[#C4972A]">{formatPrice(t.grand)}</p>
              <p className="text-sm text-[#7e7e8a] mt-1">Nakit: {formatPrice(t.grandCash)}</p>
            </div>

            {/* Notlar */}
            <textarea value={form.notes} onChange={e => setForm(p => ({ ...p, notes: e.target.value }))}
              placeholder="Genel notlar..." rows={2}
              className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-sm text-[#e5e5e8] resize-none" />
            <textarea value={form.internal_notes} onChange={e => setForm(p => ({ ...p, internal_notes: e.target.value }))}
              placeholder="Dahili notlar (musteri gormez)..." rows={2}
              className="w-full bg-yellow-500/5 border border-yellow-500/20 rounded-lg p-3 text-sm text-yellow-300 resize-none" />

            <Button onClick={handleCreate} disabled={!form.customer_name}
              className="w-full bg-[#C4972A] hover:bg-[#d4a73a] text-white" data-testid="create-proposal-btn">
              <Plus className="w-4 h-4 mr-2" /> Teklif Olustur
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
