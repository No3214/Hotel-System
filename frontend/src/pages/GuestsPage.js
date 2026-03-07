import { getGuests, createGuest, updateGuest, getLoyaltyStats, getGuestLoyalty, updateGuestLoyalty, getAIRetargetingCampaigns } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Users, Plus, Search, Phone, Mail, Globe, Award, TrendingUp, Star, Crown, ArrowUp, RefreshCw, Sparkles, Loader2, Send } from 'lucide-react';

const LOYALTY_ICONS = {
  bronze: Award,
  silver: Star,
  gold: Crown,
  platinum: Crown,
};

const LOYALTY_COLORS = {
  bronze: { bg: 'bg-amber-700/15', text: 'text-amber-600', border: 'border-amber-700/30' },
  silver: { bg: 'bg-slate-300/15', text: 'text-slate-300', border: 'border-slate-400/30' },
  gold: { bg: 'bg-yellow-400/15', text: 'text-yellow-400', border: 'border-yellow-500/30' },
  platinum: { bg: 'bg-purple-300/15', text: 'text-purple-300', border: 'border-purple-400/30' },
};

export default function GuestsPage() {
  const [guests, setGuests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [open, setOpen] = useState(false);
  const [detailGuest, setDetailGuest] = useState(null);
  const [loyaltyDetail, setLoyaltyDetail] = useState(null);
  const [loyaltyStats, setLoyaltyStats] = useState(null);
  const [tab, setTab] = useState('all');
  const [form, setForm] = useState({ name: '', email: '', phone: '', nationality: '', notes: '' });

  // Phase 12 AI Retargeting State
  const [retargetingCampaigns, setRetargetingCampaigns] = useState([]);
  const [retargetingLoading, setRetargetingLoading] = useState(false);

  const load = () => {
    getGuests({ search: search || undefined })
      .then(r => setGuests(r.data.guests))
      .catch(console.error)
      .finally(() => setLoading(false));
    getLoyaltyStats().then(r => setLoyaltyStats(r.data)).catch(() => {});
  };

  useEffect(() => { load(); }, [search]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleCreate = async () => {
    if (!form.name) return;
    await createGuest(form);
    setForm({ name: '', email: '', phone: '', nationality: '', notes: '' });
    setOpen(false);
    load();
  };

  const openGuestDetail = async (guest) => {
    setDetailGuest(guest);
    try {
      const r = await getGuestLoyalty(guest.id);
      setLoyaltyDetail(r.data);
    } catch { setLoyaltyDetail(null); }
  };

  const handleRefreshLoyalty = async (guestId) => {
    await updateGuestLoyalty(guestId);
    openGuestDetail(detailGuest);
    load();
  };

  const loadRetargeting = async () => {
    setRetargetingLoading(true);
    try {
      const res = await getAIRetargetingCampaigns();
      if (res.data?.success) setRetargetingCampaigns(res.data.campaigns || []);
    } catch(e) { console.error("Retargeting load err", e); }
    setRetargetingLoading(false);
  };

  const getLoyaltyInfo = (guest) => {
    const stays = guest.total_stays || 0;
    if (stays >= 10) return { level: 'platinum', label: 'Platin', discount: 15 };
    if (stays >= 5) return { level: 'gold', label: 'Altin', discount: 10 };
    if (stays >= 3) return { level: 'silver', label: 'Gumus', discount: 5 };
    return { level: 'bronze', label: 'Bronz', discount: 0 };
  };

  const filteredGuests = tab === 'vip'
    ? guests.filter(g => (g.total_stays || 0) >= 3)
    : guests;

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="guests-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Misafirler</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">{guests.length} kayitli misafir</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-guest-btn">
              <Plus className="w-4 h-4 mr-2" /> Misafir Ekle
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
            <DialogHeader>
              <DialogTitle className="text-[#C4972A]">Yeni Misafir</DialogTitle>
            </DialogHeader>
            <div className="space-y-3">
              <Input placeholder="Ad Soyad *" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
                className="bg-white/5 border-white/10" data-testid="guest-name-input" />
              <Input placeholder="E-posta" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Input placeholder="Telefon" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Input placeholder="Uyruk" value={form.nationality} onChange={e => setForm({ ...form, nationality: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Input placeholder="Notlar" value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Button onClick={handleCreate} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-guest-btn">
                Kaydet
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Loyalty Stats */}
      {loyaltyStats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="loyalty-stats">
          <div className="glass rounded-xl p-3">
            <p className="text-[10px] text-[#7e7e8a] uppercase">Toplam Misafir</p>
            <p className="text-lg font-bold text-white">{loyaltyStats.total_guests}</p>
          </div>
          <div className="glass rounded-xl p-3">
            <p className="text-[10px] text-[#7e7e8a] uppercase">Tekrar Gelen</p>
            <p className="text-lg font-bold text-green-400">{loyaltyStats.returning_guests}</p>
            <p className="text-[10px] text-[#7e7e8a]">%{loyaltyStats.return_rate} oran</p>
          </div>
          <div className="glass rounded-xl p-3">
            <div className="flex items-center gap-1 mb-1">
              {Object.entries(loyaltyStats.level_counts || {}).map(([level, count]) => {
                const colors = LOYALTY_COLORS[level] || {};
                return count > 0 ? (
                  <Badge key={level} className={`${colors.bg} ${colors.text} text-[10px]`}>{count}</Badge>
                ) : null;
              })}
            </div>
            <p className="text-[10px] text-[#7e7e8a]">Seviye Dagilimi</p>
          </div>
          <div className="glass rounded-xl p-3">
            <p className="text-[10px] text-[#7e7e8a] uppercase">VIP Misafirler</p>
            <div className="flex items-center gap-1 mt-1">
              {(loyaltyStats.top_vips || []).slice(0, 3).map((v, i) => (
                <div key={i} className="w-6 h-6 rounded-full bg-[#C4972A]/20 flex items-center justify-center text-[9px] text-[#C4972A] font-bold" title={v.name}>
                  {v.name?.[0]}
                </div>
              ))}
              {(loyaltyStats.top_vips?.length || 0) > 3 && (
                <span className="text-[10px] text-[#7e7e8a]">+{loyaltyStats.top_vips.length - 3}</span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tabs + Search */}
      <div className="flex items-center gap-3 flex-wrap">
        <Button variant={tab === 'all' ? 'default' : 'ghost'} onClick={() => setTab('all')}
          className={tab === 'all' ? 'bg-[#C4972A] text-white' : 'text-[#7e7e8a]'} data-testid="tab-all">
          <Users className="w-4 h-4 mr-1" /> Tumu
        </Button>
        <Button variant={tab === 'vip' ? 'default' : 'ghost'} onClick={() => setTab('vip')}
          className={tab === 'vip' ? 'bg-[#C4972A] text-white' : 'text-[#7e7e8a]'} data-testid="tab-vip">
          <Crown className="w-4 h-4 mr-1" /> VIP
        </Button>
        <Button variant={tab === 'ai-retargeting' ? 'default' : 'ghost'} 
          onClick={() => { setTab('ai-retargeting'); if(retargetingCampaigns.length===0) loadRetargeting(); }}
          className={tab === 'ai-retargeting' ? 'bg-[#1a1a22] border border-[#C4972A]/50 text-[#C4972A]' : 'text-[#7e7e8a]'} data-testid="tab-ai">
          <Sparkles className="w-4 h-4 mr-1 text-[#C4972A]" /> AI Retargeting
        </Button>
        {tab !== 'ai-retargeting' && (
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#7e7e8a]" />
            <Input placeholder="Misafir ara..." value={search} onChange={e => setSearch(e.target.value)}
              className="pl-10 bg-white/5 border-white/10" data-testid="guest-search" />
          </div>
        )}
      </div>

      {/* Guest List OR AI Retargeting List */}
      <div className="space-y-2">
        {tab === 'ai-retargeting' ? (
           <div className="space-y-4">
              <div className="flex items-center justify-between bg-[#C4972A]/5 border border-[#C4972A]/20 p-4 rounded-xl">
                 <div>
                    <h3 className="text-[#C4972A] font-bold flex items-center gap-2"><Sparkles className="w-5 h-5" /> AI Lifecycle Pazarlamacısı</h3>
                    <p className="text-xs text-[#a9a9b2] mt-1">Eski misafirlerinizi analiz edip onları tekrar getirecek özel e-posta/SMS taslakları oluşturur.</p>
                 </div>
                 <Button onClick={loadRetargeting} disabled={retargetingLoading} className="bg-[#1a1a22] text-[#C4972A] border border-[#C4972A]/30 hover:bg-[#C4972A]/10">
                    {retargetingLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <RefreshCw className="w-4 h-4 mr-2" />}
                    Yeni Kampanyalar Üret
                 </Button>
              </div>

              {retargetingLoading ? (
                 <div className="text-center py-12 text-[#7e7e8a]">
                    <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin text-[#C4972A]" />
                    <p>AI eski rezervasyonları tarıyor ve kişiye özel fırsatlar yazıyor...</p>
                 </div>
              ) : retargetingCampaigns.length > 0 ? (
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {retargetingCampaigns.map((camp, i) => (
                       <div key={i} className="glass rounded-xl p-5 hover:border-[#C4972A]/30 transition-all border border-white/5 relative group">
                          <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                             <Button size="sm" className="h-7 text-xs bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20"><Send className="w-3 h-3 mr-1" /> Gönder</Button>
                          </div>
                          <div className="flex items-center gap-2 mb-3">
                             <div className="w-8 h-8 rounded-full bg-[#C4972A]/10 flex items-center justify-center text-[#C4972A] font-bold text-sm">
                               {camp.guest_name?.[0]}
                             </div>
                             <div>
                                <h4 className="text-sm font-bold text-[#e5e5e8]">{camp.guest_name}</h4>
                                <Badge className="bg-white/5 text-[#a9a9b2] mt-0.5 border-0 text-[10px]">{camp.target_segment}</Badge>
                             </div>
                          </div>
                          <div className="bg-[#1a1a22]/50 rounded-lg p-3 text-sm text-[#e5e5e8] relative">
                             <span className="absolute -top-2 left-3 bg-[#1a1a22] px-1 text-[10px] text-[#C4972A]">{camp.channel} Taslağı</span>
                             <p className="mt-2 text-xs leading-relaxed italic text-[#a9a9b2]">"{camp.message}"</p>
                          </div>
                       </div>
                    ))}
                 </div>
              ) : (
                 <div className="text-center py-12 text-[#7e7e8a]">Henüz oluşturulmuş kampanya yok.</div>
              )}
           </div>
        ) : (
           <>
             {filteredGuests.map(g => {
               const loyalty = getLoyaltyInfo(g);
          const colors = LOYALTY_COLORS[loyalty.level] || {};
          const Icon = LOYALTY_ICONS[loyalty.level] || Award;
          return (
            <div key={g.id}
              onClick={() => openGuestDetail(g)}
              className="glass rounded-xl p-4 flex items-center gap-4 hover:gold-glow transition-all cursor-pointer"
              data-testid={`guest-${g.id}`}>
              <div className="w-10 h-10 rounded-full bg-[#C4972A]/20 flex items-center justify-center text-[#C4972A] font-bold">
                {g.name?.[0] || '?'}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="font-medium truncate">{g.name}</p>
                  {(g.total_stays || 0) > 0 && (
                    <Badge className={`${colors.bg} ${colors.text} text-[10px] border ${colors.border}`}>
                      <Icon className="w-3 h-3 mr-0.5" /> {loyalty.label}
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-3 text-xs text-[#7e7e8a]">
                  {g.phone && <span className="flex items-center gap-1"><Phone className="w-3 h-3" />{g.phone}</span>}
                  {g.email && <span className="flex items-center gap-1"><Mail className="w-3 h-3" />{g.email}</span>}
                  {g.nationality && <span className="flex items-center gap-1"><Globe className="w-3 h-3" />{g.nationality}</span>}
                </div>
              </div>
              <div className="flex items-center gap-3 text-right">
                {(g.total_stays || 0) > 0 && (
                  <div className="text-xs">
                    <p className="text-[#C4972A] font-semibold">{g.total_stays} konaklama</p>
                    {g.total_spent > 0 && <p className="text-[#7e7e8a]">{g.total_spent?.toLocaleString()} TL</p>}
                  </div>
                )}
                {loyalty.discount > 0 && (
                  <Badge className="bg-green-500/15 text-green-400 text-xs">%{loyalty.discount}</Badge>
                )}
                {g.vip && <Badge className="bg-[#C4972A]/20 text-[#C4972A]">VIP</Badge>}
              </div>
            </div>
          );
        })}
        {filteredGuests.length === 0 && !loading && (
          <div className="text-center py-12 text-[#7e7e8a]">
            <Users className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>{tab === 'vip' ? 'Henuz VIP misafir yok' : 'Henuz misafir kaydi yok'}</p>
          </div>
        )}
        </>
        )}
      </div>

      {/* Guest Detail Dialog */}
      <Dialog open={!!detailGuest} onOpenChange={() => { setDetailGuest(null); setLoyaltyDetail(null); }}>
        <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20 max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-[#C4972A] flex items-center gap-2">
              {detailGuest?.name}
              {loyaltyDetail?.loyalty && (
                <Badge className={`${LOYALTY_COLORS[loyaltyDetail.loyalty.level]?.bg} ${LOYALTY_COLORS[loyaltyDetail.loyalty.level]?.text}`}>
                  {loyaltyDetail.loyalty.label}
                </Badge>
              )}
            </DialogTitle>
          </DialogHeader>
          {detailGuest && (
            <div className="space-y-4">
              {/* Contact Info */}
              <div className="grid grid-cols-2 gap-3 text-sm">
                {detailGuest.phone && (
                  <div className="bg-white/3 rounded-lg p-2.5">
                    <p className="text-[10px] text-[#7e7e8a]">Telefon</p>
                    <p className="text-white">{detailGuest.phone}</p>
                  </div>
                )}
                {detailGuest.email && (
                  <div className="bg-white/3 rounded-lg p-2.5">
                    <p className="text-[10px] text-[#7e7e8a]">E-posta</p>
                    <p className="text-white truncate">{detailGuest.email}</p>
                  </div>
                )}
                {detailGuest.nationality && (
                  <div className="bg-white/3 rounded-lg p-2.5">
                    <p className="text-[10px] text-[#7e7e8a]">Uyruk</p>
                    <p className="text-white">{detailGuest.nationality}</p>
                  </div>
                )}
              </div>

              {/* Loyalty Card */}
              {loyaltyDetail?.loyalty && (
                <div className={`rounded-xl p-4 border ${LOYALTY_COLORS[loyaltyDetail.loyalty.level]?.border} ${LOYALTY_COLORS[loyaltyDetail.loyalty.level]?.bg}`}
                  data-testid="loyalty-detail-card">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className={`font-semibold ${LOYALTY_COLORS[loyaltyDetail.loyalty.level]?.text}`}>
                      Sadakat Bilgisi
                    </h4>
                    <Button size="sm" variant="ghost" onClick={() => handleRefreshLoyalty(detailGuest.id)}
                      className="h-7 text-xs text-[#7e7e8a]" data-testid="refresh-loyalty-btn">
                      <RefreshCw className="w-3 h-3 mr-1" /> Guncelle
                    </Button>
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <p className="text-[10px] text-[#7e7e8a]">Konaklama</p>
                      <p className="text-lg font-bold text-white">{loyaltyDetail.loyalty.total_stays}</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-[#7e7e8a]">Toplam Harcama</p>
                      <p className="text-lg font-bold text-white">{(loyaltyDetail.loyalty.total_spent || 0).toLocaleString()} TL</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-[#7e7e8a]">Indirim</p>
                      <p className="text-lg font-bold text-green-400">%{loyaltyDetail.loyalty.discount_percent}</p>
                    </div>
                  </div>
                  {loyaltyDetail.loyalty.next_level && (
                    <div className="mt-3 bg-black/20 rounded-lg p-2 flex items-center gap-2">
                      <ArrowUp className="w-3.5 h-3.5 text-[#C4972A]" />
                      <p className="text-xs text-[#a9a9b2]">
                        <span className="text-[#C4972A] font-medium">{loyaltyDetail.loyalty.next_level.stays_needed} konaklama</span> daha ile{' '}
                        <span className="font-medium text-white">{loyaltyDetail.loyalty.next_level.label}</span> seviyesine ulasin (%{loyaltyDetail.loyalty.next_level.discount} indirim)
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Reservation History */}
              {loyaltyDetail?.reservation_history?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-[#C4972A] mb-2">Konaklama Gecmisi</h4>
                  <div className="space-y-1.5 max-h-40 overflow-y-auto">
                    {loyaltyDetail.reservation_history.map((r, i) => (
                      <div key={i} className="bg-white/3 rounded-lg p-2.5 flex items-center justify-between text-xs">
                        <div>
                          <p className="text-white">{r.room_type || r.room_id || 'Oda'}</p>
                          <p className="text-[#7e7e8a]">{r.check_in?.slice(0, 10)} - {r.check_out?.slice(0, 10)}</p>
                        </div>
                        <div className="text-right">
                          {r.total_price > 0 && <p className="text-[#C4972A] font-medium">{r.total_price?.toLocaleString()} TL</p>}
                          <Badge className={`text-[10px] ${r.status === 'checked_out' ? 'bg-green-500/10 text-green-400' : 'bg-blue-500/10 text-blue-400'}`}>
                            {r.status === 'checked_out' ? 'Tamamlandi' : r.status}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
