import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { setupAdmin } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Lock, User, AlertCircle } from 'lucide-react';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [setupMsg, setSetupMsg] = useState('');
  const { loginUser } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Kullanici adi ve sifre gereklidir');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await loginUser(username, password);
      navigate('/admin');
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (err.response?.status === 429) {
        setError('Cok fazla deneme yaptiniz. Lutfen biraz bekleyin.');
      } else {
        setError(detail || 'Giris basarisiz');
      }
    }
    setLoading(false);
  };

  const handleSetup = async () => {
    try {
      const res = await setupAdmin();
      if (res.data.has_users) {
        setSetupMsg('Sistem zaten kurulmus. Mevcut admin bilgilerini kullanin.');
      } else if (res.data.username && res.data.password) {
        setSetupMsg(`Admin olusturuldu! Kullanici: ${res.data.username} / Sifre: ${res.data.password} — Bu sifre sadece bir kez gosterilir!`);
      } else {
        setSetupMsg(res.data.message || 'Kurulum tamamlandi');
      }
    } catch (err) {
      setSetupMsg(err.response?.data?.detail || err.response?.data?.message || 'Hata');
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center p-4 relative overflow-hidden" data-testid="login-page">
      {/* Background effects */}
      <div className="absolute inset-0 noise-bg" />
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#C4972A]/5 rounded-full blur-[120px] animate-breathe" />
      <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-[#6366f1]/5 rounded-full blur-[100px] animate-breathe" style={{ animationDelay: '1.5s' }} />

      <div className="w-full max-w-sm space-y-6 relative z-10">
        {/* Logo */}
        <div className="text-center animate-fade-in-up">
          <div className="relative inline-block">
            <div className="absolute -inset-3 bg-[#C4972A]/10 rounded-3xl blur-xl animate-pulse-gold" />
            <img
              src="/logo.jpeg"
              alt="Kozbeyli Konagi"
              className="w-20 h-20 mx-auto rounded-2xl object-cover mb-4 relative z-10 shadow-2xl"
              data-testid="login-logo"
            />
          </div>
          <h1 className="text-2xl font-bold gold-gradient-text mt-2">Kozbeyli Konagi</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">Otel Yonetim Sistemi</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="glass-strong rounded-2xl p-6 space-y-4 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
          <div className="space-y-3">
            <div className="relative group">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#7e7e8a] group-focus-within:text-[#C4972A] transition-colors" />
              <Input
                placeholder="Kullanici adi"
                value={username}
                onChange={e => setUsername(e.target.value)}
                className="pl-10 bg-white/5 border-white/10 text-white focus:border-[#C4972A]/50 focus:ring-1 focus:ring-[#C4972A]/20 transition-all rounded-xl"
                data-testid="login-username"
                autoFocus
              />
            </div>
            <div className="relative group">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#7e7e8a] group-focus-within:text-[#C4972A] transition-colors" />
              <Input
                type="password"
                placeholder="Sifre"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="pl-10 bg-white/5 border-white/10 text-white focus:border-[#C4972A]/50 focus:ring-1 focus:ring-[#C4972A]/20 transition-all rounded-xl"
                data-testid="login-password"
              />
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/10 rounded-xl p-2.5 animate-fade-in-scale" data-testid="login-error">
              <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
            </div>
          )}

          <Button type="submit" disabled={loading}
            className="w-full bg-gradient-to-r from-[#a87a1f] via-[#C4972A] to-[#dfa04e] hover:brightness-110 text-white rounded-xl h-11 font-medium transition-all duration-300 shadow-lg shadow-[#C4972A]/20 hover:shadow-xl hover:shadow-[#C4972A]/30 active:scale-[0.98]"
            data-testid="login-submit"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Giris yapiliyor...
              </span>
            ) : 'Giris Yap'}
          </Button>
        </form>

        {/* Setup */}
        <div className="text-center space-y-2 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          <button onClick={handleSetup} className="text-xs text-[#5a5a65] hover:text-[#C4972A] transition-colors duration-300" data-testid="setup-admin-btn">
            Ilk kurulum? Admin olustur
          </button>
          {setupMsg && <p className="text-xs text-[#C4972A] mt-2 bg-[#C4972A]/10 rounded-xl p-2 animate-fade-in-scale" data-testid="setup-message">{setupMsg}</p>}
        </div>
      </div>
    </div>
  );
}
