import React, { useState, useEffect } from 'react';
import { getLifecycleTemplates, previewLifecycleMessage, sendLifecycleMessage, getLifecycleHistory, getReservations } from '../api';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { MessageSquare, Send, Eye, Clock, Check, History } from 'lucide-react';

export default function LifecyclePage() {
  const [templates, setTemplates] = useState([]);
  const [reservations, setReservations] = useState([]);
  const [history, setHistory] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [selectedReservation, setSelectedReservation] = useState('');
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [tab, setTab] = useState('send');

  useEffect(() => {
    Promise.all([
      getLifecycleTemplates().then(r => setTemplates(r.data.templates)).catch(() => {}),
      getReservations({ limit: 100 }).then(r => setReservations(r.data.reservations)).catch(() => {}),
      getLifecycleHistory().then(r => setHistory(r.data.messages)).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  const handlePreview = async () => {
    if (!selectedTemplate) return;
    const r = await previewLifecycleMessage(selectedTemplate, selectedReservation || undefined);
    setPreview(r.data);
  };

  const handleSend = async (channel = 'whatsapp') => {
    if (!selectedTemplate || !selectedReservation) return;
    setSending(true);
    await sendLifecycleMessage(selectedTemplate, selectedReservation, channel);
    setHistory(prev => [{ template_key: selectedTemplate, channel, status: 'sent', created_at: new Date().toISOString(), guest_name: '...' }, ...prev]);
    setSending(false);
  };

  const TEMPLATE_ICONS = {
    booking_confirmation: '📋',
    pre_arrival: '🚗',
    welcome_checkin: '🏠',
    during_stay_day2: '☀️',
    checkout_thankyou: '🙏',
    post_stay_followup: '💌',
  };

  if (loading) return <div className="p-8"><div className="h-8 w-64 bg-white/5 rounded animate-pulse" /></div>;

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="lifecycle-page">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]" data-testid="lifecycle-title">Misafir Yasam Dongusu</h1>
        <p className="text-[#7e7e8a] text-sm mt-1">Otomatik mesaj sablonlari ve misafir iletisimi</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[['send', 'Mesaj Gonder', Send], ['history', 'Gecmis', History]].map(([id, label, Icon]) => (
          <button key={id} onClick={() => setTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all ${tab === id ? 'bg-[#C4972A]/20 text-[#C4972A]' : 'bg-white/5 text-[#7e7e8a] hover:bg-white/10'}`}>
            <Icon className="w-4 h-4" /> {label}
          </button>
        ))}
      </div>

      {tab === 'send' && (
        <>
          {/* Template Selection */}
          <div className="glass rounded-xl p-5 space-y-4">
            <h3 className="text-sm font-semibold text-[#C4972A]">Sablon ve Rezervasyon Sec</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Select value={selectedTemplate} onValueChange={v => { setSelectedTemplate(v); setPreview(null); }}>
                <SelectTrigger className="bg-white/5 border-white/10"><SelectValue placeholder="Mesaj sablonu secin" /></SelectTrigger>
                <SelectContent className="bg-[#1a1a22] border-[#C4972A]/20">
                  {templates.map(t => <SelectItem key={t.key} value={t.key}>{t.name}</SelectItem>)}
                </SelectContent>
              </Select>
              <Select value={selectedReservation} onValueChange={v => { setSelectedReservation(v); setPreview(null); }}>
                <SelectTrigger className="bg-white/5 border-white/10"><SelectValue placeholder="Rezervasyon secin (opsiyonel)" /></SelectTrigger>
                <SelectContent className="bg-[#1a1a22] border-[#C4972A]/20 max-h-48">
                  {reservations.map(r => <SelectItem key={r.id} value={r.id}>{r.guest_id} - {r.check_in} ({r.status})</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={handlePreview} className="border-[#C4972A]/30 text-[#C4972A]" data-testid="preview-btn">
                <Eye className="w-4 h-4 mr-2" /> Onizle
              </Button>
              <Button onClick={() => handleSend('whatsapp')} disabled={!selectedTemplate || !selectedReservation || sending}
                className="bg-green-600 hover:bg-green-700 text-white" data-testid="send-wa-btn">
                <Send className="w-4 h-4 mr-2" /> {sending ? 'Gonderiliyor...' : 'WhatsApp'}
              </Button>
              <Button onClick={() => handleSend('sms')} disabled={!selectedTemplate || !selectedReservation || sending}
                className="bg-blue-600 hover:bg-blue-700 text-white" data-testid="send-sms-btn">
                <Send className="w-4 h-4 mr-2" /> SMS
              </Button>
            </div>
          </div>

          {/* Preview */}
          {preview && (
            <div className="glass rounded-xl p-5" data-testid="message-preview">
              <h3 className="text-sm font-semibold text-[#C4972A] mb-3">Mesaj Onizleme</h3>
              <div className="bg-[#0a0a0f] rounded-lg p-4 border border-white/5">
                <pre className="text-sm text-[#e5e5e8] whitespace-pre-wrap font-sans">{preview.message}</pre>
              </div>
            </div>
          )}

          {/* Templates Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map(t => (
              <div key={t.key} className={`glass rounded-xl p-4 cursor-pointer transition-all hover:gold-glow ${selectedTemplate === t.key ? 'border border-[#C4972A]/40' : ''}`}
                onClick={() => { setSelectedTemplate(t.key); setPreview(null); }} data-testid={`template-${t.key}`}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg">{TEMPLATE_ICONS[t.key] || '📧'}</span>
                  <h4 className="text-sm font-medium text-white">{t.name}</h4>
                </div>
                <p className="text-xs text-[#7e7e8a] line-clamp-3">{t.content.substring(0, 120)}...</p>
                <div className="flex gap-1 mt-2 flex-wrap">
                  {t.variables?.slice(0, 4).map(v => (
                    <Badge key={v} className="bg-white/5 text-[#7e7e8a] text-[10px]">{`{${v}}`}</Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {tab === 'history' && (
        <div className="space-y-3">
          {history.length === 0 ? (
            <div className="text-center py-12 text-[#7e7e8a]">
              <History className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>Henuz mesaj gonderilmemis</p>
            </div>
          ) : history.map((msg, i) => (
            <div key={i} className="glass rounded-xl p-4 flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <Check className="w-5 h-5 text-green-400" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-white">{msg.template_key?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                  <Badge className={msg.channel === 'whatsapp' ? 'bg-green-500/10 text-green-400 text-[10px]' : 'bg-blue-500/10 text-blue-400 text-[10px]'}>
                    {msg.channel}
                  </Badge>
                </div>
                <p className="text-xs text-[#7e7e8a] mt-1">
                  {msg.guest_name && `${msg.guest_name} | `}{msg.created_at?.slice(0, 16).replace('T', ' ')}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
