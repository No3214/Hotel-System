import React, { useState, useEffect } from 'react';
import { getMessages, sendWhatsAppWebhook, sendInstagramWebhook } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { MessageCircle, Send, Phone, Instagram, Info } from 'lucide-react';

export default function MessagesPage() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [testForm, setTestForm] = useState({ from_number: '+905321234567', message: '', sender_name: 'Test Misafir' });
  const [igForm, setIgForm] = useState({ sender: 'test_user', message: '' });

  const load = () => {
    getMessages({ platform: filter !== 'all' ? filter : undefined })
      .then(r => setMessages(r.data.messages))
      .catch(console.error)
      .finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, [filter]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleWATest = async () => {
    if (!testForm.message) return;
    await sendWhatsAppWebhook(testForm);
    setTestForm({ ...testForm, message: '' });
    load();
  };

  const handleIGTest = async () => {
    if (!igForm.message) return;
    await sendInstagramWebhook(igForm);
    setIgForm({ ...igForm, message: '' });
    load();
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="messages-page">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Mesajlar</h1>
        <p className="text-[#7e7e8a] text-sm mt-1">WhatsApp & Instagram mesajlari — AI otomatik yanit</p>
      </div>

      {/* Test Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* WhatsApp Test */}
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-medium text-green-400 mb-3 flex items-center gap-2">
            <Phone className="w-4 h-4" /> WhatsApp Test
          </h3>
          <div className="flex gap-2">
            <Input value={testForm.from_number} onChange={e => setTestForm({ ...testForm, from_number: e.target.value })}
              className="w-40 bg-white/5 border-white/10 text-sm" placeholder="Numara" />
            <Input value={testForm.message} onChange={e => setTestForm({ ...testForm, message: e.target.value })}
              className="flex-1 bg-white/5 border-white/10" placeholder="WhatsApp mesaji yazin..."
              onKeyDown={e => e.key === 'Enter' && handleWATest()} data-testid="wa-test-input" />
            <Button onClick={handleWATest} className="bg-green-600 hover:bg-green-700 text-white" data-testid="wa-test-send">
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Instagram Test */}
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-medium text-pink-400 mb-3 flex items-center gap-2">
            <Instagram className="w-4 h-4" /> Instagram DM Test
          </h3>
          <div className="flex gap-2">
            <Input value={igForm.sender} onChange={e => setIgForm({ ...igForm, sender: e.target.value })}
              className="w-40 bg-white/5 border-white/10 text-sm" placeholder="Kullanici adi" />
            <Input value={igForm.message} onChange={e => setIgForm({ ...igForm, message: e.target.value })}
              className="flex-1 bg-white/5 border-white/10" placeholder="Instagram mesaji yazin..."
              onKeyDown={e => e.key === 'Enter' && handleIGTest()} data-testid="ig-test-input" />
            <Button onClick={handleIGTest} className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white" data-testid="ig-test-send">
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Integration Info */}
      <div className="bg-gradient-to-r from-purple-500/5 to-pink-500/5 border border-purple-500/10 rounded-xl p-4">
        <div className="flex gap-3">
          <Info className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
          <div className="text-xs text-[#a9a9b2] space-y-1">
            <p className="text-purple-300 font-medium">Instagram & WhatsApp Entegrasyonu</p>
            <p>Gercek mesajlari almak icin Meta Business Suite uzerinden webhook ayarlari gereklidir:</p>
            <ul className="list-disc list-inside space-y-0.5 text-[#7e7e8a]">
              <li>WhatsApp: <code className="text-green-300/70 bg-white/5 px-1 rounded">WHATSAPP_ACCESS_TOKEN</code>, <code className="text-green-300/70 bg-white/5 px-1 rounded">WHATSAPP_PHONE_NUMBER_ID</code></li>
              <li>Instagram: <code className="text-pink-300/70 bg-white/5 px-1 rounded">INSTAGRAM_ACCESS_TOKEN</code>, <code className="text-pink-300/70 bg-white/5 px-1 rounded">INSTAGRAM_PAGE_ID</code></li>
              <li>Webhook URL'ler Railway env vars'a eklenmeli</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {[
          { id: 'all', label: 'Tumu', icon: MessageCircle },
          { id: 'whatsapp', label: 'WhatsApp', icon: Phone },
          { id: 'instagram', label: 'Instagram', icon: Instagram },
        ].map(f => (
          <button
            key={f.id}
            onClick={() => setFilter(f.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs transition-all ${
              filter === f.id ? 'bg-[#C4972A]/20 text-[#C4972A]' : 'bg-white/5 text-[#7e7e8a] hover:bg-white/10'
            }`}
          >
            <f.icon className="w-3 h-3" /> {f.label}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="space-y-3">
        {messages.map(msg => (
          <div key={msg.id} className="glass rounded-xl p-4" data-testid={`message-${msg.id}`}>
            <div className="flex items-center gap-2 mb-2">
              <Badge className={msg.platform === 'whatsapp' ? 'bg-green-500/20 text-green-400' : 'bg-pink-500/20 text-pink-400'}>
                {msg.platform === 'whatsapp' ? <Phone className="w-3 h-3 mr-1" /> : <Instagram className="w-3 h-3 mr-1" />}
                {msg.platform}
              </Badge>
              <span className="text-xs text-[#7e7e8a]">{msg.sender_name || msg.from_number || msg.sender}</span>
              <span className="text-xs text-[#7e7e8a] ml-auto">{msg.created_at?.slice(0, 10)} {msg.created_at?.slice(11, 16)}</span>
            </div>
            <div className="space-y-2">
              <div className="bg-white/5 rounded-lg p-3">
                <p className="text-sm">{msg.message}</p>
              </div>
              {msg.response && (
                <div className="bg-[#C4972A]/5 border border-[#C4972A]/10 rounded-lg p-3 ml-6">
                  <p className="text-xs text-[#C4972A]/60 mb-1">AI Yanit</p>
                  <p className="text-sm text-[#a9a9b2]">{msg.response}</p>
                </div>
              )}
            </div>
          </div>
        ))}
        {messages.length === 0 && !loading && (
          <div className="text-center py-12 text-[#7e7e8a]">
            <MessageCircle className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Henuz mesaj yok</p>
            <p className="text-xs mt-1">Yukaridaki test panellerinden deneme mesaji gonderebilirsiniz</p>
          </div>
        )}
      </div>
    </div>
  );
}
