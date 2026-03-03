import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Heart, Phone, Calendar, Users, Mail, MapPin, Coffee, Wine,
  Camera, Music, Sparkles, FileText, RefreshCw, ChevronRight,
  Check, Clock, DollarSign, Trash2, Eye, ExternalLink
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import api from '../api';

const STATUS_MAP = {
  new: { label: 'Yeni', color: 'bg-blue-500/20 text-blue-400' },
  contacted: { label: 'Iletisime Gecildi', color: 'bg-yellow-500/20 text-yellow-400' },
  quoted: { label: 'Teklif Verildi', color: 'bg-purple-500/20 text-purple-400' },
  confirmed: { label: 'Onaylandi', color: 'bg-green-500/20 text-green-400' },
  cancelled: { label: 'Iptal', color: 'bg-red-500/20 text-red-400' },
};

const ORG_TYPES = {
  dugun: 'Dugun', nisan: 'Nisan', soz: 'Soz', kina: 'Kina',
  dogum_gunu: 'Dogum Gunu', yil_donumu: 'Yil Donumu',
  kurumsal: 'Kurumsal', diger: 'Diger',
};

export default function OrganizationPage() {
  const [inquiries, setInquiries] = useState([]);
  const [stats, setStats] = useState({});
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState('all');

  const load = useCallback(async () => {
    try {
      const [inqRes, statsRes, infoRes] = await Promise.all([
        api.get('/organization/inquiries'),
        api.get('/organization/stats'),
        api.get('/organization/info'),
      ]);
      setInquiries(inqRes.data.inquiries || []);
      setStats(statsRes.data);
      setInfo(infoRes.data);
    } catch (err) { console.error(err); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const updateStatus = async (id, status) => {
    try {
      await api.patch(`/organization/inquiries/${id}`, { status });
      load();
    } catch (err) { console.error(err); }
  };

  const deleteInquiry = async (id) => {
    if (!window.confirm('Talebi silmek istediginize emin misiniz?')) return;
    try { await api.delete(`/organization/inquiries/${id}`); load(); } catch (err) { console.error(err); }
  };

  const filtered = filter === 'all' ? inquiries : inquiries.filter(i => i.status === filter);

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1600px]" data-testid="organization-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A] flex items-center gap-3">
            <Heart className="w-8 h-8" />
            Organizasyon Yonetimi
          </h1>
          <p className="text-[#7e7e8a] text-sm mt-1">Dugun, nisan, ozel kutlama talepleri</p>
        </div>
        <Button onClick={load} variant="outline" className="border-[#C4972A]/30 text-[#C4972A]" data-testid="refresh-btn">
          <RefreshCw className="w-4 h-4 mr-2" /> Yenile
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { label: 'Toplam', value: stats.total || 0, color: 'text-[#e5e5e8]' },
          { label: 'Yeni', value: stats.new || 0, color: 'text-blue-400' },
          { label: 'Iletisimde', value: stats.contacted || 0, color: 'text-yellow-400' },
          { label: 'Teklif', value: stats.quoted || 0, color: 'text-purple-400' },
          { label: 'Onaylandi', value: stats.confirmed || 0, color: 'text-green-400' },
        ].map((s, i) => (
          <div key={i} className="glass rounded-xl p-4 text-center">
            <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
            <p className="text-xs text-[#7e7e8a]">{s.label}</p>
          </div>
        ))}
      </div>

      {/* PDF Sunumlar */}
      {info?.presentations && (
        <div className="glass rounded-xl p-4">
          <h3 className="font-semibold text-[#e5e5e8] mb-3 flex items-center gap-2">
            <FileText className="w-5 h-5 text-[#C4972A]" /> Sunum Dosyalari
          </h3>
          <div className="flex flex-wrap gap-3">
            {info.presentations.map(pdf => (
              <a key={pdf.id} href={pdf.url} target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-[#C4972A]/10 border border-[#C4972A]/30 rounded-lg text-sm text-[#C4972A] hover:bg-[#C4972A]/20 transition-all"
                data-testid={`pdf-${pdf.id}`}>
                <FileText className="w-4 h-4" /> {pdf.name} <ExternalLink className="w-3 h-3" />
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Filter */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {['all', 'new', 'contacted', 'quoted', 'confirmed', 'cancelled'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-all ${
              filter === f ? 'bg-[#C4972A] text-white' : 'bg-white/5 text-[#7e7e8a] hover:bg-white/10'
            }`} data-testid={`filter-${f}`}>
            {f === 'all' ? 'Tumu' : STATUS_MAP[f]?.label || f}
          </button>
        ))}
      </div>

      {/* Inquiries List */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="text-center py-12 text-[#7e7e8a]">
            <Heart className="w-16 h-16 mx-auto mb-3 opacity-30" />
            <p>{filter === 'all' ? 'Henuz organizasyon talebi yok' : 'Bu filtrede talep yok'}</p>
          </div>
        ) : filtered.map(inq => {
          const status = STATUS_MAP[inq.status] || STATUS_MAP.new;
          return (
            <motion.div key={inq.id} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }}
              className="glass rounded-xl p-4 hover:bg-white/5 transition-all cursor-pointer"
              onClick={() => setSelected(inq)} data-testid={`inquiry-${inq.id}`}>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="flex items-center gap-4">
                  <div className="p-2 rounded-lg bg-pink-500/20">
                    <Heart className="w-5 h-5 text-pink-400" />
                  </div>
                  <div>
                    <p className="font-semibold text-[#e5e5e8]">{inq.guest_name}</p>
                    <p className="text-sm text-[#7e7e8a]">{inq.phone} {inq.email && `| ${inq.email}`}</p>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge className="bg-pink-500/20 text-pink-400">{ORG_TYPES[inq.org_type] || inq.org_type}</Badge>
                  {inq.date && <Badge className="bg-white/10 text-[#a9a9b2]"><Calendar className="w-3 h-3 mr-1" />{inq.date}</Badge>}
                  {inq.guest_count_estimate > 0 && <Badge className="bg-white/10 text-[#a9a9b2]"><Users className="w-3 h-3 mr-1" />{inq.guest_count_estimate}K</Badge>}
                  <Badge className={status.color}>{status.label}</Badge>
                  {inq.price_quote > 0 && <Badge className="bg-green-500/20 text-green-400">{inq.price_quote.toLocaleString()} TL</Badge>}
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="ghost" onClick={e => { e.stopPropagation(); setSelected(inq); }}
                    className="text-[#C4972A]"><Eye className="w-3 h-3" /></Button>
                  <Button size="sm" variant="ghost" onClick={e => { e.stopPropagation(); deleteInquiry(inq.id); }}
                    className="text-red-400"><Trash2 className="w-3 h-3" /></Button>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Detail Dialog */}
      <Dialog open={!!selected} onOpenChange={() => setSelected(null)}>
        <DialogContent className="bg-[#1a1a2e] border-white/10 text-white max-w-2xl max-h-[80vh] overflow-y-auto">
          {selected && (
            <>
              <DialogHeader>
                <DialogTitle className="text-[#C4972A] flex items-center gap-2">
                  <Heart className="w-5 h-5" /> {selected.guest_name} - {ORG_TYPES[selected.org_type]}
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                {/* Kisisel */}
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div><span className="text-[#7e7e8a]">Telefon:</span> <span className="text-[#e5e5e8]">{selected.phone}</span></div>
                  <div><span className="text-[#7e7e8a]">E-posta:</span> <span className="text-[#e5e5e8]">{selected.email || '-'}</span></div>
                  <div><span className="text-[#7e7e8a]">Tarih:</span> <span className="text-[#e5e5e8]">{selected.date || '-'}</span></div>
                  <div><span className="text-[#7e7e8a]">Alt. Tarih:</span> <span className="text-[#e5e5e8]">{selected.alt_date || '-'}</span></div>
                  <div><span className="text-[#7e7e8a]">Saat:</span> <span className="text-[#e5e5e8]">{selected.start_time || '-'} - {selected.end_time || '-'}</span></div>
                  <div><span className="text-[#7e7e8a]">Kisi:</span> <span className="text-[#e5e5e8]">{selected.guest_count_estimate || '-'} (kesin: {selected.guest_count_final || '-'})</span></div>
                  <div><span className="text-[#7e7e8a]">Cocuk 0-6:</span> <span className="text-[#e5e5e8]">{selected.child_0_6 || 0}</span></div>
                  <div><span className="text-[#7e7e8a]">Cocuk 7-12:</span> <span className="text-[#e5e5e8]">{selected.child_7_12 || 0}</span></div>
                </div>

                {/* Konaklama */}
                {selected.needs_accommodation && (
                  <div className="bg-blue-500/10 rounded-lg p-3">
                    <h4 className="text-blue-400 font-medium mb-2">Konaklama</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>Giris: {selected.checkin_date || '-'}</div>
                      <div>Cikis: {selected.checkout_date || '-'}</div>
                      <div>2'lik: {selected.double_rooms || 0}</div>
                      <div>3'luk: {selected.triple_rooms || 0}</div>
                      <div>Aile: {selected.family_rooms || 0}</div>
                      <div>Gelin Odasi: {selected.bridal_suite ? 'Evet' : 'Hayir'}</div>
                    </div>
                  </div>
                )}

                {/* Menu & Diger */}
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div><span className="text-[#7e7e8a]">Menu:</span> <span className="text-[#e5e5e8]">{selected.menu_type || '-'}</span></div>
                  <div><span className="text-[#7e7e8a]">Dekorasyon:</span> <span className="text-[#e5e5e8]">{selected.decoration_package || '-'}</span></div>
                  <div><span className="text-[#7e7e8a]">Foto/Video:</span> <span className="text-[#e5e5e8]">{selected.wants_photo_video ? 'Evet' : 'Hayir'}</span></div>
                  <div><span className="text-[#7e7e8a]">Muzik:</span> <span className="text-[#e5e5e8]">{selected.music_preference || '-'}</span></div>
                  <div><span className="text-[#7e7e8a]">Butce:</span> <span className="text-[#e5e5e8]">{selected.budget_min || 0} - {selected.budget_max || 0} TL</span></div>
                  <div><span className="text-[#7e7e8a]">Referans:</span> <span className="text-[#e5e5e8]">{selected.referral_source || '-'}</span></div>
                </div>

                {selected.extra_notes && (
                  <div className="bg-white/5 rounded-lg p-3">
                    <span className="text-[#7e7e8a] text-sm">Notlar:</span>
                    <p className="text-[#e5e5e8] text-sm mt-1">{selected.extra_notes}</p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex flex-wrap gap-2 pt-2 border-t border-white/10">
                  {Object.entries(STATUS_MAP).map(([key, val]) => (
                    <Button key={key} size="sm" variant={selected.status === key ? 'default' : 'outline'}
                      className={selected.status === key ? 'bg-[#C4972A]' : 'border-white/10 text-[#a9a9b2]'}
                      onClick={() => { updateStatus(selected.id, key); setSelected({ ...selected, status: key }); }}
                      data-testid={`status-${key}`}>
                      {val.label}
                    </Button>
                  ))}
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
