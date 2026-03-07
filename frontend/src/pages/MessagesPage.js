import React, { useState, useEffect } from 'react';
import { getMessages, sendWhatsAppWebhook, translateMessage } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { MessageCircle, Send, Phone, Instagram, Languages, Loader2, Sparkles } from 'lucide-react';

export default function MessagesPage() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [testForm, setTestForm] = useState({ from_number: '+905321234567', message: '', sender_name: 'Test Misafir' });

  // Translation State
  const [translatingId, setTranslatingId] = useState(null);
  const [translations, setTranslations] = useState({});
  const [replyContext, setReplyContext] = useState({});

  const load = () => {
    getMessages({ platform: filter !== 'all' ? filter : undefined })
      .then(r => setMessages(r.data.messages))
      .catch(console.error)
      .finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, [filter]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleTest = async () => {
    if (!testForm.message) return;
    await sendWhatsAppWebhook(testForm);
    setTestForm({ ...testForm, message: '' });
    load();
  };

  const handleTranslate = async (msgId, messageText) => {
    setTranslatingId(msgId);
    try {
      const context = replyContext[msgId] || '';
      const res = await translateMessage({ message: messageText, hotel_context: context });
      if (res.data.success) {
        setTranslations({ ...translations, [msgId]: res.data.data });
      }
    } catch (e) {
      console.error(e);
      alert('Ceviri sirasinda bir hata olustu.');
    }
    setTranslatingId(null);
  };

  const handleContextChange = (msgId, text) => {
    setReplyContext({ ...replyContext, [msgId]: text });
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="messages-page">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Mesajlar</h1>
        <p className="text-[#7e7e8a] text-sm mt-1">WhatsApp & Instagram mesajlari</p>
      </div>

      {/* Test WhatsApp */}
      <div className="glass rounded-xl p-5">
        <h3 className="text-sm font-medium text-[#C4972A] mb-3 flex items-center gap-2">
          <Phone className="w-4 h-4" /> WhatsApp Test (Webhook Simulasyonu)
        </h3>
        <div className="flex gap-2">
          <Input value={testForm.from_number} onChange={e => setTestForm({ ...testForm, from_number: e.target.value })}
            className="w-40 bg-white/5 border-white/10 text-sm" placeholder="Numara" />
          <Input value={testForm.message} onChange={e => setTestForm({ ...testForm, message: e.target.value })}
            className="flex-1 bg-white/5 border-white/10" placeholder="Mesaj yazin..."
            onKeyDown={e => e.key === 'Enter' && handleTest()} data-testid="wa-test-input" />
          <Button onClick={handleTest} className="bg-green-600 hover:bg-green-700 text-white" data-testid="wa-test-send">
            <Send className="w-4 h-4" />
          </Button>
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
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Badge className={msg.platform === 'whatsapp' ? 'bg-green-500/20 text-green-400' : 'bg-pink-500/20 text-pink-400'}>
                  {msg.platform}
                </Badge>
                <span className="text-xs text-[#7e7e8a]">{msg.sender_name || msg.from_number || msg.sender}</span>
              </div>
              <span className="text-xs text-[#7e7e8a]">{msg.created_at?.slice(11, 16)}</span>
            </div>
            
            <div className="space-y-3">
              {/* Original Message */}
              <div className="bg-white/5 rounded-lg p-3">
                <p className="text-sm">{msg.message}</p>
                
                {/* AI Translate Button */}
                {!msg.response && !translations[msg.id] && (
                  <div className="mt-3 flex items-center justify-end border-t border-white/5 pt-2">
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => handleTranslate(msg.id, msg.message)}
                      disabled={translatingId === msg.id}
                      className="h-7 text-xs text-blue-400 hover:text-blue-300 hover:bg-blue-500/10"
                    >
                      {translatingId === msg.id ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : <Languages className="w-3 h-3 mr-1" />}
                      Gemini ile Cevir & Yanitla
                    </Button>
                  </div>
                )}
              </div>

              {/* Engine/Auto Response */}
              {msg.response && (
                <div className="bg-[#C4972A]/5 border border-[#C4972A]/10 rounded-lg p-3 ml-6">
                  <p className="text-xs text-[#C4972A]/60 mb-1">Bot Yaniti</p>
                  <p className="text-sm text-[#a9a9b2]">{msg.response}</p>
                </div>
              )}

              {/* AI Translation & Smart Reply Section */}
              {translations[msg.id] && !msg.response && (
                <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-3 ml-6 space-y-3">
                  <div className="flex items-center gap-1.5 text-xs text-blue-400 font-medium pb-2 border-b border-blue-500/10">
                    <Sparkles className="w-4 h-4" /> AI Ceviri & Akilli Yanit
                    <Badge className="ml-2 bg-blue-500/20 text-blue-300 hover:bg-blue-500/20">{translations[msg.id].detected_language}</Badge>
                  </div>
                  
                  <div>
                    <p className="text-xs text-blue-300/70 mb-1">Turkce Cevirisi:</p>
                    <p className="text-sm text-[#e5e5e8]">{translations[msg.id].translated_text}</p>
                  </div>

                  <div className="bg-[#1a1a22] p-2.5 rounded border border-white/5">
                    <p className="text-xs text-blue-300/70 mb-1">AI'in Onerdigi Orijinal Dildeki Yanit:</p>
                    <p className="text-sm text-green-400 font-medium">{translations[msg.id].suggested_reply}</p>
                  </div>

                  <div className="pt-2 border-t border-blue-500/10">
                    <p className="text-xs text-[#7e7e8a] mb-1.5">Yaniti Yonlendir (Opsiyonel Baglam Ekle):</p>
                    <div className="flex gap-2">
                      <Input 
                        value={replyContext[msg.id] || ''} 
                        onChange={e => handleContextChange(msg.id, e.target.value)}
                        placeholder="Örn: Erken check-in yapamayiz, odalar dolu de." 
                        className="h-8 bg-black/20 border-white/5 text-xs"
                      />
                      <Button 
                        size="sm"
                        onClick={() => handleTranslate(msg.id, msg.message)}
                        disabled={translatingId === msg.id}
                        className="h-8 bg-blue-600 hover:bg-blue-700 text-white text-xs px-3"
                      >
                        {translatingId === msg.id ? <Loader2 className="w-3 h-3 animate-spin" /> : 'Yeniden Uret'}
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        {messages.length === 0 && !loading && (
          <div className="text-center py-12 text-[#7e7e8a]">
            <MessageCircle className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Henuz mesaj yok</p>
          </div>
        )}
      </div>
    </div>
  );
}
