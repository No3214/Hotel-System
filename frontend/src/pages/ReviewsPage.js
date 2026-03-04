import React, { useState, useEffect, useCallback } from 'react';
import { getReviews, createReview, generateReviewResponse, updateReview, deleteReview, getReviewStats, postReviewToGoogle, syncGoogleReviews, getGoogleReviewConfig } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Star, Plus, Trash2, Sparkles, Copy, Check, RefreshCw, MessageSquare, TrendingUp, Send, Settings, ExternalLink, AlertCircle } from 'lucide-react';

const TONES = [
  { value: 'professional', label: 'Profesyonel' },
  { value: 'friendly', label: 'Samimi' },
  { value: 'formal', label: 'Resmi' },
];

function StarRating({ rating, onChange, interactive = false }) {
  return (
    <div className="flex gap-1" data-testid="star-rating">
      {[1, 2, 3, 4, 5].map(i => (
        <Star
          key={i}
          className={`w-5 h-5 transition-colors ${i <= rating ? 'text-[#C4972A] fill-[#C4972A]' : 'text-[#3a3a45]'} ${interactive ? 'cursor-pointer hover:text-[#C4972A]' : ''}`}
          onClick={() => interactive && onChange?.(i)}
          data-testid={`star-${i}`}
        />
      ))}
    </div>
  );
}

function ReviewCard({ review, onGenerate, onDelete, onPostToGoogle, generating, posting }) {
  const [copied, setCopied] = useState(false);
  const [tone, setTone] = useState('professional');
  const [editedResponse, setEditedResponse] = useState(review.ai_response || '');
  const [saving, setSaving] = useState(false);

  useEffect(() => { setEditedResponse(review.ai_response || ''); }, [review.ai_response]);

  const copyResponse = () => {
    navigator.clipboard.writeText(editedResponse);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const saveEdited = async () => {
    if (editedResponse === review.ai_response) return;
    setSaving(true);
    await updateReview(review.id, { ai_response: editedResponse }).catch(console.error);
    setSaving(false);
  };

  return (
    <div className="bg-[#12121a] border border-white/5 rounded-xl p-5 space-y-4 hover:border-[#C4972A]/20 transition-colors" data-testid={`review-card-${review.id}`}>
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#C4972A] to-[#8a5f1a] flex items-center justify-center text-white font-semibold text-sm">
              {review.reviewer_name?.charAt(0)?.toUpperCase() || '?'}
            </div>
            <div>
              <p className="text-white font-medium text-sm" data-testid="reviewer-name">{review.reviewer_name}</p>
              <div className="flex items-center gap-2">
                <StarRating rating={review.rating} />
                <Badge variant="outline" className="text-[10px] border-white/10 text-[#7e7e8a]">
                  {review.platform === 'google' ? 'Google' : review.platform}
                </Badge>
                {review.google_reply_posted && (
                  <Badge className="bg-emerald-500/10 text-emerald-400 border-0 text-[10px]">
                    <Check className="w-2.5 h-2.5 mr-0.5" /> Google'a Gonderildi
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </div>
        <div className="flex gap-1">
          <Button size="icon" variant="ghost" className="h-7 w-7 text-[#7e7e8a] hover:text-red-400 hover:bg-red-400/10"
            onClick={() => onDelete(review.id)} data-testid={`delete-review-${review.id}`}>
            <Trash2 className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>

      {/* Review text */}
      <p className="text-[#c8c8d0] text-sm leading-relaxed bg-white/3 rounded-lg p-3 border-l-2 border-[#C4972A]/30" data-testid="review-text">
        "{review.review_text}"
      </p>

      {/* AI Response Section */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-[#C4972A]" />
          <span className="text-xs font-medium text-[#C4972A] uppercase tracking-wide">AI Yanit</span>
          {review.ai_response && (
            <Badge className="bg-emerald-500/10 text-emerald-400 border-0 text-[10px]">Hazir</Badge>
          )}
        </div>

        {review.ai_response ? (
          <div className="space-y-2">
            <textarea
              value={editedResponse}
              onChange={e => setEditedResponse(e.target.value)}
              className="w-full bg-[#0f0f14] border border-white/10 rounded-lg p-3 text-sm text-[#e5e5e8] resize-none focus:border-[#C4972A]/40 focus:outline-none transition-colors"
              rows={4}
              data-testid={`response-textarea-${review.id}`}
            />
            <div className="flex items-center gap-2 flex-wrap">
              <Button size="sm" variant="outline" className="h-7 text-xs border-white/10 text-[#a9a9b2] hover:border-[#C4972A]/30 hover:text-[#C4972A]"
                onClick={copyResponse} data-testid={`copy-response-${review.id}`}>
                {copied ? <Check className="w-3 h-3 mr-1" /> : <Copy className="w-3 h-3 mr-1" />}
                {copied ? 'Kopyalandi' : 'Kopyala'}
              </Button>
              {editedResponse !== review.ai_response && (
                <Button size="sm" className="h-7 text-xs bg-[#C4972A] hover:bg-[#a87a1f] text-white"
                  onClick={saveEdited} disabled={saving} data-testid={`save-response-${review.id}`}>
                  {saving ? 'Kaydediliyor...' : 'Kaydet'}
                </Button>
              )}
              {review.google_review_name && !review.google_reply_posted && (
                <Button size="sm" className="h-7 text-xs bg-blue-600 hover:bg-blue-700 text-white"
                  onClick={() => onPostToGoogle(review.id)} disabled={posting === review.id}>
                  <Send className="w-3 h-3 mr-1" />
                  {posting === review.id ? 'Gonderiliyor...' : "Google'a Gonder"}
                </Button>
              )}
              <div className="flex-1" />
              <select value={tone} onChange={e => setTone(e.target.value)}
                className="h-7 bg-[#0f0f14] border border-white/10 rounded text-xs text-[#a9a9b2] px-2" data-testid={`tone-select-${review.id}`}>
                {TONES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
              <Button size="sm" className="h-7 text-xs bg-white/5 hover:bg-[#C4972A]/15 text-[#C4972A] border border-[#C4972A]/20"
                onClick={() => onGenerate(review.id, tone)} disabled={generating === review.id} data-testid={`regenerate-${review.id}`}>
                <RefreshCw className={`w-3 h-3 mr-1 ${generating === review.id ? 'animate-spin' : ''}`} />
                Yeniden Olustur
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <select value={tone} onChange={e => setTone(e.target.value)}
              className="h-8 bg-[#0f0f14] border border-white/10 rounded text-xs text-[#a9a9b2] px-2" data-testid={`tone-select-new-${review.id}`}>
              {TONES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
            <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white text-xs h-8"
              onClick={() => onGenerate(review.id, tone)} disabled={generating === review.id} data-testid={`generate-response-${review.id}`}>
              {generating === review.id ? (
                <><RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" /> Olusturuluyor...</>
              ) : (
                <><Sparkles className="w-3.5 h-3.5 mr-1.5" /> AI Yanit Olustur</>
              )}
            </Button>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-white/5">
        <span className="text-[10px] text-[#5a5a65]">
          {review.review_date || review.created_at?.split('T')[0]}
        </span>
        {review.responded_at && (
          <span className="text-[10px] text-emerald-400/60">
            Yanitlandi: {typeof review.responded_at === 'string' ? review.responded_at.split('T')[0] : ''}
          </span>
        )}
      </div>
    </div>
  );
}

export default function ReviewsPage() {
  const [reviews, setReviews] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(null);
  const [posting, setPosting] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [open, setOpen] = useState(false);
  const [configOpen, setConfigOpen] = useState(false);
  const [googleConfig, setGoogleConfig] = useState(null);
  const [form, setForm] = useState({ reviewer_name: '', rating: 5, review_text: '', platform: 'google', review_date: '' });

  const load = useCallback(() => {
    Promise.all([
      getReviews().then(r => setReviews(r.data.reviews)),
      getReviewStats().then(r => setStats(r.data)),
    ]).catch(console.error).finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async () => {
    if (!form.reviewer_name || !form.review_text) return;
    await createReview(form);
    setForm({ reviewer_name: '', rating: 5, review_text: '', platform: 'google', review_date: '' });
    setOpen(false);
    load();
  };

  const handleGenerate = async (reviewId, tone) => {
    setGenerating(reviewId);
    try { await generateReviewResponse(reviewId, tone); load(); } catch (err) { console.error(err); }
    setGenerating(null);
  };

  const handlePostToGoogle = async (reviewId) => {
    setPosting(reviewId);
    try {
      const res = await postReviewToGoogle(reviewId);
      if (res.data.posted) {
        load();
      } else {
        alert(res.data.reason || 'Google API hatasi');
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Google API baglantisi ayarlanmamis');
    }
    setPosting(null);
  };

  const handleSyncGoogle = async () => {
    setSyncing(true);
    try {
      const res = await syncGoogleReviews();
      if (res.data.success) {
        alert(`${res.data.synced} yeni yorum senkronize edildi`);
        load();
      } else {
        setConfigOpen(true);
        // Load config for setup guide
        try {
          const cfg = await getGoogleReviewConfig();
          setGoogleConfig(cfg.data);
        } catch (e) { console.error(e); }
      }
    } catch (err) { console.error(err); }
    setSyncing(false);
  };

  const handleDelete = async (id) => {
    await deleteReview(id).catch(console.error);
    load();
  };

  const loadConfig = async () => {
    try {
      const cfg = await getGoogleReviewConfig();
      setGoogleConfig(cfg.data);
      setConfigOpen(true);
    } catch (e) { console.error(e); }
  };

  if (loading) {
    return (
      <div className="p-8 space-y-6">
        <div className="h-8 w-64 bg-white/5 rounded animate-pulse" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="h-48 bg-white/5 rounded-xl animate-pulse" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="reviews-page">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]" data-testid="reviews-title">Google Yorumlari</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">AI destekli profesyonel yorum yanitlama + Google API entegrasyonu</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <Button variant="outline" className="border-white/10 text-[#7e7e8a] hover:text-[#C4972A] hover:border-[#C4972A]/30 text-xs"
            onClick={loadConfig}>
            <Settings className="w-3.5 h-3.5 mr-1.5" /> Google API Ayarlari
          </Button>
          <Button variant="outline" className="border-blue-500/30 text-blue-400 hover:bg-blue-500/10 text-xs"
            onClick={handleSyncGoogle} disabled={syncing}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Senkronize Ediliyor...' : "Google'dan Cek"}
          </Button>
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-review-btn">
                <Plus className="w-4 h-4 mr-2" /> Yorum Ekle
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
              <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Google Yorumu</DialogTitle></DialogHeader>
              <div className="space-y-3">
                <Input placeholder="Misafir adi *" value={form.reviewer_name}
                  onChange={e => setForm({ ...form, reviewer_name: e.target.value })}
                  className="bg-white/5 border-white/10 text-white" data-testid="review-name-input" />
                <div className="space-y-1">
                  <label className="text-xs text-[#7e7e8a]">Puan</label>
                  <StarRating rating={form.rating} onChange={r => setForm({ ...form, rating: r })} interactive />
                </div>
                <textarea
                  placeholder="Yorum metni *"
                  value={form.review_text}
                  onChange={e => setForm({ ...form, review_text: e.target.value })}
                  className="w-full bg-white/5 border border-white/10 rounded-md p-3 text-sm text-white resize-none focus:border-[#C4972A]/40 focus:outline-none"
                  rows={4}
                  data-testid="review-text-input"
                />
                <Input type="date" value={form.review_date}
                  onChange={e => setForm({ ...form, review_date: e.target.value })}
                  className="bg-white/5 border-white/10 text-white" data-testid="review-date-input" />
                <Button className="w-full bg-[#C4972A] hover:bg-[#a87a1f] text-white" onClick={handleCreate} data-testid="submit-review-btn">
                  Yorum Ekle
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Google API Config Dialog */}
      <Dialog open={configOpen} onOpenChange={setConfigOpen}>
        <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20 max-w-lg max-h-[80vh] overflow-y-auto">
          <DialogHeader><DialogTitle className="text-[#C4972A]">Google Business API Kurulumu</DialogTitle></DialogHeader>
          <div className="space-y-4 text-sm">
            <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3 flex gap-2">
              <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div className="text-amber-200/80 text-xs">
                Google yorumlariniza otomatik yanit verebilmek icin Google Business Profile API entegrasyonu gereklidir.
              </div>
            </div>

            {googleConfig && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${googleConfig.configured ? 'bg-emerald-400' : 'bg-red-400'}`} />
                  <span className="text-[#a9a9b2] text-xs">Client ID/Secret: {googleConfig.configured ? 'Ayarlandi' : 'Eksik'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${googleConfig.has_account_id ? 'bg-emerald-400' : 'bg-red-400'}`} />
                  <span className="text-[#a9a9b2] text-xs">Account ID: {googleConfig.has_account_id ? 'Ayarlandi' : 'Eksik'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${googleConfig.has_location_id ? 'bg-emerald-400' : 'bg-red-400'}`} />
                  <span className="text-[#a9a9b2] text-xs">Location ID: {googleConfig.has_location_id ? 'Ayarlandi' : 'Eksik'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${googleConfig.has_refresh_token ? 'bg-emerald-400' : 'bg-red-400'}`} />
                  <span className="text-[#a9a9b2] text-xs">Refresh Token: {googleConfig.has_refresh_token ? 'Ayarlandi' : 'Eksik'}</span>
                </div>
              </div>
            )}

            <div className="space-y-2">
              <h4 className="text-[#C4972A] font-medium text-xs uppercase">Kurulum Adimlari</h4>
              <ol className="space-y-1.5 text-xs text-[#a9a9b2]">
                <li>1. <a href="https://console.cloud.google.com" target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">Google Cloud Console</a>'a gidin</li>
                <li>2. Yeni proje olusturun veya mevcut projeyi secin</li>
                <li>3. <strong>My Business Business Information API</strong> etkinlestirin</li>
                <li>4. <strong>Kimlik Bilgileri</strong> &gt; OAuth 2.0 istemci kimligi olusturun</li>
                <li>5. <strong>Redirect URI:</strong> <code className="text-[#C4972A] bg-white/5 px-1 rounded">https://hotel-system-production.up.railway.app/api/reviews/google-callback</code></li>
                <li>6. Asagidaki degiskenleri Railway environment variables'a ekleyin:</li>
              </ol>
              <div className="bg-black/30 rounded-lg p-3 text-xs font-mono text-[#a9a9b2] space-y-1">
                <div>GOOGLE_BUSINESS_CLIENT_ID=xxx</div>
                <div>GOOGLE_BUSINESS_CLIENT_SECRET=xxx</div>
                <div>GOOGLE_BUSINESS_ACCOUNT_ID=xxx</div>
                <div>GOOGLE_BUSINESS_LOCATION_ID=xxx</div>
                <div>GOOGLE_BUSINESS_REFRESH_TOKEN=xxx</div>
              </div>
              <p className="text-[10px] text-[#7e7e8a]">
                Account ID ve Location ID bilgilerini Google Business Profile yonetim panelinizden bulabilirsiniz.
                Refresh token icin OAuth2 playground kullanabilirsiniz.
              </p>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3" data-testid="review-stats">
          <div className="bg-[#12121a] border border-white/5 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-1">
              <MessageSquare className="w-4 h-4 text-[#C4972A]" />
              <span className="text-xs text-[#7e7e8a]">Toplam Yorum</span>
            </div>
            <p className="text-2xl font-bold text-white" data-testid="stat-total">{stats.total}</p>
          </div>
          <div className="bg-[#12121a] border border-white/5 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              <span className="text-xs text-[#7e7e8a]">Ortalama Puan</span>
            </div>
            <p className="text-2xl font-bold text-white" data-testid="stat-avg">{stats.avg_rating || '-'}</p>
          </div>
          <div className="bg-[#12121a] border border-white/5 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-1">
              <Check className="w-4 h-4 text-emerald-400" />
              <span className="text-xs text-[#7e7e8a]">Yanitlanan</span>
            </div>
            <p className="text-2xl font-bold text-white" data-testid="stat-responded">{stats.responded}</p>
          </div>
          <div className="bg-[#12121a] border border-white/5 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span className="text-xs text-[#7e7e8a]">Bekleyen</span>
            </div>
            <p className="text-2xl font-bold text-white" data-testid="stat-pending">{stats.pending}</p>
          </div>
          <div className="bg-[#12121a] border border-white/5 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-1">
              <ExternalLink className="w-4 h-4 text-blue-400" />
              <span className="text-xs text-[#7e7e8a]">Google'a Gonderilen</span>
            </div>
            <p className="text-2xl font-bold text-white">{stats.google_posted || 0}</p>
          </div>
        </div>
      )}

      {/* Reviews List */}
      {reviews.length === 0 ? (
        <div className="text-center py-16" data-testid="empty-reviews">
          <MessageSquare className="w-12 h-12 text-[#3a3a45] mx-auto mb-3" />
          <p className="text-[#7e7e8a]">Henuz yorum eklenmemis</p>
          <p className="text-[#5a5a65] text-sm mt-1">Google yorumlarinizi ekleyerek AI ile profesyonel yanitlar olusturun</p>
          <Button className="mt-4 bg-blue-600 hover:bg-blue-700 text-white text-xs"
            onClick={handleSyncGoogle} disabled={syncing}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${syncing ? 'animate-spin' : ''}`} />
            Google'dan Yorumlari Cek
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4" data-testid="reviews-list">
          {reviews.map(review => (
            <ReviewCard
              key={review.id}
              review={review}
              onGenerate={handleGenerate}
              onDelete={handleDelete}
              onPostToGoogle={handlePostToGoogle}
              generating={generating}
              posting={posting}
            />
          ))}
        </div>
      )}
    </div>
  );
}
