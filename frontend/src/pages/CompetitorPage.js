import React, { useState, useEffect } from 'react';
import {
  getCompetitors, addCompetitor, analyzeCompetitor,
  compareCompetitorRatings, getCompetitorSWOT, getMarketPosition
} from '../api';
import {
  BarChart3, Loader2, Plus, Star, Globe, TrendingUp, TrendingDown,
  Award, Shield, Target, AlertCircle, ChevronDown, ChevronRight,
  Zap, Users, MapPin, DollarSign, RefreshCw
} from 'lucide-react';

const card = { background: '#1a1a2e', borderRadius: 12, padding: 20, border: '1px solid #2a2a3e' };
const goldBtn = { background: '#C4972A', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', cursor: 'pointer', fontWeight: 600, fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 6 };
const ghostBtn = { background: 'transparent', color: '#aaa', border: '1px solid #333', borderRadius: 8, padding: '8px 16px', cursor: 'pointer', fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 4 };
const inputStyle = { background: '#0d0d1a', border: '1px solid #2a2a3e', borderRadius: 8, padding: '8px 12px', color: '#e5e5e8', fontSize: 13, width: '100%' };
const pill = (active) => ({
  padding: '6px 14px', borderRadius: 20, fontSize: 12, fontWeight: 600, cursor: 'pointer', border: 'none',
  background: active ? '#C4972A' : '#2a2a3e', color: active ? '#fff' : '#aaa', transition: 'all 0.2s'
});

const RatingBar = ({ label, rating, maxRating = 5, color = '#C4972A' }) => (
  <div style={{ marginBottom: 8 }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
      <span style={{ fontSize: 12, color: '#aaa' }}>{label}</span>
      <span style={{ fontSize: 12, color, fontWeight: 600 }}>{rating || 'N/A'}</span>
    </div>
    <div style={{ background: '#0d0d1a', borderRadius: 8, height: 6, overflow: 'hidden' }}>
      <div style={{ background: color, height: '100%', width: `${((rating || 0) / maxRating) * 100}%`, borderRadius: 8, transition: 'width 0.5s' }} />
    </div>
  </div>
);

export default function CompetitorPage() {
  const [tab, setTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [competitors, setCompetitors] = useState([]);
  const [comparison, setComparison] = useState(null);
  const [marketPos, setMarketPos] = useState(null);
  const [swotResult, setSWOTResult] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analyzingId, setAnalyzingId] = useState(null);
  const [showAdd, setShowAdd] = useState(false);
  const [newComp, setNewComp] = useState({ name: '', location: 'Foca, Izmir', type: 'butik_otel' });
  const [expandedComp, setExpandedComp] = useState(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [compRes, posRes] = await Promise.all([
        getCompetitors(),
        getMarketPosition()
      ]);
      setCompetitors(compRes.data.competitors || []);
      setMarketPos(posRes.data);
    } catch { }
    setLoading(false);
  };

  const loadComparison = async () => {
    try {
      const r = await compareCompetitorRatings();
      setComparison(r.data);
    } catch { }
  };

  const handleSWOT = async () => {
    setLoading(true);
    try {
      const r = await getCompetitorSWOT();
      setSWOTResult(r.data);
    } catch { }
    setLoading(false);
  };

  const handleAnalyze = async (id) => {
    setAnalyzingId(id);
    try {
      const r = await analyzeCompetitor(id);
      setAnalysisResult(r.data);
    } catch { }
    setAnalyzingId(null);
  };

  const handleAddCompetitor = async () => {
    if (!newComp.name.trim()) return;
    try {
      await addCompetitor(newComp);
      setShowAdd(false);
      setNewComp({ name: '', location: 'Foca, Izmir', type: 'butik_otel' });
      loadData();
    } catch { }
  };

  const tabs = [
    { id: 'overview', label: 'Genel Bakis', icon: BarChart3 },
    { id: 'competitors', label: 'Rakipler', icon: Users },
    { id: 'compare', label: 'Karsilastirma', icon: Target },
    { id: 'swot', label: 'SWOT Analizi', icon: Shield },
  ];

  return (
    <div style={{ padding: 24, minHeight: '100vh', color: '#e5e5e8' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: '#C4972A', margin: 0 }}>Rakip Analizi</h1>
          <p style={{ color: '#7e7e8a', fontSize: 13, margin: '4px 0 0' }}>Yakin bolge butik otellerin karsilastirmali analizi</p>
        </div>
        {marketPos && (
          <div style={{ ...card, padding: '12px 20px', display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 700, color: marketPos.market_position === 1 ? '#C4972A' : '#aaa' }}>
                #{marketPos.market_position}
              </div>
              <div style={{ fontSize: 10, color: '#aaa' }}>Pazar Sirasi</div>
            </div>
            <div style={{ width: 1, height: 30, background: '#2a2a3e' }} />
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 18, fontWeight: 600, color: marketPos.rating_difference > 0 ? '#27ae60' : '#e74c3c' }}>
                {marketPos.rating_difference > 0 ? '+' : ''}{marketPos.rating_difference}
              </div>
              <div style={{ fontSize: 10, color: '#aaa' }}>Ort. Fark</div>
            </div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap' }}>
        {tabs.map(t => (
          <button key={t.id} onClick={() => { setTab(t.id); if (t.id === 'compare') loadComparison(); }} style={pill(tab === t.id)}>
            <t.icon size={14} style={{ marginRight: 4, verticalAlign: 'middle' }} />{t.label}
          </button>
        ))}
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: 40 }}><Loader2 size={32} className="animate-spin" style={{ color: '#C4972A' }} /></div>
      )}

      {/* Tab: Genel Bakis */}
      {tab === 'overview' && !loading && marketPos && (
        <div style={{ display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
          {[
            { label: 'Ortalama Puanimiz', value: marketPos.our_average_rating, icon: Star, color: '#C4972A' },
            { label: 'Pazar Ortalamasi', value: marketPos.market_average_rating, icon: BarChart3, color: '#3498db' },
            { label: 'Toplam Yorum', value: marketPos.total_review_count, icon: Users, color: '#27ae60' },
            { label: 'Rakip Sayisi', value: marketPos.total_competitors, icon: Target, color: '#e67e22' },
          ].map(s => (
            <div key={s.label} style={card}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: s.color + '20', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <s.icon size={20} style={{ color: s.color }} />
                </div>
                <div>
                  <div style={{ fontSize: 22, fontWeight: 700 }}>{s.value}</div>
                  <div style={{ fontSize: 11, color: '#aaa' }}>{s.label}</div>
                </div>
              </div>
            </div>
          ))}

          {/* Strengths & Weaknesses */}
          <div style={card}>
            <h4 style={{ fontSize: 14, color: '#27ae60', margin: '0 0 12px' }}>
              <TrendingUp size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />Guclu Yanlarimiz
            </h4>
            {marketPos.strengths?.map((s, i) => (
              <div key={i} style={{ padding: '6px 0', borderBottom: '1px solid #2a2a3e', fontSize: 13 }}>{s}</div>
            ))}
          </div>
          <div style={card}>
            <h4 style={{ fontSize: 14, color: '#e67e22', margin: '0 0 12px' }}>
              <AlertCircle size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />Gelistirilecek Alanlar
            </h4>
            {marketPos.weaknesses?.map((w, i) => (
              <div key={i} style={{ padding: '6px 0', borderBottom: '1px solid #2a2a3e', fontSize: 13 }}>{w}</div>
            ))}
          </div>

          {/* Platform Comparison */}
          {marketPos.platform_comparison && (
            <div style={{ ...card, gridColumn: 'span 2' }}>
              <h4 style={{ fontSize: 14, color: '#C4972A', margin: '0 0 16px' }}>Platform Karsilastirmasi</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
                {Object.entries(marketPos.platform_comparison).map(([platform, data]) => (
                  <div key={platform} style={{ padding: 12, background: '#0d0d1a', borderRadius: 8 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8, textTransform: 'capitalize' }}>{platform}</div>
                    <RatingBar label="Biz" rating={data.our_rating} color="#C4972A" />
                    <RatingBar label="Rakip Ort." rating={data.competitor_average} color="#666" />
                    <div style={{ textAlign: 'center', marginTop: 8 }}>
                      <span style={{ fontSize: 14, fontWeight: 700, color: data.difference > 0 ? '#27ae60' : '#e74c3c' }}>
                        {data.difference > 0 ? '+' : ''}{data.difference}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab: Rakipler */}
      {tab === 'competitors' && !loading && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
            <button onClick={() => setShowAdd(!showAdd)} style={goldBtn}>
              <Plus size={14} /> Rakip Ekle
            </button>
          </div>

          {showAdd && (
            <div style={{ ...card, marginBottom: 16 }}>
              <h4 style={{ fontSize: 14, color: '#C4972A', margin: '0 0 12px' }}>Yeni Rakip Ekle</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
                <input value={newComp.name} onChange={e => setNewComp({ ...newComp, name: e.target.value })} placeholder="Otel Adi" style={inputStyle} />
                <input value={newComp.location} onChange={e => setNewComp({ ...newComp, location: e.target.value })} placeholder="Konum" style={inputStyle} />
                <select value={newComp.type} onChange={e => setNewComp({ ...newComp, type: e.target.value })} style={{ ...inputStyle, cursor: 'pointer' }}>
                  <option value="butik_otel">Butik Otel</option>
                  <option value="pansiyon">Pansiyon</option>
                  <option value="apart">Apart</option>
                </select>
              </div>
              <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                <button onClick={handleAddCompetitor} style={goldBtn}>Kaydet</button>
                <button onClick={() => setShowAdd(false)} style={ghostBtn}>Iptal</button>
              </div>
            </div>
          )}

          <div style={{ display: 'grid', gap: 12 }}>
            {competitors.map(comp => (
              <div key={comp.id || comp.name} style={card}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer' }} onClick={() => setExpandedComp(expandedComp === comp.id ? null : comp.id)}>
                    {expandedComp === comp.id ? <ChevronDown size={16} style={{ color: '#aaa' }} /> : <ChevronRight size={16} style={{ color: '#aaa' }} />}
                    <div>
                      <div style={{ fontSize: 15, fontWeight: 600 }}>{comp.name}</div>
                      <div style={{ fontSize: 12, color: '#aaa', display: 'flex', alignItems: 'center', gap: 8 }}>
                        <MapPin size={11} /> {comp.location}
                        <DollarSign size={11} /> {comp.price_range}
                      </div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    {Object.entries(comp.platforms || {}).map(([platform, data]) => (
                      <span key={platform} style={{ padding: '4px 8px', background: '#2a2a3e', borderRadius: 8, fontSize: 11 }}>
                        {platform}: <strong style={{ color: '#C4972A' }}>{data.rating}</strong>
                      </span>
                    ))}
                    <button onClick={() => handleAnalyze(comp.id)} disabled={analyzingId === comp.id} style={ghostBtn}>
                      {analyzingId === comp.id ? <Loader2 size={12} className="animate-spin" /> : <Zap size={12} />} Analiz
                    </button>
                  </div>
                </div>

                {expandedComp === comp.id && (
                  <div style={{ marginTop: 16, padding: 12, background: '#0d0d1a', borderRadius: 8 }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                      <div>
                        <h5 style={{ fontSize: 12, color: '#27ae60', margin: '0 0 8px' }}>Guclu Yanlar</h5>
                        {comp.strengths?.map((s, i) => (
                          <div key={i} style={{ fontSize: 12, padding: '3px 0', color: '#aaa' }}>+ {s}</div>
                        ))}
                      </div>
                      <div>
                        <h5 style={{ fontSize: 12, color: '#e67e22', margin: '0 0 8px' }}>Zayif Yanlar</h5>
                        {comp.weaknesses?.map((w, i) => (
                          <div key={i} style={{ fontSize: 12, padding: '3px 0', color: '#aaa' }}>- {w}</div>
                        ))}
                      </div>
                    </div>
                    {/* Platform Details */}
                    <div style={{ marginTop: 12 }}>
                      {Object.entries(comp.platforms || {}).map(([platform, data]) => (
                        <RatingBar key={platform} label={`${platform} (${data.review_count || 0} yorum)`} rating={data.rating} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Analysis Result */}
          {analysisResult && (
            <div style={{ ...card, marginTop: 16, border: '1px solid #C4972A30' }}>
              <h4 style={{ fontSize: 14, color: '#C4972A', margin: '0 0 12px' }}>
                <Zap size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
                AI Analiz Sonucu: {analysisResult.competitor}
              </h4>
              <div style={{ fontSize: 13, color: '#ccc', whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                {analysisResult.analysis}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab: Karsilastirma */}
      {tab === 'compare' && (
        <div>
          {comparison ? (
            <div style={{ display: 'grid', gap: 16 }}>
              {/* Our ratings */}
              <div style={card}>
                <h4 style={{ fontSize: 14, color: '#C4972A', margin: '0 0 16px' }}>Kozbeyli Konagi</h4>
                {Object.entries(comparison.kozbeyli_konagi || {}).map(([platform, data]) => (
                  <RatingBar key={platform} label={`${platform} (${data.review_count} yorum)`} rating={data.rating} color="#C4972A" />
                ))}
              </div>

              {/* Competitors */}
              {comparison.competitors?.map((comp, i) => (
                <div key={i} style={card}>
                  <h4 style={{ fontSize: 14, color: '#aaa', margin: '0 0 16px' }}>{comp.name}</h4>
                  {Object.entries(comp.platforms || {}).map(([platform, data]) => (
                    <RatingBar key={platform} label={`${platform} (${data.review_count || 0} yorum)`} rating={data.rating} color="#666" />
                  ))}
                </div>
              ))}

              {/* Platform Averages */}
              {comparison.platform_averages && (
                <div style={{ ...card, border: '1px solid #C4972A30' }}>
                  <h4 style={{ fontSize: 14, color: '#C4972A', margin: '0 0 16px' }}>Platform Ortalamalari</h4>
                  {Object.entries(comparison.platform_averages).map(([platform, data]) => (
                    <div key={platform} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #2a2a3e' }}>
                      <span style={{ fontSize: 13, textTransform: 'capitalize' }}>{platform}</span>
                      <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                        <span style={{ fontSize: 12, color: '#aaa' }}>Rakip Ort: {data.competitor_average}</span>
                        <span style={{ fontSize: 12, color: '#C4972A' }}>Biz: {data.our_rating}</span>
                        <span style={{ fontSize: 12, fontWeight: 700, color: data.difference > 0 ? '#27ae60' : '#e74c3c' }}>
                          {data.difference > 0 ? '+' : ''}{data.difference}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: 40 }}><Loader2 size={32} className="animate-spin" style={{ color: '#C4972A' }} /></div>
          )}
        </div>
      )}

      {/* Tab: SWOT */}
      {tab === 'swot' && (
        <div>
          {!swotResult ? (
            <div style={{ ...card, textAlign: 'center', padding: 40 }}>
              <Shield size={40} style={{ color: '#C4972A', marginBottom: 12 }} />
              <h3 style={{ fontSize: 16, margin: '0 0 8px' }}>SWOT Analizi</h3>
              <p style={{ fontSize: 13, color: '#aaa', marginBottom: 16 }}>AI ile kapsamli guclu/zayif yan, firsat ve tehdit analizi olusturun</p>
              <button onClick={handleSWOT} disabled={loading} style={goldBtn}>
                {loading ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />} SWOT Analizi Olustur
              </button>
            </div>
          ) : (
            <div style={card}>
              <h4 style={{ fontSize: 16, color: '#C4972A', margin: '0 0 16px' }}>
                <Shield size={16} style={{ marginRight: 6, verticalAlign: 'middle' }} />SWOT Analiz Sonucu
              </h4>
              <div style={{ fontSize: 13, color: '#ccc', whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                {swotResult.swot}
              </div>
              <div style={{ marginTop: 16, display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                <span style={{ fontSize: 11, color: '#aaa' }}>Provider: {swotResult.provider}</span>
                <span style={{ fontSize: 11, color: '#aaa' }}>Rakip: {swotResult.competitor_count}</span>
              </div>
              <button onClick={handleSWOT} disabled={loading} style={{ ...ghostBtn, marginTop: 12 }}>
                <RefreshCw size={12} /> Yeniden Olustur
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
