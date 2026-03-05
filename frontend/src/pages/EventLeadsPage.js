import React, { useState, useEffect } from 'react';
import { getEventIdeas, getTargetGroups, getEventLeads, createEventLead, updateEventLead, deleteEventLead, generateOutreachMessage, logLeadContact, getEventLeadStats, getEventSuggestions } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Plus, Trash2, Edit2, Save, X, Send, Copy, MessageCircle, Users, Target, Sparkles, TrendingUp, Calendar, Phone, Instagram, Linkedin, Facebook, Star, ChevronDown, ChevronUp, Eye } from 'lucide-react';

const LEAD_STATUS = {
  new: { label: 'Yeni', color: '#60a5fa', bg: '#60a5fa20' },
  contacted: { label: 'Iletisim', color: '#C4972A', bg: '#C4972A20' },
  interested: { label: 'Ilgili', color: '#8FAA86', bg: '#8FAA8620' },
  booked: { label: 'Rezerve', color: '#22c55e', bg: '#22c55e20' },
  lost: { label: 'Kayip', color: '#7e7e8a', bg: '#7e7e8a20' },
};

const CATEGORY_LABELS = {
  workshop: 'Workshop', wellness: 'Wellness', premium: 'Premium',
  entertainment: 'Eglence', organization: 'Organizasyon', corporate: 'Kurumsal',
  experience: 'Deneyim',
};

const REVENUE_COLORS = {
  cok_yuksek: { label: 'Cok Yuksek', color: '#22c55e' },
  yuksek: { label: 'Yuksek', color: '#8FAA86' },
  orta: { label: 'Orta', color: '#C4972A' },
};

export default function EventLeadsPage() {
  const [ideas, setIdeas] = useState([]);
  const [leads, setLeads] = useState([]);
  const [groups, setGroups] = useState([]);
  const [stats, setStats] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('ideas'); // ideas, leads, outreach
  const [selectedIdea, setSelectedIdea] = useState(null);
  const [selectedLead, setSelectedLead] = useState(null);
  const [generatedMessage, setGeneratedMessage] = useState(null);
  const [showAddLead, setShowAddLead] = useState(false);
  const [newLead, setNewLead] = useState({ group_name: '', group_type: '', platform: 'instagram', contact_info: '', notes: '', target_event: '' });
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [expandedIdea, setExpandedIdea] = useState(null);

  const loadData = async () => {
    try {
      const [ideasRes, leadsRes, groupsRes, statsRes, suggestionsRes] = await Promise.all([
        getEventIdeas(), getEventLeads(), getTargetGroups(), getEventLeadStats(), getEventSuggestions()
      ]);
      setIdeas(ideasRes.data.ideas || []);
      setLeads(leadsRes.data.leads || []);
      setGroups(groupsRes.data.groups || []);
      setStats(statsRes.data);
      setSuggestions(suggestionsRes.data.suggestions || []);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  useEffect(() => { loadData(); }, []);

  const handleAddLead = async () => {
    if (!newLead.group_name || !newLead.group_type) return;
    await createEventLead(newLead);
    setNewLead({ group_name: '', group_type: '', platform: 'instagram', contact_info: '', notes: '', target_event: '' });
    setShowAddLead(false);
    loadData();
  };

  const handleDeleteLead = async (id) => {
    if (!window.confirm('Bu lead silinsin mi?')) return;
    await deleteEventLead(id);
    loadData();
  };

  const handleStatusChange = async (id, status) => {
    await updateEventLead(id, { status });
    loadData();
  };

  const handleGenerateMessage = async (lead, eventId, platform) => {
    try {
      const res = await generateOutreachMessage({ lead_id: lead.id, event_id: eventId, platform });
      setGeneratedMessage(res.data);
    } catch (err) { console.error(err); }
  };

  const handleCopyMessage = (text) => {
    navigator.clipboard.writeText(text);
  };

  const handleLogContact = async (leadId) => {
    await logLeadContact(leadId);
    loadData();
  };

  const filteredIdeas = categoryFilter === 'all' ? ideas : ideas.filter(i => i.category === categoryFilter);

  if (loading) return <div className="p-8"><div className="h-8 w-48 bg-white/5 rounded animate-pulse" /></div>;

  return (
    <div className="p-6 lg:p-8 max-w-[1400px]" data-testid="event-leads-page">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#C4972A]">Etkinlik & Lead Yonetimi</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">Etkinlik fikirleri, hedef kitle bulma ve mesaj gonderme</p>
        </div>
        <div className="flex gap-2">
          {['ideas', 'leads', 'outreach'].map(v => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-4 py-2 rounded-lg text-sm transition-all ${view === v ? 'bg-[#C4972A]/15 text-[#C4972A]' : 'text-[#7e7e8a] hover:bg-white/5'}`}
            >
              {v === 'ideas' ? 'Etkinlik Fikirleri' : v === 'leads' ? 'Lead\'ler' : 'Mesaj Gonder'}
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-5 gap-3 mb-6">
          {[
            { label: 'Toplam Lead', value: stats.total, icon: Users, color: '#C4972A' },
            { label: 'Yeni', value: stats.new, icon: Star, color: '#60a5fa' },
            { label: 'Iletisimde', value: stats.contacted, icon: Send, color: '#C4972A' },
            { label: 'Ilgili', value: stats.interested, icon: Target, color: '#8FAA86' },
            { label: 'Rezerve', value: stats.booked, icon: Calendar, color: '#22c55e' },
          ].map(s => (
            <div key={s.label} className="glass rounded-xl p-3">
              <div className="flex items-center gap-2 mb-1">
                <s.icon className="w-3.5 h-3.5" style={{ color: s.color }} />
                <span className="text-[10px] text-[#7e7e8a]">{s.label}</span>
              </div>
              <span className="text-xl font-bold" style={{ color: s.color }}>{s.value}</span>
            </div>
          ))}
        </div>
      )}

      {/* ─── ETKINLIK FIKIRLERI ─── */}
      {view === 'ideas' && (
        <>
          {/* Bu Ay Onerileri */}
          {suggestions.length > 0 && (
            <div className="mb-6">
              <h2 className="text-sm font-medium text-[#C4972A] mb-3 flex items-center gap-2">
                <Sparkles className="w-4 h-4" /> Bu Ay Icin Onerilen Etkinlikler
              </h2>
              <div className="grid grid-cols-4 gap-3">
                {suggestions.slice(0, 4).map(s => {
                  const rev = REVENUE_COLORS[s.revenue_potential] || REVENUE_COLORS.orta;
                  return (
                    <div key={s.id} className="glass rounded-xl p-4 border border-[#C4972A]/10 hover:border-[#C4972A]/30 transition-all cursor-pointer"
                      onClick={() => { setExpandedIdea(expandedIdea === s.id ? null : s.id); }}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] px-2 py-0.5 rounded bg-[#C4972A]/10 text-[#C4972A]">
                          {CATEGORY_LABELS[s.category] || s.category}
                        </span>
                        <span className="text-[10px] font-medium" style={{ color: rev.color }}>
                          <TrendingUp className="w-3 h-3 inline mr-1" />{rev.label}
                        </span>
                      </div>
                      <h3 className="text-sm font-medium text-[#e5e5e8] mb-1">{s.name}</h3>
                      <p className="text-[10px] text-[#7e7e8a] line-clamp-2">{s.description}</p>
                      <div className="mt-2 text-[10px] text-[#C4972A]">{s.price_range}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Category Filter */}
          <div className="flex gap-2 mb-4 flex-wrap">
            <button onClick={() => setCategoryFilter('all')} className={`px-3 py-1.5 rounded-lg text-xs transition-all ${categoryFilter === 'all' ? 'bg-[#C4972A]/15 text-[#C4972A]' : 'text-[#7e7e8a] hover:bg-white/5'}`}>
              Hepsi
            </button>
            {Object.entries(CATEGORY_LABELS).map(([k, v]) => (
              <button key={k} onClick={() => setCategoryFilter(k)} className={`px-3 py-1.5 rounded-lg text-xs transition-all ${categoryFilter === k ? 'bg-[#C4972A]/15 text-[#C4972A]' : 'text-[#7e7e8a] hover:bg-white/5'}`}>
                {v}
              </button>
            ))}
          </div>

          {/* Ideas Grid */}
          <div className="space-y-3">
            {filteredIdeas.map(idea => {
              const rev = REVENUE_COLORS[idea.revenue_potential] || REVENUE_COLORS.orta;
              const isExpanded = expandedIdea === idea.id;
              return (
                <div key={idea.id} className="glass rounded-xl overflow-hidden">
                  <div className="p-4 cursor-pointer hover:bg-white/[0.02] transition-all"
                    onClick={() => setExpandedIdea(isExpanded ? null : idea.id)}>
                    <div className="flex items-center gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-sm font-medium text-[#e5e5e8]">{idea.name}</h3>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-[#7e7e8a]">
                            {CATEGORY_LABELS[idea.category]}
                          </span>
                          <span className="text-[10px] font-medium" style={{ color: rev.color }}>
                            {rev.label} Gelir
                          </span>
                        </div>
                        <p className="text-xs text-[#7e7e8a]">{idea.description}</p>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <div className="text-xs text-[#C4972A] font-medium">{idea.price_range}</div>
                        <div className="text-[10px] text-[#7e7e8a]">{idea.capacity}</div>
                      </div>
                      {isExpanded ? <ChevronUp className="w-4 h-4 text-[#7e7e8a]" /> : <ChevronDown className="w-4 h-4 text-[#7e7e8a]" />}
                    </div>
                  </div>
                  {isExpanded && (
                    <div className="px-4 pb-4 pt-2 border-t border-white/5">
                      <div className="grid grid-cols-3 gap-4 text-xs">
                        <div>
                          <span className="text-[#7e7e8a] block mb-1">En Iyi Gunler</span>
                          <div className="flex gap-1 flex-wrap">
                            {idea.best_days.map(d => <span key={d} className="px-2 py-0.5 rounded bg-[#C4972A]/10 text-[#C4972A] text-[10px]">{d}</span>)}
                          </div>
                        </div>
                        <div>
                          <span className="text-[#7e7e8a] block mb-1">En Iyi Aylar</span>
                          <div className="flex gap-1 flex-wrap">
                            {(idea.best_months.includes('tum_yil') ? ['Tum Yil'] : idea.best_months.slice(0, 4)).map(m => <span key={m} className="px-2 py-0.5 rounded bg-white/5 text-[#a9a9b2] text-[10px]">{m}</span>)}
                          </div>
                        </div>
                        <div>
                          <span className="text-[#7e7e8a] block mb-1">Sure</span>
                          <span className="text-[#e5e5e8]">{idea.duration}</span>
                        </div>
                      </div>
                      <div className="mt-3">
                        <span className="text-[#7e7e8a] text-xs block mb-1">Hedef Kitle</span>
                        <div className="flex gap-1 flex-wrap">
                          {idea.target_audience.map(t => {
                            const grp = groups.find(g => g.id === t);
                            return <span key={t} className="px-2 py-0.5 rounded bg-[#8FAA86]/10 text-[#8FAA86] text-[10px]">{grp?.name || t}</span>;
                          })}
                        </div>
                      </div>
                      <div className="mt-3">
                        <span className="text-[#7e7e8a] text-xs block mb-1">Gereksinimler</span>
                        <div className="flex gap-1 flex-wrap">
                          {idea.needs.map(n => <span key={n} className="px-2 py-0.5 rounded bg-white/5 text-[#a9a9b2] text-[10px]">{n}</span>)}
                        </div>
                      </div>
                      <div className="mt-3 flex gap-2">
                        <Button size="sm" className="bg-[#8FAA86] hover:bg-[#7a9874] text-white text-xs"
                          onClick={(e) => { e.stopPropagation(); setSelectedIdea(idea); setView('leads'); }}>
                          <Target className="w-3 h-3 mr-1" /> Lead Bul
                        </Button>
                        <Button size="sm" variant="outline" className="border-[#C4972A]/30 text-[#C4972A] text-xs"
                          onClick={(e) => { e.stopPropagation(); setSelectedIdea(idea); setView('outreach'); }}>
                          <Send className="w-3 h-3 mr-1" /> Mesaj Olustur
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}

      {/* ─── LEADS ─── */}
      {view === 'leads' && (
        <>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-medium text-[#e5e5e8]">
              Lead Listesi {selectedIdea && <span className="text-[#C4972A]">({selectedIdea.name} icin)</span>}
            </h2>
            <Button onClick={() => setShowAddLead(true)} className="bg-[#C4972A] hover:bg-[#a87a1f] text-white text-xs">
              <Plus className="w-3.5 h-3.5 mr-1" /> Yeni Lead
            </Button>
          </div>

          {/* Add Lead Form */}
          {showAddLead && (
            <div className="glass rounded-xl p-4 mb-4 space-y-3">
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="text-[10px] text-[#7e7e8a] block mb-1">Grup / Kisi Adi</label>
                  <Input value={newLead.group_name} onChange={e => setNewLead({ ...newLead, group_name: e.target.value })}
                    className="bg-white/5 border-white/10 text-white text-sm" placeholder="Ornek: Izmir Yoga Toplulugu" />
                </div>
                <div>
                  <label className="text-[10px] text-[#7e7e8a] block mb-1">Grup Tipi</label>
                  <select value={newLead.group_type} onChange={e => setNewLead({ ...newLead, group_type: e.target.value })}
                    className="w-full p-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm outline-none">
                    <option value="">Sec...</option>
                    {groups.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-[10px] text-[#7e7e8a] block mb-1">Platform</label>
                  <select value={newLead.platform} onChange={e => setNewLead({ ...newLead, platform: e.target.value })}
                    className="w-full p-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm outline-none">
                    <option value="instagram">Instagram</option>
                    <option value="facebook">Facebook</option>
                    <option value="whatsapp">WhatsApp</option>
                    <option value="linkedin">LinkedIn</option>
                    <option value="email">Email</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[10px] text-[#7e7e8a] block mb-1">Iletisim (username/tel/email)</label>
                  <Input value={newLead.contact_info} onChange={e => setNewLead({ ...newLead, contact_info: e.target.value })}
                    className="bg-white/5 border-white/10 text-white text-sm" placeholder="@username veya 05xx..." />
                </div>
                <div>
                  <label className="text-[10px] text-[#7e7e8a] block mb-1">Hedef Etkinlik</label>
                  <select value={newLead.target_event} onChange={e => setNewLead({ ...newLead, target_event: e.target.value })}
                    className="w-full p-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm outline-none">
                    <option value="">Genel</option>
                    {ideas.map(i => <option key={i.id} value={i.id}>{i.name}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="text-[10px] text-[#7e7e8a] block mb-1">Notlar</label>
                <Input value={newLead.notes || ''} onChange={e => setNewLead({ ...newLead, notes: e.target.value })}
                  className="bg-white/5 border-white/10 text-white text-sm" placeholder="Opsiyonel notlar..." />
              </div>
              <div className="flex gap-2">
                <Button onClick={handleAddLead} className="bg-[#8FAA86] hover:bg-[#7a9874] text-white text-xs">
                  <Save className="w-3.5 h-3.5 mr-1" /> Kaydet
                </Button>
                <Button variant="ghost" onClick={() => setShowAddLead(false)} className="text-[#7e7e8a] text-xs">
                  <X className="w-3.5 h-3.5 mr-1" /> Iptal
                </Button>
              </div>
            </div>
          )}

          {/* Target Groups Info */}
          <div className="mb-4">
            <h3 className="text-xs text-[#7e7e8a] mb-2">Hedef Kitle Gruplari - Arama Ipuclari</h3>
            <div className="flex gap-2 flex-wrap">
              {groups.map(g => (
                <div key={g.id} className="glass rounded-lg p-2 text-[10px] cursor-pointer hover:border-[#C4972A]/20 transition-all"
                  onClick={() => { setNewLead({ ...newLead, group_type: g.id }); setShowAddLead(true); }}>
                  <span className="text-[#e5e5e8] font-medium">{g.name}</span>
                  <div className="text-[#7e7e8a] mt-0.5">{g.search_tags.slice(0, 3).join(', ')}</div>
                  <div className="flex gap-1 mt-1">
                    {g.platforms.map(p => (
                      <span key={p} className="px-1 py-0.5 rounded bg-white/5 text-[#a9a9b2]">{p}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Leads List */}
          <div className="space-y-2">
            {leads.length === 0 && (
              <div className="glass rounded-xl p-8 text-center text-[#7e7e8a]">
                <Users className="w-6 h-6 mx-auto mb-2 opacity-30" />
                <p className="text-sm">Henuz lead eklenmemis. Hedef kitle gruplarina tiklayin veya "Yeni Lead" butonunu kullanin.</p>
              </div>
            )}
            {leads.map(lead => {
              const st = LEAD_STATUS[lead.status] || LEAD_STATUS.new;
              const grp = groups.find(g => g.id === lead.group_type);
              const evt = ideas.find(i => i.id === lead.target_event);
              return (
                <div key={lead.id} className="glass rounded-xl p-3 group hover:border-[#C4972A]/20 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-sm font-medium text-[#e5e5e8] truncate">{lead.group_name}</h3>
                        <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: st.bg, color: st.color }}>{st.label}</span>
                        {grp && <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-[#7e7e8a]">{grp.name}</span>}
                      </div>
                      <div className="flex items-center gap-3 text-[10px] text-[#7e7e8a]">
                        <span>{lead.platform}</span>
                        {lead.contact_info && <span>{lead.contact_info}</span>}
                        {evt && <span className="text-[#C4972A]">Hedef: {evt.name}</span>}
                        {lead.messages_sent > 0 && <span>{lead.messages_sent} mesaj gonderildi</span>}
                      </div>
                    </div>
                    <div className="flex gap-1 items-center">
                      {/* Status buttons */}
                      <select
                        value={lead.status}
                        onChange={e => handleStatusChange(lead.id, e.target.value)}
                        className="text-[10px] p-1 rounded bg-white/5 border border-white/10 text-[#a9a9b2] outline-none"
                      >
                        {Object.entries(LEAD_STATUS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
                      </select>
                      <button onClick={() => { setSelectedLead(lead); setView('outreach'); }}
                        className="p-1.5 rounded-lg hover:bg-[#C4972A]/10 text-[#C4972A]" title="Mesaj Olustur">
                        <Send className="w-3.5 h-3.5" />
                      </button>
                      <button onClick={() => handleDeleteLead(lead.id)}
                        className="p-1.5 rounded-lg hover:bg-red-400/10 text-red-400 opacity-0 group-hover:opacity-100" title="Sil">
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}

      {/* ─── MESAJ GONDER ─── */}
      {view === 'outreach' && (
        <>
          <div className="grid grid-cols-12 gap-6">
            {/* Left: Lead + Event Selection */}
            <div className="col-span-5 space-y-4">
              {/* Select Lead */}
              <div className="glass rounded-xl p-4">
                <label className="text-xs text-[#7e7e8a] mb-2 block">Lead Sec</label>
                {leads.length === 0 ? (
                  <p className="text-xs text-[#7e7e8a]">Once lead ekleyin.</p>
                ) : (
                  <div className="space-y-1 max-h-[200px] overflow-y-auto">
                    {leads.map(l => (
                      <button
                        key={l.id}
                        onClick={() => setSelectedLead(l)}
                        className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-all ${selectedLead?.id === l.id ? 'bg-[#C4972A]/15 text-[#C4972A]' : 'text-[#a9a9b2] hover:bg-white/5'}`}
                      >
                        <span className="font-medium">{l.group_name}</span>
                        <span className="text-[10px] ml-2 text-[#7e7e8a]">{l.platform}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Select Event */}
              <div className="glass rounded-xl p-4">
                <label className="text-xs text-[#7e7e8a] mb-2 block">Etkinlik Sec</label>
                <div className="space-y-1 max-h-[200px] overflow-y-auto">
                  {ideas.map(i => (
                    <button
                      key={i.id}
                      onClick={() => setSelectedIdea(i)}
                      className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-all ${selectedIdea?.id === i.id ? 'bg-[#C4972A]/15 text-[#C4972A]' : 'text-[#a9a9b2] hover:bg-white/5'}`}
                    >
                      <span className="font-medium">{i.name}</span>
                      <span className="text-[10px] ml-2 text-[#7e7e8a]">{i.price_range}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Platform & Generate */}
              {selectedLead && selectedIdea && (
                <div className="glass rounded-xl p-4 space-y-3">
                  <label className="text-xs text-[#7e7e8a] block">Platform & Mesaj Uret</label>
                  <div className="flex gap-2">
                    {['whatsapp', 'instagram', 'linkedin'].map(p => (
                      <Button key={p} size="sm" onClick={() => handleGenerateMessage(selectedLead, selectedIdea.id, p)}
                        className="bg-white/5 hover:bg-white/10 text-[#e5e5e8] text-xs border border-white/10">
                        {p === 'whatsapp' ? <MessageCircle className="w-3 h-3 mr-1" /> :
                         p === 'instagram' ? <Instagram className="w-3 h-3 mr-1" /> :
                         <Linkedin className="w-3 h-3 mr-1" />}
                        {p}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right: Generated Message */}
            <div className="col-span-7">
              <div className="sticky top-4">
                <h3 className="text-sm text-[#7e7e8a] mb-3 flex items-center gap-2">
                  <Eye className="w-4 h-4" /> Uretilen Mesaj
                </h3>
                {generatedMessage ? (
                  <div className="glass rounded-xl p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] px-2 py-0.5 rounded bg-[#C4972A]/10 text-[#C4972A]">{generatedMessage.platform}</span>
                        <span className="text-[10px] text-[#7e7e8a]">{generatedMessage.event}</span>
                        <span className="text-[10px] text-[#7e7e8a]">→ {generatedMessage.lead}</span>
                      </div>
                    </div>
                    <div className="p-4 rounded-lg bg-white/5 border border-white/10">
                      <pre className="text-sm text-[#e5e5e8] whitespace-pre-wrap font-sans leading-relaxed">
                        {generatedMessage.message}
                      </pre>
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={() => handleCopyMessage(generatedMessage.message)}
                        className="bg-[#C4972A] hover:bg-[#a87a1f] text-white text-xs">
                        <Copy className="w-3.5 h-3.5 mr-1" /> Kopyala
                      </Button>
                      {selectedLead && (
                        <Button onClick={() => handleLogContact(selectedLead.id)}
                          className="bg-[#8FAA86] hover:bg-[#7a9874] text-white text-xs">
                          <Send className="w-3.5 h-3.5 mr-1" /> Gonderildi Olarak Isaretle
                        </Button>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="glass rounded-xl p-12 text-center text-[#7e7e8a]">
                    <MessageCircle className="w-8 h-8 mx-auto mb-3 opacity-30" />
                    <p className="text-sm">Sol taraftan lead ve etkinlik secin, sonra platform butonuna tiklayin.</p>
                    <p className="text-[10px] mt-2">Otomatik mesaj olusturulacak.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
