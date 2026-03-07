import React, { useState, useEffect } from 'react';
import {
  getLocalSEOReport, getMetaTemplates, getAllSEOSchemas,
  suggestKeywords, analyzeSEO, generateMetaTags
} from '../api';
import {
  Search, Loader2, CheckCircle2, AlertCircle, Globe, FileText,
  Code, Tag, BarChart3, Copy, RefreshCw, Zap, ArrowRight, Clock
} from 'lucide-react';

const card = { background: '#1a1a2e', borderRadius: 12, padding: 20, border: '1px solid #2a2a3e' };
const goldBtn = { background: '#C4972A', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', cursor: 'pointer', fontWeight: 600, fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 6 };
const ghostBtn = { background: 'transparent', color: '#aaa', border: '1px solid #333', borderRadius: 8, padding: '8px 16px', cursor: 'pointer', fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 4 };
const inputStyle = { background: '#0d0d1a', border: '1px solid #2a2a3e', borderRadius: 8, padding: '8px 12px', color: '#e5e5e8', fontSize: 13, width: '100%' };
const pill = (active) => ({
  padding: '6px 14px', borderRadius: 20, fontSize: 12, fontWeight: 600, cursor: 'pointer', border: 'none',
  background: active ? '#C4972A' : '#2a2a3e', color: active ? '#fff' : '#aaa', transition: 'all 0.2s'
});

const STATUS_COLORS = { done: '#27ae60', warning: '#f39c12', todo: '#e74c3c' };
const STATUS_LABELS = { done: 'Tamamlandi', warning: 'Dikkat', todo: 'Yapilacak' };

const ScoreBar = ({ score, max = 100, label }) => (
  <div style={{ marginBottom: 12 }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
      <span style={{ color: '#aaa', fontSize: 12 }}>{label}</span>
      <span style={{ color: '#C4972A', fontSize: 12, fontWeight: 600 }}>{score}/{max}</span>
    </div>
    <div style={{ background: '#0d0d1a', borderRadius: 8, height: 8, overflow: 'hidden' }}>
      <div style={{ background: score >= max * 0.7 ? '#27ae60' : score >= max * 0.4 ? '#f39c12' : '#e74c3c', height: '100%', width: `${(score / max) * 100}%`, borderRadius: 8, transition: 'width 0.5s' }} />
    </div>
  </div>
);

export default function SEOPage() {
  const [tab, setTab] = useState('report');
  const [loading, setLoading] = useState(false);
  const [localReport, setLocalReport] = useState(null);
  const [metaTemplates, setMetaTemplates] = useState(null);
  const [schemas, setSchemas] = useState(null);
  const [keywords, setKeywords] = useState(null);
  const [keywordTopic, setKeywordTopic] = useState('');
  const [metaResult, setMetaResult] = useState(null);
  const [metaPageType, setMetaPageType] = useState('home');
  const [metaContent, setMetaContent] = useState('');
  const [analyzeContent, setAnalyzeContent] = useState('');
  const [analyzeResult, setAnalyzeResult] = useState(null);
  const [copied, setCopied] = useState('');

  useEffect(() => { loadLocalReport(); }, []);

  const loadLocalReport = async () => {
    setLoading(true);
    try {
      const r = await getLocalSEOReport();
      setLocalReport(r.data);
    } catch { }
    setLoading(false);
  };

  const loadMetaTemplates = async () => {
    if (metaTemplates) return;
    try {
      const r = await getMetaTemplates();
      setMetaTemplates(r.data.templates);
    } catch { }
  };

  const loadSchemas = async () => {
    if (schemas) return;
    try {
      const r = await getAllSEOSchemas();
      setSchemas(r.data);
    } catch { }
  };

  const handleKeywordSearch = async () => {
    if (!keywordTopic.trim()) return;
    setLoading(true);
    try {
      const r = await suggestKeywords({ topic: keywordTopic });
      setKeywords(r.data);
    } catch { }
    setLoading(false);
  };

  const handleGenerateMeta = async () => {
    setLoading(true);
    try {
      const r = await generateMetaTags({ page_type: metaPageType, content: metaContent });
      setMetaResult(r.data);
    } catch { }
    setLoading(false);
  };

  const handleAnalyze = async () => {
    if (!analyzeContent.trim()) return;
    setLoading(true);
    try {
      const r = await analyzeSEO({ content: analyzeContent, page_type: 'general' });
      setAnalyzeResult(r.data);
    } catch { }
    setLoading(false);
  };

  const copyToClipboard = (text, key) => {
    navigator.clipboard.writeText(typeof text === 'string' ? text : JSON.stringify(text, null, 2));
    setCopied(key);
    setTimeout(() => setCopied(''), 2000);
  };

  const tabs = [
    { id: 'report', label: 'Yerel SEO Raporu', icon: BarChart3 },
    { id: 'keywords', label: 'Anahtar Kelime', icon: Search },
    { id: 'meta', label: 'Meta Tag Uretici', icon: Tag },
    { id: 'schema', label: 'Schema.org', icon: Code },
    { id: 'analyze', label: 'SEO Analiz', icon: Zap },
  ];

  return (
    <div style={{ padding: 24, minHeight: '100vh', color: '#e5e5e8' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: '#C4972A', margin: 0 }}>SEO Yonetimi</h1>
          <p style={{ color: '#7e7e8a', fontSize: 13, margin: '4px 0 0' }}>Arama motoru optimizasyonu ve icerik analizi</p>
        </div>
        {localReport && (
          <div style={{ ...card, padding: '12px 20px', display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: 28, fontWeight: 700, color: localReport.score >= 70 ? '#27ae60' : localReport.score >= 40 ? '#f39c12' : '#e74c3c' }}>
              {localReport.score}
            </span>
            <div>
              <div style={{ fontSize: 11, color: '#aaa' }}>SEO Skoru</div>
              <div style={{ fontSize: 11, color: '#666' }}>{localReport.done}/{localReport.total_items} tamamlandi</div>
            </div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap' }}>
        {tabs.map(t => (
          <button key={t.id} onClick={() => { setTab(t.id); if (t.id === 'meta') loadMetaTemplates(); if (t.id === 'schema') loadSchemas(); }} style={pill(tab === t.id)}>
            <t.icon size={14} style={{ marginRight: 4, verticalAlign: 'middle' }} />{t.label}
          </button>
        ))}
      </div>

      {/* Tab: Yerel SEO Raporu */}
      {tab === 'report' && (
        <div>
          {loading ? (
            <div style={{ textAlign: 'center', padding: 40 }}><Loader2 size={32} className="animate-spin" style={{ color: '#C4972A' }} /></div>
          ) : localReport ? (
            <div style={{ display: 'grid', gap: 16 }}>
              {/* Summary */}
              <div style={{ ...card, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
                {[
                  { label: 'Tamamlandi', value: localReport.done, color: '#27ae60', icon: CheckCircle2 },
                  { label: 'Dikkat Gereken', value: localReport.warning, color: '#f39c12', icon: AlertCircle },
                  { label: 'Yapilacak', value: localReport.todo, color: '#e74c3c', icon: Clock },
                ].map(s => (
                  <div key={s.label} style={{ textAlign: 'center' }}>
                    <s.icon size={24} style={{ color: s.color, marginBottom: 4 }} />
                    <div style={{ fontSize: 24, fontWeight: 700, color: s.color }}>{s.value}</div>
                    <div style={{ fontSize: 11, color: '#aaa' }}>{s.label}</div>
                  </div>
                ))}
              </div>
              {/* Checklist */}
              {localReport.checklist?.map((item, i) => (
                <div key={i} style={{ ...card, display: 'flex', alignItems: 'center', gap: 16 }}>
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: STATUS_COLORS[item.status], flexShrink: 0 }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 14, fontWeight: 600 }}>{item.item}</div>
                    <div style={{ fontSize: 12, color: '#aaa', marginTop: 2 }}>{item.description}</div>
                  </div>
                  <span style={{ fontSize: 11, padding: '4px 10px', borderRadius: 12, background: STATUS_COLORS[item.status] + '20', color: STATUS_COLORS[item.status], fontWeight: 600 }}>
                    {STATUS_LABELS[item.status]}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ ...card, textAlign: 'center', padding: 40 }}>
              <Globe size={40} style={{ color: '#333', marginBottom: 12 }} />
              <p style={{ color: '#aaa' }}>Rapor yuklenemedi</p>
              <button onClick={loadLocalReport} style={goldBtn}><RefreshCw size={14} /> Tekrar Dene</button>
            </div>
          )}
        </div>
      )}

      {/* Tab: Anahtar Kelime */}
      {tab === 'keywords' && (
        <div>
          <div style={{ ...card, marginBottom: 16 }}>
            <h3 style={{ fontSize: 16, margin: '0 0 12px', color: '#C4972A' }}>Anahtar Kelime Arastirmasi</h3>
            <div style={{ display: 'flex', gap: 8 }}>
              <input value={keywordTopic} onChange={e => setKeywordTopic(e.target.value)} placeholder="Konu giriniz (ornek: kahvalti, havuz, dugun)" style={inputStyle} onKeyDown={e => e.key === 'Enter' && handleKeywordSearch()} />
              <button onClick={handleKeywordSearch} disabled={loading} style={goldBtn}>
                {loading ? <Loader2 size={14} className="animate-spin" /> : <Search size={14} />} Ara
              </button>
            </div>
          </div>
          {keywords && (
            <div style={{ display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
              {[
                { key: 'primary', label: 'Ana Anahtar Kelimeler', color: '#C4972A' },
                { key: 'secondary', label: 'Ikincil Anahtar Kelimeler', color: '#3498db' },
                { key: 'long_tail', label: 'Uzun Kuyruk Kelimeler', color: '#27ae60' },
              ].map(group => (
                <div key={group.key} style={card}>
                  <h4 style={{ fontSize: 14, color: group.color, margin: '0 0 12px' }}>{group.label}</h4>
                  {keywords[group.key]?.map((kw, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #2a2a3e' }}>
                      <span style={{ fontSize: 13 }}>{kw}</span>
                      <button onClick={() => copyToClipboard(kw, `${group.key}-${i}`)} style={{ ...ghostBtn, padding: '4px 8px', fontSize: 11 }}>
                        {copied === `${group.key}-${i}` ? <CheckCircle2 size={12} /> : <Copy size={12} />}
                      </button>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab: Meta Tag Uretici */}
      {tab === 'meta' && (
        <div>
          <div style={{ ...card, marginBottom: 16 }}>
            <h3 style={{ fontSize: 16, margin: '0 0 12px', color: '#C4972A' }}>Meta Tag Uretici (AI Destekli)</h3>
            <div style={{ display: 'grid', gap: 12 }}>
              <div>
                <label style={{ fontSize: 12, color: '#aaa', marginBottom: 4, display: 'block' }}>Sayfa Turu</label>
                <select value={metaPageType} onChange={e => setMetaPageType(e.target.value)} style={{ ...inputStyle, cursor: 'pointer' }}>
                  {['home', 'rooms', 'restaurant', 'events', 'contact', 'blog_post'].map(t => (
                    <option key={t} value={t}>{t.replace('_', ' ').toUpperCase()}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ fontSize: 12, color: '#aaa', marginBottom: 4, display: 'block' }}>Ek Icerik (opsiyonel)</label>
                <textarea value={metaContent} onChange={e => setMetaContent(e.target.value)} placeholder="Sayfa icerigi veya anahtar kelimeler..." style={{ ...inputStyle, height: 80, resize: 'vertical' }} />
              </div>
              <button onClick={handleGenerateMeta} disabled={loading} style={goldBtn}>
                {loading ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />} Meta Tag Uret
              </button>
            </div>
          </div>
          {metaResult && (
            <div style={card}>
              <h4 style={{ fontSize: 14, color: '#C4972A', margin: '0 0 16px' }}>Uretilen Meta Taglar</h4>
              {[
                { label: 'Title', value: metaResult.title },
                { label: 'Description', value: metaResult.description },
                { label: 'OG Image', value: metaResult.og_image },
              ].map(item => (
                <div key={item.label} style={{ marginBottom: 12, padding: 12, background: '#0d0d1a', borderRadius: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontSize: 11, color: '#C4972A', fontWeight: 600 }}>{item.label}</span>
                    <button onClick={() => copyToClipboard(item.value, item.label)} style={{ ...ghostBtn, padding: '2px 6px', fontSize: 10 }}>
                      {copied === item.label ? 'Kopyalandi!' : 'Kopyala'}
                    </button>
                  </div>
                  <div style={{ fontSize: 13, color: '#e5e5e8' }}>{item.value}</div>
                </div>
              ))}
              {metaResult.keywords && (
                <div style={{ padding: 12, background: '#0d0d1a', borderRadius: 8 }}>
                  <span style={{ fontSize: 11, color: '#C4972A', fontWeight: 600 }}>Keywords</span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
                    {(Array.isArray(metaResult.keywords) ? metaResult.keywords : [metaResult.keywords]).map((kw, i) => (
                      <span key={i} style={{ padding: '4px 10px', background: '#2a2a3e', borderRadius: 12, fontSize: 11, color: '#aaa' }}>{kw}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          {/* Templates */}
          {metaTemplates && (
            <div style={{ ...card, marginTop: 16 }}>
              <h4 style={{ fontSize: 14, color: '#aaa', margin: '0 0 12px' }}>Varsayilan Sablonlar</h4>
              {Object.entries(metaTemplates).map(([key, tpl]) => (
                <div key={key} style={{ marginBottom: 12, padding: 12, background: '#0d0d1a', borderRadius: 8 }}>
                  <div style={{ fontSize: 12, color: '#C4972A', fontWeight: 600, marginBottom: 4 }}>{key.toUpperCase()}</div>
                  <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 2 }}>{tpl.title}</div>
                  <div style={{ fontSize: 12, color: '#aaa' }}>{tpl.description}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab: Schema.org */}
      {tab === 'schema' && (
        <div>
          {schemas ? (
            <div style={{ display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))' }}>
              {Object.entries(schemas).map(([type, schema]) => (
                <div key={type} style={card}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                    <h4 style={{ fontSize: 14, color: '#C4972A', margin: 0 }}>
                      <Code size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />{type}
                    </h4>
                    <button onClick={() => copyToClipboard(schema, type)} style={{ ...ghostBtn, padding: '4px 8px', fontSize: 11 }}>
                      {copied === type ? <CheckCircle2 size={12} /> : <Copy size={12} />} {copied === type ? 'Kopyalandi' : 'JSON-LD Kopyala'}
                    </button>
                  </div>
                  <pre style={{ background: '#0d0d1a', borderRadius: 8, padding: 12, fontSize: 11, color: '#8FAA86', overflow: 'auto', maxHeight: 300, margin: 0 }}>
                    {JSON.stringify(schema, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: 40 }}><Loader2 size={32} className="animate-spin" style={{ color: '#C4972A' }} /></div>
          )}
        </div>
      )}

      {/* Tab: SEO Analiz */}
      {tab === 'analyze' && (
        <div>
          <div style={{ ...card, marginBottom: 16 }}>
            <h3 style={{ fontSize: 16, margin: '0 0 12px', color: '#C4972A' }}>Icerik SEO Analizi</h3>
            <p style={{ fontSize: 12, color: '#aaa', margin: '0 0 12px' }}>HTML icerik yapistirin, SEO uyumlulugunu analiz edelim</p>
            <textarea value={analyzeContent} onChange={e => setAnalyzeContent(e.target.value)} placeholder="HTML icerik yapistirin..." style={{ ...inputStyle, height: 150, resize: 'vertical', fontFamily: 'monospace' }} />
            <button onClick={handleAnalyze} disabled={loading || !analyzeContent.trim()} style={{ ...goldBtn, marginTop: 12 }}>
              {loading ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />} Analiz Et
            </button>
          </div>
          {analyzeResult && (
            <div style={card}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
                <div style={{ width: 64, height: 64, borderRadius: '50%', background: analyzeResult.score >= 80 ? '#27ae6020' : analyzeResult.score >= 40 ? '#f39c1220' : '#e74c3c20', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <span style={{ fontSize: 24, fontWeight: 700, color: analyzeResult.score >= 80 ? '#27ae60' : analyzeResult.score >= 40 ? '#f39c12' : '#e74c3c' }}>
                    {analyzeResult.grade}
                  </span>
                </div>
                <div>
                  <div style={{ fontSize: 20, fontWeight: 700 }}>Skor: {analyzeResult.score}/100</div>
                  <div style={{ fontSize: 13, color: '#aaa' }}>{analyzeResult.summary}</div>
                </div>
              </div>
              {/* Category Scores */}
              {analyzeResult.categories && Object.entries(analyzeResult.categories).map(([key, cat]) => (
                <ScoreBar key={key} score={cat.score} max={cat.max} label={key.charAt(0).toUpperCase() + key.slice(1)} />
              ))}
              {/* Suggestions */}
              {analyzeResult.suggestions?.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <h4 style={{ fontSize: 14, color: '#C4972A', margin: '0 0 12px' }}>Iyilestirme Onerileri</h4>
                  {analyzeResult.suggestions.map((s, i) => (
                    <div key={i} style={{ display: 'flex', gap: 8, padding: '8px 0', borderBottom: '1px solid #2a2a3e' }}>
                      <ArrowRight size={14} style={{ color: '#f39c12', flexShrink: 0, marginTop: 2 }} />
                      <span style={{ fontSize: 13, color: '#ccc' }}>{s}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
