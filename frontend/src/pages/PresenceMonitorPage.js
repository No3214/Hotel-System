import React, { useState, useEffect } from 'react';
import {
  getPresencePlatforms, runPresenceAudit, auditSinglePlatform,
  getPresenceHistory, getPresenceAuditDetail, getPresenceTruthSource
} from '../api';
import {
  Globe, Loader2, CheckCircle2, AlertCircle, Eye, Star,
  Clock, ExternalLink, ChevronDown, ChevronRight, Search,
  Play, BarChart3, History, Shield, Camera, FileText,
  MessageCircle, Settings, MapPin, Phone, Mail, Wifi
} from 'lucide-react';

// ==================== STYLES ====================
const card = { background: '#1a1a2e', borderRadius: 12, padding: 20, border: '1px solid #2a2a3e' };
const goldBtn = { background: '#C4972A', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', cursor: 'pointer', fontWeight: 600, fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 6 };
const ghostBtn = { background: 'transparent', color: '#aaa', border: '1px solid #333', borderRadius: 8, padding: '8px 16px', cursor: 'pointer', fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 4 };
const inputStyle = { background: '#0d0d1a', border: '1px solid #2a2a3e', borderRadius: 8, padding: '8px 12px', color: '#e5e5e8', fontSize: 13, width: '100%' };
const selectStyle = { ...inputStyle, cursor: 'pointer' };
const pill = (active) => ({
  padding: '6px 14px', borderRadius: 20, fontSize: 12, fontWeight: 600, cursor: 'pointer', border: 'none',
  background: active ? '#C4972A' : '#2a2a3e', color: active ? '#fff' : '#aaa', transition: 'all 0.2s'
});

const SEVERITY_COLORS = { critical: '#e74c3c', high: '#e67e22', medium: '#f39c12', info: '#3498db' };
const GRADE_COLORS = { A: '#27ae60', B: '#8FAA86', C: '#f39c12', D: '#e67e22', F: '#e74c3c' };

const CATEGORY_ICONS = {
  identity: Shield, visual: Camera, content: FileText, reviews: MessageCircle, technical: Settings
};

const PLATFORM_ICONS = {
  google_business: Globe, booking: Globe, tripadvisor: Star, instagram: Camera,
  facebook: Globe, airbnb: Globe, expedia: Globe, trivago: Search
};

// ==================== HELPERS ====================
const getGrade = (score) => {
  if (score >= 90) return 'A';
  if (score >= 75) return 'B';
  if (score >= 60) return 'C';
  if (score >= 40) return 'D';
  return 'F';
};

const GradeBadge = ({ score, size = 'normal' }) => {
  const grade = getGrade(score);
  const c = GRADE_COLORS[grade];
  const s = size === 'large'
    ? { fontSize: 28, padding: '8px 18px', borderRadius: 12 }
    : { fontSize: 13, padding: '4px 12px', borderRadius: 10 };
  return (
    <span style={{ ...s, fontWeight: 700, background: `${c}20`, color: c, display: 'inline-block' }}>
      {grade} ({Math.round(score)})
    </span>
  );
};

const SeverityBadge = ({ severity }) => {
  const c = SEVERITY_COLORS[severity] || '#888';
  return (
    <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 8, fontWeight: 600, background: `${c}20`, color: c }}>
      {severity}
    </span>
  );
};

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

const Spinner = () => <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />;

// ==================== TAB 1: GENEL BAKIS ====================
function OverviewTab({ platforms, categories, truthSource, lastAudit, onRunAudit, onGoHistory, auditLoading }) {
  const platformEntries = platforms ? Object.entries(platforms) : [];
  const categoryEntries = categories ? Object.entries(categories) : [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Truth Source */}
      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
          <Shield size={18} color="#C4972A" />
          <span style={{ fontSize: 16, fontWeight: 700, color: '#e5e5e8' }}>Dogru Bilgi Kaynagi (Truth Source)</span>
        </div>
        {truthSource ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 14 }}>
            {truthSource.name && (
              <div><span style={{ fontSize: 11, color: '#888' }}>Otel Adi</span><div style={{ color: '#e5e5e8', fontSize: 14, fontWeight: 600 }}>{truthSource.name}</div></div>
            )}
            {truthSource.address && (
              <div><span style={{ fontSize: 11, color: '#888' }}>Adres</span><div style={{ color: '#e5e5e8', fontSize: 13 }}>{truthSource.address}</div></div>
            )}
            {truthSource.phone && (
              <div><span style={{ fontSize: 11, color: '#888' }}>Telefon</span><div style={{ color: '#e5e5e8', fontSize: 13 }}>{truthSource.phone}</div></div>
            )}
            {truthSource.email && (
              <div><span style={{ fontSize: 11, color: '#888' }}>E-posta</span><div style={{ color: '#e5e5e8', fontSize: 13 }}>{truthSource.email}</div></div>
            )}
            {truthSource.website && (
              <div><span style={{ fontSize: 11, color: '#888' }}>Website</span><div style={{ color: '#C4972A', fontSize: 13 }}>{truthSource.website}</div></div>
            )}
            {truthSource.check_in && (
              <div><span style={{ fontSize: 11, color: '#888' }}>Check-in</span><div style={{ color: '#e5e5e8', fontSize: 13 }}>{truthSource.check_in}</div></div>
            )}
            {truthSource.check_out && (
              <div><span style={{ fontSize: 11, color: '#888' }}>Check-out</span><div style={{ color: '#e5e5e8', fontSize: 13 }}>{truthSource.check_out}</div></div>
            )}
          </div>
        ) : (
          <span style={{ color: '#666', fontSize: 13 }}>Bilgi yuklenemiyor.</span>
        )}
      </div>

      {/* Platforms Grid */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <Globe size={18} color="#C4972A" />
          <span style={{ fontSize: 16, fontWeight: 700, color: '#e5e5e8' }}>Platformlar</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 }}>
          {platformEntries.map(([id, p]) => {
            const Icon = PLATFORM_ICONS[id] || Globe;
            const result = lastAudit?.platform_results?.[id];
            return (
              <div key={id} style={{ ...card, padding: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Icon size={16} color="#C4972A" />
                    <span style={{ fontWeight: 700, color: '#e5e5e8', fontSize: 14 }}>{p.name}</span>
                  </div>
                  <div style={{ display: 'flex', gap: 4 }}>
                    <span style={{ fontSize: 10, padding: '2px 6px', borderRadius: 6, background: '#2a2a3e', color: '#aaa' }}>{p.type}</span>
                    <span style={{ fontSize: 10, padding: '2px 6px', borderRadius: 6, background: p.priority === 'critical' ? '#e74c3c20' : p.priority === 'high' ? '#e67e2220' : '#2a2a3e', color: p.priority === 'critical' ? '#e74c3c' : p.priority === 'high' ? '#e67e22' : '#aaa' }}>
                      {p.priority}
                    </span>
                  </div>
                </div>
                {p.url && (
                  <a href={p.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: 11, color: '#C4972A', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 4, marginBottom: 8 }}>
                    <ExternalLink size={11} /> Platforma Git
                  </a>
                )}
                {result ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
                    <GradeBadge score={result.score || 0} />
                    {result.issues_count !== undefined && (
                      <span style={{ fontSize: 11, color: '#888' }}>{result.issues_count} sorun</span>
                    )}
                  </div>
                ) : (
                  <span style={{ fontSize: 11, color: '#555' }}>Henuz denetlenmedi</span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Categories */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <BarChart3 size={18} color="#C4972A" />
          <span style={{ fontSize: 16, fontWeight: 700, color: '#e5e5e8' }}>Kategoriler</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 14 }}>
          {categoryEntries.map(([id, cat]) => {
            const CatIcon = CATEGORY_ICONS[id] || CheckCircle2;
            const catScore = lastAudit?.category_scores?.[id];
            return (
              <div key={id} style={{ ...card, padding: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <CatIcon size={15} color="#C4972A" />
                  <span style={{ fontWeight: 600, color: '#e5e5e8', fontSize: 13 }}>{cat.label}</span>
                </div>
                <div style={{ fontSize: 11, color: '#888', marginBottom: 6 }}>{cat.description}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 12, color: '#C4972A', fontWeight: 600 }}>Agirlik: %{Math.round(cat.weight * 100)}</span>
                  {catScore !== undefined && <GradeBadge score={catScore} />}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Actions */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <button onClick={onRunAudit} disabled={auditLoading} style={{ ...goldBtn, opacity: auditLoading ? 0.6 : 1 }}>
          {auditLoading ? <Spinner /> : <Play size={14} />} Toplu Denetim Baslat
        </button>
        <button onClick={onGoHistory} style={ghostBtn}>
          <History size={14} /> Gecmisi Gor
        </button>
      </div>
    </div>
  );
}

// ==================== TAB 2: PLATFORM DENETIMI ====================
function AuditTab({ platforms, truthSource }) {
  const [selectedPlatform, setSelectedPlatform] = useState('');
  const [formData, setFormData] = useState({});
  const [auditResult, setAuditResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const platformEntries = platforms ? Object.entries(platforms) : [];
  const currentPlatform = platforms?.[selectedPlatform];

  useEffect(() => {
    if (selectedPlatform && truthSource) {
      setFormData({
        name: truthSource.name || '',
        address: truthSource.address || '',
        phone: truthSource.phone || '',
        email: truthSource.email || '',
        website: truthSource.website || '',
        photo_count: '',
        cover_photo_ok: true,
        outdated_photos: false,
        description: '',
        description_checked: false,
        room_count: '',
        amenities_wifi: true,
        amenities_parking: true,
        amenities_pool: false,
        amenities_spa: false,
        rating: '',
        review_count: '',
        response_rate: '',
        unanswered_negative: '0',
        check_in: truthSource.check_in || '14:00',
        check_out: truthSource.check_out || '11:00',
        latitude: truthSource.latitude || '',
        longitude: truthSource.longitude || ''
      });
      setAuditResult(null);
      setError(null);
    }
  }, [selectedPlatform, truthSource]);

  const updateField = (field, value) => setFormData(prev => ({ ...prev, [field]: value }));

  const handleAudit = async () => {
    if (!selectedPlatform) return;
    setLoading(true);
    setError(null);
    try {
      const res = await auditSinglePlatform({ platform_id: selectedPlatform, data: formData });
      setAuditResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Denetim sirasinda hata olustu.');
    } finally {
      setLoading(false);
    }
  };

  const checks = currentPlatform?.checks || {};
  const hasCategory = (cat) => checks[cat] && checks[cat].length > 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Platform Selector */}
      <div style={card}>
        <label style={{ fontSize: 13, color: '#888', marginBottom: 6, display: 'block' }}>Platform Secin</label>
        <select
          value={selectedPlatform}
          onChange={e => setSelectedPlatform(e.target.value)}
          style={{ ...selectStyle, maxWidth: 350 }}
        >
          <option value="">-- Platform Secin --</option>
          {platformEntries.map(([id, p]) => (
            <option key={id} value={id}>{p.name}</option>
          ))}
        </select>
      </div>

      {/* Form */}
      {selectedPlatform && currentPlatform && (
        <div style={card}>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#e5e5e8', marginBottom: 16 }}>
            {currentPlatform.name} - Denetim Verileri
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Identity */}
            {hasCategory('identity') && (
              <fieldset style={{ border: '1px solid #2a2a3e', borderRadius: 10, padding: 16 }}>
                <legend style={{ color: '#C4972A', fontWeight: 600, fontSize: 13, padding: '0 8px' }}>
                  <Shield size={13} style={{ marginRight: 4, verticalAlign: 'middle' }} /> Kimlik (Identity)
                </legend>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <div>
                    <label style={{ fontSize: 11, color: '#888' }}>Otel Adi</label>
                    <input style={inputStyle} value={formData.name || ''} onChange={e => updateField('name', e.target.value)} />
                  </div>
                  <div>
                    <label style={{ fontSize: 11, color: '#888' }}>Telefon</label>
                    <input style={inputStyle} value={formData.phone || ''} onChange={e => updateField('phone', e.target.value)} />
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <label style={{ fontSize: 11, color: '#888' }}>Adres</label>
                    <input style={inputStyle} value={formData.address || ''} onChange={e => updateField('address', e.target.value)} />
                  </div>
                  <div>
                    <label style={{ fontSize: 11, color: '#888' }}>E-posta</label>
                    <input style={inputStyle} value={formData.email || ''} onChange={e => updateField('email', e.target.value)} />
                  </div>
                  <div>
                    <label style={{ fontSize: 11, color: '#888' }}>Website</label>
                    <input style={inputStyle} value={formData.website || ''} onChange={e => updateField('website', e.target.value)} />
                  </div>
                </div>
              </fieldset>
            )}

            {/* Visual */}
            {hasCategory('visual') && (
              <fieldset style={{ border: '1px solid #2a2a3e', borderRadius: 10, padding: 16 }}>
                <legend style={{ color: '#C4972A', fontWeight: 600, fontSize: 13, padding: '0 8px' }}>
                  <Camera size={13} style={{ marginRight: 4, verticalAlign: 'middle' }} /> Gorsel (Visual)
                </legend>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
                  <div>
                    <label style={{ fontSize: 11, color: '#888' }}>Fotograf Sayisi</label>
                    <input type="number" style={inputStyle} value={formData.photo_count || ''} onChange={e => updateField('photo_count', e.target.value)} />
                  </div>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#e5e5e8', fontSize: 13, cursor: 'pointer' }}>
                    <input type="checkbox" checked={formData.cover_photo_ok || false} onChange={e => updateField('cover_photo_ok', e.target.checked)} />
                    Kapak Fotografi Uygun
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#e5e5e8', fontSize: 13, cursor: 'pointer' }}>
                    <input type="checkbox" checked={formData.outdated_photos || false} onChange={e => updateField('outdated_photos', e.target.checked)} />
                    Eski Fotograflar Var
                  </label>
                </div>
              </fieldset>
            )}

            {/* Content */}
            {hasCategory('content') && (
              <fieldset style={{ border: '1px solid #2a2a3e', borderRadius: 10, padding: 16 }}>
                <legend style={{ color: '#C4972A', fontWeight: 600, fontSize: 13, padding: '0 8px' }}>
                  <FileText size={13} style={{ marginRight: 4, verticalAlign: 'middle' }} /> Icerik (Content)
                </legend>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  <div>
                    <label style={{ fontSize: 11, color: '#888' }}>Aciklama</label>
                    <textarea rows={3} style={{ ...inputStyle, resize: 'vertical' }} value={formData.description || ''} onChange={e => updateField('description', e.target.value)} />
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                    <div>
                      <label style={{ fontSize: 11, color: '#888' }}>Oda Sayisi</label>
                      <input type="number" style={inputStyle} value={formData.room_count || ''} onChange={e => updateField('room_count', e.target.value)} />
                    </div>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#e5e5e8', fontSize: 13, cursor: 'pointer' }}>
                      <input type="checkbox" checked={formData.description_checked || false} onChange={e => updateField('description_checked', e.target.checked)} />
                      Aciklama Kontrol Edildi
                    </label>
                  </div>
                  <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                    <span style={{ fontSize: 12, color: '#888', fontWeight: 600 }}>Olanaklar:</span>
                    {['wifi', 'parking', 'pool', 'spa'].map(a => (
                      <label key={a} style={{ display: 'flex', alignItems: 'center', gap: 4, color: '#e5e5e8', fontSize: 12, cursor: 'pointer' }}>
                        <input type="checkbox" checked={formData[`amenities_${a}`] || false} onChange={e => updateField(`amenities_${a}`, e.target.checked)} />
                        {a.charAt(0).toUpperCase() + a.slice(1)}
                      </label>
                    ))}
                  </div>
                </div>
              </fieldset>
            )}

            {/* Reviews */}
            {hasCategory('reviews') && (
              <fieldset style={{ border: '1px solid #2a2a3e', borderRadius: 10, padding: 16 }}>
                <legend style={{ color: '#C4972A', fontWeight: 600, fontSize: 13, padding: '0 8px' }}>
                  <MessageCircle size={13} style={{ marginRight: 4, verticalAlign: 'middle' }} /> Yorumlar (Reviews)
                </legend>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <div>
                    <label style={{ fontSize: 11, color: '#888' }}>Puan (1-5)</label>
                    <input type="number" min="1" max="5" step="0.1" style={inputStyle} value={formData.rating || ''} onChange={e => updateField('rating', e.target.value)} />
                  </div>
                  <div>
                    <label style={{ fontSize: 11, color: '#888' }}>Yorum Sayisi</label>
                    <input type="number" style={inputStyle} value={formData.review_count || ''} onChange={e => updateField('review_count', e.target.value)} />
                  </div>
                  <div>
                    <label style={{ fontSize: 11, color: '#888' }}>Yanit Orani (%)</label>
                    <input type="number" min="0" max="100" style={inputStyle} value={formData.response_rate || ''} onChange={e => updateField('response_rate', e.target.value)} />
                  </div>
                  <div>
                    <label style={{ fontSize: 11, color: '#888' }}>Yanitlanmamis Olumsuz</label>
                    <input type="number" style={inputStyle} value={formData.unanswered_negative || ''} onChange={e => updateField('unanswered_negative', e.target.value)} />
                  </div>
                </div>
              </fieldset>
            )}

            {/* Technical */}
            {hasCategory('technical') && (
              <fieldset style={{ border: '1px solid #2a2a3e', borderRadius: 10, padding: 16 }}>
                <legend style={{ color: '#C4972A', fontWeight: 600, fontSize: 13, padding: '0 8px' }}>
                  <Settings size={13} style={{ marginRight: 4, verticalAlign: 'middle' }} /> Teknik (Technical)
                </legend>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <div>
                    <label style={{ fontSize: 11, color: '#888' }}>Check-in Saati</label>
                    <input type="time" style={inputStyle} value={formData.check_in || ''} onChange={e => updateField('check_in', e.target.value)} />
                  </div>
                  <div>
                    <label style={{ fontSize: 11, color: '#888' }}>Check-out Saati</label>
                    <input type="time" style={inputStyle} value={formData.check_out || ''} onChange={e => updateField('check_out', e.target.value)} />
                  </div>
                  <div>
                    <label style={{ fontSize: 11, color: '#888' }}>Enlem (Latitude)</label>
                    <input type="text" style={inputStyle} value={formData.latitude || ''} onChange={e => updateField('latitude', e.target.value)} />
                  </div>
                  <div>
                    <label style={{ fontSize: 11, color: '#888' }}>Boylam (Longitude)</label>
                    <input type="text" style={inputStyle} value={formData.longitude || ''} onChange={e => updateField('longitude', e.target.value)} />
                  </div>
                </div>
              </fieldset>
            )}
          </div>

          <div style={{ marginTop: 16 }}>
            <button onClick={handleAudit} disabled={loading} style={{ ...goldBtn, opacity: loading ? 0.6 : 1 }}>
              {loading ? <Spinner /> : <Play size={14} />} Denetimi Baslat
            </button>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{ ...card, borderColor: '#e74c3c40', background: '#e74c3c10' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#e74c3c' }}>
            <AlertCircle size={16} />
            <span style={{ fontSize: 13 }}>{error}</span>
          </div>
        </div>
      )}

      {/* Results */}
      {auditResult && (
        <div style={card}>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#e5e5e8', marginBottom: 16 }}>Denetim Sonuclari</div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
            <GradeBadge score={auditResult.overall_score || auditResult.score || 0} size="large" />
            <div>
              <div style={{ fontSize: 13, color: '#888' }}>Genel Puan</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: '#e5e5e8' }}>{Math.round(auditResult.overall_score || auditResult.score || 0)}/100</div>
            </div>
          </div>

          {/* Category Scores */}
          {auditResult.category_scores && (
            <div style={{ marginBottom: 20 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#aaa', marginBottom: 10 }}>Kategori Puanlari</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 10 }}>
                {Object.entries(auditResult.category_scores).map(([cat, score]) => {
                  const CatIcon = CATEGORY_ICONS[cat] || CheckCircle2;
                  return (
                    <div key={cat} style={{ background: '#0d0d1a', borderRadius: 8, padding: 12, border: '1px solid #2a2a3e' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                        <CatIcon size={13} color="#888" />
                        <span style={{ fontSize: 12, color: '#aaa', textTransform: 'capitalize' }}>{cat}</span>
                      </div>
                      <GradeBadge score={score} />
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Issues */}
          {auditResult.issues && auditResult.issues.length > 0 && (
            <div>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#aaa', marginBottom: 10 }}>
                Sorunlar ({auditResult.issues.length})
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {auditResult.issues.map((issue, idx) => (
                  <div key={idx} style={{ background: '#0d0d1a', borderRadius: 8, padding: 12, border: '1px solid #2a2a3e' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                      <SeverityBadge severity={issue.severity} />
                      <span style={{ fontSize: 11, color: '#666', textTransform: 'capitalize' }}>{issue.category}</span>
                    </div>
                    <div style={{ fontSize: 13, color: '#e5e5e8', marginBottom: 4 }}>{issue.message}</div>
                    {issue.fix && (
                      <div style={{ fontSize: 12, color: '#8FAA86', display: 'flex', alignItems: 'flex-start', gap: 4, marginTop: 4 }}>
                        <CheckCircle2 size={12} style={{ marginTop: 2, flexShrink: 0 }} /> {issue.fix}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {auditResult.issues && auditResult.issues.length === 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#27ae60', fontSize: 14 }}>
              <CheckCircle2 size={16} /> Sorun bulunamadi, harika!
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ==================== TAB 3: GECMIS ====================
function HistoryTab() {
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  const [detail, setDetail] = useState({});

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const res = await getPresenceHistory(20);
      setAudits(res.data?.audits || []);
    } catch (err) {
      setError('Gecmis yuklenirken hata olustu.');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = async (id) => {
    if (expandedId === id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(id);
    if (!detail[id]) {
      try {
        const res = await getPresenceAuditDetail(id);
        setDetail(prev => ({ ...prev, [id]: res.data }));
      } catch {
        setDetail(prev => ({ ...prev, [id]: { error: true } }));
      }
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ ...card, borderColor: '#e74c3c40' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#e74c3c' }}>
          <AlertCircle size={16} /> <span style={{ fontSize: 13 }}>{error}</span>
        </div>
      </div>
    );
  }

  if (audits.length === 0) {
    return (
      <div style={{ ...card, textAlign: 'center', padding: 40 }}>
        <History size={32} color="#333" style={{ marginBottom: 8 }} />
        <div style={{ color: '#666', fontSize: 14 }}>Henuz denetim gecmisi bulunmuyor.</div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {/* Table Header */}
      <div style={{ display: 'grid', gridTemplateColumns: '40px 1fr 100px 80px 100px 100px', gap: 12, padding: '8px 16px', fontSize: 11, color: '#666', fontWeight: 600 }}>
        <span></span>
        <span>Tarih</span>
        <span>Puan</span>
        <span>Not</span>
        <span>Toplam Sorun</span>
        <span>Kritik</span>
      </div>

      {audits.map(audit => {
        const expanded = expandedId === audit.id;
        const d = detail[audit.id];
        const criticalCount = audit.critical_issues ?? audit.issues?.filter(i => i.severity === 'critical').length ?? 0;
        const totalIssues = audit.total_issues ?? audit.issues?.length ?? 0;

        return (
          <div key={audit.id}>
            <div
              onClick={() => toggleExpand(audit.id)}
              style={{ ...card, padding: '12px 16px', cursor: 'pointer', display: 'grid', gridTemplateColumns: '40px 1fr 100px 80px 100px 100px', gap: 12, alignItems: 'center', transition: 'background 0.2s' }}
            >
              <span>{expanded ? <ChevronDown size={16} color="#888" /> : <ChevronRight size={16} color="#888" />}</span>
              <span style={{ fontSize: 13, color: '#e5e5e8' }}>
                {audit.created_at ? new Date(audit.created_at).toLocaleString('tr-TR') : '-'}
              </span>
              <span style={{ fontSize: 14, fontWeight: 700, color: '#e5e5e8' }}>{Math.round(audit.overall_score || 0)}</span>
              <span><GradeBadge score={audit.overall_score || 0} /></span>
              <span style={{ fontSize: 13, color: '#aaa' }}>{totalIssues}</span>
              <span style={{ fontSize: 13, color: criticalCount > 0 ? '#e74c3c' : '#666', fontWeight: criticalCount > 0 ? 700 : 400 }}>
                {criticalCount}
              </span>
            </div>

            {expanded && (
              <div style={{ background: '#12122a', borderRadius: '0 0 12px 12px', padding: 16, marginTop: -4, border: '1px solid #2a2a3e', borderTop: 'none' }}>
                {!d ? (
                  <div style={{ display: 'flex', justifyContent: 'center', padding: 16 }}><Spinner /></div>
                ) : d.error ? (
                  <span style={{ color: '#e74c3c', fontSize: 13 }}>Detay yuklenemedi.</span>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {/* Platform Results */}
                    {d.platform_results && (
                      <div>
                        <div style={{ fontSize: 12, fontWeight: 600, color: '#888', marginBottom: 8 }}>Platform Sonuclari</div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 8 }}>
                          {Object.entries(d.platform_results).map(([pid, pr]) => (
                            <div key={pid} style={{ background: '#1a1a2e', borderRadius: 8, padding: 10, border: '1px solid #2a2a3e' }}>
                              <div style={{ fontSize: 12, color: '#aaa', marginBottom: 4 }}>{pid.replace(/_/g, ' ')}</div>
                              <GradeBadge score={pr.score || 0} />
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Issues Summary */}
                    {d.issues && d.issues.length > 0 && (
                      <div>
                        <div style={{ fontSize: 12, fontWeight: 600, color: '#888', marginBottom: 8 }}>Sorunlar ({d.issues.length})</div>
                        {d.issues.slice(0, 10).map((issue, idx) => (
                          <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0', fontSize: 12 }}>
                            <SeverityBadge severity={issue.severity} />
                            <span style={{ color: '#e5e5e8' }}>{issue.message}</span>
                          </div>
                        ))}
                        {d.issues.length > 10 && (
                          <div style={{ fontSize: 11, color: '#666', marginTop: 4 }}>
                            ... ve {d.issues.length - 10} sorun daha
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ==================== MAIN PAGE ====================
export default function PresenceMonitorPage() {
  const [tab, setTab] = useState('overview');
  const [platforms, setPlatforms] = useState(null);
  const [categories, setCategories] = useState(null);
  const [truthSource, setTruthSource] = useState(null);
  const [lastAudit, setLastAudit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [auditLoading, setAuditLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [platformsRes, truthRes, historyRes] = await Promise.all([
        getPresencePlatforms(),
        getPresenceTruthSource(),
        getPresenceHistory(1)
      ]);
      setPlatforms(platformsRes.data?.platforms || null);
      setCategories(platformsRes.data?.categories || null);
      setTruthSource(truthRes.data?.truth_source || platformsRes.data?.truth_source || null);

      const audits = historyRes.data?.audits || [];
      if (audits.length > 0) {
        setLastAudit(audits[0]);
      }
    } catch (err) {
      setError('Veriler yuklenirken hata olustu.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunFullAudit = async () => {
    if (!platforms || !truthSource) return;
    setAuditLoading(true);
    try {
      const platformData = {};
      Object.keys(platforms).forEach(id => {
        platformData[id] = {
          name: truthSource.name || '',
          address: truthSource.address || '',
          phone: truthSource.phone || '',
          email: truthSource.email || '',
          website: truthSource.website || ''
        };
      });
      const res = await runPresenceAudit({ platforms: platformData });
      setLastAudit(res.data);
    } catch (err) {
      setError('Toplu denetim sirasinda hata olustu.');
    } finally {
      setAuditLoading(false);
    }
  };

  const overallScore = lastAudit?.overall_score;

  return (
    <div style={{ background: '#0d0d1a', minHeight: '100vh', color: '#e5e5e8', padding: '24px 32px' }}>
      {/* CSS for spinner */}
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Eye size={24} color="#C4972A" />
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0, color: '#e5e5e8' }}>Online Varlik Izleme</h1>
            <span style={{ fontSize: 12, color: '#666' }}>Kozbeyli Konagi - OTA ve platform gorunurluk denetimi</span>
          </div>
        </div>
        {overallScore !== undefined && overallScore !== null && (
          <GradeBadge score={overallScore} size="large" />
        )}
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 24, flexWrap: 'wrap' }}>
        <TabButton active={tab === 'overview'} onClick={() => setTab('overview')} icon={BarChart3} label="Genel Bakis" />
        <TabButton active={tab === 'audit'} onClick={() => setTab('audit')} icon={Search} label="Platform Denetimi" />
        <TabButton active={tab === 'history'} onClick={() => setTab('history')} icon={History} label="Gecmis" />
      </div>

      {/* Error */}
      {error && (
        <div style={{ ...card, borderColor: '#e74c3c40', background: '#e74c3c10', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#e74c3c' }}>
            <AlertCircle size={16} />
            <span style={{ fontSize: 13 }}>{error}</span>
            <button onClick={() => setError(null)} style={{ ...ghostBtn, marginLeft: 'auto', padding: '4px 10px', fontSize: 11 }}>Kapat</button>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: 60 }}>
          <Loader2 size={28} color="#C4972A" style={{ animation: 'spin 1s linear infinite' }} />
        </div>
      ) : (
        <>
          {tab === 'overview' && (
            <OverviewTab
              platforms={platforms}
              categories={categories}
              truthSource={truthSource}
              lastAudit={lastAudit}
              onRunAudit={handleRunFullAudit}
              onGoHistory={() => setTab('history')}
              auditLoading={auditLoading}
            />
          )}
          {tab === 'audit' && (
            <AuditTab platforms={platforms} truthSource={truthSource} />
          )}
          {tab === 'history' && (
            <HistoryTab />
          )}
        </>
      )}
    </div>
  );
}
