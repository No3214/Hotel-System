import React, { useState, useEffect, useRef } from 'react';
import {
  getSocialPosts, createSocialPost, updateSocialPost, deleteSocialPost,
  publishSocialPost, getSocialTemplates, getSocialStats, convertImageLink,
  checkDuplicateMedia, aiGenerateContent, getAITopics, getAutoPublishSettings,
  updateAutoPublishSettings, triggerAutoPublish, getAutoPublishHistory, getContentCalendar,
  batchDriveImport, publishToPlatforms, getPlatformStatus,
  getContentQueue, addToQueue, removeFromQueue, getOptimalTime, getRecyclablePosts,
  recyclePost, getWeeklyPlan, getPostScore, getEscalations, resolveEscalation,
  getEscalationStats, publishScheduledPosts
} from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import {
  Plus, Trash2, Edit2, Save, X, Send, Copy, Instagram, Facebook, Twitter,
  MessageCircle, Eye, BarChart3, FileText, Sparkles, Clock, Linkedin, Video,
  Image, Link, Loader2, Wand2, Calendar, Settings, Zap, RotateCcw, CheckCircle2,
  AlertCircle, Bot, ChevronRight, Upload, FolderOpen, ExternalLink, Wifi, WifiOff,
  List, RefreshCw, Star, AlertTriangle, TrendingUp, Award
} from 'lucide-react';

const PLATFORMS = [
  { id: 'instagram', name: 'Instagram', icon: Instagram, color: '#E1306C' },
  { id: 'facebook', name: 'Facebook', icon: Facebook, color: '#1877F2' },
  { id: 'twitter', name: 'X (Twitter)', icon: Twitter, color: '#e5e5e8' },
  { id: 'tiktok', name: 'TikTok', icon: Video, color: '#00F2EA' },
  { id: 'linkedin', name: 'LinkedIn', icon: Linkedin, color: '#0A66C2' },
  { id: 'whatsapp', name: 'WhatsApp', icon: MessageCircle, color: '#25D366' },
];

const POST_TYPE_LABELS = {
  text: 'Genel', promo: 'Promosyon', event: 'Etkinlik',
  menu_highlight: 'Menu Vitrin', announcement: 'Duyuru',
};

const STATUS_COLORS = {
  draft: { bg: '#7e7e8a20', text: '#7e7e8a', label: 'Taslak' },
  scheduled: { bg: '#C4972A20', text: '#C4972A', label: 'Planlanmis' },
  published: { bg: '#8FAA8620', text: '#8FAA86', label: 'Yayinlandi' },
};

export default function SocialMediaPage() {
  const [posts, setPosts] = useState([]);
  const [templates, setTemplates] = useState({});
  const [frameStyles, setFrameStyles] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('list'); // list, create, edit, preview
  const [editPost, setEditPost] = useState(null);
  const [filter, setFilter] = useState('all');
  const [uploading, setUploading] = useState(false);
  const [activeTab, setActiveTab] = useState('posts'); // posts, ai, batch, autopublish, calendar
  const previewRef = useRef(null);

  const loadData = async () => {
    try {
      const [postsRes, templatesRes, statsRes] = await Promise.all([
        getSocialPosts(), getSocialTemplates(), getSocialStats()
      ]);
      setPosts(postsRes.data.posts || []);
      setTemplates(templatesRes.data.templates || {});
      setFrameStyles(templatesRes.data.frame_styles || []);
      setStats(statsRes.data);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  useEffect(() => { loadData(); }, []);

  const startCreate = (type = 'text') => {
    const tpl = templates[type] || {};
    setEditPost({
      title: tpl.title || '',
      content: tpl.content || '',
      platforms: [],
      post_type: type,
      frame_style: 'default',
      hashtags: tpl.hashtags || ['KozbeyliKonagi'],
      status: 'draft',
      image_url: null,
    });
    setView('create');
    setActiveTab('posts');
  };

  const [imageLink, setImageLink] = useState('');
  const [duplicateWarning, setDuplicateWarning] = useState(null);

  const handleImageLink = async () => {
    if (!imageLink.trim()) return;

    setUploading(true);
    setDuplicateWarning(null);
    try {
      const res = await convertImageLink(imageLink);
      const directUrl = res.data.image_url;

      const dupCheck = await checkDuplicateMedia(directUrl);
      if (dupCheck.data.duplicate) {
        const existing = dupCheck.data.existing_post;
        setDuplicateWarning({
          message: dupCheck.data.message,
          existingPost: existing,
        });
        setUploading(false);
        return;
      }

      setEditPost({ ...editPost, image_url: directUrl });
      setImageLink('');
    } catch (err) {
      console.error('Gorsel linki cevirilmedi:', err);
      alert('Gorsel linki gecersiz. Lutfen Google Drive paylasim linkini kontrol edin.');
    }
    setUploading(false);
  };

  const handleSave = async () => {
    try {
      if (editPost.id) {
        await updateSocialPost(editPost.id, editPost);
      } else {
        await createSocialPost(editPost);
      }
      setView('list');
      setEditPost(null);
      setDuplicateWarning(null);
      loadData();
    } catch (err) {
      if (err.response?.status === 409) {
        setDuplicateWarning({
          message: err.response.data?.detail || 'Bu gorsel daha once kullanilmis.',
        });
      } else {
        console.error(err);
      }
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bu gonderiyi silmek istediginize emin misiniz?')) return;
    await deleteSocialPost(id);
    loadData();
  };

  const [publishing, setPublishing] = useState(null);
  const [publishResult, setPublishResult] = useState(null);

  const handlePublish = async (id) => {
    setPublishing(id);
    setPublishResult(null);
    try {
      const res = await publishToPlatforms(id);
      setPublishResult({ postId: id, results: res.data.results });
      loadData();
      // Clear result after 5 seconds
      setTimeout(() => setPublishResult(null), 5000);
    } catch (err) {
      // Fallback to simple publish
      await publishSocialPost(id);
      loadData();
    }
    setPublishing(null);
  };

  const copyContent = (post) => {
    const text = `${post.title}\n\n${post.content}\n\n${post.hashtags?.map(h => '#' + h).join(' ') || ''}`;
    navigator.clipboard.writeText(text);
  };

  const filteredPosts = filter === 'all' ? posts : posts.filter(p => p.status === filter);

  if (loading) return <div className="p-8"><div className="h-8 w-48 bg-white/5 rounded animate-pulse" /></div>;

  return (
    <div className="p-6 lg:p-8 max-w-[1400px]" data-testid="social-media-page">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#C4972A]">Sosyal Medya Yayinlayici</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">AI destekli icerik olustur, duzenle ve otomatik paylas</p>
        </div>
        {activeTab === 'posts' && view === 'list' && (
          <div className="flex gap-2">
            <Button onClick={() => setActiveTab('ai')} className="bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-700 hover:to-pink-600 text-white" data-testid="ai-generate-btn">
              <Wand2 className="w-4 h-4 mr-1" /> AI Icerik Uret
            </Button>
            <Button onClick={() => startCreate('text')} className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="new-post-btn">
              <Plus className="w-4 h-4 mr-1" /> Yeni Gonderi
            </Button>
          </div>
        )}
        {(view === 'create' || view === 'edit') && (
          <Button variant="ghost" onClick={() => { setView('list'); setEditPost(null); }} className="text-[#7e7e8a]">
            <X className="w-4 h-4 mr-1" /> Iptal
          </Button>
        )}
      </div>

      {/* Tab Navigation */}
      {view === 'list' && (
        <div className="flex gap-1 mb-6 p-1 bg-white/5 rounded-xl w-fit">
          {[
            { id: 'posts', label: 'Gonderiler', icon: FileText },
            { id: 'ai', label: 'AI Icerik', icon: Wand2 },
            { id: 'batch', label: 'Toplu Yukle', icon: Upload },
            { id: 'autopublish', label: 'Oto-Yayinla', icon: Zap },
            { id: 'calendar', label: 'Takvim', icon: Calendar },
            { id: 'queue', label: 'Kuyruk', icon: List },
            { id: 'planner', label: 'Haftalik Plan', icon: Calendar },
            { id: 'recycle', label: 'Geri Donusum', icon: RefreshCw },
            { id: 'escalation', label: 'Escalation', icon: AlertTriangle },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-[#C4972A]/15 text-[#C4972A]'
                  : 'text-[#7e7e8a] hover:bg-white/5'
              }`}
              data-testid={`tab-${tab.id}`}
            >
              <tab.icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          ))}
        </div>
      )}

      {/* Stats */}
      {activeTab === 'posts' && view === 'list' && stats && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          {[
            { label: 'Toplam', value: stats.total, icon: FileText, color: '#C4972A' },
            { label: 'Taslak', value: stats.drafts, icon: Edit2, color: '#7e7e8a' },
            { label: 'Planlanmis', value: stats.scheduled, icon: Clock, color: '#C4972A' },
            { label: 'Yayinlandi', value: stats.published, icon: Send, color: '#8FAA86' },
          ].map(s => (
            <div key={s.label} className="glass rounded-xl p-4" data-testid={`stat-${s.label.toLowerCase()}`}>
              <div className="flex items-center gap-2 mb-2">
                <s.icon className="w-4 h-4" style={{ color: s.color }} />
                <span className="text-xs text-[#7e7e8a]">{s.label}</span>
              </div>
              <span className="text-2xl font-bold" style={{ color: s.color }}>{s.value}</span>
            </div>
          ))}
        </div>
      )}

      {/* POSTS TAB */}
      {activeTab === 'posts' && view === 'list' && (
        <>
          {/* Filter Tabs */}
          <div className="flex gap-2 mb-4">
            {['all', 'draft', 'scheduled', 'published'].map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1.5 rounded-lg text-xs transition-all ${filter === f ? 'bg-[#C4972A]/15 text-[#C4972A]' : 'text-[#7e7e8a] hover:bg-white/5'}`}
                data-testid={`filter-${f}`}
              >
                {f === 'all' ? 'Hepsi' : STATUS_COLORS[f]?.label || f}
              </button>
            ))}
          </div>

          {/* Post Type Quick Create */}
          <div className="flex gap-2 mb-6 flex-wrap">
            {Object.entries(POST_TYPE_LABELS).map(([key, label]) => (
              <button
                key={key}
                onClick={() => startCreate(key)}
                className="px-3 py-1.5 rounded-lg text-xs text-[#a9a9b2] hover:bg-white/5 border border-white/5 transition-all hover:border-[#C4972A]/30"
                data-testid={`quick-create-${key}`}
              >
                + {label}
              </button>
            ))}
          </div>

          {/* Publish Result Feedback */}
          {publishResult && (
            <div className="mb-4 p-4 rounded-xl border border-[#8FAA86]/30 bg-[#8FAA86]/10">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="w-4 h-4 text-[#8FAA86]" />
                <span className="text-sm text-[#8FAA86] font-medium">Yayinlama Sonuclari</span>
              </div>
              <div className="flex gap-3">
                {Object.entries(publishResult.results).map(([platform, result]) => {
                  const plat = PLATFORMS.find(p => p.id === platform);
                  const PIcon = plat?.icon || FileText;
                  const isSuccess = result.status === 'published' || result.status === 'mock_published';
                  return (
                    <div key={platform} className="flex items-center gap-1.5 text-xs">
                      <PIcon className="w-3.5 h-3.5" style={{ color: plat?.color || '#7e7e8a' }} />
                      <span className={isSuccess ? 'text-[#8FAA86]' : 'text-red-400'}>
                        {result.status === 'published' ? 'Yayinlandi' :
                         result.status === 'mock_published' ? 'Mock OK' :
                         result.status === 'not_supported' ? 'Manuel' :
                         'Hata'}
                      </span>
                      {result.mock && <WifiOff className="w-3 h-3 text-amber-400" title="Mock mod" />}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Posts List */}
          <div className="space-y-3">
            {filteredPosts.length === 0 && (
              <div className="glass rounded-xl p-12 text-center text-[#7e7e8a]">
                <FileText className="w-8 h-8 mx-auto mb-3 opacity-30" />
                <p>Henuz gonderi yok. Yeni bir gonderi olusturun.</p>
              </div>
            )}
            {filteredPosts.map((post, i) => {
              const statusStyle = STATUS_COLORS[post.status] || STATUS_COLORS.draft;
              return (
                <div key={post.id} className="glass rounded-xl p-4 group hover:border-[#C4972A]/20 transition-all" data-testid={`post-${i}`}>
                  <div className="flex items-start gap-4">
                    <FramePreviewMini post={post} frameStyles={frameStyles} />

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-sm font-medium text-[#e5e5e8] truncate">{post.title || 'Basliksiz'}</h3>
                        <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: statusStyle.bg, color: statusStyle.text }}>
                          {statusStyle.label}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-[#7e7e8a]">
                          {POST_TYPE_LABELS[post.post_type] || post.post_type}
                        </span>
                        {post.source === 'ai_auto_publish' && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/15 text-purple-400 flex items-center gap-0.5">
                            <Bot className="w-2.5 h-2.5" /> AI
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-[#7e7e8a] line-clamp-2 mb-2">{post.content}</p>
                      <div className="flex items-center gap-3">
                        <div className="flex gap-1">
                          {(post.platforms || []).map(p => {
                            const plat = PLATFORMS.find(pl => pl.id === p);
                            if (!plat) return null;
                            const PIcon = plat.icon;
                            return <PIcon key={p} className="w-3.5 h-3.5" style={{ color: plat.color }} />;
                          })}
                        </div>
                        {post.hashtags?.length > 0 && (
                          <span className="text-[10px] text-[#7e7e8a]">
                            {post.hashtags.slice(0, 3).map(h => '#' + h).join(' ')}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => copyContent(post)} className="p-1.5 rounded-lg hover:bg-white/5 text-[#7e7e8a]" title="Kopyala"><Copy className="w-3.5 h-3.5" /></button>
                      <button onClick={() => { setEditPost({ ...post }); setView('edit'); }} className="p-1.5 rounded-lg hover:bg-white/5 text-[#7e7e8a]" title="Duzenle"><Edit2 className="w-3.5 h-3.5" /></button>
                      {post.status !== 'published' && (
                        <button
                          onClick={() => handlePublish(post.id)}
                          disabled={publishing === post.id}
                          className="p-1.5 rounded-lg hover:bg-[#8FAA86]/10 text-[#8FAA86] disabled:opacity-50"
                          title="Platformlara Yayinla"
                        >
                          {publishing === post.id ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                        </button>
                      )}
                      {post.publish_results && (
                        <span className="text-[9px] text-[#8FAA86]" title={JSON.stringify(post.publish_results)}>
                          <Wifi className="w-3 h-3 inline" />
                        </span>
                      )}
                      <button onClick={() => handleDelete(post.id)} className="p-1.5 rounded-lg hover:bg-red-400/10 text-red-400" title="Sil"><Trash2 className="w-3.5 h-3.5" /></button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}

      {/* AI CONTENT TAB */}
      {activeTab === 'ai' && view === 'list' && (
        <AIContentGenerator
          onContentGenerated={(generated) => {
            setEditPost({
              title: generated.title,
              content: generated.content,
              platforms: [],
              post_type: generated.post_type || 'text',
              frame_style: 'default',
              hashtags: generated.hashtags || ['KozbeyliKonagi'],
              status: 'draft',
              image_url: null,
            });
            setView('create');
            setActiveTab('posts');
          }}
        />
      )}

      {/* BATCH DRIVE IMPORT TAB */}
      {activeTab === 'batch' && view === 'list' && (
        <BatchDrivePanel onComplete={() => { setActiveTab('posts'); loadData(); }} />
      )}

      {/* AUTO-PUBLISH TAB */}
      {activeTab === 'autopublish' && view === 'list' && (
        <AutoPublishPanel onRefresh={loadData} />
      )}

      {/* CALENDAR TAB */}
      {activeTab === 'calendar' && view === 'list' && (
        <ContentCalendarPanel />
      )}

      {/* CONTENT QUEUE TAB */}
      {activeTab === 'queue' && view === 'list' && (
        <ContentQueuePanel onRefresh={loadData} />
      )}

      {/* WEEKLY PLANNER TAB */}
      {activeTab === 'planner' && view === 'list' && (
        <WeeklyPlannerPanel />
      )}

      {/* RECYCLE TAB */}
      {activeTab === 'recycle' && view === 'list' && (
        <RecyclePanel onRefresh={loadData} />
      )}

      {/* ESCALATION TAB */}
      {activeTab === 'escalation' && view === 'list' && (
        <EscalationPanel />
      )}

      {/* CREATE / EDIT VIEW */}
      {(view === 'create' || view === 'edit') && editPost && (
        <div className="grid grid-cols-12 gap-6">
          {/* Editor */}
          <div className="col-span-7 space-y-4">
            {/* Post Type */}
            <div className="glass rounded-xl p-4">
              <label className="text-xs text-[#7e7e8a] mb-2 block">Gonderi Turu</label>
              <div className="flex gap-2 flex-wrap">
                {Object.entries(POST_TYPE_LABELS).map(([key, label]) => (
                  <button
                    key={key}
                    onClick={() => setEditPost({ ...editPost, post_type: key })}
                    className={`px-3 py-1.5 rounded-lg text-xs transition-all ${editPost.post_type === key ? 'bg-[#C4972A]/15 text-[#C4972A]' : 'text-[#7e7e8a] hover:bg-white/5'}`}
                    data-testid={`type-${key}`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Title & Content */}
            <div className="glass rounded-xl p-4 space-y-3">
              <div>
                <label className="text-xs text-[#7e7e8a] mb-1 block">Baslik</label>
                <Input
                  value={editPost.title}
                  onChange={e => setEditPost({ ...editPost, title: e.target.value })}
                  className="bg-white/5 border-white/10 text-white"
                  placeholder="Gonderi basligi"
                  data-testid="post-title"
                />
              </div>
              <div>
                <label className="text-xs text-[#7e7e8a] mb-1 block">Icerik</label>
                <textarea
                  value={editPost.content}
                  onChange={e => setEditPost({ ...editPost, content: e.target.value })}
                  className="w-full min-h-[160px] p-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm resize-y outline-none focus:border-[#C4972A]/50"
                  placeholder="Gonderi icerigi yazin..."
                  data-testid="post-content"
                />
              </div>
            </div>

            {/* Platforms */}
            <div className="glass rounded-xl p-4">
              <label className="text-xs text-[#7e7e8a] mb-2 block">Platformlar</label>
              <div className="flex gap-2">
                {PLATFORMS.map(p => {
                  const PIcon = p.icon;
                  const selected = editPost.platforms?.includes(p.id);
                  return (
                    <button
                      key={p.id}
                      onClick={() => {
                        const plats = selected
                          ? editPost.platforms.filter(x => x !== p.id)
                          : [...(editPost.platforms || []), p.id];
                        setEditPost({ ...editPost, platforms: plats });
                      }}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs transition-all border ${selected ? 'border-white/20' : 'border-transparent hover:bg-white/5'}`}
                      style={{ background: selected ? `${p.color}15` : 'transparent', color: selected ? p.color : '#7e7e8a' }}
                      data-testid={`platform-${p.id}`}
                    >
                      <PIcon className="w-4 h-4" />
                      {p.name}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Hashtags */}
            <div className="glass rounded-xl p-4">
              <label className="text-xs text-[#7e7e8a] mb-1 block">Hashtag'ler (virgul ile ayirin)</label>
              <Input
                value={(editPost.hashtags || []).join(', ')}
                onChange={e => setEditPost({ ...editPost, hashtags: e.target.value.split(',').map(h => h.trim()).filter(Boolean) })}
                className="bg-white/5 border-white/10 text-white text-sm"
                placeholder="KozbeyliKonagi, TasOtel, Foca"
                data-testid="post-hashtags"
              />
            </div>

            {/* Image from Google Drive Link */}
            <div className="glass rounded-xl p-4">
              <label className="text-xs text-[#7e7e8a] mb-2 block">Gorsel (Google Drive Linki)</label>
              {editPost.image_url ? (
                <div className="relative group">
                  <img
                    src={editPost.image_url}
                    alt="Gonderi gorseli"
                    className="w-full h-32 object-cover rounded-lg"
                    onError={(e) => { e.target.style.display = 'none'; }}
                  />
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center gap-2">
                    <button
                      onClick={() => setEditPost({ ...editPost, image_url: null })}
                      className="p-2 bg-red-500/20 rounded-lg hover:bg-red-500/30 text-red-400"
                      title="Kaldir"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <Input
                      value={imageLink}
                      onChange={(e) => setImageLink(e.target.value)}
                      placeholder="https://drive.google.com/file/d/..."
                      className="bg-white/5 border-white/10 text-white text-sm flex-1"
                      data-testid="image-link-input"
                    />
                    <Button
                      onClick={handleImageLink}
                      disabled={uploading || !imageLink.trim()}
                      className="bg-[#5B7A4A] hover:bg-[#4a6a3a] text-white px-3"
                      data-testid="add-image-btn"
                    >
                      {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Link className="w-4 h-4" />}
                    </Button>
                  </div>
                  <p className="text-[10px] text-[#5a5a65]">
                    Google Drive'da gorseli paylasa ac, linki yapistir
                  </p>
                </div>
              )}
              {duplicateWarning && (
                <div className="mt-2 p-3 rounded-lg border border-amber-500/30 bg-amber-500/10">
                  <div className="flex items-start gap-2">
                    <span className="text-amber-400 text-sm font-bold mt-0.5">!</span>
                    <div className="flex-1">
                      <p className="text-xs text-amber-300 font-medium">{duplicateWarning.message}</p>
                      {duplicateWarning.existingPost && (
                        <p className="text-[10px] text-amber-400/70 mt-1">
                          Gonderi: "{duplicateWarning.existingPost.title || 'Basliksiz'}" -- Durum: {STATUS_COLORS[duplicateWarning.existingPost.status]?.label || duplicateWarning.existingPost.status}
                        </p>
                      )}
                      <button
                        onClick={() => { setDuplicateWarning(null); setImageLink(''); }}
                        className="text-[10px] text-amber-400 hover:text-amber-300 underline mt-1"
                      >
                        Tamam, farkli gorsel kullanacagim
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Save */}
            <div className="flex gap-2">
              <Button onClick={handleSave} className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="save-post-btn">
                <Save className="w-4 h-4 mr-1" /> Kaydet
              </Button>
              <Button
                onClick={() => { setEditPost({ ...editPost, status: 'scheduled' }); setTimeout(handleSave, 100); }}
                variant="outline" className="border-[#C4972A]/30 text-[#C4972A]"
              >
                <Clock className="w-4 h-4 mr-1" /> Planla
              </Button>
            </div>
          </div>

          {/* Preview */}
          <div className="col-span-5">
            <div className="sticky top-4">
              <h3 className="text-sm text-[#7e7e8a] mb-3 flex items-center gap-2">
                <Eye className="w-4 h-4" /> Onizleme
              </h3>

              {/* Frame Style Selector */}
              <div className="flex gap-2 mb-3">
                {(frameStyles.length > 0 ? frameStyles : [
                  { id: 'default', name: 'Varsayilan', bg: '#515249', text: '#F8F5EF', accent: '#B07A2A' },
                  { id: 'elegant', name: 'Elegans', bg: '#1E1B16', text: '#F8F5EF', accent: '#C5A059' },
                  { id: 'bold', name: 'Cesur', bg: '#8FAA86', text: '#1E1B16', accent: '#515249' },
                  { id: 'minimal', name: 'Minimal', bg: '#F3EEE4', text: '#1E1B16', accent: '#515249' },
                  { id: 'festive', name: 'Senlik', bg: '#3F403A', text: '#F8F5EF', accent: '#D4A847' },
                ]).map(s => (
                  <button
                    key={s.id}
                    onClick={() => setEditPost({ ...editPost, frame_style: s.id })}
                    className={`w-8 h-8 rounded-lg border-2 transition-all ${editPost.frame_style === s.id ? 'border-[#C4972A] scale-110' : 'border-transparent'}`}
                    style={{ background: s.bg }}
                    title={s.name}
                    data-testid={`frame-${s.id}`}
                  />
                ))}
              </div>

              <FramePreview post={editPost} frameStyles={frameStyles} ref={previewRef} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


/* ─── AI Content Generator Panel ─── */
function AIContentGenerator({ onContentGenerated }) {
  const [topics, setTopics] = useState([]);
  const [tones, setTones] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState('morning');
  const [selectedTone, setSelectedTone] = useState('warm');
  const [selectedPlatform, setSelectedPlatform] = useState('instagram');
  const [customPrompt, setCustomPrompt] = useState('');
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getAITopics().then(res => {
      setTopics(res.data.topics || []);
      setTones(res.data.tones || []);
    }).catch(console.error);
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    setResult(null);
    try {
      const res = await aiGenerateContent({
        post_type: selectedTopic === 'menu_highlight' ? 'menu_highlight' : 'text',
        topic: selectedTopic,
        platform: selectedPlatform,
        custom_prompt: customPrompt || undefined,
        tone: selectedTone,
      });
      setResult(res.data.generated);
    } catch (err) {
      setError(err.response?.data?.detail || 'Icerik uretimi basarisiz oldu');
    }
    setGenerating(false);
  };

  return (
    <div className="space-y-6">
      <div className="glass rounded-xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-pink-500 flex items-center justify-center">
            <Wand2 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-[#e5e5e8]">AI Icerik Uretici</h2>
            <p className="text-xs text-[#7e7e8a]">Gemini AI ile otomatik sosyal medya icerigi olusturun</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* Left: Settings */}
          <div className="space-y-4">
            {/* Topic */}
            <div>
              <label className="text-xs text-[#7e7e8a] mb-2 block">Konu</label>
              <div className="grid grid-cols-2 gap-2">
                {topics.map(t => (
                  <button
                    key={t.id}
                    onClick={() => setSelectedTopic(t.id)}
                    className={`px-3 py-2 rounded-lg text-xs text-left transition-all ${
                      selectedTopic === t.id
                        ? 'bg-purple-500/15 text-purple-400 border border-purple-500/30'
                        : 'text-[#7e7e8a] hover:bg-white/5 border border-transparent'
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Tone */}
            <div>
              <label className="text-xs text-[#7e7e8a] mb-2 block">Ton</label>
              <div className="flex gap-2">
                {tones.map(t => (
                  <button
                    key={t.id}
                    onClick={() => setSelectedTone(t.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs transition-all ${
                      selectedTone === t.id
                        ? 'bg-[#C4972A]/15 text-[#C4972A]'
                        : 'text-[#7e7e8a] hover:bg-white/5'
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Platform */}
            <div>
              <label className="text-xs text-[#7e7e8a] mb-2 block">Hedef Platform</label>
              <div className="flex gap-2">
                {PLATFORMS.slice(0, 4).map(p => {
                  const PIcon = p.icon;
                  return (
                    <button
                      key={p.id}
                      onClick={() => setSelectedPlatform(p.id)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all ${
                        selectedPlatform === p.id
                          ? 'border border-white/20'
                          : 'border border-transparent hover:bg-white/5'
                      }`}
                      style={{
                        background: selectedPlatform === p.id ? `${p.color}15` : 'transparent',
                        color: selectedPlatform === p.id ? p.color : '#7e7e8a',
                      }}
                    >
                      <PIcon className="w-3.5 h-3.5" />
                      {p.name}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Custom Prompt */}
            <div>
              <label className="text-xs text-[#7e7e8a] mb-1 block">Ozel Yonerge (opsiyonel)</label>
              <textarea
                value={customPrompt}
                onChange={e => setCustomPrompt(e.target.value)}
                className="w-full min-h-[80px] p-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm resize-y outline-none focus:border-purple-500/50"
                placeholder="Ornegin: Bugun organik zeytinyagi hasadimiz basladi, bunu vurgula..."
              />
            </div>

            <Button
              onClick={handleGenerate}
              disabled={generating}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-700 hover:to-pink-600 text-white"
              data-testid="generate-btn"
            >
              {generating ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Icerik Uretiliyor...</>
              ) : (
                <><Sparkles className="w-4 h-4 mr-2" /> Icerik Uret</>
              )}
            </Button>
          </div>

          {/* Right: Result */}
          <div>
            {error && (
              <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10">
                <div className="flex items-center gap-2 text-red-400 text-sm">
                  <AlertCircle className="w-4 h-4" />
                  {error}
                </div>
              </div>
            )}

            {!result && !error && !generating && (
              <div className="h-full flex items-center justify-center text-[#7e7e8a] text-sm">
                <div className="text-center">
                  <Wand2 className="w-12 h-12 mx-auto mb-3 opacity-20" />
                  <p>Konu ve ton seciniz, sonra "Icerik Uret" butonuna basin</p>
                </div>
              </div>
            )}

            {generating && (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-purple-600/20 to-pink-500/20 flex items-center justify-center">
                    <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
                  </div>
                  <p className="text-sm text-[#7e7e8a]">AI icerik uretiyor...</p>
                </div>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                <div className="p-4 rounded-xl border border-purple-500/20 bg-purple-500/5">
                  <div className="flex items-center gap-2 mb-3">
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                    <span className="text-xs text-green-400 font-medium">Icerik Uretildi</span>
                  </div>

                  <div className="mb-3">
                    <label className="text-[10px] text-[#7e7e8a] uppercase tracking-wider">Baslik</label>
                    <p className="text-sm text-[#e5e5e8] font-medium mt-0.5">{result.title}</p>
                  </div>

                  <div className="mb-3">
                    <label className="text-[10px] text-[#7e7e8a] uppercase tracking-wider">Icerik</label>
                    <p className="text-sm text-[#c5c5ce] mt-0.5 leading-relaxed">{result.content}</p>
                  </div>

                  <div className="mb-4">
                    <label className="text-[10px] text-[#7e7e8a] uppercase tracking-wider">Hashtagler</label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {result.hashtags?.map((h, i) => (
                        <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-[#C4972A]/10 text-[#C4972A]">
                          #{h}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      onClick={() => onContentGenerated(result)}
                      className="flex-1 bg-[#C4972A] hover:bg-[#a87a1f] text-white text-xs"
                    >
                      <ChevronRight className="w-3.5 h-3.5 mr-1" /> Gonderi Olarak Kullan
                    </Button>
                    <Button
                      onClick={handleGenerate}
                      variant="outline"
                      className="border-purple-500/30 text-purple-400 text-xs"
                    >
                      <RotateCcw className="w-3.5 h-3.5 mr-1" /> Yeniden Uret
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


/* ─── Auto-Publish Settings Panel ─── */
function AutoPublishPanel({ onRefresh }) {
  const [settings, setSettings] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [triggering, setTriggering] = useState(false);

  useEffect(() => {
    Promise.all([
      getAutoPublishSettings(),
      getAutoPublishHistory(10),
    ]).then(([settingsRes, historyRes]) => {
      setSettings(settingsRes.data || { enabled: false, interval_hours: 24, platforms: [], tone: 'warm' });
      setHistory(historyRes.data?.history || []);
    }).catch(err => {
      console.error(err);
      setSettings({ enabled: false, interval_hours: 24, platforms: [], tone: 'warm' });
    }).finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateAutoPublishSettings(settings);
    } catch (err) { console.error(err); }
    setSaving(false);
  };

  const handleTrigger = async () => {
    setTriggering(true);
    try {
      await triggerAutoPublish();
      setTimeout(async () => {
        const res = await getAutoPublishHistory(10);
        setHistory(res.data.history || []);
        onRefresh();
        setTriggering(false);
      }, 3000);
    } catch (err) {
      console.error(err);
      setTriggering(false);
    }
  };

  const topicLabels = {
    morning: 'Sabah / Gunaydin',
    menu_highlight: 'Menu Vitrin',
    seasonal: 'Mevsimsel',
    local: 'Yerel Gezilecek',
    weekend: 'Hafta Sonu',
    guest_story: 'Misafir Deneyimi',
    behind_scenes: 'Sahne Arkasi',
    event: 'Etkinlik',
  };

  if (loading) return <div className="p-8"><div className="h-8 w-48 bg-white/5 rounded animate-pulse" /></div>;

  return (
    <div className="grid grid-cols-12 gap-6">
      {/* Settings */}
      <div className="col-span-7 space-y-4">
        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-[#e5e5e8]">Otomatik Yayinlama</h2>
                <p className="text-xs text-[#7e7e8a]">AI her gun otomatik icerik uretsin</p>
              </div>
            </div>

            {/* Enable Toggle */}
            <button
              onClick={() => setSettings({ ...settings, enabled: !settings.enabled })}
              className={`relative w-12 h-6 rounded-full transition-all ${
                settings.enabled ? 'bg-[#8FAA86]' : 'bg-white/10'
              }`}
            >
              <div className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-all ${
                settings.enabled ? 'left-6' : 'left-0.5'
              }`} />
            </button>
          </div>

          {/* Frequency */}
          <div className="mb-4">
            <label className="text-xs text-[#7e7e8a] mb-2 block">Siklik</label>
            <div className="flex gap-2">
              {[
                { id: 'daily', label: 'Her Gun' },
                { id: 'twice_weekly', label: 'Haftada 2' },
                { id: 'weekly', label: 'Haftada 1' },
              ].map(f => (
                <button
                  key={f.id}
                  onClick={() => setSettings({ ...settings, frequency: f.id })}
                  className={`px-4 py-2 rounded-lg text-xs transition-all ${
                    settings.frequency === f.id
                      ? 'bg-[#C4972A]/15 text-[#C4972A]'
                      : 'text-[#7e7e8a] hover:bg-white/5'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          {/* Preferred Time */}
          <div className="mb-4">
            <label className="text-xs text-[#7e7e8a] mb-2 block">Tercih Edilen Saat</label>
            <Input
              type="time"
              value={settings.preferred_time || '10:00'}
              onChange={e => setSettings({ ...settings, preferred_time: e.target.value })}
              className="bg-white/5 border-white/10 text-white w-40"
            />
          </div>

          {/* Platforms */}
          <div className="mb-4">
            <label className="text-xs text-[#7e7e8a] mb-2 block">Hedef Platformlar</label>
            <div className="flex gap-2 flex-wrap">
              {PLATFORMS.map(p => {
                const PIcon = p.icon;
                const selected = settings.platforms?.includes(p.id);
                return (
                  <button
                    key={p.id}
                    onClick={() => {
                      const plats = selected
                        ? settings.platforms.filter(x => x !== p.id)
                        : [...(settings.platforms || []), p.id];
                      setSettings({ ...settings, platforms: plats });
                    }}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all border ${
                      selected ? 'border-white/20' : 'border-transparent hover:bg-white/5'
                    }`}
                    style={{
                      background: selected ? `${p.color}15` : 'transparent',
                      color: selected ? p.color : '#7e7e8a',
                    }}
                  >
                    <PIcon className="w-3.5 h-3.5" />
                    {p.name}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Topics Rotation */}
          <div className="mb-4">
            <label className="text-xs text-[#7e7e8a] mb-2 block">Konu Rotasyonu</label>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(topicLabels).map(([id, label]) => {
                const selected = settings.topics?.includes(id);
                return (
                  <button
                    key={id}
                    onClick={() => {
                      const topics = selected
                        ? settings.topics.filter(t => t !== id)
                        : [...(settings.topics || []), id];
                      setSettings({ ...settings, topics });
                    }}
                    className={`px-3 py-2 rounded-lg text-xs text-left transition-all border ${
                      selected
                        ? 'bg-[#C4972A]/10 text-[#C4972A] border-[#C4972A]/30'
                        : 'text-[#7e7e8a] hover:bg-white/5 border-transparent'
                    }`}
                  >
                    {label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Auto Approve */}
          <div className="mb-6 flex items-center justify-between p-3 rounded-lg bg-white/5">
            <div>
              <p className="text-xs text-[#e5e5e8]">Otomatik Onayla</p>
              <p className="text-[10px] text-[#7e7e8a]">Aciksa direkt yayinlanir, kapaliysa taslak olarak olusturulur</p>
            </div>
            <button
              onClick={() => setSettings({ ...settings, auto_approve: !settings.auto_approve })}
              className={`relative w-10 h-5 rounded-full transition-all ${
                settings.auto_approve ? 'bg-[#8FAA86]' : 'bg-white/10'
              }`}
            >
              <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${
                settings.auto_approve ? 'left-5' : 'left-0.5'
              }`} />
            </button>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <Button onClick={handleSave} disabled={saving} className="bg-[#C4972A] hover:bg-[#a87a1f] text-white">
              {saving ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Save className="w-4 h-4 mr-1" />}
              Kaydet
            </Button>
            <Button
              onClick={handleTrigger}
              disabled={triggering}
              variant="outline"
              className="border-purple-500/30 text-purple-400"
            >
              {triggering ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Sparkles className="w-4 h-4 mr-1" />}
              Simdi Uret
            </Button>
          </div>
        </div>
      </div>

      {/* History */}
      <div className="col-span-5">
        <div className="glass rounded-xl p-6">
          <h3 className="text-sm font-medium text-[#e5e5e8] mb-4 flex items-center gap-2">
            <Clock className="w-4 h-4 text-[#C4972A]" /> Gecmis
          </h3>

          {history.length === 0 && (
            <p className="text-xs text-[#7e7e8a] text-center py-6">Henuz otomatik icerik uretilmedi</p>
          )}

          <div className="space-y-3">
            {history.map((h, i) => (
              <div key={i} className="p-3 rounded-lg bg-white/5">
                <div className="flex items-center gap-2 mb-1">
                  {h.status === 'error' ? (
                    <AlertCircle className="w-3.5 h-3.5 text-red-400" />
                  ) : h.auto_approved ? (
                    <Send className="w-3.5 h-3.5 text-[#8FAA86]" />
                  ) : (
                    <FileText className="w-3.5 h-3.5 text-[#C4972A]" />
                  )}
                  <span className="text-xs text-[#e5e5e8] font-medium truncate">{h.title || h.error || 'Icerik'}</span>
                </div>
                {h.content_preview && (
                  <p className="text-[10px] text-[#7e7e8a] line-clamp-2 mb-1">{h.content_preview}</p>
                )}
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-[10px] text-[#5a5a65]">
                    {topicLabels[h.topic] || h.topic}
                  </span>
                  <span className="text-[10px] text-[#5a5a65]">
                    {h.created_at ? new Date(h.created_at).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : ''}
                  </span>
                  {h.publish_results && Object.entries(h.publish_results).map(([plat, res]) => (
                    <span key={plat} className={`text-[10px] px-1.5 py-0.5 rounded ${
                      res.status === 'published' ? 'bg-green-500/15 text-green-400' :
                      res.status === 'mock_published' ? 'bg-yellow-500/15 text-yellow-400' :
                      'bg-red-500/15 text-red-400'
                    }`}>
                      {plat}: {res.status === 'published' ? 'Yayinda' : res.status === 'mock_published' ? 'Mock' : 'Hata'}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}


/* ─── Content Calendar Panel ─── */
function ContentCalendarPanel() {
  const [calendar, setCalendar] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getContentCalendar(14).then(res => {
      setCalendar(res.data.calendar || []);
    }).catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8"><div className="h-8 w-48 bg-white/5 rounded animate-pulse" /></div>;

  return (
    <div className="glass rounded-xl p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
          <Calendar className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-[#e5e5e8]">Icerik Takvimi</h2>
          <p className="text-xs text-[#7e7e8a]">Yaklasan 14 gunluk gonderi plani</p>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-3">
        {calendar.map((day, i) => {
          const isToday = i === 0;
          return (
            <div
              key={day.date}
              className={`rounded-xl p-3 transition-all ${
                isToday
                  ? 'bg-[#C4972A]/10 border border-[#C4972A]/30'
                  : 'bg-white/5 border border-white/5'
              }`}
            >
              <div className="text-center mb-2">
                <span className={`text-[10px] font-medium ${isToday ? 'text-[#C4972A]' : 'text-[#7e7e8a]'}`}>
                  {day.day_name}
                </span>
                <p className={`text-sm font-bold ${isToday ? 'text-[#C4972A]' : 'text-[#e5e5e8]'}`}>
                  {day.date.split('-')[2]}
                </p>
              </div>

              {day.post_count > 0 ? (
                <div className="space-y-1">
                  {day.posts.slice(0, 3).map((post, j) => {
                    const statusStyle = STATUS_COLORS[post.status] || STATUS_COLORS.draft;
                    return (
                      <div key={j} className="p-1.5 rounded-md bg-white/5">
                        <p className="text-[9px] text-[#c5c5ce] truncate">{post.title || 'Basliksiz'}</p>
                        <span className="text-[8px] px-1 py-0.5 rounded" style={{ background: statusStyle.bg, color: statusStyle.text }}>
                          {statusStyle.label}
                        </span>
                      </div>
                    );
                  })}
                  {day.post_count > 3 && (
                    <p className="text-[9px] text-[#7e7e8a] text-center">+{day.post_count - 3} daha</p>
                  )}
                </div>
              ) : (
                <div className="text-center py-2">
                  <span className="text-[10px] text-[#5a5a65]">Bos</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}


/* ─── Batch Drive Import Panel ─── */
function BatchDrivePanel({ onComplete }) {
  const [driveLinks, setDriveLinks] = useState('');
  const [platforms, setPlatforms] = useState(['instagram', 'facebook']);
  const [tone, setTone] = useState('warm');
  const [autoCaption, setAutoCaption] = useState(true);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [platformStatus, setPlatformStatus] = useState(null);

  useEffect(() => {
    getPlatformStatus().then(res => setPlatformStatus(res.data?.platforms || null)).catch(() => {});
  }, []);

  const handleImport = async () => {
    const links = driveLinks.split('\n').map(l => l.trim()).filter(Boolean);
    if (links.length === 0) return;

    setImporting(true);
    setError(null);
    setResult(null);

    try {
      const res = await batchDriveImport({
        drive_links: links,
        platforms,
        tone,
        auto_caption: autoCaption,
        post_type: 'text',
      });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Toplu yukleme basarisiz oldu');
    }
    setImporting(false);
  };

  const toneOptions = [
    { id: 'warm', label: 'Sicak & Samimi' },
    { id: 'professional', label: 'Profesyonel' },
    { id: 'playful', label: 'Eglenceli' },
    { id: 'elegant', label: 'Zarif' },
  ];

  const linkCount = driveLinks.split('\n').map(l => l.trim()).filter(Boolean).length;

  return (
    <div className="space-y-6">
      <div className="glass rounded-xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center">
            <Upload className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-[#e5e5e8]">Toplu Drive Yukleme</h2>
            <p className="text-xs text-[#7e7e8a]">Google Drive linklerini yapistirin, AI otomatik caption uretsin</p>
          </div>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Left: Input */}
          <div className="col-span-7 space-y-4">
            {/* Drive Links */}
            <div>
              <label className="text-xs text-[#7e7e8a] mb-2 block flex items-center gap-2">
                <FolderOpen className="w-3.5 h-3.5" />
                Google Drive Linkleri (her satira bir link)
              </label>
              <textarea
                value={driveLinks}
                onChange={e => setDriveLinks(e.target.value)}
                className="w-full min-h-[200px] p-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm resize-y outline-none focus:border-green-500/50 font-mono"
                placeholder={`https://drive.google.com/file/d/.../view\nhttps://drive.google.com/file/d/.../view\nhttps://drive.google.com/file/d/.../view`}
                data-testid="batch-drive-input"
              />
              <div className="flex items-center justify-between mt-1">
                <p className="text-[10px] text-[#5a5a65]">
                  Drive'da gorselleri "Linke sahip olan herkes gorebilir" yapmayi unutmayin
                </p>
                <span className={`text-xs font-medium ${linkCount > 0 ? 'text-green-400' : 'text-[#7e7e8a]'}`}>
                  {linkCount} gorsel
                </span>
              </div>
            </div>

            {/* Tone */}
            <div>
              <label className="text-xs text-[#7e7e8a] mb-2 block">AI Caption Tonu</label>
              <div className="flex gap-2">
                {toneOptions.map(t => (
                  <button
                    key={t.id}
                    onClick={() => setTone(t.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs transition-all ${
                      tone === t.id
                        ? 'bg-[#C4972A]/15 text-[#C4972A]'
                        : 'text-[#7e7e8a] hover:bg-white/5'
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Platforms */}
            <div>
              <label className="text-xs text-[#7e7e8a] mb-2 block">Hedef Platformlar</label>
              <div className="flex gap-2">
                {PLATFORMS.map(p => {
                  const PIcon = p.icon;
                  const selected = platforms.includes(p.id);
                  const status = platformStatus?.[p.id];
                  return (
                    <button
                      key={p.id}
                      onClick={() => {
                        setPlatforms(selected
                          ? platforms.filter(x => x !== p.id)
                          : [...platforms, p.id]
                        );
                      }}
                      className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs transition-all border ${
                        selected ? 'border-white/20' : 'border-transparent hover:bg-white/5'
                      }`}
                      style={{
                        background: selected ? `${p.color}15` : 'transparent',
                        color: selected ? p.color : '#7e7e8a',
                      }}
                    >
                      <PIcon className="w-3.5 h-3.5" />
                      {p.name}
                      {status && (
                        status.configured
                          ? <Wifi className="w-2.5 h-2.5 text-green-400" />
                          : <WifiOff className="w-2.5 h-2.5 text-amber-400" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Auto Caption Toggle */}
            <div className="flex items-center justify-between p-3 rounded-lg bg-white/5">
              <div>
                <p className="text-xs text-[#e5e5e8] flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                  AI Otomatik Caption
                </p>
                <p className="text-[10px] text-[#7e7e8a]">Her gorsel icin AI baslik, icerik ve hashtag uretir</p>
              </div>
              <button
                onClick={() => setAutoCaption(!autoCaption)}
                className={`relative w-10 h-5 rounded-full transition-all ${autoCaption ? 'bg-purple-500' : 'bg-white/10'}`}
              >
                <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${autoCaption ? 'left-5' : 'left-0.5'}`} />
              </button>
            </div>

            {/* Import Button */}
            <Button
              onClick={handleImport}
              disabled={importing || linkCount === 0}
              className="w-full bg-gradient-to-r from-green-600 to-emerald-500 hover:from-green-700 hover:to-emerald-600 text-white py-3"
              data-testid="batch-import-btn"
            >
              {importing ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> {linkCount} Gorsel Isleniyor...</>
              ) : (
                <><Upload className="w-4 h-4 mr-2" /> {linkCount} Gorseli Yukle & Caption Uret</>
              )}
            </Button>
          </div>

          {/* Right: Results / Info */}
          <div className="col-span-5 space-y-4">
            {/* Platform Status */}
            {platformStatus && (
              <div className="glass rounded-xl p-4">
                <h3 className="text-xs font-medium text-[#e5e5e8] mb-3 flex items-center gap-2">
                  <Settings className="w-3.5 h-3.5 text-[#C4972A]" /> Platform Durumu
                </h3>
                <div className="space-y-2">
                  {Object.entries(platformStatus).map(([key, status]) => {
                    const plat = PLATFORMS.find(p => p.id === key);
                    if (!plat) return null;
                    const PIcon = plat.icon;
                    return (
                      <div key={key} className="flex items-center justify-between p-2 rounded-lg bg-white/5">
                        <div className="flex items-center gap-2">
                          <PIcon className="w-3.5 h-3.5" style={{ color: plat.color }} />
                          <span className="text-xs text-[#c5c5ce]">{plat.name}</span>
                        </div>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full ${
                          status.mode === 'live'
                            ? 'bg-green-500/15 text-green-400'
                            : status.mode === 'mock'
                            ? 'bg-amber-500/15 text-amber-400'
                            : 'bg-white/5 text-[#7e7e8a]'
                        }`}>
                          {status.mode === 'live' ? 'Aktif' : status.mode === 'mock' ? 'Mock' : 'Manuel'}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* How to use */}
            {!result && !error && (
              <div className="glass rounded-xl p-4">
                <h3 className="text-xs font-medium text-[#e5e5e8] mb-3">Nasil Kullanilir?</h3>
                <ol className="space-y-2 text-[11px] text-[#7e7e8a]">
                  <li className="flex gap-2">
                    <span className="text-[#C4972A] font-bold">1.</span>
                    Google Drive'a gorselleri yukleyin
                  </li>
                  <li className="flex gap-2">
                    <span className="text-[#C4972A] font-bold">2.</span>
                    Her gorseli "Linke sahip olan herkes" ile paylasin
                  </li>
                  <li className="flex gap-2">
                    <span className="text-[#C4972A] font-bold">3.</span>
                    Paylasim linklerini kopyalayip buraya yapistirin
                  </li>
                  <li className="flex gap-2">
                    <span className="text-[#C4972A] font-bold">4.</span>
                    AI otomatik caption/hashtag uretir
                  </li>
                  <li className="flex gap-2">
                    <span className="text-[#C4972A] font-bold">5.</span>
                    Taslak olarak kaydedilir, tek tikla yayinlayin
                  </li>
                </ol>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10">
                <div className="flex items-center gap-2 text-red-400 text-sm">
                  <AlertCircle className="w-4 h-4" />
                  {error}
                </div>
              </div>
            )}

            {/* Result */}
            {result && (
              <div className="space-y-3">
                <div className="p-4 rounded-xl border border-green-500/20 bg-green-500/5">
                  <div className="flex items-center gap-2 mb-3">
                    <CheckCircle2 className="w-5 h-5 text-green-400" />
                    <span className="text-sm text-green-400 font-medium">
                      {result.created} Gonderi Olusturuldu
                    </span>
                  </div>

                  {result.errors > 0 && (
                    <div className="mb-3 p-2 rounded-lg bg-red-500/10 border border-red-500/20">
                      <span className="text-xs text-red-400">{result.errors} gorsel yuklenemedi</span>
                      {result.error_details?.map((e, i) => (
                        <p key={i} className="text-[10px] text-red-400/70 mt-1">{e.error}</p>
                      ))}
                    </div>
                  )}

                  {/* Created posts preview */}
                  <div className="space-y-2 max-h-[300px] overflow-y-auto">
                    {result.posts?.map((post, i) => (
                      <div key={i} className="p-3 rounded-lg bg-white/5">
                        <div className="flex items-start gap-3">
                          {post.image_url && (
                            <img
                              src={post.image_url}
                              alt=""
                              className="w-12 h-12 rounded-lg object-cover flex-shrink-0"
                              onError={(e) => { e.target.style.display = 'none'; }}
                            />
                          )}
                          <div className="flex-1 min-w-0">
                            <p className="text-xs text-[#e5e5e8] font-medium truncate">{post.title}</p>
                            <p className="text-[10px] text-[#7e7e8a] line-clamp-2">{post.content}</p>
                            {post.hashtags?.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-1">
                                {post.hashtags.slice(0, 4).map((h, j) => (
                                  <span key={j} className="text-[9px] text-[#C4972A]">#{h}</span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <Button
                    onClick={onComplete}
                    className="w-full mt-3 bg-[#C4972A] hover:bg-[#a87a1f] text-white text-xs"
                  >
                    <ChevronRight className="w-3.5 h-3.5 mr-1" /> Gonderilere Git & Yayinla
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


/* ─── Frame Preview (Full) ─── */
const FramePreview = React.forwardRef(({ post, frameStyles }, ref) => {
  const styles = (frameStyles.length > 0 ? frameStyles : [
    { id: 'default', bg: '#515249', text: '#F8F5EF', accent: '#B07A2A' },
    { id: 'elegant', bg: '#1E1B16', text: '#F8F5EF', accent: '#C5A059' },
    { id: 'bold', bg: '#8FAA86', text: '#1E1B16', accent: '#515249' },
    { id: 'minimal', bg: '#F3EEE4', text: '#1E1B16', accent: '#515249' },
    { id: 'festive', bg: '#3F403A', text: '#F8F5EF', accent: '#D4A847' },
  ]).find(s => s.id === post.frame_style) || { bg: '#515249', text: '#F8F5EF', accent: '#B07A2A' };

  const hasImage = post.image_url;

  return (
    <div
      ref={ref}
      className="rounded-2xl overflow-hidden"
      style={{
        background: styles.bg,
        aspectRatio: '1/1',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: hasImage ? 'flex-end' : 'center',
        alignItems: 'center',
        padding: hasImage ? 0 : 32,
        position: 'relative',
      }}
      data-testid="frame-preview"
    >
      {/* Background Image */}
      {hasImage && (
        <img
          src={post.image_url}
          alt="Post"
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
          }}
        />
      )}

      {/* Overlay for image */}
      {hasImage && (
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 50%)',
        }} />
      )}

      {/* Corner decorations */}
      <div style={{ position: 'absolute', top: 16, left: 16, width: 24, height: 24, borderTop: `2px solid ${hasImage ? '#fff' : styles.accent}40`, borderLeft: `2px solid ${hasImage ? '#fff' : styles.accent}40` }} />
      <div style={{ position: 'absolute', top: 16, right: 16, width: 24, height: 24, borderTop: `2px solid ${hasImage ? '#fff' : styles.accent}40`, borderRight: `2px solid ${hasImage ? '#fff' : styles.accent}40` }} />
      <div style={{ position: 'absolute', bottom: 16, left: 16, width: 24, height: 24, borderBottom: `2px solid ${hasImage ? '#fff' : styles.accent}40`, borderLeft: `2px solid ${hasImage ? '#fff' : styles.accent}40` }} />
      <div style={{ position: 'absolute', bottom: 16, right: 16, width: 24, height: 24, borderBottom: `2px solid ${hasImage ? '#fff' : styles.accent}40`, borderRight: `2px solid ${hasImage ? '#fff' : styles.accent}40` }} />

      {/* Logo */}
      <img
        src="/brand/KOZBEYLI_BEYAZ_LOGO.png"
        alt="Logo"
        style={{
          width: hasImage ? 40 : 60,
          height: 'auto',
          marginBottom: hasImage ? 8 : 16,
          filter: (!hasImage && styles.bg === '#F3EEE4') ? 'invert(1)' : 'none',
          position: hasImage ? 'absolute' : 'relative',
          top: hasImage ? 20 : 'auto',
          zIndex: 1,
        }}
        onError={(e) => { e.target.style.display = 'none'; }}
      />

      {/* Content container */}
      <div style={{
        position: 'relative',
        zIndex: 1,
        padding: hasImage ? '24px 32px 32px' : 0,
        textAlign: 'center',
      }}>
        <h2 style={{
          color: hasImage ? '#fff' : styles.accent,
          fontSize: 11,
          letterSpacing: '0.15em',
          textTransform: 'uppercase',
          fontWeight: 600,
          marginBottom: 8,
          fontFamily: "'Alifira', serif",
        }}>
          {post.title || 'Baslik'}
        </h2>

        <p style={{
          color: hasImage ? '#fff' : styles.text,
          fontSize: 13,
          textAlign: 'center',
          lineHeight: 1.6,
          maxWidth: '85%',
          margin: '0 auto',
          opacity: hasImage ? 1 : 0.9,
        }}>
          {post.content?.substring(0, 100) || 'Gonderi icerigi...'}
        </p>
      </div>

      {/* Brand */}
      <div style={{
        position: 'absolute', bottom: 24,
        color: hasImage ? 'rgba(255,255,255,0.6)' : `${styles.text}60`,
        fontSize: 9,
        letterSpacing: '0.15em',
        textTransform: 'uppercase',
        zIndex: 1,
      }}>
        KOZBEYLI KONAGI
      </div>
    </div>
  );
});

/* ─── Frame Preview Mini (for list) ─── */
function FramePreviewMini({ post, frameStyles }) {
  const styles = (frameStyles.length > 0 ? frameStyles : [
    { id: 'default', bg: '#515249', text: '#F8F5EF', accent: '#B07A2A' },
    { id: 'elegant', bg: '#1E1B16', text: '#F8F5EF', accent: '#C5A059' },
    { id: 'bold', bg: '#8FAA86', text: '#1E1B16', accent: '#515249' },
    { id: 'minimal', bg: '#F3EEE4', text: '#1E1B16', accent: '#515249' },
    { id: 'festive', bg: '#3F403A', text: '#F8F5EF', accent: '#D4A847' },
  ]).find(s => s.id === post.frame_style) || { bg: '#515249', text: '#F8F5EF', accent: '#B07A2A' };

  return (
    <div
      style={{
        width: 52, height: 52, borderRadius: 10,
        background: styles.bg,
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        flexShrink: 0, border: `1px solid ${styles.accent}30`,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {post.image_url ? (
        <>
          <img
            src={post.image_url}
            alt=""
            style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }}
          />
          <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.3)' }} />
          <Image style={{ width: 16, height: 16, color: '#fff', position: 'relative', zIndex: 1 }} />
        </>
      ) : (
        <>
          <div style={{ width: 16, height: 1.5, background: styles.accent, marginBottom: 3, borderRadius: 1 }} />
          <div style={{ width: 24, height: 1, background: `${styles.text}40`, marginBottom: 2, borderRadius: 1 }} />
          <div style={{ width: 20, height: 1, background: `${styles.text}20`, borderRadius: 1 }} />
        </>
      )}
    </div>
  );
}


// ==================== CONTENT QUEUE PANEL ====================
function ContentQueuePanel({ onRefresh }) {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [optimalTime, setOptimalTime] = useState(null);

  const loadQueue = async () => {
    setLoading(true);
    try {
      const res = await getContentQueue();
      setQueue(res.data || []);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  const loadOptimalTime = async () => {
    try {
      const res = await getOptimalTime('instagram,facebook', '');
      setOptimalTime(res.data);
    } catch (err) { console.error(err); }
  };

  useEffect(() => { loadQueue(); loadOptimalTime(); }, []);

  const handleRemove = async (postId) => {
    try {
      await removeFromQueue(postId);
      loadQueue();
      if (onRefresh) onRefresh();
    } catch (err) { console.error(err); }
  };

  const handlePublishScheduled = async () => {
    try {
      await publishScheduledPosts();
      loadQueue();
      if (onRefresh) onRefresh();
    } catch (err) { console.error(err); }
  };

  if (loading) return <div className="text-center py-12 text-[#7e7e8a]"><Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />Kuyruk yukleniyor...</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white">Icerik Kuyrugu</h2>
          <p className="text-xs text-[#7e7e8a]">Sira tabanlı gonderi kuyrugu - otomatik yayinlama icin sirala</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handlePublishScheduled} className="bg-green-600/80 hover:bg-green-600 text-white text-xs">
            <Send className="w-3.5 h-3.5 mr-1" /> Planlanmislari Yayinla
          </Button>
          <Button onClick={loadQueue} variant="ghost" className="text-[#7e7e8a]">
            <RefreshCw className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>

      {/* Optimal Time Info */}
      {optimalTime && (
        <div className="glass rounded-xl p-4 border border-[#C4972A]/20">
          <div className="flex items-center gap-2 mb-1">
            <Clock className="w-4 h-4 text-[#C4972A]" />
            <span className="text-sm font-medium text-[#C4972A]">Optimal Yayinlama Saati</span>
          </div>
          <p className="text-white text-lg font-bold">{optimalTime.optimal_time || optimalTime}</p>
          <p className="text-xs text-[#7e7e8a]">Instagram & Facebook icin bugunun en iyi saati</p>
        </div>
      )}

      {/* Queue Items */}
      {queue.length === 0 ? (
        <div className="glass rounded-xl p-8 text-center">
          <List className="w-8 h-8 text-[#7e7e8a] mx-auto mb-2" />
          <p className="text-[#7e7e8a]">Kuyrukta gonderi yok</p>
          <p className="text-xs text-[#7e7e8a] mt-1">Gonderiler sekmesinden kuyruga ekleyin</p>
        </div>
      ) : (
        <div className="space-y-3">
          {queue.map((post, idx) => (
            <div key={post.id || idx} className="glass rounded-xl p-4 flex items-center gap-4">
              <div className="w-8 h-8 rounded-lg bg-[#C4972A]/10 flex items-center justify-center text-[#C4972A] font-bold text-sm">
                {idx + 1}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-medium truncate">{post.title || 'Baslıksiz'}</p>
                <p className="text-xs text-[#7e7e8a] truncate">{(post.content || '').slice(0, 80)}</p>
                <div className="flex gap-1 mt-1">
                  {(post.platforms || []).map(p => (
                    <span key={p} className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-[#7e7e8a]">{p}</span>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs px-2 py-1 rounded" style={{
                  background: post.status === 'scheduled' ? '#C4972A20' : '#7e7e8a20',
                  color: post.status === 'scheduled' ? '#C4972A' : '#7e7e8a'
                }}>
                  {post.status === 'scheduled' ? 'Planlanmis' : 'Taslak'}
                </span>
                <button onClick={() => handleRemove(post.id)} className="text-red-400 hover:text-red-300 p-1">
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}


// ==================== WEEKLY PLANNER PANEL ====================
function WeeklyPlannerPanel() {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadPlan = async () => {
    setLoading(true);
    try {
      const res = await getWeeklyPlan();
      setPlan(res.data);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  useEffect(() => { loadPlan(); }, []);

  if (loading) return <div className="text-center py-12 text-[#7e7e8a]"><Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />Plan yukleniyor...</div>;

  const DAY_COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f97316', '#22c55e', '#06b6d4', '#C4972A'];
  const TOPIC_ICONS = {
    morning: '☀️', menu_highlight: '🍽️', local: '🏛️', behind_scenes: '🎬',
    guest_story: '💬', weekend: '🏖️', seasonal: '🌸',
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white">Haftalik Icerik Plani</h2>
          <p className="text-xs text-[#7e7e8a]">
            {plan?.week_start ? `Hafta: ${plan.week_start}` : 'Otomatik oluşturulan haftalık plan'}
          </p>
        </div>
        <Button onClick={loadPlan} variant="ghost" className="text-[#7e7e8a]">
          <RefreshCw className="w-3.5 h-3.5 mr-1" /> Yenile
        </Button>
      </div>

      {plan?.plan ? (
        <div className="grid grid-cols-7 gap-3">
          {plan.plan.map((day, idx) => (
            <div key={day.date} className="glass rounded-xl p-4 border-t-2" style={{ borderColor: DAY_COLORS[idx] }}>
              <div className="text-center mb-3">
                <span className="text-xs font-bold" style={{ color: DAY_COLORS[idx] }}>{day.day_name}</span>
                <p className="text-[10px] text-[#7e7e8a]">{day.date}</p>
              </div>
              <div className="text-2xl text-center mb-2">{TOPIC_ICONS[day.topic] || '📝'}</div>
              <p className="text-xs text-white text-center font-medium mb-2">{day.label?.split(' - ')[1] || day.topic}</p>
              <div className="text-center">
                <span className="text-[10px] px-2 py-1 rounded-full bg-[#C4972A]/10 text-[#C4972A]">
                  <Clock className="w-3 h-3 inline mr-0.5" />{day.optimal_time}
                </span>
              </div>
              <div className="flex justify-center gap-1 mt-2">
                {(day.platforms || []).map(p => (
                  <span key={p} className="text-[9px] px-1 py-0.5 rounded bg-white/5 text-[#7e7e8a]">{p}</span>
                ))}
              </div>
              <div className="mt-2 text-center">
                <span className="text-[10px] px-2 py-0.5 rounded" style={{
                  background: day.status === 'planned' ? '#7e7e8a20' : '#8FAA8620',
                  color: day.status === 'planned' ? '#7e7e8a' : '#8FAA86',
                }}>
                  {day.status === 'planned' ? 'Planlandı' : 'Hazir'}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass rounded-xl p-8 text-center">
          <Calendar className="w-8 h-8 text-[#7e7e8a] mx-auto mb-2" />
          <p className="text-[#7e7e8a]">Henuz plan olusturulmadı</p>
        </div>
      )}
    </div>
  );
}


// ==================== RECYCLE PANEL ====================
function RecyclePanel({ onRefresh }) {
  const [recyclable, setRecyclable] = useState([]);
  const [loading, setLoading] = useState(true);
  const [recycling, setRecycling] = useState(null);
  const [scores, setScores] = useState({});

  const loadRecyclable = async () => {
    setLoading(true);
    try {
      const res = await getRecyclablePosts();
      setRecyclable(res.data || []);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  useEffect(() => { loadRecyclable(); }, []);

  const handleRecycle = async (postId) => {
    setRecycling(postId);
    try {
      await recyclePost(postId);
      loadRecyclable();
      if (onRefresh) onRefresh();
    } catch (err) { console.error(err); }
    setRecycling(null);
  };

  const loadScore = async (postId) => {
    if (scores[postId]) return;
    try {
      const res = await getPostScore(postId);
      setScores(prev => ({ ...prev, [postId]: res.data }));
    } catch (err) { console.error(err); }
  };

  const GRADE_COLORS = { A: '#22c55e', B: '#C4972A', C: '#f97316', D: '#ef4444' };

  if (loading) return <div className="text-center py-12 text-[#7e7e8a]"><Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />Geri donusum yukleniyor...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white">Icerik Geri Donusumu</h2>
          <p className="text-xs text-[#7e7e8a]">30+ gun once yayinlanmis basarili gonderileri tekrar paylas</p>
        </div>
        <Button onClick={loadRecyclable} variant="ghost" className="text-[#7e7e8a]">
          <RefreshCw className="w-3.5 h-3.5" />
        </Button>
      </div>

      {recyclable.length === 0 ? (
        <div className="glass rounded-xl p-8 text-center">
          <RefreshCw className="w-8 h-8 text-[#7e7e8a] mx-auto mb-2" />
          <p className="text-[#7e7e8a]">Geri donusturulebilecek gonderi bulunamadı</p>
          <p className="text-xs text-[#7e7e8a] mt-1">30 gunden eski yayinlanmis gonderiler burada gorunur</p>
        </div>
      ) : (
        <div className="space-y-3">
          {recyclable.map(post => (
            <div key={post.id} className="glass rounded-xl p-4">
              <div className="flex items-start gap-4">
                {post.image_url && (
                  <img src={post.image_url} alt="" className="w-16 h-16 rounded-lg object-cover" />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm font-medium truncate">{post.title || 'Baslıksiz'}</p>
                  <p className="text-xs text-[#7e7e8a] truncate">{(post.content || '').slice(0, 100)}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] text-[#7e7e8a]">
                      Yayinlanma: {post.published_at ? new Date(post.published_at).toLocaleDateString('tr-TR') : '-'}
                    </span>
                    <div className="flex gap-1">
                      {(post.platforms || []).map(p => (
                        <span key={p} className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-[#7e7e8a]">{p}</span>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {/* Performance Score */}
                  {scores[post.id] ? (
                    <div className="text-center">
                      <span className="text-lg font-bold" style={{ color: GRADE_COLORS[scores[post.id].grade] }}>
                        {scores[post.id].grade}
                      </span>
                      <p className="text-[10px] text-[#7e7e8a]">{scores[post.id].score}/100</p>
                    </div>
                  ) : (
                    <button onClick={() => loadScore(post.id)} className="text-xs text-[#C4972A] hover:underline">
                      <Star className="w-3.5 h-3.5" />
                    </button>
                  )}
                  <Button
                    onClick={() => handleRecycle(post.id)}
                    disabled={recycling === post.id}
                    className="bg-[#C4972A]/80 hover:bg-[#C4972A] text-white text-xs"
                  >
                    {recycling === post.id ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <><RotateCcw className="w-3.5 h-3.5 mr-1" /> Tekrar Paylas</>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}


// ==================== ESCALATION PANEL ====================
function EscalationPanel() {
  const [escalations, setEscalations] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');

  const loadData = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filterStatus !== 'all') params.status = filterStatus;
      const [escRes, statsRes] = await Promise.all([
        getEscalations(params),
        getEscalationStats(),
      ]);
      setEscalations(escRes.data?.escalations || []);
      setStats(statsRes.data);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  useEffect(() => { loadData(); }, [filterStatus]);

  const handleResolve = async (id) => {
    try {
      await resolveEscalation(id, 'Yonetici tarafından cozuldu');
      loadData();
    } catch (err) { console.error(err); }
  };

  const SEVERITY_COLORS = {
    HIGH: { bg: '#ef444420', text: '#ef4444', label: 'Yuksek' },
    MEDIUM: { bg: '#f9731620', text: '#f97316', label: 'Orta' },
    LOW: { bg: '#C4972A20', text: '#C4972A', label: 'Dusuk' },
  };

  const REASON_LABELS = {
    urgent_situation: 'Acil Durum',
    very_negative_sentiment: 'Negatif Duygu',
    ai_uncertainty: 'AI Belirsizlik',
    repeated_question: 'Tekrar Soru',
  };

  if (loading) return <div className="text-center py-12 text-[#7e7e8a]"><Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />Yukleniyor...</div>;

  return (
    <div className="space-y-6">
      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-4 gap-4">
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-4 h-4 text-[#C4972A]" />
              <span className="text-xs text-[#7e7e8a]">Toplam</span>
            </div>
            <span className="text-2xl font-bold text-white">{stats.total || 0}</span>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-4 h-4 text-red-400" />
              <span className="text-xs text-[#7e7e8a]">Acik</span>
            </div>
            <span className="text-2xl font-bold text-red-400">{stats.open || 0}</span>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 className="w-4 h-4 text-green-400" />
              <span className="text-xs text-[#7e7e8a]">Cozuldu</span>
            </div>
            <span className="text-2xl font-bold text-green-400">{stats.resolved || 0}</span>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-[#C4972A]" />
              <span className="text-xs text-[#7e7e8a]">Cozum Oranı</span>
            </div>
            <span className="text-2xl font-bold text-[#C4972A]">
              {stats.total ? Math.round((stats.resolved / stats.total) * 100) : 0}%
            </span>
          </div>
        </div>
      )}

      {/* Filter */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {[
            { id: 'all', label: 'Tumu' },
            { id: 'open', label: 'Acik' },
            { id: 'resolved', label: 'Cozuldu' },
          ].map(f => (
            <button
              key={f.id}
              onClick={() => setFilterStatus(f.id)}
              className={`px-3 py-1.5 rounded-lg text-xs transition-all ${
                filterStatus === f.id ? 'bg-[#C4972A]/15 text-[#C4972A]' : 'text-[#7e7e8a] hover:bg-white/5'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
        <Button onClick={loadData} variant="ghost" className="text-[#7e7e8a]">
          <RefreshCw className="w-3.5 h-3.5" />
        </Button>
      </div>

      {/* List */}
      {escalations.length === 0 ? (
        <div className="glass rounded-xl p-8 text-center">
          <CheckCircle2 className="w-8 h-8 text-green-400 mx-auto mb-2" />
          <p className="text-[#7e7e8a]">Escalation kaydı bulunamadı</p>
        </div>
      ) : (
        <div className="space-y-3">
          {escalations.map(esc => {
            const sev = SEVERITY_COLORS[esc.severity] || SEVERITY_COLORS.LOW;
            return (
              <div key={esc.id} className="glass rounded-xl p-4 border-l-4" style={{ borderColor: sev.text }}>
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs px-2 py-0.5 rounded" style={{ background: sev.bg, color: sev.text }}>
                        {sev.label}
                      </span>
                      <span className="text-xs text-[#7e7e8a]">
                        {REASON_LABELS[esc.reason] || esc.reason}
                      </span>
                      <span className="text-[10px] text-[#7e7e8a]">
                        {esc.platform}
                      </span>
                    </div>
                    <p className="text-white text-sm mt-1">{esc.message}</p>
                    {esc.ai_response && (
                      <p className="text-xs text-[#7e7e8a] mt-1 italic">AI: {esc.ai_response}</p>
                    )}
                    <p className="text-[10px] text-[#7e7e8a] mt-1">
                      {esc.created_at ? new Date(esc.created_at).toLocaleString('tr-TR') : ''}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    {esc.status === 'open' ? (
                      <Button onClick={() => handleResolve(esc.id)} className="bg-green-600/80 hover:bg-green-600 text-white text-xs">
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Coz
                      </Button>
                    ) : (
                      <span className="text-xs px-2 py-1 rounded bg-green-500/10 text-green-400">Cozuldu</span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
