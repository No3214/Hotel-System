import React, { useState } from 'react';
import { login, setAuthToken, setupAdmin } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Lock, User, AlertCircle } from 'lucide-react';

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [setupMsg, setSetupMsg] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username || !password) return;
    setLoading(true);
    setError('');
    try {
      const res = await login({ username, password });
      setAuthToken(res.data.token);
      localStorage.setItem('kozbeyli_user', JSON.stringify(res.data.user));
      onLogin(res.data.user);
    } catch (err) {
      setError(err.response?.data?.detail || 'Giris basarisiz');
    }
    setLoading(false);
  };

  const handleSetup = async () => {
    try {
      const res = await setupAdmin();
      if (res.data.has_users) {
        // System already set up
        setSetupMsg('Sistem zaten kurulmus. Mevcut admin bilgilerini kullanin.');
      } else if (res.data.username && res.data.password) {
        // New admin created
        setSetupMsg(`Admin olusturuldu! Kullanici: ${res.data.username} / Sifre: ${res.data.password}`);
      } else {
        setSetupMsg(res.data.message || 'Kurulum tamamlandi');
      }
    } catch (err) {
      setSetupMsg(err.response?.data?.detail || err.response?.data?.message || 'Hata');
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center p-4" data-testid="login-page">
      <div className="w-full max-w-sm space-y-6">
        {/* Logo */}
        <div className="text-center">
          <img
            src="/logo.jpeg"
            alt="Kozbeyli Konagi"
            className="w-20 h-20 mx-auto rounded-2xl object-cover mb-4"
            data-testid="login-logo"
          />
          <h1 className="text-2xl font-bold text-[#C4972A]">Kozbeyli Konagi</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">Otel Yonetim Sistemi</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="bg-[#12121a] rounded-xl border border-white/5 p-6 space-y-4">
          <div className="space-y-3">
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#7e7e8a]" />
              <Input
                placeholder="Kullanici adi"
                value={username}
                onChange={e => setUsername(e.target.value)}
                className="pl-10 bg-white/5 border-white/10 text-white"
                data-testid="login-username"
                autoFocus
              />
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#7e7e8a]" />
              <Input
                type="password"
                placeholder="Sifre"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="pl-10 bg-white/5 border-white/10 text-white"
                data-testid="login-password"
              />
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/10 rounded-lg p-2.5" data-testid="login-error">
              <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
            </div>
          )}

          <Button type="submit" disabled={loading} className="w-full bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="login-submit">
            {loading ? 'Giris yapiliyor...' : 'Giris Yap'}
          </Button>
        </form>

        {/* Setup */}
        <div className="text-center space-y-2">
          <button onClick={handleSetup} className="text-xs text-[#5a5a65] hover:text-[#C4972A] transition-colors" data-testid="setup-admin-btn">
            Ilk kurulum? Admin olustur
          </button>
          {setupMsg && <p className="text-xs text-[#C4972A] mt-2 bg-[#C4972A]/10 rounded p-2" data-testid="setup-message">{setupMsg}</p>}
          <p className="text-xs text-[#4a4a55] mt-3">
            Varsayilan: admin / kozbeyli2026
          </p>
        </div>
      </div>
    </div>
  );
}
