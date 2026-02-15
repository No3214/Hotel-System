import React, { useState, useEffect, useRef } from 'react';
import { getSocialPosts, createSocialPost, updateSocialPost, deleteSocialPost, publishSocialPost, getSocialTemplates, getSocialStats } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Plus, Trash2, Edit2, Save, X, Send, Copy, Instagram, Facebook, Twitter, MessageCircle, Eye, BarChart3, FileText, Sparkles, Clock } from 'lucide-react';

const PLATFORMS = [
  { id: 'instagram', name: 'Instagram', icon: Instagram, color: '#E1306C' },
  { id: 'facebook', name: 'Facebook', icon: Facebook, color: '#1877F2' },
  { id: 'twitter', name: 'X (Twitter)', icon: Twitter, color: '#e5e5e8' },
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
    });
    setView('create');
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
      loadData();
    } catch (err) { console.error(err); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bu gonderiyi silmek istediginize emin misiniz?')) return;
    await deleteSocialPost(id);
    loadData();
  };

  const handlePublish = async (id) => {
    await publishSocialPost(id);
    loadData();
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
          <p className="text-[#7e7e8a] text-sm mt-1">Icerik olustur, duzenle ve platformlara paylas</p>
        </div>
        {view === 'list' && (
          <div className="flex gap-2">
            <Button onClick={() => startCreate('menu_highlight')} className="bg-[#8FAA86] hover:bg-[#7a9874] text-white" data-testid="new-menu-post">
              <Sparkles className="w-4 h-4 mr-1" /> Menu Vitrin
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

      {/* Stats */}
      {view === 'list' && stats && (
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

      {/* LIST VIEW */}
      {view === 'list' && (
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
                    {/* Frame Preview Mini */}
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
                      </div>
                      <p className="text-xs text-[#7e7e8a] line-clamp-2 mb-2">{post.content}</p>
                      <div className="flex items-center gap-3">
                        {/* Platform Icons */}
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
                        <button onClick={() => handlePublish(post.id)} className="p-1.5 rounded-lg hover:bg-[#8FAA86]/10 text-[#8FAA86]" title="Yayinla"><Send className="w-3.5 h-3.5" /></button>
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

/* ─── Frame Preview (Full) ─── */
const FramePreview = React.forwardRef(({ post, frameStyles }, ref) => {
  const styles = (frameStyles.length > 0 ? frameStyles : [
    { id: 'default', bg: '#515249', text: '#F8F5EF', accent: '#B07A2A' },
    { id: 'elegant', bg: '#1E1B16', text: '#F8F5EF', accent: '#C5A059' },
    { id: 'bold', bg: '#8FAA86', text: '#1E1B16', accent: '#515249' },
    { id: 'minimal', bg: '#F3EEE4', text: '#1E1B16', accent: '#515249' },
    { id: 'festive', bg: '#3F403A', text: '#F8F5EF', accent: '#D4A847' },
  ]).find(s => s.id === post.frame_style) || { bg: '#515249', text: '#F8F5EF', accent: '#B07A2A' };

  return (
    <div
      ref={ref}
      className="rounded-2xl overflow-hidden"
      style={{
        background: styles.bg,
        aspectRatio: '1/1',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 32,
        position: 'relative',
      }}
      data-testid="frame-preview"
    >
      {/* Corner decorations */}
      <div style={{ position: 'absolute', top: 16, left: 16, width: 24, height: 24, borderTop: `2px solid ${styles.accent}40`, borderLeft: `2px solid ${styles.accent}40` }} />
      <div style={{ position: 'absolute', top: 16, right: 16, width: 24, height: 24, borderTop: `2px solid ${styles.accent}40`, borderRight: `2px solid ${styles.accent}40` }} />
      <div style={{ position: 'absolute', bottom: 16, left: 16, width: 24, height: 24, borderBottom: `2px solid ${styles.accent}40`, borderLeft: `2px solid ${styles.accent}40` }} />
      <div style={{ position: 'absolute', bottom: 16, right: 16, width: 24, height: 24, borderBottom: `2px solid ${styles.accent}40`, borderRight: `2px solid ${styles.accent}40` }} />

      {/* Logo */}
      <img
        src="/brand/KOZBEYLI_BEYAZ_LOGO.png"
        alt="Logo"
        style={{ width: 60, height: 'auto', marginBottom: 16, filter: styles.bg === '#F3EEE4' ? 'invert(1)' : 'none' }}
        onError={(e) => { e.target.style.display = 'none'; }}
      />

      {/* Title */}
      <h2 style={{
        color: styles.accent,
        fontSize: 11,
        letterSpacing: '0.15em',
        textTransform: 'uppercase',
        fontWeight: 600,
        marginBottom: 8,
        fontFamily: "'Alifira', serif",
      }}>
        {post.title || 'Baslik'}
      </h2>

      {/* Content */}
      <p style={{
        color: styles.text,
        fontSize: 13,
        textAlign: 'center',
        lineHeight: 1.6,
        maxWidth: '85%',
        opacity: 0.9,
      }}>
        {post.content?.substring(0, 150) || 'Gonderi icerigi...'}
      </p>

      {/* Brand */}
      <div style={{
        position: 'absolute', bottom: 24,
        color: `${styles.text}60`,
        fontSize: 9,
        letterSpacing: '0.15em',
        textTransform: 'uppercase',
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
      }}
    >
      <div style={{ width: 16, height: 1.5, background: styles.accent, marginBottom: 3, borderRadius: 1 }} />
      <div style={{ width: 24, height: 1, background: `${styles.text}40`, marginBottom: 2, borderRadius: 1 }} />
      <div style={{ width: 20, height: 1, background: `${styles.text}20`, borderRadius: 1 }} />
    </div>
  );
}
