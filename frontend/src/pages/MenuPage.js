import React, { useState, useEffect } from 'react';
import { getMenuItems, createMenuItem, updateMenuItem, deleteMenuItem, getMenuCategories, createMenuCategory, updateMenuCategory, deleteMenuCategory, getMenuTheme, updateMenuTheme, getAIMenuEngineering } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Plus, Trash2, Edit2, Save, X, ExternalLink, Palette, UtensilsCrossed, ChevronDown, ChevronUp, Eye, Sparkles, Loader2, TrendingUp, AlertTriangle } from 'lucide-react';

const TABS = [
  { id: 'items', label: 'Menu Ogeleri', icon: UtensilsCrossed },
  { id: 'theme', label: 'Tema Ayarlari', icon: Palette },
];

export default function MenuPage() {
  const [tab, setTab] = useState('items');
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [activeCat, setActiveCat] = useState(null);
  const [theme, setTheme] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editingItem, setEditingItem] = useState(null);
  const [newItem, setNewItem] = useState(null);
  const [newCategory, setNewCategory] = useState(null);
  const [editingCat, setEditingCat] = useState(null);

  // AI Menu Engineering State
  const [aiReport, setAiReport] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [showAiPanel, setShowAiPanel] = useState(false);

  const loadData = async () => {
    try {
      const [itemsRes, catsRes, themeRes] = await Promise.all([
        getMenuItems(), getMenuCategories(), getMenuTheme()
      ]);
      setItems(itemsRes.data.items || []);
      setCategories(catsRes.data.categories || []);
      setTheme(themeRes.data);
      if (!activeCat && catsRes.data.categories?.length) {
        setActiveCat(catsRes.data.categories[0].key);
      }
    } catch (err) {
      console.error('Menu data load error:', err);
    }
    setLoading(false);
  };

  useEffect(() => { loadData(); }, []);

  const filteredItems = items.filter(i => i.category === activeCat);

  // Item CRUD
  const handleSaveItem = async (item) => {
    try {
      if (item.id) {
        await updateMenuItem(item.id, { name: item.name, desc: item.desc, price_try: parseFloat(item.price_try), is_available: item.is_available, sort_order: item.sort_order });
      } else {
        await createMenuItem({ ...item, price_try: parseFloat(item.price_try), category: activeCat });
      }
      setEditingItem(null);
      setNewItem(null);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteItem = async (id) => {
    if (!window.confirm('Bu ogeyi silmek istediginize emin misiniz?')) return;
    await deleteMenuItem(id);
    loadData();
  };

  // Category CRUD
  const handleSaveCategory = async (cat) => {
    try {
      if (cat.id) {
        await updateMenuCategory(cat.id, { name_tr: cat.name_tr, name_en: cat.name_en, icon: cat.icon, sort_order: cat.sort_order, is_active: cat.is_active });
      } else {
        await createMenuCategory(cat);
      }
      setNewCategory(null);
      setEditingCat(null);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteCategory = async (id) => {
    if (!window.confirm('Bu kategoriyi ve tum ogelerini silmek istediginize emin misiniz?')) return;
    await deleteMenuCategory(id);
    setActiveCat(null);
    loadData();
  };

  // Theme save
  const handleSaveTheme = async () => {
    try {
      await updateMenuTheme(theme);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const publicUrl = `${window.location.origin}/menu`;

  const handleRunAIAnalytics = async () => {
    setAiLoading(true);
    setShowAiPanel(true);
    try {
       const res = await getAIMenuEngineering();
       if (res.data?.success) setAiReport(res.data.report);
    } catch(e) { console.error("AI Engineering load error", e); }
    setAiLoading(false);
  };

  if (loading) return <div className="p-8"><div className="h-8 w-48 bg-white/5 rounded animate-pulse" /></div>;

  return (
    <div className="p-6 lg:p-8 max-w-[1400px]" data-testid="menu-admin-page">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#C4972A]">QR Menu Yonetimi</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">Menu ogeleri, kategoriler ve tema ayarlari</p>
        </div>
        <a
          href="/menu"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#8FAA86]/20 text-[#8FAA86] hover:bg-[#8FAA86]/30 transition-colors text-sm"
          data-testid="preview-menu-btn"
        >
          <Eye className="w-4 h-4" />
          Public Menu Onizleme
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>

      {/* Public URL & AI Actions */}
      <div className="flex gap-4 mb-6">
        <div className="glass rounded-xl p-4 flex items-center gap-3 flex-1 flex-wrap">
          <span className="text-xs text-[#7e7e8a]">QR Menu URL:</span>
          <code className="text-sm text-[#C4972A] bg-[#C4972A]/10 px-3 py-1 rounded-lg truncate" data-testid="public-url">{publicUrl}</code>
        </div>
        <div className="glass rounded-xl p-4 border border-[#C4972A]/20 bg-[#C4972A]/5 flex items-center">
          <Button 
            onClick={handleRunAIAnalytics} 
            disabled={aiLoading}
            className="bg-[#C4972A] hover:bg-[#a87a1f] text-white whitespace-nowrap"
          >
            {aiLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
            AI Menü Optimizasyonu
          </Button>
        </div>
      </div>

      {/* AI Menu Engineering Panel */}
      {showAiPanel && (
        <div className="glass rounded-xl p-6 border border-[#C4972A]/30 mb-8 relative overflow-hidden animate-fade-in-up">
           <div className="absolute top-0 right-0 w-64 h-64 bg-[#C4972A]/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
           <div className="relative z-10 flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-[#C4972A] flex items-center gap-2">
                 <Sparkles className="w-5 h-5" /> AI Executive Chef (Menu Engineering Matrix)
              </h3>
              <button onClick={() => setShowAiPanel(false)} className="text-[#7e7e8a] hover:text-white"><X className="w-4 h-4" /></button>
           </div>
           
           {aiLoading ? (
             <div className="flex items-center gap-3 text-[#7e7e8a] py-6 justify-center">
                <Loader2 className="w-5 h-5 animate-spin text-[#C4972A]" /> 
                <span>AI siparişleri, karlılık oranlarını ve anlık hava durumunu sentezliyor...</span>
             </div>
           ) : aiReport ? (
             <div className="space-y-4 relative z-10">
                <div className="bg-[#1a1a22]/80 border border-white/5 rounded-lg p-3 text-sm text-[#e5e5e8]">
                   <p className="text-[#C4972A] mb-1 font-medium text-xs">Durum Tespiti & Şefin Yorumu</p>
                   {aiReport.weather_context}
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                   <MatrixCard title="Yıldızlar (Stars)" icon={Sparkles} color="text-yellow-400" bg="bg-yellow-500/10" items={aiReport.stars} />
                   <MatrixCard title="Bulmacalar (Puzzles)" icon={TrendingUp} color="text-blue-400" bg="bg-blue-500/10" items={aiReport.puzzles} />
                   <MatrixCard title="Çiftçi Atları (Plowhorses)" icon={TrendingUp} color="text-emerald-400" bg="bg-emerald-500/10" items={aiReport.plowhorses} />
                   <MatrixCard title="Köpekler (Dogs)" icon={AlertTriangle} color="text-red-400" bg="bg-red-500/10" items={aiReport.dogs} />
                </div>
                
                <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-4 mt-2">
                   <h4 className="text-emerald-400 text-sm font-bold mb-2">Aksiyon Planı</h4>
                   <p className="text-sm text-[#e5e5e8] whitespace-pre-wrap">{aiReport.action_plan}</p>
                </div>
             </div>
           ) : (
              <div className="text-[#7e7e8a] text-sm text-center py-4">Rapor oluşturulamadı. Lütfen tekrar deneyin.</div>
           )}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all ${tab === t.id ? 'bg-[#C4972A]/15 text-[#C4972A]' : 'text-[#7e7e8a] hover:bg-white/5'}`}
            data-testid={`tab-${t.id}`}
          >
            <t.icon className="w-4 h-4" />
            {t.label}
          </button>
        ))}
      </div>

      {/* Items Tab */}
      {tab === 'items' && (
        <div className="grid grid-cols-12 gap-6">
          {/* Categories sidebar */}
          <div className="col-span-3 space-y-2">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-[#e5e5e8]">Kategoriler</h3>
              <button
                onClick={() => setNewCategory({ key: '', name_tr: '', name_en: '', icon: 'utensils', sort_order: categories.length, is_active: true })}
                className="text-[#C4972A] hover:text-[#a87a1f]"
                data-testid="add-category-btn"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>

            {/* New category form */}
            {newCategory && (
              <div className="glass rounded-lg p-3 space-y-2 mb-2">
                <Input placeholder="Anahtar (orn: tatli)" value={newCategory.key} onChange={e => setNewCategory({ ...newCategory, key: e.target.value })} className="h-8 text-xs bg-white/5 border-white/10 text-white" data-testid="new-cat-key" />
                <Input placeholder="Turkce ad" value={newCategory.name_tr} onChange={e => setNewCategory({ ...newCategory, name_tr: e.target.value })} className="h-8 text-xs bg-white/5 border-white/10 text-white" data-testid="new-cat-name" />
                <div className="flex gap-1">
                  <Button size="sm" onClick={() => handleSaveCategory(newCategory)} className="flex-1 h-7 text-xs bg-[#C4972A]" data-testid="save-new-cat">Kaydet</Button>
                  <Button size="sm" variant="ghost" onClick={() => setNewCategory(null)} className="h-7 text-xs text-[#7e7e8a]"><X className="w-3 h-3" /></Button>
                </div>
              </div>
            )}

            {categories.map(cat => (
              <div key={cat.id}>
                {editingCat?.id === cat.id ? (
                  <div className="glass rounded-lg p-3 space-y-2">
                    <Input value={editingCat.name_tr} onChange={e => setEditingCat({ ...editingCat, name_tr: e.target.value })} className="h-7 text-xs bg-white/5 border-white/10 text-white" />
                    <div className="flex gap-1">
                      <Button size="sm" onClick={() => handleSaveCategory(editingCat)} className="flex-1 h-6 text-xs bg-[#C4972A]">Kaydet</Button>
                      <Button size="sm" variant="ghost" onClick={() => setEditingCat(null)} className="h-6 text-xs"><X className="w-3 h-3" /></Button>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => setActiveCat(cat.key)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-all group ${activeCat === cat.key ? 'bg-[#C4972A]/15 text-[#C4972A]' : 'text-[#a9a9b2] hover:bg-white/5'}`}
                    data-testid={`cat-btn-${cat.key}`}
                  >
                    <span className="truncate">{cat.name_tr}</span>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Edit2 className="w-3 h-3" onClick={(e) => { e.stopPropagation(); setEditingCat({ ...cat }); }} />
                      <Trash2 className="w-3 h-3 text-red-400" onClick={(e) => { e.stopPropagation(); handleDeleteCategory(cat.id); }} />
                    </div>
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* Items list */}
          <div className="col-span-9">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-[#e5e5e8]">
                {categories.find(c => c.key === activeCat)?.name_tr || 'Kategori Sec'}
              </h3>
              {activeCat && (
                <Button size="sm" onClick={() => setNewItem({ name: '', desc: '', price_try: '', is_available: true, sort_order: filteredItems.length })} className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-item-btn">
                  <Plus className="w-4 h-4 mr-1" /> Yeni Oge
                </Button>
              )}
            </div>

            {/* New item form */}
            {newItem && (
              <div className="glass rounded-xl p-4 mb-4 space-y-3">
                <div className="grid grid-cols-3 gap-3">
                  <Input placeholder="Urun adi" value={newItem.name} onChange={e => setNewItem({ ...newItem, name: e.target.value })} className="bg-white/5 border-white/10 text-white" data-testid="new-item-name" />
                  <Input placeholder="Fiyat (TL)" type="number" value={newItem.price_try} onChange={e => setNewItem({ ...newItem, price_try: e.target.value })} className="bg-white/5 border-white/10 text-white" data-testid="new-item-price" />
                  <Input placeholder="Aciklama" value={newItem.desc} onChange={e => setNewItem({ ...newItem, desc: e.target.value })} className="bg-white/5 border-white/10 text-white" data-testid="new-item-desc" />
                </div>
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => handleSaveItem(newItem)} className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="save-new-item">
                    <Save className="w-4 h-4 mr-1" /> Kaydet
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setNewItem(null)} className="text-[#7e7e8a]">Iptal</Button>
                </div>
              </div>
            )}

            {/* Items table */}
            <div className="space-y-2">
              {filteredItems.length === 0 && !newItem && (
                <div className="glass rounded-xl p-8 text-center text-[#7e7e8a]">
                  {activeCat ? 'Bu kategoride oge yok. Yeni oge ekleyin.' : 'Soldan bir kategori secin.'}
                </div>
              )}

              {filteredItems.map((item, i) => (
                <div key={item.id} className="glass rounded-xl p-4 flex items-center gap-4 group" data-testid={`admin-item-${i}`}>
                  {editingItem?.id === item.id ? (
                    <>
                      <div className="flex-1 grid grid-cols-3 gap-3">
                        <Input value={editingItem.name} onChange={e => setEditingItem({ ...editingItem, name: e.target.value })} className="bg-white/5 border-white/10 text-white h-8 text-sm" />
                        <Input type="number" value={editingItem.price_try} onChange={e => setEditingItem({ ...editingItem, price_try: e.target.value })} className="bg-white/5 border-white/10 text-white h-8 text-sm" />
                        <Input value={editingItem.desc} onChange={e => setEditingItem({ ...editingItem, desc: e.target.value })} className="bg-white/5 border-white/10 text-white h-8 text-sm" />
                      </div>
                      <div className="flex gap-1">
                        <Button size="sm" onClick={() => handleSaveItem(editingItem)} className="h-8 bg-[#C4972A]"><Save className="w-3 h-3" /></Button>
                        <Button size="sm" variant="ghost" onClick={() => setEditingItem(null)} className="h-8"><X className="w-3 h-3" /></Button>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-medium text-[#e5e5e8]">{item.name}</h4>
                          {!item.is_available && <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-400/10 text-red-400">Pasif</span>}
                        </div>
                        {item.desc && <p className="text-xs text-[#7e7e8a] mt-0.5">{item.desc}</p>}
                      </div>
                      <span className="text-base font-bold text-[#C4972A]">{item.price_try} <span className="text-xs text-[#7e7e8a] font-normal">TL</span></span>
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => setEditingItem({ ...item })} className="p-1.5 rounded-lg hover:bg-white/5 text-[#7e7e8a]" data-testid={`edit-item-${i}`}><Edit2 className="w-3.5 h-3.5" /></button>
                        <button onClick={() => handleDeleteItem(item.id)} className="p-1.5 rounded-lg hover:bg-red-400/10 text-red-400" data-testid={`delete-item-${i}`}><Trash2 className="w-3.5 h-3.5" /></button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Theme Tab */}
      {tab === 'theme' && theme && (
        <div className="space-y-6 max-w-3xl">
          {/* Brand */}
          <Section title="Marka">
            <div className="grid grid-cols-2 gap-4">
              <Field label="Marka Adi" value={theme.brand_name} onChange={v => setTheme({ ...theme, brand_name: v })} testId="theme-brand" />
              <Field label="Slogan" value={theme.tagline} onChange={v => setTheme({ ...theme, tagline: v })} testId="theme-tagline" />
            </div>
          </Section>

          {/* Colors */}
          <Section title="Renkler">
            <div className="grid grid-cols-3 gap-4">
              {theme.colors && Object.entries(theme.colors).map(([key, val]) => (
                <ColorField key={key} label={key} value={val} onChange={v => setTheme({ ...theme, colors: { ...theme.colors, [key]: v } })} />
              ))}
            </div>
          </Section>

          {/* Background */}
          <Section title="Arka Plan">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-[#7e7e8a] mb-1 block">Mod</label>
                <select
                  value={theme.background?.mode || 'gradient'}
                  onChange={e => setTheme({ ...theme, background: { ...theme.background, mode: e.target.value } })}
                  className="w-full h-9 rounded-lg bg-white/5 border border-white/10 text-white text-sm px-3"
                  data-testid="theme-bg-mode"
                >
                  <option value="gradient">Gradient</option>
                  <option value="solid">Duz Renk</option>
                </select>
              </div>
              <Field label="Deger" value={theme.background?.value || ''} onChange={v => setTheme({ ...theme, background: { ...theme.background, value: v } })} testId="theme-bg-value" />
            </div>
          </Section>

          {/* Components */}
          <Section title="Bilesenler">
            <div className="grid grid-cols-3 gap-4">
              <Field label="Border Radius" value={theme.components?.radius} onChange={v => setTheme({ ...theme, components: { ...theme.components, radius: parseInt(v) || 0 } })} testId="theme-radius" type="number" />
              <Field label="Heading Tracking" value={theme.components?.headingTracking} onChange={v => setTheme({ ...theme, components: { ...theme.components, headingTracking: parseFloat(v) || 0 } })} testId="theme-tracking" type="number" />
              <div className="flex items-center gap-2 mt-6">
                <input
                  type="checkbox"
                  checked={theme.components?.headingUppercase || false}
                  onChange={e => setTheme({ ...theme, components: { ...theme.components, headingUppercase: e.target.checked } })}
                  className="rounded"
                  data-testid="theme-uppercase"
                />
                <label className="text-xs text-[#e5e5e8]">Basliklar Buyuk Harf</label>
              </div>
            </div>
          </Section>

          {/* Save */}
          <Button onClick={handleSaveTheme} className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="save-theme-btn">
            <Save className="w-4 h-4 mr-2" /> Temayi Kaydet
          </Button>
        </div>
      )}
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="glass rounded-xl p-5">
      <h3 className="text-sm font-medium text-[#C4972A] mb-4">{title}</h3>
      {children}
    </div>
  );
}

function Field({ label, value, onChange, testId, type = 'text' }) {
  return (
    <div>
      <label className="text-xs text-[#7e7e8a] mb-1 block">{label}</label>
      <Input
        type={type}
        value={value || ''}
        onChange={e => onChange(e.target.value)}
        className="bg-white/5 border-white/10 text-white text-sm h-9"
        data-testid={testId}
      />
    </div>
  );
}

function ColorField({ label, value, onChange }) {
  return (
    <div className="flex items-center gap-2">
      <input
        type="color"
        value={value || '#000000'}
        onChange={e => onChange(e.target.value)}
        className="w-8 h-8 rounded-lg border-0 cursor-pointer"
        data-testid={`color-${label}`}
      />
      <div className="flex-1">
        <label className="text-xs text-[#7e7e8a] block">{label}</label>
        <Input
          value={value || ''}
          onChange={e => onChange(e.target.value)}
          className="bg-white/5 border-white/10 text-white text-xs h-7 mt-0.5"
        />
      </div>
    </div>
  );
}

function MatrixCard({ title, icon: Icon, color, bg, items }) {
  return (
    <div className={`glass rounded-xl p-4 hover:border-white/10 transition-colors ${bg}`}>
      <h4 className={`text-sm font-bold flex items-center gap-2 mb-3 ${color}`}>
        <Icon className="w-4 h-4" /> {title}
      </h4>
      <ul className="space-y-2 text-xs text-[#a9a9b2]">
        {items && items.length > 0 ? items.map((item, i) => (
          <li key={i} className="flex gap-2.5 items-start">
             <span className="mt-1 w-1 h-1 rounded-full bg-white/30 shrink-0" />
             <span className="leading-relaxed">{item}</span>
          </li>
        )) : <li>Listelenecek ürün yok.</li>}
      </ul>
    </div>
  );
}
