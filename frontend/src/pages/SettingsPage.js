import React, { useState, useEffect } from 'react';
import { getSettings, updateSettings } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Settings, Save, Bell, Globe, Shield, Sparkles } from 'lucide-react';

export default function SettingsPage() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    getSettings().then(r => setSettings(r.data)).catch(console.error).finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    await updateSettings(settings);
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const toggle = (key) => setSettings(prev => ({ ...prev, [key]: !prev[key] }));

  if (loading || !settings) return <div className="p-8"><div className="h-8 w-48 bg-white/5 rounded animate-pulse" /></div>;

  return (
    <div className="p-6 lg:p-8 space-y-8 max-w-[900px]" data-testid="settings-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Ayarlar</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">Sistem yapilandirmasi</p>
        </div>
        <Button onClick={handleSave} disabled={saving} className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="save-settings-btn">
          {saved ? <span className="text-green-300">Kaydedildi!</span> : <><Save className="w-4 h-4 mr-2" /> Kaydet</>}
        </Button>
      </div>

      {/* General */}
      <section className="glass rounded-xl p-5 space-y-4">
        <h3 className="text-base font-semibold text-[#C4972A] flex items-center gap-2"><Settings className="w-4 h-4" /> Genel Ayarlar</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-[#7e7e8a] mb-1 block">Otel Adi</label>
            <Input value={settings.hotel_name || ''} onChange={e => setSettings({ ...settings, hotel_name: e.target.value })} className="bg-white/5 border-white/10" />
          </div>
          <div>
            <label className="text-xs text-[#7e7e8a] mb-1 block">Telefon</label>
            <Input value={settings.phone || ''} onChange={e => setSettings({ ...settings, phone: e.target.value })} className="bg-white/5 border-white/10" />
          </div>
          <div>
            <label className="text-xs text-[#7e7e8a] mb-1 block">E-posta</label>
            <Input value={settings.email || ''} onChange={e => setSettings({ ...settings, email: e.target.value })} className="bg-white/5 border-white/10" />
          </div>
          <div>
            <label className="text-xs text-[#7e7e8a] mb-1 block">Zaman Dilimi</label>
            <Input value={settings.timezone || ''} onChange={e => setSettings({ ...settings, timezone: e.target.value })} className="bg-white/5 border-white/10" />
          </div>
        </div>
      </section>

      {/* Integrations */}
      <section className="glass rounded-xl p-5 space-y-4">
        <h3 className="text-base font-semibold text-[#C4972A] flex items-center gap-2"><Bell className="w-4 h-4" /> Entegrasyonlar</h3>
        <div className="space-y-3">
          {[
            { key: 'whatsapp_enabled', label: 'WhatsApp Entegrasyonu', desc: 'WhatsApp uzerinden mesaj alimi ve otomatik yanit' },
            { key: 'instagram_enabled', label: 'Instagram Entegrasyonu', desc: 'Instagram DM ve yorum otomasyonu' },
            { key: 'auto_reply_enabled', label: 'Otomatik Yanit', desc: 'AI destekli otomatik mesaj yanitlama' },
            { key: 'auto_housekeeping', label: 'Otomatik Kat Hizmetleri', desc: 'Check-out sonrasi otomatik temizlik gorevi olusturma' },
          ].map(item => (
            <div key={item.key} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
              <div>
                <p className="text-sm font-medium">{item.label}</p>
                <p className="text-xs text-[#7e7e8a]">{item.desc}</p>
              </div>
              <button
                onClick={() => toggle(item.key)}
                className={`w-12 h-6 rounded-full transition-all relative ${settings[item.key] ? 'bg-[#C4972A]' : 'bg-white/10'}`}
                data-testid={`toggle-${item.key}`}
              >
                <span className={`w-5 h-5 rounded-full bg-white absolute top-0.5 transition-all ${settings[item.key] ? 'left-6' : 'left-0.5'}`} />
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* AI */}
      <section className="glass rounded-xl p-5 space-y-4">
        <h3 className="text-base font-semibold text-[#C4972A] flex items-center gap-2"><Sparkles className="w-4 h-4" /> AI Yapilandirmasi</h3>
        <div className="p-3 bg-white/5 rounded-lg">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400" />
            <p className="text-sm">Google Gemini AI - Aktif</p>
          </div>
          <p className="text-xs text-[#7e7e8a] mt-1">Model: gemini-2.5-flash | Kozbeyli Konagi ozel prompt ile yapilandirilmis</p>
        </div>
        <div className="p-3 bg-white/5 rounded-lg">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-yellow-400" />
            <p className="text-sm">Yedek LLM'ler - Hazir</p>
          </div>
          <p className="text-xs text-[#7e7e8a] mt-1">Groq, DeepSeek, OpenRouter anahtarlari yapilandirilmis (yedek olarak)</p>
        </div>
      </section>

      {/* Security */}
      <section className="glass rounded-xl p-5 space-y-4">
        <h3 className="text-base font-semibold text-[#C4972A] flex items-center gap-2"><Shield className="w-4 h-4" /> Guvenlik & KVKK</h3>
        <div className="p-3 bg-white/5 rounded-lg">
          <p className="text-sm">KVKK Uyumu - Aktif</p>
          <p className="text-xs text-[#7e7e8a] mt-1">Kisisel veri koruma politikasi yapilandirilmis. Veri saklama suresi: 10 yil.</p>
        </div>
        <div className="p-3 bg-white/5 rounded-lg">
          <p className="text-sm">Lisans: T.C. Kultur ve Turizm Bakanligi Tesis Izin Belgesi No: 2025-35-1824</p>
        </div>
      </section>
    </div>
  );
}
