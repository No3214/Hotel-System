import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageCircle, Send, Bell, CheckCircle, Clock, 
  Users, Phone, Calendar, RefreshCw, Settings, 
  AlertTriangle, ExternalLink, Instagram, FileText,
  Zap, ChevronRight
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import api from '../api';

function PlatformBadge({ configured }) {
  return (
    <Badge className={configured ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}>
      {configured ? 'API Bagli' : 'Mock Mod'}
    </Badge>
  );
}

function StatCard({ icon: Icon, value, label, color }) {
  return (
    <div className="glass rounded-xl p-4" data-testid={`stat-${label}`}>
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <p className="text-2xl font-bold text-[#e5e5e8]">{value}</p>
          <p className="text-xs text-[#7e7e8a]">{label}</p>
        </div>
      </div>
    </div>
  );
}

export default function WhatsAppPage() {
  const [sessions, setSessions] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [config, setConfig] = useState({});
  const [webhookStatus, setWebhookStatus] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [igSessions, setIgSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('notifications');
  const [selectedSession, setSelectedSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sendForm, setSendForm] = useState({ to: '', message: '' });
  const [sending, setSending] = useState(false);

  const load = useCallback(async () => {
    try {
      const [sessionsRes, notificationsRes, configRes, statusRes, templatesRes, igRes] = await Promise.all([
        api.get('/whatsapp/sessions'),
        api.get('/whatsapp/notifications'),
        api.get('/whatsapp/config'),
        api.get('/webhooks/status').catch(() => ({ data: null })),
        api.get('/whatsapp/templates').catch(() => ({ data: { templates: [] } })),
        api.get('/webhooks/instagram/sessions').catch(() => ({ data: { sessions: [] } })),
      ]);
      setSessions(sessionsRes.data.sessions || []);
      setNotifications(notificationsRes.data.notifications || []);
      setConfig(configRes.data);
      setWebhookStatus(statusRes.data);
      setTemplates(templatesRes.data.templates || []);
      setIgSessions(igRes.data.sessions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const loadMessages = async (sessionId) => {
    setSelectedSession(sessionId);
    try {
      const isIg = sessionId.startsWith('ig_');
      const endpoint = isIg ? '/webhooks/instagram/messages' : '/whatsapp/messages';
      const res = await api.get(endpoint, { params: { session_id: sessionId } });
      setMessages(res.data.messages || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSend = async () => {
    if (!sendForm.to || !sendForm.message) return;
    setSending(true);
    try {
      await api.post('/whatsapp/send', sendForm);
      setSendForm({ to: '', message: '' });
      load();
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  const TABS = [
    { key: 'notifications', label: 'Bildirimler', icon: Bell },
    { key: 'sessions', label: 'WhatsApp', icon: MessageCircle },
    { key: 'instagram', label: 'Instagram', icon: Instagram },
    { key: 'templates', label: 'Sablonlar', icon: FileText },
    { key: 'send', label: 'Mesaj Gonder', icon: Send },
    { key: 'settings', label: 'Ayarlar', icon: Settings },
  ];

  const waMsgCount = webhookStatus?.whatsapp?.total_messages || 0;
  const igMsgCount = webhookStatus?.instagram?.total_messages || 0;

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1600px]" data-testid="whatsapp-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A] flex items-center gap-3">
            <Zap className="w-8 h-8" />
            Mesajlasma Merkezi
          </h1>
          <p className="text-[#7e7e8a] text-sm mt-1">WhatsApp & Instagram mesajlari, sablonlar ve bildirimler</p>
        </div>
        <div className="flex items-center gap-3">
          <PlatformBadge configured={config.configured} />
          <Button onClick={load} variant="outline" className="border-[#C4972A]/30 text-[#C4972A]" data-testid="refresh-btn">
            <RefreshCw className="w-4 h-4 mr-2" /> Yenile
          </Button>
        </div>
      </div>

      {/* Config Warning */}
      {!config.configured && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4" data-testid="mock-warning">
          <div className="flex items-center gap-2 text-yellow-400 mb-2">
            <AlertTriangle className="w-5 h-5" />
            <span className="font-semibold">WhatsApp API Yapilandirilmadi</span>
          </div>
          <p className="text-sm text-[#a9a9b2]">
            Sistem mock modda calisiyor. Mesajlar veritabaninda saklanir. Gercek gonderim icin Meta Business API ayarlarini yapin.
          </p>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {TABS.map(tab => (
          <button
            key={tab.key}
            onClick={() => { setActiveTab(tab.key); setSelectedSession(null); }}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-all ${
              activeTab === tab.key
                ? 'bg-[#C4972A] text-white'
                : 'bg-white/5 text-[#7e7e8a] hover:bg-white/10'
            }`}
            data-testid={`tab-${tab.key}`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Panel */}
        <div className="space-y-4">
          {activeTab === 'notifications' && (
            <>
              <h2 className="text-lg font-semibold text-[#e5e5e8] flex items-center gap-2">
                <Bell className="w-5 h-5 text-[#C4972A]" />
                Grup Bildirimleri ({notifications.length})
              </h2>
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                <AnimatePresence>
                  {notifications.map((notif, idx) => (
                    <motion.div
                      key={notif.id || idx}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="glass rounded-xl p-4"
                      data-testid={`notification-${idx}`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <Badge className="bg-green-500/20 text-green-400">
                          {notif.type === 'table_reservation' ? 'Masa Rez.' : notif.type === 'cleaning' ? 'Temizlik' : 'Bildirim'}
                        </Badge>
                        <Badge className={notif.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'}>
                          {notif.status === 'pending' ? 'Bekliyor' : 'Gonderildi'}
                        </Badge>
                      </div>
                      <pre className="text-sm text-[#a9a9b2] whitespace-pre-wrap font-sans">{notif.message}</pre>
                      <p className="text-xs text-[#7e7e8a] mt-2">{new Date(notif.created_at).toLocaleString('tr-TR')}</p>
                    </motion.div>
                  ))}
                </AnimatePresence>
                {notifications.length === 0 && (
                  <div className="text-center py-8 text-[#7e7e8a]">
                    <Bell className="w-12 h-12 mx-auto mb-2 opacity-30" />
                    <p>Henuz bildirim yok</p>
                  </div>
                )}
              </div>
            </>
          )}

          {activeTab === 'sessions' && (
            <>
              <h2 className="text-lg font-semibold text-[#e5e5e8] flex items-center gap-2">
                <MessageCircle className="w-5 h-5 text-green-400" />
                WhatsApp Konusmalari ({sessions.length})
              </h2>
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {sessions.map((session, idx) => (
                  <button
                    key={session._id || idx}
                    onClick={() => loadMessages(session._id)}
                    className={`w-full text-left p-4 rounded-xl transition-all ${
                      selectedSession === session._id ? 'bg-[#C4972A]/20 border border-[#C4972A]/50' : 'glass hover:bg-white/10'
                    }`}
                    data-testid={`wa-session-${idx}`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-[#e5e5e8]">{session.contact_name || session._id}</span>
                      <Badge className="bg-green-500/20 text-green-400">{session.message_count} mesaj</Badge>
                    </div>
                    <p className="text-sm text-[#7e7e8a] truncate">{session.last_message}</p>
                    <p className="text-xs text-[#7e7e8a] mt-1">{session.last_time && new Date(session.last_time).toLocaleString('tr-TR')}</p>
                  </button>
                ))}
                {sessions.length === 0 && (
                  <div className="text-center py-8 text-[#7e7e8a]">
                    <MessageCircle className="w-12 h-12 mx-auto mb-2 opacity-30" />
                    <p>Henuz WhatsApp konusmasi yok</p>
                  </div>
                )}
              </div>
            </>
          )}

          {activeTab === 'instagram' && (
            <>
              <h2 className="text-lg font-semibold text-[#e5e5e8] flex items-center gap-2">
                <Instagram className="w-5 h-5 text-pink-400" />
                Instagram DM ({igSessions.length})
              </h2>
              {webhookStatus?.instagram && !webhookStatus.instagram.configured && (
                <div className="bg-pink-500/10 border border-pink-500/30 rounded-lg p-3 text-sm text-pink-300">
                  Instagram API yapilandirilmadi. Mock modda calisiyor.
                </div>
              )}
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {igSessions.map((session, idx) => (
                  <button
                    key={session._id || idx}
                    onClick={() => loadMessages(session._id)}
                    className={`w-full text-left p-4 rounded-xl transition-all ${
                      selectedSession === session._id ? 'bg-pink-500/20 border border-pink-500/50' : 'glass hover:bg-white/10'
                    }`}
                    data-testid={`ig-session-${idx}`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-[#e5e5e8]">{session._id}</span>
                      <Badge className="bg-pink-500/20 text-pink-400">{session.message_count} mesaj</Badge>
                    </div>
                    <p className="text-sm text-[#7e7e8a] truncate">{session.last_message}</p>
                  </button>
                ))}
                {igSessions.length === 0 && (
                  <div className="text-center py-8 text-[#7e7e8a]">
                    <Instagram className="w-12 h-12 mx-auto mb-2 opacity-30" />
                    <p>Henuz Instagram DM yok</p>
                  </div>
                )}
              </div>
            </>
          )}

          {activeTab === 'templates' && (
            <>
              <h2 className="text-lg font-semibold text-[#e5e5e8] flex items-center gap-2">
                <FileText className="w-5 h-5 text-[#C4972A]" />
                Mesaj Sablonlari ({templates.length})
              </h2>
              <div className="space-y-3">
                {templates.map((tmpl, idx) => (
                  <div key={idx} className="glass rounded-xl p-4" data-testid={`template-${idx}`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-[#e5e5e8]">{tmpl.name}</span>
                      <ChevronRight className="w-4 h-4 text-[#7e7e8a]" />
                    </div>
                    <p className="text-sm text-[#a9a9b2]">{tmpl.description}</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {tmpl.params?.map((p, pi) => (
                        <Badge key={pi} className="bg-blue-500/10 text-blue-400 text-xs">{p}</Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {activeTab === 'send' && (
            <div className="glass rounded-xl p-6 space-y-4">
              <h2 className="text-lg font-semibold text-[#e5e5e8] flex items-center gap-2">
                <Send className="w-5 h-5 text-[#C4972A]" />
                Manuel Mesaj Gonder
              </h2>
              <div className="space-y-3">
                <div>
                  <label className="text-sm text-[#7e7e8a] mb-1 block">Telefon Numarasi</label>
                  <Input
                    value={sendForm.to}
                    onChange={e => setSendForm(p => ({ ...p, to: e.target.value }))}
                    placeholder="0532 234 26 86"
                    className="bg-white/5 border-white/10"
                    data-testid="send-phone-input"
                  />
                </div>
                <div>
                  <label className="text-sm text-[#7e7e8a] mb-1 block">Mesaj</label>
                  <textarea
                    value={sendForm.message}
                    onChange={e => setSendForm(p => ({ ...p, message: e.target.value }))}
                    placeholder="Mesajinizi yazin..."
                    rows={4}
                    className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-sm text-[#e5e5e8] resize-none"
                    data-testid="send-message-input"
                  />
                </div>
                <Button
                  onClick={handleSend}
                  disabled={sending || !sendForm.to || !sendForm.message}
                  className="w-full bg-[#C4972A] hover:bg-[#d4a73a] text-white"
                  data-testid="send-btn"
                >
                  <Send className="w-4 h-4 mr-2" />
                  {sending ? 'Gonderiliyor...' : 'Gonder'}
                </Button>
                {!config.configured && (
                  <p className="text-xs text-yellow-400">Mock modda: Mesaj veritabanina kaydedilecek, gercek gonderim yapilmayacak.</p>
                )}
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="glass rounded-xl p-6 space-y-4">
              <h2 className="text-lg font-semibold text-[#e5e5e8] flex items-center gap-2">
                <Settings className="w-5 h-5 text-[#C4972A]" />
                Platform Ayarlari
              </h2>
              
              {/* WhatsApp Config */}
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-green-400 flex items-center gap-2">
                  <MessageCircle className="w-4 h-4" /> WhatsApp Business API
                </h3>
                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <span className="text-[#a9a9b2]">Access Token</span>
                  <Badge className={config.has_token ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}>
                    {config.has_token ? 'Ayarli' : 'Eksik'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <span className="text-[#a9a9b2]">Phone Number ID</span>
                  <Badge className={config.has_phone_id ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}>
                    {config.has_phone_id ? 'Ayarli' : 'Eksik'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <span className="text-[#a9a9b2]">Verify Token</span>
                  <code className="text-xs text-[#C4972A] bg-[#C4972A]/10 px-2 py-1 rounded">{config.verify_token}</code>
                </div>
              </div>

              {/* Instagram Config */}
              <div className="space-y-3 mt-4">
                <h3 className="text-sm font-medium text-pink-400 flex items-center gap-2">
                  <Instagram className="w-4 h-4" /> Instagram Messaging API
                </h3>
                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <span className="text-[#a9a9b2]">Durum</span>
                  <PlatformBadge configured={webhookStatus?.instagram?.configured} />
                </div>
              </div>

              {/* Webhook URLs */}
              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 mt-4 space-y-2">
                <h3 className="text-blue-400 font-medium mb-2">Webhook URL'leri</h3>
                <div>
                  <p className="text-xs text-[#7e7e8a]">WhatsApp:</p>
                  <code className="text-xs text-[#a9a9b2] break-all" data-testid="wa-webhook-url">
                    {window.location.origin.replace(/:\d+$/, '')}/api/webhooks/whatsapp
                  </code>
                </div>
                <div>
                  <p className="text-xs text-[#7e7e8a]">Instagram:</p>
                  <code className="text-xs text-[#a9a9b2] break-all" data-testid="ig-webhook-url">
                    {window.location.origin.replace(/:\d+$/, '')}/api/webhooks/instagram
                  </code>
                </div>
              </div>

              <a href="https://developers.facebook.com/apps/" target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-2 text-[#C4972A] hover:underline text-sm">
                <ExternalLink className="w-4 h-4" /> Meta Business Developer Portal
              </a>
            </div>
          )}
        </div>

        {/* Right Panel - Messages */}
        <div className="glass rounded-xl p-4 min-h-[500px]">
          {selectedSession ? (
            <>
              <div className="flex items-center justify-between mb-4 pb-4 border-b border-white/10">
                <h3 className="font-semibold text-[#e5e5e8] flex items-center gap-2">
                  {selectedSession.startsWith('ig_') ? (
                    <Instagram className="w-4 h-4 text-pink-400" />
                  ) : (
                    <MessageCircle className="w-4 h-4 text-green-400" />
                  )}
                  {selectedSession}
                </h3>
                <Button variant="ghost" size="sm" onClick={() => setSelectedSession(null)} className="text-[#7e7e8a]">
                  Kapat
                </Button>
              </div>
              <div className="space-y-3 max-h-[500px] overflow-y-auto">
                {messages.map((msg, idx) => (
                  <div
                    key={msg.id || idx}
                    className={`p-3 rounded-lg max-w-[85%] ${
                      msg.direction === 'incoming' ? 'bg-white/5 mr-auto' : 'bg-[#C4972A]/20 ml-auto'
                    }`}
                  >
                    <p className="text-sm text-[#e5e5e8] whitespace-pre-wrap">{msg.text}</p>
                    <p className="text-xs text-[#7e7e8a] mt-1">{new Date(msg.created_at).toLocaleTimeString('tr-TR')}</p>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-[#7e7e8a]">
              <MessageCircle className="w-16 h-16 mb-4 opacity-30" />
              <p>Konusma secin</p>
            </div>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={MessageCircle} value={waMsgCount} label="WhatsApp Mesaj" color="bg-green-500/20 text-green-400" />
        <StatCard icon={Instagram} value={igMsgCount} label="Instagram Mesaj" color="bg-pink-500/20 text-pink-400" />
        <StatCard icon={Users} value={sessions.length + igSessions.length} label="Toplam Konusma" color="bg-blue-500/20 text-blue-400" />
        <StatCard icon={Bell} value={notifications.length} label="Bildirim" color="bg-yellow-500/20 text-yellow-400" />
      </div>
    </div>
  );
}
