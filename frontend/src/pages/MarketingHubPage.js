import React, { useState, useEffect } from 'react';
import {
  getAdAudiences, getAdPerformance,
  createAdCampaign, getAdCampaigns, updateAdCampaignStatus,
  getReputationOverview, analyzeReview, getReputationReviews, getCompetitorComparison,
  addReputationReview,
  getMarketingOverview, getChannelPerformance, getConversionFunnel, getROIReport,
  getGoogleKeywordPlans, getGoogleAdFormats, createGoogleCampaign, getGoogleCampaigns,
  updateGoogleCampaign, addGoogleAd, getGooglePerformance, deleteGoogleCampaign,
  getAIProviders, getAIRouting, testAI
} from '../api';
import { Input } from '../components/ui/input';
import {
  TrendingUp, Target, Star, BarChart3, Loader2, Copy, Plus,
  DollarSign, Eye, MousePointer, ArrowUp, ArrowDown, Minus,
  Globe, Award, AlertCircle, CheckCircle2, Search,
  Zap, PieChart, Users, MessageCircle, Trash2
} from 'lucide-react';

// ==================== STYLES ====================
const card = { background: '#1a1a2e', borderRadius: 12, padding: 20, border: '1px solid #2a2a3e' };
const goldBtn = { background: '#C4972A', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', cursor: 'pointer', fontWeight: 600, fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 6 };
const ghostBtn = { background: 'transparent', color: '#aaa', border: '1px solid #333', borderRadius: 8, padding: '8px 16px', cursor: 'pointer', fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 4 };
const dangerBtn = { ...ghostBtn, borderColor: '#e74c3c40', color: '#e74c3c' };
const pill = (active) => ({
  padding: '6px 14px', borderRadius: 20, fontSize: 12, fontWeight: 600, cursor: 'pointer', border: 'none',
  background: active ? '#C4972A' : '#2a2a3e', color: active ? '#fff' : '#aaa', transition: 'all 0.2s'
});
const statCard = (color = '#C4972A') => ({
  background: `${color}15`, borderRadius: 10, padding: '14px 16px', border: `1px solid ${color}30`,
  display: 'flex', flexDirection: 'column', gap: 4
});
const inputStyle = { background: '#0d0d1a', border: '1px solid #2a2a3e', borderRadius: 8, padding: '8px 12px', color: '#e5e5e8', fontSize: 13, width: '100%' };
const selectStyle = { ...inputStyle, cursor: 'pointer' };

// ==================== HELPER COMPONENTS ====================
const StatBox = ({ label, value, icon: Icon, color = '#C4972A', suffix = '', trend }) => (
  <div style={statCard(color)}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span style={{ fontSize: 11, color: '#888' }}>{label}</span>
      {Icon && <Icon size={14} color={color} />}
    </div>
    <div style={{ display: 'flex', alignItems: 'baseline', gap: 4 }}>
      <span style={{ fontSize: 22, fontWeight: 700, color }}>{value}</span>
      {suffix && <span style={{ fontSize: 11, color: '#666' }}>{suffix}</span>}
    </div>
    {trend !== undefined && (
      <span style={{ fontSize: 11, color: trend > 0 ? '#8FAA86' : trend < 0 ? '#e74c3c' : '#888' }}>
        {trend > 0 ? <ArrowUp size={10} /> : trend < 0 ? <ArrowDown size={10} /> : <Minus size={10} />}
        {' '}{Math.abs(trend)}% bu ay
      </span>
    )}
  </div>
);

const TabButton = ({ active, onClick, icon: Icon, label }) => (
  <button onClick={onClick} style={{
    display: 'flex', alignItems: 'center', gap: 6, padding: '10px 18px', borderRadius: 10,
    background: active ? '#C4972A20' : 'transparent', color: active ? '#C4972A' : '#888',
    border: active ? '1px solid #C4972A40' : '1px solid transparent', cursor: 'pointer',
    fontWeight: active ? 700 : 400, fontSize: 13, transition: 'all 0.2s'
  }}>
    <Icon size={16} /> {label}
  </button>
);

const StatusBadge = ({ status }) => {
  const colors = { active: '#8FAA86', paused: '#C4972A', draft: '#7e7e8a', completed: '#3498db' };
  const labels = { active: 'Aktif', paused: 'Durduruldu', draft: 'Taslak', completed: 'Tamamlandi' };
  const c = colors[status] || '#7e7e8a';
  return (
    <span style={{ fontSize: 11, padding: '3px 10px', borderRadius: 12, fontWeight: 600, background: `${c}20`, color: c }}>
      {labels[status] || status}
    </span>
  );
};

// ==================== META ADS TAB ====================
function MetaAdsTab() {
  const [audiences, setAudiences] = useState({});
  const [campaigns, setCampaigns] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newCampaign, setNewCampaign] = useState({ name: '', objective: 'awareness', segment: 'weekend_getaway', platform: 'both', budget_daily: 50 });

  useEffect(() => {
    Promise.all([
      getAdAudiences().catch(() => ({ data: { audiences: {} } })),
      getAdCampaigns().catch(() => ({ data: { campaigns: [] } })),
      getAdPerformance().catch(() => ({ data: {} })),
    ]).then(([audRes, campRes, perfRes]) => {
      setAudiences(audRes.data.audiences || {});
      setCampaigns(campRes.data.campaigns || []);
      setPerformance(perfRes.data);
      setLoading(false);
    });
  }, []);

  const handleCreateCampaign = async () => {
    if (!newCampaign.name) return;
    try {
      const res = await createAdCampaign(newCampaign);
      setCampaigns(prev => [res.data, ...prev]);
      setShowCreate(false);
      setNewCampaign({ name: '', objective: 'awareness', segment: 'weekend_getaway', platform: 'both', budget_daily: 50 });
    } catch (e) { console.error(e); }
  };

  const handleStatusChange = async (id, status) => {
    try {
      await updateAdCampaignStatus({ campaign_id: id, status });
      setCampaigns(prev => prev.map(c => c.id === id ? { ...c, status } : c));
    } catch (e) { console.error(e); }
  };

  if (loading) return <div style={{ padding: 40, textAlign: 'center' }}><Loader2 className="animate-spin" size={24} /></div>;

  const summary = performance?.summary;
  const segmentLabels = { wedding: 'Dugun', weekend_getaway: 'Tatil', foodie: 'Gastronomi', corporate: 'Kurumsal', romantic: 'Romantik' };
  const objectiveLabels = { awareness: 'Farkindalik', traffic: 'Trafik', conversions: 'Donusum', engagement: 'Etkilesim' };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {summary && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12 }}>
          <StatBox label="Toplam Harcama" value={`${summary.total_spend} TL`} icon={DollarSign} color="#e74c3c" />
          <StatBox label="Gosterim" value={summary.total_impressions?.toLocaleString()} icon={Eye} color="#3498db" />
          <StatBox label="Tiklama" value={summary.total_clicks?.toLocaleString()} icon={MousePointer} color="#C4972A" />
          <StatBox label="Donusum" value={summary.total_conversions} icon={Target} color="#8FAA86" />
          <StatBox label="CTR" value={`%${summary.ctr}`} icon={TrendingUp} color="#9b59b6" />
          <StatBox label="ROAS" value={`${summary.roas}x`} icon={Zap} color="#f39c12" />
        </div>
      )}

      {/* Create Campaign */}
      <div style={card}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h3 style={{ color: '#C4972A', fontSize: 15, margin: 0 }}>
            <Target size={16} style={{ marginRight: 6 }} />Meta Kampanyalar
          </h3>
          <button onClick={() => setShowCreate(!showCreate)} style={goldBtn}>
            <Plus size={14} /> Yeni Kampanya
          </button>
        </div>

        {showCreate && (
          <div style={{ background: '#0d0d1a', borderRadius: 8, padding: 16, marginBottom: 12 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 10 }}>
              <Input placeholder="Kampanya adi" value={newCampaign.name} onChange={e => setNewCampaign({ ...newCampaign, name: e.target.value })} />
              <Input type="number" placeholder="Gunluk butce (TL)" value={newCampaign.budget_daily} onChange={e => setNewCampaign({ ...newCampaign, budget_daily: Number(e.target.value) })} />
            </div>
            <div style={{ marginBottom: 10 }}>
              <span style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 4 }}>Hedef</span>
              <div style={{ display: 'flex', gap: 6 }}>
                {Object.entries(objectiveLabels).map(([k, v]) => (
                  <button key={k} onClick={() => setNewCampaign({ ...newCampaign, objective: k })} style={pill(newCampaign.objective === k)}>{v}</button>
                ))}
              </div>
            </div>
            <div style={{ marginBottom: 10 }}>
              <span style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 4 }}>Segment</span>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {Object.entries(segmentLabels).map(([k, v]) => (
                  <button key={k} onClick={() => setNewCampaign({ ...newCampaign, segment: k })} style={pill(newCampaign.segment === k)}>{v}</button>
                ))}
              </div>
            </div>
            <div style={{ marginBottom: 10 }}>
              <span style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 4 }}>Platform</span>
              <div style={{ display: 'flex', gap: 6 }}>
                {['both', 'facebook', 'instagram'].map(p => (
                  <button key={p} onClick={() => setNewCampaign({ ...newCampaign, platform: p })} style={pill(newCampaign.platform === p)}>
                    {p === 'both' ? 'Her Ikisi' : p.charAt(0).toUpperCase() + p.slice(1)}
                  </button>
                ))}
              </div>
            </div>
            {audiences[newCampaign.segment] && (
              <div style={{ background: '#1a1a2e', borderRadius: 6, padding: 10, marginBottom: 10, fontSize: 12, color: '#888' }}>
                Hedef: {audiences[newCampaign.segment].demographics} | Yas: {audiences[newCampaign.segment].age_range} | Butce onerisi: {audiences[newCampaign.segment].budget_suggestion}
              </div>
            )}
            <button onClick={handleCreateCampaign} disabled={!newCampaign.name} style={goldBtn}>Olustur</button>
          </div>
        )}

        {campaigns.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 30, color: '#666' }}>Henuz kampanya yok</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {campaigns.map(camp => (
              <div key={camp.id} style={{ background: '#0d0d1a', borderRadius: 8, padding: 14, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 600, color: '#e5e5e8', fontSize: 14 }}>{camp.name}</div>
                  <div style={{ fontSize: 12, color: '#888', marginTop: 2 }}>
                    {objectiveLabels[camp.objective] || camp.objective} | {camp.budget_daily} TL/gun | {camp.platform}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                  <StatusBadge status={camp.status} />
                  {camp.status === 'draft' && <button onClick={() => handleStatusChange(camp.id, 'active')} style={{ ...ghostBtn, padding: '4px 8px', fontSize: 11 }}>Baslat</button>}
                  {camp.status === 'active' && <button onClick={() => handleStatusChange(camp.id, 'paused')} style={{ ...ghostBtn, padding: '4px 8px', fontSize: 11 }}>Durdur</button>}
                  {camp.status === 'paused' && <button onClick={() => handleStatusChange(camp.id, 'active')} style={{ ...ghostBtn, padding: '4px 8px', fontSize: 11 }}>Devam</button>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Campaign Performance */}
      {performance?.campaigns && (
        <div style={card}>
          <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>
            <BarChart3 size={16} style={{ marginRight: 6 }} />Performans
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {performance.campaigns.map(c => (
              <div key={c.id} style={{ background: '#0d0d1a', borderRadius: 8, padding: 14 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ fontWeight: 600, color: '#e5e5e8', fontSize: 13 }}>{c.name}</span>
                  <StatusBadge status={c.status} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 8, fontSize: 12 }}>
                  <div><span style={{ color: '#666' }}>Harcama</span><br /><span style={{ color: '#e74c3c', fontWeight: 600 }}>{c.spend} TL</span></div>
                  <div><span style={{ color: '#666' }}>Gosterim</span><br /><span style={{ color: '#3498db', fontWeight: 600 }}>{c.impressions?.toLocaleString()}</span></div>
                  <div><span style={{ color: '#666' }}>Tiklama</span><br /><span style={{ color: '#C4972A', fontWeight: 600 }}>{c.clicks}</span></div>
                  <div><span style={{ color: '#666' }}>Donusum</span><br /><span style={{ color: '#8FAA86', fontWeight: 600 }}>{c.conversions}</span></div>
                  <div><span style={{ color: '#666' }}>CTR</span><br /><span style={{ color: '#9b59b6', fontWeight: 600 }}>%{c.ctr}</span></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ==================== GOOGLE ADS TAB ====================
function GoogleAdsTab() {
  const [campaigns, setCampaigns] = useState([]);
  const [keywordPlans, setKeywordPlans] = useState({});
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showAddAd, setShowAddAd] = useState(null); // campaign_id
  const [newCampaign, setNewCampaign] = useState({ name: '', campaign_type: 'search', keyword_plan: 'otel', budget_daily: 50, bid_strategy: 'maximize_clicks' });
  const [newAd, setNewAd] = useState({ headline1: '', headline2: '', headline3: '', description1: '', description2: '', final_url: 'https://kozbeylikonagi.com', path1: '', path2: '' });

  useEffect(() => {
    Promise.all([
      getGoogleCampaigns().catch(() => ({ data: { campaigns: [] } })),
      getGoogleKeywordPlans().catch(() => ({ data: { plans: {} } })),
      getGooglePerformance().catch(() => ({ data: {} })),
    ]).then(([campRes, kwRes, perfRes]) => {
      setCampaigns(campRes.data.campaigns || []);
      setKeywordPlans(kwRes.data.plans || {});
      setPerformance(perfRes.data);
      setLoading(false);
    });
  }, []);

  const handleCreate = async () => {
    if (!newCampaign.name) return;
    try {
      const res = await createGoogleCampaign(newCampaign);
      setCampaigns(prev => [res.data, ...prev]);
      setShowCreate(false);
      setNewCampaign({ name: '', campaign_type: 'search', keyword_plan: 'otel', budget_daily: 50, bid_strategy: 'maximize_clicks' });
    } catch (e) { console.error(e); }
  };

  const handleStatusChange = async (id, status) => {
    try {
      await updateGoogleCampaign({ campaign_id: id, status });
      setCampaigns(prev => prev.map(c => c.id === id ? { ...c, status } : c));
    } catch (e) { console.error(e); }
  };

  const handleAddAd = async (campaignId) => {
    try {
      await addGoogleAd({ campaign_id: campaignId, ...newAd });
      // Refresh campaigns
      const res = await getGoogleCampaigns();
      setCampaigns(res.data.campaigns || []);
      setShowAddAd(null);
      setNewAd({ headline1: '', headline2: '', headline3: '', description1: '', description2: '', final_url: 'https://kozbeylikonagi.com', path1: '', path2: '' });
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id) => {
    try {
      await deleteGoogleCampaign(id);
      setCampaigns(prev => prev.filter(c => c.id !== id));
    } catch (e) { console.error(e); }
  };

  if (loading) return <div style={{ padding: 40, textAlign: 'center' }}><Loader2 className="animate-spin" size={24} /></div>;

  const summary = performance?.summary;
  const typeLabels = { search: 'Arama', display: 'Goruntulu', local: 'Yerel' };
  const planLabels = { otel: 'Otel & Konaklama', dugun: 'Dugun & Organizasyon', restoran: 'Restoran & Yemek', kurumsal: 'Kurumsal Etkinlik' };
  const bidLabels = { maximize_clicks: 'Max Tiklama', target_cpa: 'Hedef CPA', manual_cpc: 'Manuel CPC' };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Performance Summary */}
      {summary && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12 }}>
          <StatBox label="Toplam Harcama" value={`${summary.total_spend} TL`} icon={DollarSign} color="#e74c3c" />
          <StatBox label="Gosterim" value={summary.total_impressions?.toLocaleString()} icon={Eye} color="#3498db" />
          <StatBox label="Tiklama" value={summary.total_clicks?.toLocaleString()} icon={MousePointer} color="#C4972A" />
          <StatBox label="Donusum" value={summary.total_conversions} icon={Target} color="#8FAA86" />
          <StatBox label="Ort. CPC" value={`${summary.avg_cpc} TL`} icon={DollarSign} color="#9b59b6" />
          <StatBox label="Kalite Skoru" value={summary.quality_score_avg} icon={Star} color="#f39c12" suffix="/10" />
        </div>
      )}

      {/* Campaign Type Performance */}
      {performance?.by_campaign_type && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 12 }}>
          {Object.entries(performance.by_campaign_type).map(([type, data]) => (
            <div key={type} style={card}>
              <h4 style={{ color: '#C4972A', marginBottom: 8, fontSize: 13 }}>{typeLabels[type] || type} Reklamlar</h4>
              <div style={{ fontSize: 12, display: 'flex', flexDirection: 'column', gap: 4 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#888' }}>Gosterim</span><span style={{ color: '#e5e5e8' }}>{data.impressions?.toLocaleString()}</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#888' }}>Tiklama</span><span style={{ color: '#e5e5e8' }}>{data.clicks?.toLocaleString()}</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#888' }}>Harcama</span><span style={{ color: '#e74c3c' }}>{data.spend} TL</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#888' }}>CTR</span><span style={{ color: '#8FAA86' }}>%{data.ctr}</span></div>
                {data.calls && <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#888' }}>Arama</span><span style={{ color: '#C4972A' }}>{data.calls}</span></div>}
                {data.directions && <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#888' }}>Yol Tarifi</span><span style={{ color: '#C4972A' }}>{data.directions}</span></div>}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Top Keywords */}
      {performance?.top_keywords && (
        <div style={card}>
          <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>En Iyi Anahtar Kelimeler</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {performance.top_keywords.map((kw, i) => (
              <div key={i} style={{ background: '#0d0d1a', borderRadius: 8, padding: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#e5e5e8', fontWeight: 600, fontSize: 13 }}>"{kw.keyword}"</span>
                <div style={{ display: 'flex', gap: 16, fontSize: 12 }}>
                  <span style={{ color: '#3498db' }}>{kw.impressions} gosterim</span>
                  <span style={{ color: '#C4972A' }}>{kw.clicks} tiklama</span>
                  <span style={{ color: '#8FAA86' }}>%{kw.ctr} CTR</span>
                  <span style={{ color: '#e74c3c' }}>{kw.avg_cpc} TL CPC</span>
                  <span style={{ color: '#f39c12' }}>Kalite: {kw.quality_score}/10</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Campaigns */}
      <div style={card}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h3 style={{ color: '#C4972A', fontSize: 15, margin: 0 }}>
            <Target size={16} style={{ marginRight: 6 }} />Google Kampanyalar
          </h3>
          <button onClick={() => setShowCreate(!showCreate)} style={goldBtn}>
            <Plus size={14} /> Yeni Kampanya
          </button>
        </div>

        {showCreate && (
          <div style={{ background: '#0d0d1a', borderRadius: 8, padding: 16, marginBottom: 12 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 10 }}>
              <Input placeholder="Kampanya adi" value={newCampaign.name} onChange={e => setNewCampaign({ ...newCampaign, name: e.target.value })} />
              <Input type="number" placeholder="Gunluk butce (TL)" value={newCampaign.budget_daily} onChange={e => setNewCampaign({ ...newCampaign, budget_daily: Number(e.target.value) })} />
            </div>
            <div style={{ marginBottom: 10 }}>
              <span style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 4 }}>Kampanya Turu</span>
              <div style={{ display: 'flex', gap: 6 }}>
                {Object.entries(typeLabels).map(([k, v]) => (
                  <button key={k} onClick={() => setNewCampaign({ ...newCampaign, campaign_type: k })} style={pill(newCampaign.campaign_type === k)}>{v}</button>
                ))}
              </div>
            </div>
            <div style={{ marginBottom: 10 }}>
              <span style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 4 }}>Anahtar Kelime Plani</span>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {Object.entries(planLabels).map(([k, v]) => (
                  <button key={k} onClick={() => setNewCampaign({ ...newCampaign, keyword_plan: k })} style={pill(newCampaign.keyword_plan === k)}>{v}</button>
                ))}
              </div>
            </div>
            {keywordPlans[newCampaign.keyword_plan] && (
              <div style={{ background: '#1a1a2e', borderRadius: 6, padding: 10, marginBottom: 10, fontSize: 12 }}>
                <span style={{ color: '#888' }}>Anahtar kelimeler: </span>
                <span style={{ color: '#C4972A' }}>
                  {keywordPlans[newCampaign.keyword_plan].keywords?.map(k => k.keyword).join(', ')}
                </span>
              </div>
            )}
            <div style={{ marginBottom: 10 }}>
              <span style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 4 }}>Teklif Stratejisi</span>
              <div style={{ display: 'flex', gap: 6 }}>
                {Object.entries(bidLabels).map(([k, v]) => (
                  <button key={k} onClick={() => setNewCampaign({ ...newCampaign, bid_strategy: k })} style={pill(newCampaign.bid_strategy === k)}>{v}</button>
                ))}
              </div>
            </div>
            <button onClick={handleCreate} disabled={!newCampaign.name} style={goldBtn}>Olustur</button>
          </div>
        )}

        {campaigns.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 30, color: '#666' }}>Henuz kampanya yok</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {campaigns.map(camp => (
              <div key={camp.id} style={{ background: '#0d0d1a', borderRadius: 8, padding: 14 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <div>
                    <div style={{ fontWeight: 600, color: '#e5e5e8', fontSize: 14 }}>{camp.name}</div>
                    <div style={{ fontSize: 12, color: '#888', marginTop: 2 }}>
                      {typeLabels[camp.campaign_type] || camp.campaign_type} | {camp.budget_daily} TL/gun | {bidLabels[camp.bid_strategy] || camp.bid_strategy}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                    <StatusBadge status={camp.status} />
                    {camp.status === 'draft' && <button onClick={() => handleStatusChange(camp.id, 'active')} style={{ ...ghostBtn, padding: '4px 8px', fontSize: 11 }}>Baslat</button>}
                    {camp.status === 'active' && <button onClick={() => handleStatusChange(camp.id, 'paused')} style={{ ...ghostBtn, padding: '4px 8px', fontSize: 11 }}>Durdur</button>}
                    {camp.status === 'paused' && <button onClick={() => handleStatusChange(camp.id, 'active')} style={{ ...ghostBtn, padding: '4px 8px', fontSize: 11 }}>Devam</button>}
                    <button onClick={() => handleDelete(camp.id)} style={{ ...dangerBtn, padding: '4px 8px', fontSize: 11 }}><Trash2 size={12} /></button>
                  </div>
                </div>

                {/* Keywords */}
                {camp.keywords && camp.keywords.length > 0 && (
                  <div style={{ marginBottom: 8 }}>
                    <span style={{ fontSize: 11, color: '#666' }}>Anahtar Kelimeler:</span>
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 4 }}>
                      {camp.keywords.map((kw, i) => (
                        <span key={i} style={{ fontSize: 11, padding: '2px 8px', borderRadius: 8, background: '#2a2a3e', color: '#aaa' }}>
                          {kw.keyword} <span style={{ color: '#666' }}>({kw.match_type})</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Ads */}
                {camp.ads && camp.ads.length > 0 && (
                  <div style={{ marginBottom: 8 }}>
                    <span style={{ fontSize: 11, color: '#666' }}>Reklamlar ({camp.ads.length}):</span>
                    {camp.ads.map((ad, i) => (
                      <div key={i} style={{ background: '#1a1a2e', borderRadius: 6, padding: 8, marginTop: 4, fontSize: 12 }}>
                        <div style={{ color: '#3498db', fontWeight: 600 }}>{ad.headline1}{ad.headline2 ? ` | ${ad.headline2}` : ''}{ad.headline3 ? ` | ${ad.headline3}` : ''}</div>
                        <div style={{ color: '#8FAA86', fontSize: 11 }}>{ad.final_url}{ad.path1 ? `/${ad.path1}` : ''}{ad.path2 ? `/${ad.path2}` : ''}</div>
                        <div style={{ color: '#aaa', marginTop: 2 }}>{ad.description1}</div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Add Ad Button */}
                {showAddAd === camp.id ? (
                  <div style={{ background: '#1a1a2e', borderRadius: 8, padding: 12, marginTop: 8 }}>
                    <div style={{ fontSize: 12, color: '#C4972A', fontWeight: 600, marginBottom: 8 }}>Yeni Reklam Ekle (max 30 karakter baslik, 90 karakter aciklama)</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 6, marginBottom: 6 }}>
                      <input placeholder="Baslik 1 (30 kar.)" maxLength={30} value={newAd.headline1} onChange={e => setNewAd({ ...newAd, headline1: e.target.value })} style={inputStyle} />
                      <input placeholder="Baslik 2 (30 kar.)" maxLength={30} value={newAd.headline2} onChange={e => setNewAd({ ...newAd, headline2: e.target.value })} style={inputStyle} />
                      <input placeholder="Baslik 3 (30 kar.)" maxLength={30} value={newAd.headline3} onChange={e => setNewAd({ ...newAd, headline3: e.target.value })} style={inputStyle} />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6, marginBottom: 6 }}>
                      <input placeholder="Aciklama 1 (90 kar.)" maxLength={90} value={newAd.description1} onChange={e => setNewAd({ ...newAd, description1: e.target.value })} style={inputStyle} />
                      <input placeholder="Aciklama 2 (90 kar.)" maxLength={90} value={newAd.description2} onChange={e => setNewAd({ ...newAd, description2: e.target.value })} style={inputStyle} />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 6, marginBottom: 8 }}>
                      <input placeholder="URL" value={newAd.final_url} onChange={e => setNewAd({ ...newAd, final_url: e.target.value })} style={inputStyle} />
                      <input placeholder="Yol 1" maxLength={15} value={newAd.path1} onChange={e => setNewAd({ ...newAd, path1: e.target.value })} style={inputStyle} />
                      <input placeholder="Yol 2" maxLength={15} value={newAd.path2} onChange={e => setNewAd({ ...newAd, path2: e.target.value })} style={inputStyle} />
                    </div>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button onClick={() => handleAddAd(camp.id)} disabled={!newAd.headline1} style={goldBtn}>Ekle</button>
                      <button onClick={() => setShowAddAd(null)} style={ghostBtn}>Iptal</button>
                    </div>
                  </div>
                ) : (
                  <button onClick={() => setShowAddAd(camp.id)} style={{ ...ghostBtn, padding: '4px 10px', fontSize: 11, marginTop: 4 }}>
                    <Plus size={12} /> Reklam Ekle
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ==================== REPUTATION TAB ====================
function ReputationTab() {
  const [overview, setOverview] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [competitors, setCompetitors] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzeText, setAnalyzeText] = useState('');
  const [analyzeResult, setAnalyzeResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [platformFilter, setPlatformFilter] = useState('all');
  const [showAddReview, setShowAddReview] = useState(false);
  const [newReview, setNewReview] = useState({ platform: 'google', author: '', rating: 5, text: '' });

  useEffect(() => {
    Promise.all([
      getReputationOverview().catch(() => ({ data: {} })),
      getReputationReviews().catch(() => ({ data: { reviews: [] } })),
      getCompetitorComparison().catch(() => ({ data: {} })),
    ]).then(([ovRes, revRes, compRes]) => {
      setOverview(ovRes.data);
      setReviews(revRes.data.reviews || []);
      setCompetitors(compRes.data);
      setLoading(false);
    });
  }, []);

  const handleAnalyze = async () => {
    if (!analyzeText.trim()) return;
    setAnalyzing(true);
    try {
      const res = await analyzeReview({ text: analyzeText, platform: 'google', rating: 5 });
      setAnalyzeResult(res.data);
    } catch (e) { console.error(e); }
    setAnalyzing(false);
  };

  const handleAddReview = async () => {
    try {
      const res = await addReputationReview(newReview);
      setReviews(prev => [res.data, ...prev]);
      setShowAddReview(false);
      setNewReview({ platform: 'google', author: '', rating: 5, text: '' });
    } catch (e) { console.error(e); }
  };

  if (loading) return <div style={{ padding: 40, textAlign: 'center' }}><Loader2 className="animate-spin" size={24} /></div>;

  const platforms = overview?.platforms || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {overview && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
            <StatBox label="Genel Puan" value={overview.overall_score} icon={Star} color="#f39c12" suffix="/ 5" />
            <StatBox label="Toplam Degerlendirme" value={overview.total_reviews} icon={MessageCircle} color="#3498db" />
            <StatBox label="Pozitif" value={`%${overview.sentiment_distribution?.positive}`} icon={CheckCircle2} color="#8FAA86" />
            <StatBox label="Negatif" value={`%${overview.sentiment_distribution?.negative}`} icon={AlertCircle} color="#e74c3c" />
          </div>

          {/* Platform Ratings */}
          <div style={card}>
            <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>
              <Globe size={16} style={{ marginRight: 6 }} />Platform Puanlari
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
              {[
                { key: 'google', name: 'Google', color: '#4285F4', field: 'rating' },
                { key: 'tripadvisor', name: 'TripAdvisor', color: '#00AF87', field: 'rating' },
                { key: 'booking', name: 'Booking.com', color: '#003580', field: 'rating' },
                { key: 'instagram', name: 'Instagram', color: '#E4405F', field: 'mentions' },
              ].filter(p => platforms[p.key]).map(p => (
                <div key={p.key} style={{ background: '#0d0d1a', borderRadius: 8, padding: 14 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: p.color }} />
                    <span style={{ fontWeight: 600, color: '#e5e5e8', fontSize: 13 }}>{p.name}</span>
                  </div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: p.color }}>
                    {platforms[p.key][p.field]} {p.field === 'rating' && <Star size={14} fill={p.color} />}
                  </div>
                  <div style={{ fontSize: 11, color: '#888' }}>
                    {platforms[p.key].review_count ? `${platforms[p.key].review_count} degerlendirme` : ''}
                    {platforms[p.key].response_rate ? ` | Yanit: %${platforms[p.key].response_rate}` : ''}
                    {platforms[p.key].engagement_rate ? `Etkilesim: %${platforms[p.key].engagement_rate}` : ''}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Category Scores */}
          {overview.top_categories && (
            <div style={card}>
              <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>Kategori Puanlari</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {Object.entries(overview.top_categories).map(([cat, score]) => (
                  <div key={cat} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{ width: 100, fontSize: 13, color: '#aaa', textTransform: 'capitalize' }}>{cat.replace('_', ' ')}</span>
                    <div style={{ flex: 1, height: 6, background: '#2a2a3e', borderRadius: 3 }}>
                      <div style={{ width: `${(score / 5) * 100}%`, height: '100%', background: score >= 4.5 ? '#8FAA86' : score >= 4 ? '#C4972A' : '#e74c3c', borderRadius: 3 }} />
                    </div>
                    <span style={{ fontSize: 13, fontWeight: 600, color: score >= 4.5 ? '#8FAA86' : score >= 4 ? '#C4972A' : '#e74c3c', width: 30 }}>{score}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Review Analyzer */}
      <div style={card}>
        <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>
          <Search size={16} style={{ marginRight: 6 }} />Degerlendirme Analizi
        </h3>
        <textarea value={analyzeText} onChange={e => setAnalyzeText(e.target.value)}
          placeholder="Analiz etmek istediginiz degerlendirme metnini yapin..."
          style={{ width: '100%', minHeight: 80, background: '#0d0d1a', border: '1px solid #2a2a3e', borderRadius: 8, padding: 12, color: '#e5e5e8', fontSize: 13, resize: 'vertical' }} />
        <button onClick={handleAnalyze} disabled={analyzing || !analyzeText.trim()} style={{ ...goldBtn, marginTop: 8 }}>
          {analyzing ? <><Loader2 className="animate-spin" size={14} /> Analiz Ediliyor...</> : <><Search size={14} /> Analiz Et</>}
        </button>
        {analyzeResult && (
          <div style={{ marginTop: 12, background: '#0d0d1a', borderRadius: 8, padding: 14 }}>
            <span style={{ fontSize: 12, color: '#888' }}>Duygu: </span>
            <span style={{
              fontSize: 12, fontWeight: 600, padding: '2px 8px', borderRadius: 10,
              background: analyzeResult.basic_analysis?.sentiment === 'positive' ? '#8FAA8620' : analyzeResult.basic_analysis?.sentiment === 'negative' ? '#e74c3c20' : '#C4972A20',
              color: analyzeResult.basic_analysis?.sentiment === 'positive' ? '#8FAA86' : analyzeResult.basic_analysis?.sentiment === 'negative' ? '#e74c3c' : '#C4972A',
            }}>
              {analyzeResult.basic_analysis?.sentiment === 'positive' ? 'Pozitif' : analyzeResult.basic_analysis?.sentiment === 'negative' ? 'Negatif' : 'Notr'}
            </span>
            <span style={{ fontSize: 12, color: '#888', marginLeft: 8 }}>Skor: {analyzeResult.basic_analysis?.score}/10</span>
            {analyzeResult.ai_analysis && (
              <pre style={{ color: '#ccc', fontSize: 12, whiteSpace: 'pre-wrap', lineHeight: 1.6, fontFamily: 'inherit', marginTop: 8 }}>
                {analyzeResult.ai_analysis}
              </pre>
            )}
          </div>
        )}
      </div>

      {/* Reviews List */}
      <div style={card}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h3 style={{ color: '#C4972A', fontSize: 15, margin: 0 }}>Degerlendirmeler</h3>
          <button onClick={() => setShowAddReview(!showAddReview)} style={goldBtn}><Plus size={14} /> Ekle</button>
        </div>

        {showAddReview && (
          <div style={{ background: '#0d0d1a', borderRadius: 8, padding: 14, marginBottom: 12 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 80px', gap: 8, marginBottom: 8 }}>
              <select value={newReview.platform} onChange={e => setNewReview({ ...newReview, platform: e.target.value })} style={selectStyle}>
                <option value="google">Google</option>
                <option value="tripadvisor">TripAdvisor</option>
                <option value="booking">Booking.com</option>
                <option value="instagram">Instagram</option>
              </select>
              <Input placeholder="Yazar" value={newReview.author} onChange={e => setNewReview({ ...newReview, author: e.target.value })} />
              <Input type="number" min={1} max={5} value={newReview.rating} onChange={e => setNewReview({ ...newReview, rating: Number(e.target.value) })} />
            </div>
            <textarea value={newReview.text} onChange={e => setNewReview({ ...newReview, text: e.target.value })}
              placeholder="Degerlendirme metni..." style={{ width: '100%', minHeight: 60, background: '#1a1a2e', border: '1px solid #2a2a3e', borderRadius: 8, padding: 10, color: '#e5e5e8', fontSize: 13, resize: 'vertical', marginBottom: 8 }} />
            <button onClick={handleAddReview} disabled={!newReview.text.trim()} style={goldBtn}>Kaydet</button>
          </div>
        )}

        <div style={{ display: 'flex', gap: 6, marginBottom: 12, flexWrap: 'wrap' }}>
          {['all', 'google', 'tripadvisor', 'booking', 'instagram'].map(p => (
            <button key={p} onClick={() => setPlatformFilter(p)} style={pill(platformFilter === p)}>
              {p === 'all' ? 'Tumu' : p === 'tripadvisor' ? 'TripAdvisor' : p === 'booking' ? 'Booking.com' : p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>

        {reviews.filter(r => platformFilter === 'all' || r.platform === platformFilter).length === 0 ? (
          <div style={{ textAlign: 'center', padding: 30, color: '#666' }}>Degerlendirme bulunamadi</div>
        ) : (
          reviews.filter(r => platformFilter === 'all' || r.platform === platformFilter).map(rev => (
            <div key={rev.id} style={{ background: '#0d0d1a', borderRadius: 8, padding: 12, marginBottom: 8 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ fontWeight: 600, color: '#e5e5e8', fontSize: 13 }}>{rev.author}</span>
                  <span style={{ fontSize: 11, color: '#888', background: '#2a2a3e', padding: '1px 6px', borderRadius: 6 }}>{rev.platform}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  {Array.from({ length: rev.rating }).map((_, i) => <Star key={i} size={12} fill="#f39c12" color="#f39c12" />)}
                </div>
              </div>
              <p style={{ color: '#aaa', fontSize: 12, lineHeight: 1.5, margin: 0 }}>{rev.text}</p>
              {rev.sentiment && (
                <span style={{
                  fontSize: 10, padding: '2px 6px', borderRadius: 8, marginTop: 4, display: 'inline-block',
                  background: rev.sentiment === 'positive' ? '#8FAA8620' : rev.sentiment === 'negative' ? '#e74c3c20' : '#C4972A20',
                  color: rev.sentiment === 'positive' ? '#8FAA86' : rev.sentiment === 'negative' ? '#e74c3c' : '#C4972A',
                }}>{rev.sentiment}</span>
              )}
            </div>
          ))
        )}
      </div>

      {/* Competitor Comparison */}
      {competitors?.our_hotel && (
        <div style={card}>
          <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>
            <Award size={16} style={{ marginRight: 6 }} />Rakip Karsilastirma
          </h3>
          <div style={{ background: '#0d0d1a', borderRadius: 8, padding: 14, marginBottom: 8 }}>
            <div style={{ fontWeight: 700, color: '#C4972A', fontSize: 14 }}>{competitors.our_hotel.name}</div>
            <div style={{ fontSize: 13, color: '#e5e5e8', marginTop: 4 }}>Google: {competitors.our_hotel.google_rating} | {competitors.our_hotel.review_count} yorum</div>
            <div style={{ fontSize: 12, color: '#8FAA86', marginTop: 2 }}>Guclu: {competitors.our_hotel.strengths?.join(', ')}</div>
          </div>
          {competitors.competitors?.map((comp, i) => (
            <div key={i} style={{ background: '#0d0d1a', borderRadius: 8, padding: 12, marginBottom: 6 }}>
              <div style={{ fontWeight: 600, color: '#aaa', fontSize: 13 }}>{comp.name}</div>
              <div style={{ fontSize: 12, color: '#888' }}>Google: {comp.google_rating} | {comp.review_count} yorum</div>
              <div style={{ fontSize: 11, color: '#C4972A', marginTop: 2 }}>{comp.comparison}</div>
            </div>
          ))}
          <div style={{ marginTop: 8, fontSize: 12, color: '#8FAA86', fontStyle: 'italic' }}>{competitors.market_position}</div>
        </div>
      )}
    </div>
  );
}

// ==================== ANALYTICS TAB ====================
function AnalyticsTab() {
  const [overview, setOverview] = useState(null);
  const [channels, setChannels] = useState(null);
  const [funnel, setFunnel] = useState(null);
  const [roi, setROI] = useState(null);
  const [loading, setLoading] = useState(true);
  const [subTab, setSubTab] = useState('overview');

  useEffect(() => {
    Promise.all([
      getMarketingOverview().catch(() => ({ data: {} })),
      getChannelPerformance().catch(() => ({ data: {} })),
      getConversionFunnel().catch(() => ({ data: {} })),
      getROIReport().catch(() => ({ data: {} })),
    ]).then(([ovRes, chRes, fnRes, roiRes]) => {
      setOverview(ovRes.data.overview);
      setChannels(chRes.data.channels);
      setFunnel(fnRes.data.funnel);
      setROI(roiRes.data);
      setLoading(false);
    });
  }, []);

  if (loading) return <div style={{ padding: 40, textAlign: 'center' }}><Loader2 className="animate-spin" size={24} /></div>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        {[
          { id: 'overview', label: 'Genel Bakis', icon: PieChart },
          { id: 'channels', label: 'Kanallar', icon: BarChart3 },
          { id: 'funnel', label: 'Donusum Hunisi', icon: Target },
          { id: 'roi', label: 'ROI Raporu', icon: DollarSign },
        ].map(t => (
          <button key={t.id} onClick={() => setSubTab(t.id)} style={pill(subTab === t.id)}>
            <t.icon size={12} style={{ marginRight: 4 }} />{t.label}
          </button>
        ))}
      </div>

      {subTab === 'overview' && overview && (
        <>
          <div style={card}>
            <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>Sosyal Medya</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 10 }}>
              <StatBox label="Toplam Gonderi" value={overview.social_media?.total_posts} icon={MessageCircle} color="#E4405F" />
              <StatBox label="Bu Ay" value={overview.social_media?.this_month} icon={TrendingUp} color="#3498db" />
              <StatBox label="Etkilesim" value={`%${overview.social_media?.engagement_rate}`} icon={Users} color="#8FAA86" />
              <StatBox label="Takipci Artisi" value={`%${overview.social_media?.followers_growth}`} icon={ArrowUp} color="#C4972A" />
            </div>
          </div>
          <div style={card}>
            <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>Reklamlar</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 10 }}>
              <StatBox label="Aktif Kampanya" value={overview.advertising?.active_campaigns} icon={Target} color="#C4972A" />
              <StatBox label="Toplam Harcama" value={`${overview.advertising?.total_spend} TL`} icon={DollarSign} color="#e74c3c" />
              <StatBox label="Donusum" value={overview.advertising?.conversions} icon={CheckCircle2} color="#8FAA86" />
              <StatBox label="ROAS" value={`${overview.advertising?.roas}x`} icon={Zap} color="#f39c12" />
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div style={card}>
              <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>Itibar</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                <StatBox label="Ortalama Puan" value={overview.reputation?.avg_rating} icon={Star} color="#f39c12" />
                <StatBox label="Yanit Orani" value={`%${overview.reputation?.response_rate}`} icon={MessageCircle} color="#8FAA86" />
              </div>
            </div>
            <div style={card}>
              <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>Yasam Dongusu</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                <StatBox label="Mesaj" value={overview.lifecycle?.messages_sent} icon={MessageCircle} color="#25D366" />
                <StatBox label="Acilma" value={`%${overview.lifecycle?.open_rate}`} icon={Eye} color="#3498db" />
              </div>
            </div>
          </div>
        </>
      )}

      {subTab === 'channels' && channels && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {Object.entries(channels).map(([name, data]) => {
            const colors = { instagram: '#E4405F', facebook: '#1877F2', whatsapp: '#25D366', google: '#4285F4', pinterest: '#E60023' };
            return (
              <div key={name} style={card}>
                <h4 style={{ color: colors[name] || '#C4972A', marginBottom: 10, fontSize: 14, textTransform: 'capitalize' }}>
                  {name === 'whatsapp' ? 'WhatsApp' : name === 'google' ? 'Google Business' : name.charAt(0).toUpperCase() + name.slice(1)}
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: 8, fontSize: 12 }}>
                  {Object.entries(data).map(([key, val]) => (
                    <div key={key} style={{ background: '#0d0d1a', borderRadius: 6, padding: 8 }}>
                      <div style={{ color: '#666', fontSize: 11 }}>{key.replace(/_/g, ' ')}</div>
                      <div style={{ color: '#e5e5e8', fontWeight: 600, marginTop: 2 }}>
                        {typeof val === 'number' ? (key.includes('cost') || key.includes('revenue') ? `${val.toLocaleString()} TL` : val.toLocaleString()) : val}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {subTab === 'funnel' && funnel && (
        <div style={card}>
          <h3 style={{ color: '#C4972A', marginBottom: 16, fontSize: 15 }}>Donusum Hunisi</h3>
          {Object.entries(funnel).map(([key, stage], i) => {
            const colors = ['#3498db', '#9b59b6', '#C4972A', '#8FAA86', '#f39c12'];
            const widths = [100, 75, 50, 30, 20];
            return (
              <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 12 }}>
                <div style={{ width: 120, fontSize: 13, color: '#aaa', textAlign: 'right' }}>{stage.label}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ width: `${widths[i]}%`, background: `${colors[i]}30`, borderRadius: 8, padding: '8px 14px', borderLeft: `3px solid ${colors[i]}` }}>
                    <div style={{ display: 'flex', gap: 12, fontSize: 12 }}>
                      {Object.entries(stage).filter(([k]) => k !== 'label').map(([k, v]) => (
                        <span key={k} style={{ color: '#ccc' }}>
                          <span style={{ color: '#888' }}>{k.replace(/_/g, ' ')}: </span>
                          <strong style={{ color: colors[i] }}>{typeof v === 'number' ? v.toLocaleString() : v}</strong>
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {subTab === 'roi' && roi && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
            <StatBox label="Pazarlama Harcamasi" value={`${roi.roi?.total_marketing_spend?.toLocaleString()} TL`} icon={DollarSign} color="#e74c3c" />
            <StatBox label="Atfedilen Gelir" value={`${roi.roi?.attributed_revenue?.toLocaleString()} TL`} icon={TrendingUp} color="#8FAA86" />
            <StatBox label="ROAS" value={`${roi.roi?.roas}x`} icon={Zap} color="#C4972A" />
            <StatBox label="ROI" value={`%${roi.roi?.roi_percentage}`} icon={Target} color="#f39c12" />
          </div>
          <div style={card}>
            <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>Kanal Bazli ROI</h3>
            {roi.by_channel && Object.entries(roi.by_channel).map(([name, data]) => (
              <div key={name} style={{ background: '#0d0d1a', borderRadius: 8, padding: 12, marginBottom: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#e5e5e8', fontWeight: 600, fontSize: 13, textTransform: 'capitalize' }}>{name.replace(/_/g, ' ')}</span>
                <div style={{ display: 'flex', gap: 16, fontSize: 12 }}>
                  <span style={{ color: '#e74c3c' }}>Harcama: {data.spend} TL</span>
                  <span style={{ color: '#8FAA86' }}>Gelir: {data.revenue?.toLocaleString()} TL</span>
                  <span style={{ color: '#C4972A', fontWeight: 700 }}>ROAS: {data.roas === 'infinity' ? 'sinirsiz' : `${data.roas}x`}</span>
                </div>
              </div>
            ))}
          </div>
          {roi.recommendations && (
            <div style={card}>
              <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>Oneriler</h3>
              {roi.recommendations.map((rec, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, fontSize: 13, color: '#ccc', marginBottom: 6 }}>
                  <CheckCircle2 size={14} color="#8FAA86" style={{ marginTop: 2, flexShrink: 0 }} /> {rec}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ==================== AI PROVIDERS TAB ====================
function AIProvidersTab() {
  const [providers, setProviders] = useState({});
  const [routing, setRouting] = useState({});
  const [loading, setLoading] = useState(true);
  const [testMsg, setTestMsg] = useState('');
  const [testTask, setTestTask] = useState('general');
  const [testProvider, setTestProvider] = useState('');
  const [testResult, setTestResult] = useState(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    Promise.all([
      getAIProviders().catch(() => ({ data: { providers: {} } })),
      getAIRouting().catch(() => ({ data: { routing: {} } })),
    ]).then(([provRes, routRes]) => {
      setProviders(provRes.data.providers || {});
      setRouting(routRes.data.routing || {});
      setLoading(false);
    });
  }, []);

  const handleTest = async () => {
    if (!testMsg.trim()) return;
    setTesting(true);
    try {
      const res = await testAI({ message: testMsg, task_type: testTask, preferred_provider: testProvider || undefined });
      setTestResult(res.data);
    } catch (e) { console.error(e); }
    setTesting(false);
  };

  if (loading) return <div style={{ padding: 40, textAlign: 'center' }}><Loader2 className="animate-spin" size={24} /></div>;

  const providerColors = { gemini: '#4285F4', deepseek: '#0066FF', openrouter: '#8B5CF6', groq: '#F97316' };
  const costLabels = { cok_dusuk: 'Cok Dusuk', dusuk: 'Dusuk', degisken: 'Degisken' };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Provider Status */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
        {Object.entries(providers).map(([id, p]) => (
          <div key={id} style={{ ...card, borderColor: p.available ? `${providerColors[id]}40` : '#333' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <span style={{ fontWeight: 700, color: providerColors[id] || '#C4972A', fontSize: 14 }}>{p.name}</span>
              <span style={{
                fontSize: 10, padding: '2px 8px', borderRadius: 10, fontWeight: 600,
                background: p.available ? '#8FAA8620' : '#e74c3c20',
                color: p.available ? '#8FAA86' : '#e74c3c',
              }}>{p.available ? 'Aktif' : 'Yapilandirilmadi'}</span>
            </div>
            <div style={{ fontSize: 12, color: '#888' }}>Maliyet: {costLabels[p.cost] || p.cost}</div>
            <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 6 }}>
              {p.strengths?.map(s => (
                <span key={s} style={{ fontSize: 10, padding: '1px 6px', borderRadius: 6, background: '#2a2a3e', color: '#aaa' }}>{s}</span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Task Routing Table */}
      <div style={card}>
        <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>Gorev Yonlendirme Tablosu</h3>
        <div style={{ fontSize: 12, color: '#888', marginBottom: 8 }}>Her gorev turu icin hangi AI provider kullanilir (fallback sirali)</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {Object.entries(routing).map(([task, info]) => (
            <div key={task} style={{ background: '#0d0d1a', borderRadius: 6, padding: '8px 12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: '#e5e5e8', fontSize: 13, fontWeight: 500 }}>{task.replace(/_/g, ' ')}</span>
              <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                <span style={{
                  fontSize: 11, padding: '2px 8px', borderRadius: 8, fontWeight: 600,
                  background: `${providerColors[info.active_provider] || '#C4972A'}20`,
                  color: providerColors[info.active_provider] || '#C4972A',
                }}>{info.active_provider}</span>
                {info.fallbacks?.length > 0 && (
                  <span style={{ fontSize: 10, color: '#666' }}>
                    fallback: {info.fallbacks.join(' > ')}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Test AI */}
      <div style={card}>
        <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>AI Test</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 150px 150px', gap: 8, marginBottom: 10 }}>
          <input placeholder="Test mesaji yazin..." value={testMsg} onChange={e => setTestMsg(e.target.value)} style={inputStyle} />
          <select value={testTask} onChange={e => setTestTask(e.target.value)} style={selectStyle}>
            <option value="general">Genel</option>
            <option value="chatbot">Chatbot</option>
            <option value="review_response">Yorum Yaniti</option>
            <option value="sentiment_analysis">Duygu Analizi</option>
            <option value="marketing_copy">Pazarlama</option>
            <option value="classification">Siniflandirma</option>
          </select>
          <select value={testProvider} onChange={e => setTestProvider(e.target.value)} style={selectStyle}>
            <option value="">Otomatik</option>
            {Object.entries(providers).filter(([, p]) => p.available).map(([id, p]) => (
              <option key={id} value={id}>{p.name}</option>
            ))}
          </select>
        </div>
        <button onClick={handleTest} disabled={testing || !testMsg.trim()} style={goldBtn}>
          {testing ? <><Loader2 className="animate-spin" size={14} /> Test Ediliyor...</> : <><Zap size={14} /> Test Et</>}
        </button>
        {testResult && (
          <div style={{ marginTop: 12, background: '#0d0d1a', borderRadius: 8, padding: 14 }}>
            <div style={{ display: 'flex', gap: 12, marginBottom: 8, fontSize: 12 }}>
              <span style={{ color: '#888' }}>Provider: <strong style={{ color: providerColors[testResult.provider] || '#C4972A' }}>{testResult.provider_name}</strong></span>
              <span style={{ color: '#888' }}>Gorev: <strong style={{ color: '#C4972A' }}>{testResult.task_type}</strong></span>
            </div>
            <pre style={{ color: '#ccc', fontSize: 13, whiteSpace: 'pre-wrap', lineHeight: 1.6, fontFamily: 'inherit' }}>
              {testResult.response}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

// ==================== MAIN PAGE ====================
export default function MarketingHubPage() {
  const [activeTab, setActiveTab] = useState('analytics');

  return (
    <div style={{ padding: 0 }}>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e5e5e8', margin: 0 }}>
          <TrendingUp size={22} style={{ marginRight: 8, color: '#C4972A' }} />
          Pazarlama Merkezi
        </h1>
        <p style={{ fontSize: 13, color: '#888', marginTop: 4 }}>Meta Ads, Google Ads, Itibar Yonetimi, AI Provider Yonetimi</p>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
        <TabButton active={activeTab === 'analytics'} onClick={() => setActiveTab('analytics')} icon={BarChart3} label="Analitikler" />
        <TabButton active={activeTab === 'meta_ads'} onClick={() => setActiveTab('meta_ads')} icon={Target} label="Meta Ads" />
        <TabButton active={activeTab === 'google_ads'} onClick={() => setActiveTab('google_ads')} icon={Globe} label="Google Ads" />
        <TabButton active={activeTab === 'reputation'} onClick={() => setActiveTab('reputation')} icon={Star} label="Itibar" />
        <TabButton active={activeTab === 'ai_providers'} onClick={() => setActiveTab('ai_providers')} icon={Zap} label="AI Yonetimi" />
      </div>

      {activeTab === 'analytics' && <AnalyticsTab />}
      {activeTab === 'meta_ads' && <MetaAdsTab />}
      {activeTab === 'google_ads' && <GoogleAdsTab />}
      {activeTab === 'reputation' && <ReputationTab />}
      {activeTab === 'ai_providers' && <AIProvidersTab />}
    </div>
  );
}
