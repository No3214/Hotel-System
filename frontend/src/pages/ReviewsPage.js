import React, { useState, useEffect, useCallback } from 'react';
import { getReviews, createReview, generateReviewResponse, updateReview, deleteReview, getReviewStats, getReviewAIAnalytics } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Star, Plus, Trash2, Sparkles, Copy, Check, RefreshCw, MessageSquare, TrendingUp, ThumbsUp, ThumbsDown, Loader2 } from 'lucide-react';

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

function ReviewCard({ review, onGenerate, onDelete, generating }) {
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
            Yanitlandi: {review.responded_at.split('T')[0]}
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
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ reviewer_name: '', rating: 5, review_text: '', platform: 'google', review_date: '' });
  const [aiAnalytics, setAiAnalytics] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);

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
    try {
      await generateReviewResponse(reviewId, tone);
      load();
    } catch (err) {
      console.error(err);
    }
    setGenerating(null);
  };

  const handleDelete = async (id) => {
    await deleteReview(id).catch(console.error);
    load();
  };

  const loadAiAnalytics = async () => {
    setAiLoading(true);
    try {
      const res = await getReviewAIAnalytics();
      if (res.data.success) {
        setAiAnalytics(res.data.analytics);
      }
    } catch (err) {
      console.error(err);
      alert("AI Analiz olusturulurken hata olustu.");
    }
    setAiLoading(false);
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]" data-testid="reviews-title">Google Yorumlari</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">AI destekli profesyonel yorum yanitlama</p>
        </div>
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

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="review-stats">
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
        </div>
      )}

      {/* AI Analytics Button/Panel */}
      <div className="bg-[#12121a] border border-emerald-500/20 rounded-xl p-5 mb-6 relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none transition-opacity opacity-50 group-hover:opacity-100" />
        
        <div className="flex items-center justify-between mb-4 relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-emerald-400">Gemini CX: Duygu Analizi & Ozet</h2>
              <p className="text-xs text-[#7e7e8a]">Son 50 yorumu analiz ederek genel musteri memnuniyetini olcer</p>
            </div>
          </div>
          <Button 
            onClick={loadAiAnalytics} 
            disabled={aiLoading}
            className="bg-emerald-600 hover:bg-emerald-500 text-white"
          >
            {aiLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
            {aiAnalytics ? 'Yeniden Analiz Et' : 'Analizi Baslat'}
          </Button>
        </div>

        {aiLoading && (
          <div className="flex items-center gap-3 text-[#7e7e8a] py-4 text-sm relative z-10">
             <span className="flex gap-1">
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </span>
              Gemini son misafir yorumlarini okuyor ve duygu analizi yapiyor...
          </div>
        )}

        {aiAnalytics && !aiLoading && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10 pt-4 border-t border-white/5">
            {/* Score & Summary */}
            <div className="space-y-3">
              <div className="flex items-end gap-2">
                <span className="text-4xl font-bold text-white">{aiAnalytics.sentiment_score}</span>
                <span className="text-sm text-[#7e7e8a] mb-1">/ 100</span>
              </div>
              <p className="text-sm text-[#c8c8d0] leading-relaxed">{aiAnalytics.summary}</p>
            </div>
            
            {/* Positives */}
            <div className="space-y-2 relative">
              <h4 className="text-sm font-medium flex items-center gap-2 text-emerald-400">
                <ThumbsUp className="w-4 h-4" /> En Cok Begenilenler
              </h4>
              <ul className="space-y-2">
                {aiAnalytics.positives?.map((item, i) => (
                  <li key={i} className="text-xs text-[#7e7e8a] flex items-start gap-2">
                    <span className="text-emerald-500 mt-0.5">•</span> {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Negatives */}
            <div className="space-y-2 relative">
              <h4 className="text-sm font-medium flex items-center gap-2 text-red-400">
                <ThumbsDown className="w-4 h-4" /> Gelistirilmesi Gerekenler
              </h4>
              <ul className="space-y-2">
                {aiAnalytics.negatives?.map((item, i) => (
                  <li key={i} className="text-xs text-[#7e7e8a] flex items-start gap-2">
                    <span className="text-red-500 mt-0.5">•</span> {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Reviews List */}
      {reviews.length === 0 ? (
        <div className="text-center py-16" data-testid="empty-reviews">
          <MessageSquare className="w-12 h-12 text-[#3a3a45] mx-auto mb-3" />
          <p className="text-[#7e7e8a]">Henuz yorum eklenmemis</p>
          <p className="text-[#5a5a65] text-sm mt-1">Google yorumlarinizi ekleyerek AI ile profesyonel yanitlar olusturun</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4" data-testid="reviews-list">
          {reviews.map(review => (
            <ReviewCard
              key={review.id}
              review={review}
              onGenerate={handleGenerate}
              onDelete={handleDelete}
              generating={generating}
            />
          ))}
        </div>
      )}
    </div>
  );
}
