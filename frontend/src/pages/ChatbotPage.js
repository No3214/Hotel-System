import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage, clearChat } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Send, Trash2, Sparkles, User } from 'lucide-react';

export default function ChatbotPage() {
  const [sessionId] = useState(() => `chat-${Date.now()}`);
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
      const res = await sendChatMessage({ message: text, session_id: sessionId });
      setMessages(prev => [...prev, {
        role: 'ai',
        text: res.data.response,
        intent: res.data.intent,
        time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
      }]);
    } catch {
      setMessages(prev => [...prev, { role: 'ai', text: 'Bir hata olustu. Lutfen tekrar deneyin.', time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }) }]);
    }
    setSending(false);
  };

  const handleClear = async () => {
    await clearChat(sessionId).catch(() => {});
    setMessages([]);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickMessages = [
    'Odalariniz hakkinda bilgi verir misiniz?',
    'Restoran menunuzu gormek istiyorum',
    'Iptal politikaniz nedir?',
    'Foca\'da ne yapilabilir?',
    'Etkinlikleriniz var mi?',
  ];

  return (
    <div className="flex flex-col h-full" data-testid="chatbot-page">
      {/* Header */}
      <div className="p-4 border-b border-[#C4972A]/10 flex items-center justify-between bg-[#0f0f14]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#C4972A] to-[#8a5f1a] flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-[#C4972A]">Kozbeyli AI Asistan</h2>
            <p className="text-xs text-[#7e7e8a]">Gemini AI - Her zaman hazir</p>
          </div>
        </div>
        <Button variant="ghost" size="sm" onClick={handleClear} className="text-[#7e7e8a] hover:text-red-400" data-testid="clear-chat-btn">
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#C4972A]/10 flex items-center justify-center">
              <Sparkles className="w-8 h-8 text-[#C4972A]" />
            </div>
            <h3 className="text-lg font-semibold text-[#C4972A] mb-2">Hos Geldiniz!</h3>
            <p className="text-sm text-[#7e7e8a] mb-6">Kozbeyli Konagi hakkinda her seyi sorun</p>
            <div className="flex flex-wrap gap-2 justify-center max-w-lg mx-auto">
              {quickMessages.map((msg, i) => (
                <button
                  key={i}
                  onClick={() => { setInput(msg); }}
                  className="text-xs px-3 py-2 rounded-full bg-[#C4972A]/10 text-[#C4972A] hover:bg-[#C4972A]/20 transition-colors"
                  data-testid={`quick-msg-${i}`}
                >
                  {msg}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] ${msg.role === 'user' ? '' : 'flex gap-2'}`}>
              {msg.role === 'ai' && (
                <div className="w-7 h-7 rounded-full bg-[#C4972A]/20 flex items-center justify-center flex-shrink-0 mt-1">
                  <Sparkles className="w-3.5 h-3.5 text-[#C4972A]" />
                </div>
              )}
              <div>
                <div className={msg.role === 'user' ? 'chat-bubble-user px-4 py-3 text-white' : 'chat-bubble-ai px-4 py-3'}>
                  <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
                </div>
                <p className={`text-xs mt-1 text-[#7e7e8a] ${msg.role === 'user' ? 'text-right' : ''}`}>
                  {msg.time}
                  {msg.intent && msg.intent !== 'general' && (
                    <span className="ml-2 text-[#C4972A]/60">{msg.intent}</span>
                  )}
                </p>
              </div>
            </div>
          </div>
        ))}

        {sending && (
          <div className="flex gap-2">
            <div className="w-7 h-7 rounded-full bg-[#C4972A]/20 flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-3.5 h-3.5 text-[#C4972A] animate-spin" />
            </div>
            <div className="chat-bubble-ai px-4 py-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-[#C4972A]/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-[#C4972A]/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-[#C4972A]/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-[#C4972A]/10 bg-[#0f0f14]">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Mesajinizi yazin..."
            className="flex-1 bg-white/5 border-[#C4972A]/20 focus:border-[#C4972A]/50"
            data-testid="chat-input"
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            className="bg-[#C4972A] hover:bg-[#a87a1f] text-white px-4"
            data-testid="send-message-btn"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
