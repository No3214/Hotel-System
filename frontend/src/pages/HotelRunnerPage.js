import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Globe, RefreshCw, CheckCircle, XCircle, Clock, Loader2, AlertTriangle, Wifi, WifiOff } from 'lucide-react';
import { getHotelRunnerStatus, syncHotelRunnerFull, syncHotelRunnerReservations, syncHotelRunnerAvailability, syncHotelRunnerRates, getHotelRunnerSyncLogs, getHotelRunnerConfig } from '../api';

function fmt(n) { return n?.toLocaleString('tr-TR') ?? '0'; }

export default function HotelRunnerPage() {
  const [status, setStatus] = useState(null);
  const [config, setConfig] = useState(null);
  const [syncLogs, setSyncLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(null);

  useEffect(() => { loadAll(); }, []);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [sRes, cRes, lRes] = await Promise.all([
        getHotelRunnerStatus(),
        getHotelRunnerConfig(),
        getHotelRunnerSyncLogs({}),
      ]);
      setStatus(sRes.data);
      setConfig(cRes.data);
      setSyncLogs(lRes.data.logs || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const handleSync = async (type) => {
    setSyncing(type);
    try {
      if (type === 'full') await syncHotelRunnerFull();
      else if (type === 'reservations') await syncHotelRunnerReservations();
      else if (type === 'availability') await syncHotelRunnerAvailability();
      else if (type === 'rates') await syncHotelRunnerRates();
      await loadAll();
    } catch (e) { console.error(e); }
    setSyncing(null);
  };

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <Loader2 className="w-8 h-8 animate-spin text-[#C4972A]" />
    </div>
  );

  return (
    <div className="p-6 space-y-6" data-testid="hotelrunner-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">HotelRunner Entegrasyonu</h1>
          <p className="text-sm text-[#7e7e8a] mt-1">OTA senkronizasyonu ve kanal yonetimi</p>
        </div>
        <button onClick={() => handleSync('full')} disabled={!!syncing}
          className="flex items-center gap-2 px-4 py-2 bg-[#C4972A] text-black rounded-lg font-medium hover:bg-[#d4a73a] transition-colors disabled:opacity-50"
          data-testid="full-sync-btn">
          <RefreshCw className={`w-4 h-4 ${syncing === 'full' ? 'animate-spin' : ''}`} />
          {syncing === 'full' ? 'Senkronize ediliyor...' : 'Tam Senkronizasyon'}
        </button>
      </div>

      {/* Connection Status */}
      <div className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-6" data-testid="connection-status">
        <div className="flex items-center gap-4">
          <div className={`p-3 rounded-xl ${status?.connected ? 'bg-emerald-500/10' : 'bg-yellow-500/10'}`}>
            {status?.connected ? <Wifi className="w-8 h-8 text-emerald-400" /> : <WifiOff className="w-8 h-8 text-yellow-400" />}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">
              {status?.connected ? 'Baglanti Aktif' : 'Mock Mod (API Anahtari Bekleniyor)'}
            </h2>
            <p className="text-sm text-[#7e7e8a] mt-0.5">
              {status?.mock_mode
                ? 'API anahtarlari .env dosyasina eklendikten sonra canli senkronizasyon baslar'
                : 'HotelRunner ile iki yonlu senkronizasyon aktif'}
            </p>
          </div>
        </div>

        {status?.mock_mode && (
          <div className="mt-4 bg-yellow-500/5 border border-yellow-500/10 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm text-yellow-400 font-medium">API Anahtari Gerekli</p>
                <p className="text-xs text-[#7e7e8a] mt-1">
                  Backend .env dosyasina su degiskenleri ekleyin:
                </p>
                <code className="block text-xs text-[#a9a9b2] bg-black/30 rounded p-2 mt-2 font-mono">
                  HOTELRUNNER_API_KEY=your_api_key<br/>
                  HOTELRUNNER_HOTEL_ID=your_hotel_id
                </code>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4" data-testid="sync-features">
        {[
          { key: 'reservations', title: 'Rezervasyon Senkronizasyonu', desc: 'OTA rezervasyonlarini al ve gonder', icon: CheckCircle },
          { key: 'availability', title: 'Musaitlik Senkronizasyonu', desc: 'Oda musaitliklerini guncelle', icon: Clock },
          { key: 'rates', title: 'Fiyat Senkronizasyonu', desc: 'Dinamik fiyatlari OTA lara gonder', icon: Globe },
        ].map(f => (
          <motion.div key={f.key} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-5 hover:border-[#C4972A]/30 transition-colors">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-[#C4972A]/10 rounded-lg"><f.icon className="w-5 h-5 text-[#C4972A]" /></div>
              <h3 className="text-white font-medium">{f.title}</h3>
            </div>
            <p className="text-xs text-[#7e7e8a] mb-4">{f.desc}</p>
            <button onClick={() => handleSync(f.key)} disabled={!!syncing}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-white/5 hover:bg-[#C4972A]/10 text-[#a9a9b2] hover:text-[#C4972A] rounded-lg text-sm transition-colors disabled:opacity-50"
              data-testid={`sync-${f.key}-btn`}>
              <RefreshCw className={`w-3.5 h-3.5 ${syncing === f.key ? 'animate-spin' : ''}`} />
              {syncing === f.key ? 'Calisiyor...' : 'Senkronize Et'}
            </button>
          </motion.div>
        ))}
      </div>

      {/* Sync Logs */}
      <div className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl overflow-hidden" data-testid="sync-logs">
        <div className="px-5 py-4 border-b border-[#C4972A]/10">
          <h2 className="text-white font-semibold">Senkronizasyon Gecmisi</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/[0.03]">
                <th className="px-4 py-3 text-left text-xs text-[#7e7e8a]">Zaman</th>
                <th className="px-4 py-3 text-left text-xs text-[#7e7e8a]">Tip</th>
                <th className="px-4 py-3 text-left text-xs text-[#7e7e8a]">Durum</th>
                <th className="px-4 py-3 text-left text-xs text-[#7e7e8a]">Islenen</th>
                <th className="px-4 py-3 text-left text-xs text-[#7e7e8a]">Mod</th>
              </tr>
            </thead>
            <tbody>
              {syncLogs.map((log, i) => (
                <tr key={i} className="border-b border-white/[0.02] hover:bg-white/[0.02]">
                  <td className="px-4 py-2.5 text-xs text-[#7e7e8a]">{log.timestamp ? new Date(log.timestamp).toLocaleString('tr-TR') : '-'}</td>
                  <td className="px-4 py-2.5 text-xs text-white capitalize">{log.sync_type}</td>
                  <td className="px-4 py-2.5">
                    {log.status === 'success'
                      ? <span className="text-xs text-emerald-400 flex items-center gap-1"><CheckCircle className="w-3 h-3" /> Basarili</span>
                      : <span className="text-xs text-red-400 flex items-center gap-1"><XCircle className="w-3 h-3" /> Hata</span>}
                  </td>
                  <td className="px-4 py-2.5 text-xs text-[#a9a9b2]">{log.items_processed || 0}</td>
                  <td className="px-4 py-2.5">
                    {log.mock
                      ? <span className="text-xs px-2 py-0.5 bg-yellow-500/10 text-yellow-400 rounded">Mock</span>
                      : <span className="text-xs px-2 py-0.5 bg-emerald-500/10 text-emerald-400 rounded">Canli</span>}
                  </td>
                </tr>
              ))}
              {syncLogs.length === 0 && (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-[#7e7e8a]">Henuz senkronizasyon yapilmadi</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Config Info */}
      {config && (
        <div className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-5" data-testid="hotelrunner-config">
          <h3 className="text-white font-semibold mb-3">Yapilandirma</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <ConfigItem label="Senkronizasyon Araligi" value={`${config.sync_interval_minutes} dk`} />
            <ConfigItem label="API Anahtari" value={config.api_key_set ? 'Ayarli' : 'Eksik'} ok={config.api_key_set} />
            <ConfigItem label="Hotel ID" value={config.hotel_id_set ? 'Ayarli' : 'Eksik'} ok={config.hotel_id_set} />
            <ConfigItem label="Mod" value={config.mock_mode ? 'Mock' : 'Canli'} ok={!config.mock_mode} />
          </div>
        </div>
      )}
    </div>
  );
}

function ConfigItem({ label, value, ok }) {
  return (
    <div className="bg-white/[0.02] rounded-lg p-3">
      <p className="text-xs text-[#7e7e8a]">{label}</p>
      <p className={`text-sm font-medium mt-0.5 ${ok === true ? 'text-emerald-400' : ok === false ? 'text-yellow-400' : 'text-white'}`}>{value}</p>
    </div>
  );
}
