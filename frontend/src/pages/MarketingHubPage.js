import React, { useState, useEffect } from 'react';
import {
  generateAdCopy, getAdAudiences, getAdTemplates, getAdPerformance,
  createAdCampaign, getAdCampaigns, updateAdCampaignStatus, getBudgetSuggestions,
  getReputationOverview, analyzeReview, getReputationReviews, getCompetitorComparison,
  addReputationReview, quickSentiment,
  getMarketingOverview, getChannelPerformance, getConversionFunnel, getROIReport
} from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import {
  TrendingUp, Target, Star, BarChart3, Loader2, Sparkles, Copy, RefreshCw,
  DollarSign, Eye, MousePointer, ArrowUp, ArrowDown, Minus, Plus,
  Instagram, Facebook, MessageCircle, Globe, Award, AlertCircle, CheckCircle2,
  Zap, PieChart, Users, ExternalLink, Search
} from 'lucide-react';

// ==================== STYLES ====================
const card = { background: '#1a1a2e', borderRadius: 12, padding: 20, border: '1px solid #2a2a3e' };
const goldBtn = { background: '#C4972A', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', cursor: 'pointer', fontWeight: 600, fontSize: 13 };
const ghostBtn = { background: 'transparent', color: '#aaa', border: '1px solid #333', borderRadius: 8, padding: '8px 16px', cursor: 'pointer', fontSize: 13 };
const pill = (active) => ({
  padding: '6px 14px', borderRadius: 20, fontSize: 12, fontWeight: 600, cursor: 'pointer', border: 'none',
  background: active ? '#C4972A' : '#2a2a3e', color: active ? '#fff' : '#aaa', transition: 'all 0.2s'
});
const statCard = (color = '#C4972A') => ({
  background: `${color}15`, borderRadius: 10, padding: '14px 16px', border: `1px solid ${color}30`,
  display: 'flex', flexDirection: 'column', gap: 4
});

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
    {trend && (
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

// ==================== META ADS TAB ====================
function MetaAdsTab() {
  const [audiences, setAudiences] = useState({});
  const [campaigns, setCampaigns] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [selectedSegment, setSelectedSegment] = useState('weekend_getaway');
  const [selectedType, setSelectedType] = useState('weekend');
  const [generatedCopy, setGeneratedCopy] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newCampaign, setNewCampaign] = useState({ name: '', objective: 'awareness', budget_daily: 50 });

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

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await generateAdCopy({ segment: selectedSegment, ad_type: selectedType, platform: 'both' });
      setGeneratedCopy(res.data);
    } catch (e) { console.error(e); }
    setGenerating(false);
  };

  const handleCreateCampaign = async () => {
    try {
      const res = await createAdCampaign({ ...newCampaign, segment: selectedSegment, ad_copy: generatedCopy });
      setCampaigns(prev => [res.data, ...prev]);
      setShowCreate(false);
      setNewCampaign({ name: '', objective: 'awareness', budget_daily: 50 });
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
  const typeLabels = { wedding: 'Dugun Mekani', weekend: 'Hafta Sonu', restaurant: 'Restoran', seasonal: 'Mevsimsel' };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Performance Summary */}
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

      {/* AI Ad Copy Generator */}
      <div style={card}>
        <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>
          <Sparkles size={16} style={{ marginRight: 6 }} />AI Reklam Metni Olustur
        </h3>

        <div style={{ marginBottom: 12 }}>
          <span style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 6 }}>Hedef Kitle</span>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {Object.keys(segmentLabels).map(s => (
              <button key={s} onClick={() => setSelectedSegment(s)} style={pill(selectedSegment === s)}>
                {segmentLabels[s]}
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: 12 }}>
          <span style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 6 }}>Reklam Turu</span>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {Object.keys(typeLabels).map(t => (
              <button key={t} onClick={() => setSelectedType(t)} style={pill(selectedType === t)}>
                {typeLabels[t]}
              </button>
            ))}
          </div>
        </div>

        {audiences[selectedSegment] && (
          <div style={{ background: '#0d0d1a', borderRadius: 8, padding: 12, marginBottom: 12, fontSize: 12 }}>
            <div style={{ color: '#C4972A', fontWeight: 600, marginBottom: 4 }}>{audiences[selectedSegment].name}</div>
            <div style={{ color: '#888' }}>Yas: {audiences[selectedSegment].age_range} | Bolge: {audiences[selectedSegment].geo}</div>
            <div style={{ color: '#666', marginTop: 2 }}>Ilgi: {audiences[selectedSegment].interests?.join(', ')}</div>
            <div style={{ color: '#8FAA86', marginTop: 4 }}>Onerilen Butce: {audiences[selectedSegment].budget_suggestion}</div>
          </div>
        )}

        <button onClick={handleGenerate} disabled={generating} style={goldBtn}>
          {generating ? <><Loader2 className="animate-spin" size={14} /> Olusturuluyor...</> : <><Sparkles size={14} /> Reklam Metni Olustur</>}
        </button>

        {generatedCopy && (
          <div style={{ marginTop: 16, background: '#0d0d1a', borderRadius: 8, padding: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <span style={{ color: '#C4972A', fontWeight: 600, fontSize: 13 }}>AI Reklam Metni</span>
              <button onClick={() => navigator.clipboard.writeText(generatedCopy.ad_copy)} style={{ ...ghostBtn, padding: '4px 8px' }}>
                <Copy size={12} /> Kopyala
              </button>
            </div>
            <pre style={{ color: '#ccc', fontSize: 13, whiteSpace: 'pre-wrap', lineHeight: 1.6, fontFamily: 'inherit' }}>
              {generatedCopy.ad_copy}
            </pre>
          </div>
        )}
      </div>

      {/* Campaigns List */}
      <div style={card}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h3 style={{ color: '#C4972A', fontSize: 15 }}>
            <Target size={16} style={{ marginRight: 6 }} />Kampanyalar
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
            <div style={{ display: 'flex', gap: 6, marginBottom: 10 }}>
              {['awareness', 'traffic', 'conversions', 'engagement'].map(obj => (
                <button key={obj} onClick={() => setNewCampaign({ ...newCampaign, objective: obj })} style={pill(newCampaign.objective === obj)}>
                  {obj === 'awareness' ? 'Farkindalik' : obj === 'traffic' ? 'Trafik' : obj === 'conversions' ? 'Donusum' : 'Etkilesim'}
                </button>
              ))}
            </div>
            <button onClick={handleCreateCampaign} disabled={!newCampaign.name} style={goldBtn}>Olustur</button>
          </div>
        )}

        {campaigns.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 30, color: '#666' }}>
            <Target size={32} style={{ marginBottom: 8, opacity: 0.3 }} />
            <div>Henuz kampanya yok</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {campaigns.map(camp => (
              <div key={camp.id} style={{ background: '#0d0d1a', borderRadius: 8, padding: 14, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 600, color: '#e5e5e8', fontSize: 14 }}>{camp.name}</div>
                  <div style={{ fontSize: 12, color: '#888', marginTop: 2 }}>
                    {camp.objective} | {camp.budget_daily} TL/gun | {camp.platform}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                  <span style={{
                    fontSize: 11, padding: '3px 10px', borderRadius: 12, fontWeight: 600,
                    background: camp.status === 'active' ? '#8FAA8620' : camp.status === 'paused' ? '#C4972A20' : '#7e7e8a20',
                    color: camp.status === 'active' ? '#8FAA86' : camp.status === 'paused' ? '#C4972A' : '#7e7e8a',
                  }}>
                    {camp.status === 'active' ? 'Aktif' : camp.status === 'paused' ? 'Durduruldu' : camp.status === 'draft' ? 'Taslak' : camp.status}
                  </span>
                  {camp.status === 'draft' && <button onClick={() => handleStatusChange(camp.id, 'active')} style={{ ...ghostBtn, padding: '4px 8px', fontSize: 11 }}>Baslat</button>}
                  {camp.status === 'active' && <button onClick={() => handleStatusChange(camp.id, 'paused')} style={{ ...ghostBtn, padding: '4px 8px', fontSize: 11 }}>Durdur</button>}
                  {camp.status === 'paused' && <button onClick={() => handleStatusChange(camp.id, 'active')} style={{ ...ghostBtn, padding: '4px 8px', fontSize: 11 }}>Devam</button>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Demo Campaigns Performance */}
      {performance?.campaigns && (
        <div style={card}>
          <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>
            <BarChart3 size={16} style={{ marginRight: 6 }} />Kampanya Performanslari
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {performance.campaigns.map(c => (
              <div key={c.id} style={{ background: '#0d0d1a', borderRadius: 8, padding: 14 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ fontWeight: 600, color: '#e5e5e8', fontSize: 13 }}>{c.name}</span>
                  <span style={{
                    fontSize: 11, padding: '2px 8px', borderRadius: 10,
                    background: c.status === 'active' ? '#8FAA8620' : '#C4972A20',
                    color: c.status === 'active' ? '#8FAA86' : '#C4972A',
                  }}>{c.status === 'active' ? 'Aktif' : 'Durduruldu'}</span>
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
      {/* Overall Score */}
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
              {platforms.google && (
                <div style={{ background: '#0d0d1a', borderRadius: 8, padding: 14 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#4285F4' }} />
                    <span style={{ fontWeight: 600, color: '#e5e5e8', fontSize: 13 }}>Google</span>
                  </div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: '#f39c12' }}>{platforms.google.rating} <Star size={14} fill="#f39c12" /></div>
                  <div style={{ fontSize: 11, color: '#888' }}>{platforms.google.review_count} degerlendirme | Yanit orani: %{platforms.google.response_rate}</div>
                </div>
              )}
              {platforms.tripadvisor && (
                <div style={{ background: '#0d0d1a', borderRadius: 8, padding: 14 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#00AF87' }} />
                    <span style={{ fontWeight: 600, color: '#e5e5e8', fontSize: 13 }}>TripAdvisor</span>
                  </div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: '#00AF87' }}>{platforms.tripadvisor.rating} <Star size={14} fill="#00AF87" /></div>
                  <div style={{ fontSize: 11, color: '#888' }}>{platforms.tripadvisor.review_count} degerlendirme</div>
                </div>
              )}
              {platforms.booking && (
                <div style={{ background: '#0d0d1a', borderRadius: 8, padding: 14 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#003580' }} />
                    <span style={{ fontWeight: 600, color: '#e5e5e8', fontSize: 13 }}>Booking.com</span>
                  </div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: '#003580' }}>{platforms.booking.rating} <Star size={14} fill="#003580" /></div>
                  <div style={{ fontSize: 11, color: '#888' }}>{platforms.booking.review_count} degerlendirme</div>
                </div>
              )}
              {platforms.instagram && (
                <div style={{ background: '#0d0d1a', borderRadius: 8, padding: 14 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#E4405F' }} />
                    <span style={{ fontWeight: 600, color: '#e5e5e8', fontSize: 13 }}>Instagram</span>
                  </div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: '#E4405F' }}>{platforms.instagram.mentions}</div>
                  <div style={{ fontSize: 11, color: '#888' }}>mention | Etkilesim: %{platforms.instagram.engagement_rate}</div>
                </div>
              )}
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
                      <div style={{ width: `${(score / 5) * 100}%`, height: '100%', background: score >= 4.5 ? '#8FAA86' : score >= 4 ? '#C4972A' : '#e74c3c', borderRadius: 3, transition: 'width 0.5s' }} />
                    </div>
                    <span style={{ fontSize: 13, fontWeight: 600, color: score >= 4.5 ? '#8FAA86' : score >= 4 ? '#C4972A' : '#e74c3c', width: 30 }}>{score}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* AI Review Analyzer */}
      <div style={card}>
        <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>
          <Sparkles size={16} style={{ marginRight: 6 }} />AI Degerlendirme Analizi
        </h3>
        <textarea
          value={analyzeText}
          onChange={e => setAnalyzeText(e.target.value)}
          placeholder="Analiz etmek istediginiz degerlendirme metnini yapin..."
          style={{ width: '100%', minHeight: 80, background: '#0d0d1a', border: '1px solid #2a2a3e', borderRadius: 8, padding: 12, color: '#e5e5e8', fontSize: 13, resize: 'vertical' }}
        />
        <button onClick={handleAnalyze} disabled={analyzing || !analyzeText.trim()} style={{ ...goldBtn, marginTop: 8 }}>
          {analyzing ? <><Loader2 className="animate-spin" size={14} /> Analiz Ediliyor...</> : <><Search size={14} /> Analiz Et</>}
        </button>

        {analyzeResult && (
          <div style={{ marginTop: 12, background: '#0d0d1a', borderRadius: 8, padding: 14 }}>
            <div style={{ marginBottom: 8 }}>
              <span style={{ fontSize: 12, color: '#888' }}>Duygu: </span>
              <span style={{
                fontSize: 12, fontWeight: 600, padding: '2px 8px', borderRadius: 10,
                background: analyzeResult.basic_analysis?.sentiment === 'positive' ? '#8FAA8620' : analyzeResult.basic_analysis?.sentiment === 'negative' ? '#e74c3c20' : '#C4972A20',
                color: analyzeResult.basic_analysis?.sentiment === 'positive' ? '#8FAA86' : analyzeResult.basic_analysis?.sentiment === 'negative' ? '#e74c3c' : '#C4972A',
              }}>
                {analyzeResult.basic_analysis?.sentiment === 'positive' ? 'Pozitif' : analyzeResult.basic_analysis?.sentiment === 'negative' ? 'Negatif' : 'Notr'}
              </span>
              <span style={{ fontSize: 12, color: '#888', marginLeft: 8 }}>Skor: {analyzeResult.basic_analysis?.score}/10</span>
            </div>
            {analyzeResult.ai_analysis && (
              <pre style={{ color: '#ccc', fontSize: 12, whiteSpace: 'pre-wrap', lineHeight: 1.6, fontFamily: 'inherit' }}>
                {analyzeResult.ai_analysis}
              </pre>
            )}
          </div>
        )}
      </div>

      {/* Reviews List */}
      <div style={card}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h3 style={{ color: '#C4972A', fontSize: 15 }}>Degerlendirmeler</h3>
          <button onClick={() => setShowAddReview(!showAddReview)} style={goldBtn}>
            <Plus size={14} /> Ekle
          </button>
        </div>

        {showAddReview && (
          <div style={{ background: '#0d0d1a', borderRadius: 8, padding: 14, marginBottom: 12 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 80px', gap: 8, marginBottom: 8 }}>
              <select value={newReview.platform} onChange={e => setNewReview({ ...newReview, platform: e.target.value })}
                style={{ background: '#1a1a2e', border: '1px solid #2a2a3e', borderRadius: 8, padding: 8, color: '#e5e5e8', fontSize: 13 }}>
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
              <p style={{ color: '#aaa', fontSize: 12, lineHeight: 1.5 }}>{rev.text}</p>
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
      {competitors && (
        <div style={card}>
          <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>
            <Award size={16} style={{ marginRight: 6 }} />Rakip Karsilastirma
          </h3>
          <div style={{ background: '#0d0d1a', borderRadius: 8, padding: 14, marginBottom: 8 }}>
            <div style={{ fontWeight: 700, color: '#C4972A', fontSize: 14 }}>{competitors.our_hotel?.name}</div>
            <div style={{ fontSize: 13, color: '#e5e5e8', marginTop: 4 }}>Google: {competitors.our_hotel?.google_rating} | {competitors.our_hotel?.review_count} yorum</div>
            <div style={{ fontSize: 12, color: '#8FAA86', marginTop: 2 }}>Guclu yonler: {competitors.our_hotel?.strengths?.join(', ')}</div>
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
      {/* Sub-tabs */}
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

      {/* Overview */}
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
                <StatBox label="Mesaj Gonderilen" value={overview.lifecycle?.messages_sent} icon={MessageCircle} color="#25D366" />
                <StatBox label="Acilma Orani" value={`%${overview.lifecycle?.open_rate}`} icon={Eye} color="#3498db" />
              </div>
            </div>
          </div>
        </>
      )}

      {/* Channels */}
      {subTab === 'channels' && channels && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {Object.entries(channels).map(([name, data]) => (
            <div key={name} style={card}>
              <h4 style={{ color: name === 'instagram' ? '#E4405F' : name === 'facebook' ? '#1877F2' : name === 'whatsapp' ? '#25D366' : name === 'google' ? '#4285F4' : '#E60023', marginBottom: 10, fontSize: 14, textTransform: 'capitalize' }}>
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
          ))}
        </div>
      )}

      {/* Funnel */}
      {subTab === 'funnel' && funnel && (
        <div style={card}>
          <h3 style={{ color: '#C4972A', marginBottom: 16, fontSize: 15 }}>Donusum Hunisi</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {Object.entries(funnel).map(([key, stage], i) => {
              const colors = ['#3498db', '#9b59b6', '#C4972A', '#8FAA86', '#f39c12'];
              const widths = [100, 75, 50, 30, 20];
              return (
                <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  <div style={{ width: 120, fontSize: 13, color: '#aaa', textAlign: 'right' }}>{stage.label}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{
                      width: `${widths[i]}%`, background: `${colors[i]}30`, borderRadius: 8, padding: '8px 14px',
                      borderLeft: `3px solid ${colors[i]}`, transition: 'width 0.5s'
                    }}>
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
        </div>
      )}

      {/* ROI */}
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
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {roi.by_channel && Object.entries(roi.by_channel).map(([name, data]) => (
                <div key={name} style={{ background: '#0d0d1a', borderRadius: 8, padding: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#e5e5e8', fontWeight: 600, fontSize: 13, textTransform: 'capitalize' }}>{name.replace(/_/g, ' ')}</span>
                  <div style={{ display: 'flex', gap: 16, fontSize: 12 }}>
                    <span style={{ color: '#e74c3c' }}>Harcama: {data.spend} TL</span>
                    <span style={{ color: '#8FAA86' }}>Gelir: {data.revenue?.toLocaleString()} TL</span>
                    <span style={{ color: '#C4972A', fontWeight: 700 }}>ROAS: {data.roas === 'infinity' ? 'sinirsiz' : `${data.roas}x`}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {roi.recommendations && (
            <div style={card}>
              <h3 style={{ color: '#C4972A', marginBottom: 12, fontSize: 15 }}>
                <Sparkles size={16} style={{ marginRight: 6 }} />Oneriler
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {roi.recommendations.map((rec, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, fontSize: 13, color: '#ccc' }}>
                    <CheckCircle2 size={14} color="#8FAA86" style={{ marginTop: 2, flexShrink: 0 }} />
                    {rec}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
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
        <p style={{ fontSize: 13, color: '#888', marginTop: 4 }}>Meta Ads, Itibar Yonetimi ve Performans Analitikleri</p>
      </div>

      {/* Tab Navigation */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
        <TabButton active={activeTab === 'analytics'} onClick={() => setActiveTab('analytics')} icon={BarChart3} label="Analitikler" />
        <TabButton active={activeTab === 'meta_ads'} onClick={() => setActiveTab('meta_ads')} icon={Target} label="Meta Ads" />
        <TabButton active={activeTab === 'reputation'} onClick={() => setActiveTab('reputation')} icon={Star} label="Itibar Yonetimi" />
      </div>

      {/* Tab Content */}
      {activeTab === 'analytics' && <AnalyticsTab />}
      {activeTab === 'meta_ads' && <MetaAdsTab />}
      {activeTab === 'reputation' && <ReputationTab />}
    </div>
  );
}
