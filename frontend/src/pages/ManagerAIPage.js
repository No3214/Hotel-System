import React, { useState, useRef, useEffect } from 'react';
import { sendManagerCommand } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Send, Zap, Activity } from 'lucide-react';

export default function ManagerAIPage() {
  const [sessionId] = useState(() => `manager-${Date.now()}`);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || sending) return;

    setMessages(prev => [...prev, { role: 'user', text, time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }) }]);
    setInput('');
    setSending(true);

    try {
      const res = await sendManagerCommand({ message: text, session_id: sessionId });
      setMessages(prev => [...prev, {
        role: 'ai',
        text: res.data.response,
        time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
      }]);
    } catch {
      setMessages(prev => [...prev, { role: 'ai', text: 'Bir hata olustu. Lutfen tekrar deneyin.', time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }) }]);
    }
    setSending(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickMessages = [
    'Bugunku durum nedir?',
    'Son 7 gunluk gelir ne kadar?',
    'Yarin kac kisi giris yapiyor?',
    'Bekleyen personel gorevleri nelerdir?',
  ];

  return (
    <div className="flex flex-col h-full" data-testid="manager-ai-page">
      {/* Header */}
      <div className="p-4 border-b border-[#2A9D8F]/10 flex items-center justify-between bg-[#0f0f14]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#2A9D8F] to-[#1d6b61] flex items-center justify-center">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-[#2A9D8F]">Manager AI (İş Zekası)</h2>
            <p className="text-xs text-[#7e7e8a]">Konuşmalı Veri Analizi</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12 animate-fade-in-up">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#2A9D8F]/10 flex items-center justify-center">
              <Activity className="w-8 h-8 text-[#2A9D8F]" />
            </div>
            <h3 className="text-lg font-semibold text-[#2A9D8F] mb-2">Manager AI'a Hoş Geldiniz!</h3>
            <p className="text-sm text-[#7e7e8a] mb-6">Otel verilerini sorgulayın ve anlık durum raporu alın.</p>
            <div className="flex flex-wrap gap-2 justify-center max-w-lg mx-auto">
              {quickMessages.map((msg, i) => (
                <button
                  key={i}
                  onClick={() => { setInput(msg); }}
                  className="text-xs px-3 py-2 rounded-full bg-[#2A9D8F]/10 text-[#2A9D8F] hover:bg-[#2A9D8F]/20 transition-colors"
                >
                  {msg}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] ${msg.role === 'user' ? 'ml-auto' : 'flex gap-2 mr-auto'}`}>
              {msg.role === 'ai' && (
                <div className="w-7 h-7 rounded-full bg-[#2A9D8F]/20 flex items-center justify-center flex-shrink-0 mt-1">
                  <Activity className="w-3.5 h-3.5 text-[#2A9D8F]" />
                </div>
              )}
              <div className="flex flex-col">
                <div className={`px-4 py-3 rounded-2xl ${
                  msg.role === 'user' 
                    ? 'bg-[#2A9D8F] text-white rounded-tr-sm' 
                    : 'bg-[#1a1a22] border border-[#2A9D8F]/20 text-[#e5e5e8] rounded-tl-sm'
                }`}>
                  <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
                </div>
                <p className={`text-xs mt-1 text-[#5a5a65] ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                  {msg.time}
                </p>
              </div>
            </div>
          </div>
        ))}

        {sending && (
          <div className="flex gap-2">
            <div className="w-7 h-7 rounded-full bg-[#2A9D8F]/20 flex items-center justify-center flex-shrink-0">
              <Zap className="w-3.5 h-3.5 text-[#2A9D8F] animate-pulse" />
            </div>
            <div className="bg-[#1a1a22] border border-[#2A9D8F]/20 px-4 py-3 rounded-2xl rounded-tl-sm">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-[#2A9D8F]/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-[#2A9D8F]/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-[#2A9D8F]/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-[#2A9D8F]/10 bg-[#0f0f14]">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Yönetici asistanınıza bir soru sorun..."
            className="flex-1 bg-white/5 border-[#2A9D8F]/20 focus:border-[#2A9D8F]/50 text-white"
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            className="bg-[#2A9D8F] hover:bg-[#21867a] text-white px-4"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
