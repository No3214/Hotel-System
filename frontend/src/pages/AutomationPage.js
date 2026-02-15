import React, { useState, useEffect } from 'react';
import {
  runPaymentReminder, runCancellationCheck, getKitchenForecast,
  getAutomationLogs, getAutomationSummary,
  runBreakfastNotification, runMorningReminders, runCleaningNotification,
  getScheduledJobs, getGroupNotifications
} from '../api';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  Bot, CreditCard, XCircle, UtensilsCrossed, Play, Clock,
  Coffee, Sparkles, Brush, Bell, CalendarClock, MessageSquare
} from 'lucide-react';

const BOTS = [
  { id: 'breakfast', name: 'Kahvalti Hazirligi', desc: 'Sabah kahvalti misafir sayisi bildirimi', icon: Coffee, color: '#f59e0b', schedule: 'Her gece 01:00' },
  { id: 'morning', name: 'Sabah Hatirlama', desc: 'Tuvalet temizlik + check-in odasi hazirligi', icon: Sparkles, color: '#3b82f6', schedule: 'Her gun 08:30' },
  { id: 'cleaning', name: 'Temizlik Listesi', desc: 'Check-out sonrasi temizlenecek oda listesi', icon: Brush, color: '#10b981', schedule: 'Her gun 12:30' },
  { id: 'payment', name: 'Odeme Hatirlatma', desc: 'Cumartesi check-in: on odeme kontrolu', icon: CreditCard, color: '#eab308', schedule: 'Manuel' },
  { id: 'cancellation', name: 'Iptal Denetcisi', desc: 'Iptal ceza hesaplama otomasyonu', icon: XCircle, color: '#ef4444', schedule: 'Manuel' },
  { id: 'kitchen', name: 'Mutfak Tahmini', desc: '7 gunluk yemek planlama', icon: UtensilsCrossed, color: '#22c55e', schedule: 'Manuel' },
];

export default function AutomationPage() {
  const [summary, setSummary] = useState(null);
  const [logs, setLogs] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [running, setRunning] = useState(null);
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(true);
  const [jobs, setJobs] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [activeTab, setActiveTab] = useState('bots');

  useEffect(() => {
    Promise.all([
      getAutomationSummary().then(r => setSummary(r.data)),
      getAutomationLogs({ limit: 20 }).then(r => setLogs(r.data.logs)),
      getScheduledJobs().then(r => setJobs(r.data.jobs)).catch(() => {}),
      getGroupNotifications({ limit: 20 }).then(r => setNotifications(r.data.notifications)).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  const runBot = async (botId) => {
    setRunning(botId);
    try {
      let res;
      if (botId === 'breakfast') {
        res = await runBreakfastNotification();
      } else if (botId === 'morning') {
        res = await runMorningReminders();
      } else if (botId === 'cleaning') {
        res = await runCleaningNotification();
      } else if (botId === 'payment') {
        res = await runPaymentReminder();
      } else if (botId === 'cancellation') {
        res = await runCancellationCheck();
      } else if (botId === 'kitchen') {
        res = await getKitchenForecast(7);
        setForecast(res.data.forecast);
      }
      setResults(prev => ({ ...prev, [botId]: res.data }));
      getAutomationLogs({ limit: 20 }).then(r => setLogs(r.data.logs));
      getAutomationSummary().then(r => setSummary(r.data));
      getGroupNotifications({ limit: 20 }).then(r => setNotifications(r.data.notifications)).catch(() => {});
    } catch (err) {
      console.error(err);
    }
    setRunning(null);
  };

  const getResultText = (botId, result) => {
    if (!result) return null;
    switch (botId) {
      case 'breakfast': return result.notification?.message || 'Bildirim gonderildi';
      case 'morning': return `${result.notifications?.length || 0} hatirlama gonderildi`;
      case 'cleaning': return result.notification?.message || 'Temizlik bildirimi gonderildi';
      case 'payment': return `${result.reminders_created} hatirlatma olusturuldu`;
      case 'cancellation': return `${result.processed} iptal islendi`;
      case 'kitchen': return `${result.forecast_days} gunluk tahmin hazir`;
      default: return 'Tamamlandi';
    }
  };

  const getLogIcon = (type) => {
    switch (type) {
      case 'breakfast_prep': return <Coffee className="w-3.5 h-3.5 text-amber-400" />;
      case 'morning_toilet_reminder': return <Sparkles className="w-3.5 h-3.5 text-blue-400" />;
      case 'morning_checkin_reminder': return <Bell className="w-3.5 h-3.5 text-blue-400" />;
      case 'checkout_cleaning': return <Brush className="w-3.5 h-3.5 text-green-400" />;
      case 'payment_reminder': return <CreditCard className="w-3.5 h-3.5 text-yellow-400" />;
      case 'cancellation_penalty': return <XCircle className="w-3.5 h-3.5 text-red-400" />;
      default: return <Bot className="w-3.5 h-3.5 text-[#C4972A]" />;
    }
  };

  if (loading) return <div className="p-8"><div className="h-8 w-64 bg-white/5 rounded animate-pulse" /></div>;

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="automation-page">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]" data-testid="automation-title">Otomasyon</h1>
        <p className="text-[#7e7e8a] text-sm mt-1">Zamanli gorevler ve operasyonel bildirimler</p>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3" data-testid="automation-summary">
          <div className="glass rounded-xl p-3 flex items-center gap-2">
            <Bot className="w-4 h-4 text-[#C4972A]" />
            <div><p className="text-[10px] text-[#7e7e8a]">Toplam</p><p className="text-lg font-bold text-white">{summary.total_logs}</p></div>
          </div>
          <div className="glass rounded-xl p-3 flex items-center gap-2">
            <Coffee className="w-4 h-4 text-amber-400" />
            <div><p className="text-[10px] text-[#7e7e8a]">Kahvalti</p><p className="text-lg font-bold text-white">{summary.breakfast_preps || 0}</p></div>
          </div>
          <div className="glass rounded-xl p-3 flex items-center gap-2">
            <Brush className="w-4 h-4 text-green-400" />
            <div><p className="text-[10px] text-[#7e7e8a]">Temizlik</p><p className="text-lg font-bold text-white">{summary.cleaning_notifications || 0}</p></div>
          </div>
          <div className="glass rounded-xl p-3 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-400" />
            <div><p className="text-[10px] text-[#7e7e8a]">Hatirlama</p><p className="text-lg font-bold text-white">{summary.morning_reminders || 0}</p></div>
          </div>
          <div className="glass rounded-xl p-3 flex items-center gap-2">
            <CreditCard className="w-4 h-4 text-yellow-400" />
            <div><p className="text-[10px] text-[#7e7e8a]">Odeme</p><p className="text-lg font-bold text-white">{summary.payment_reminders}</p></div>
          </div>
          <div className="glass rounded-xl p-3 flex items-center gap-2">
            <XCircle className="w-4 h-4 text-red-400" />
            <div><p className="text-[10px] text-[#7e7e8a]">Iptal</p><p className="text-lg font-bold text-white">{summary.cancellation_checks}</p></div>
          </div>
        </div>
      )}

      {/* Scheduled Jobs Status */}
      {jobs.length > 0 && (
        <div className="glass rounded-xl p-4" data-testid="scheduled-jobs">
          <h3 className="text-sm font-semibold text-[#C4972A] mb-3 flex items-center gap-2">
            <CalendarClock className="w-4 h-4" /> Zamanli Gorevler
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
            {jobs.map(job => (
              <div key={job.id} className="bg-white/3 rounded-lg p-3 flex items-center justify-between">
                <div>
                  <p className="text-sm text-white font-medium">{job.name}</p>
                  <p className="text-[10px] text-[#7e7e8a]">
                    Sonraki: {job.next_run ? new Date(job.next_run).toLocaleString('tr-TR') : '-'}
                  </p>
                </div>
                <Badge className={`text-[10px] ${job.status === 'active' ? 'bg-green-500/15 text-green-400' : 'bg-gray-500/15 text-gray-400'}`}>
                  {job.status === 'active' ? 'Aktif' : 'Durduruldu'}
                </Badge>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab Switch */}
      <div className="flex gap-2">
        <Button
          variant={activeTab === 'bots' ? 'default' : 'ghost'}
          className={activeTab === 'bots' ? 'bg-[#C4972A] text-white' : 'text-[#7e7e8a]'}
          onClick={() => setActiveTab('bots')}
          data-testid="tab-bots"
        >
          <Bot className="w-4 h-4 mr-1" /> Botlar
        </Button>
        <Button
          variant={activeTab === 'notifications' ? 'default' : 'ghost'}
          className={activeTab === 'notifications' ? 'bg-[#C4972A] text-white' : 'text-[#7e7e8a]'}
          onClick={() => setActiveTab('notifications')}
          data-testid="tab-notifications"
        >
          <MessageSquare className="w-4 h-4 mr-1" /> Grup Bildirimleri
        </Button>
        <Button
          variant={activeTab === 'logs' ? 'default' : 'ghost'}
          className={activeTab === 'logs' ? 'bg-[#C4972A] text-white' : 'text-[#7e7e8a]'}
          onClick={() => setActiveTab('logs')}
          data-testid="tab-logs"
        >
          <Clock className="w-4 h-4 mr-1" /> Islem Gecmisi
        </Button>
      </div>

      {/* Bots Tab */}
      {activeTab === 'bots' && (
        <>
          {/* Operational Bots Header */}
          <div>
            <h3 className="text-base font-semibold text-white mb-1">Operasyonel Bildirimler</h3>
            <p className="text-xs text-[#7e7e8a]">WhatsApp grubuna otomatik bildirim gonderir (mock modda DB'ye kaydeder)</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {BOTS.map(bot => {
              const Icon = bot.icon;
              const result = results[bot.id];
              const resultText = getResultText(bot.id, result);
              return (
                <div key={bot.id} className="glass rounded-xl p-5 space-y-3" data-testid={`bot-${bot.id}`}>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${bot.color}15` }}>
                      <Icon className="w-5 h-5" style={{ color: bot.color }} />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-sm font-semibold text-white">{bot.name}</h3>
                      <p className="text-xs text-[#7e7e8a]">{bot.desc}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className="bg-white/5 text-[#7e7e8a] text-[10px]">
                      <CalendarClock className="w-3 h-3 mr-1" /> {bot.schedule}
                    </Badge>
                  </div>
                  <Button onClick={() => runBot(bot.id)} disabled={running === bot.id}
                    className="w-full bg-[#C4972A]/15 hover:bg-[#C4972A]/25 text-[#C4972A] border border-[#C4972A]/20"
                    data-testid={`run-${bot.id}`}>
                    {running === bot.id ? (
                      <><Clock className="w-4 h-4 mr-2 animate-spin" /> Calisiyor...</>
                    ) : (
                      <><Play className="w-4 h-4 mr-2" /> Manuel Calistir</>
                    )}
                  </Button>
                  {resultText && (
                    <div className="bg-white/5 rounded-lg p-3 text-xs text-[#a9a9b2]">
                      {resultText}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Kitchen Forecast */}
          {forecast && (
            <div className="glass rounded-xl p-5" data-testid="kitchen-forecast">
              <h3 className="text-base font-semibold text-[#C4972A] mb-3 flex items-center gap-2">
                <UtensilsCrossed className="w-4 h-4" /> 7 Gunluk Mutfak Tahmini
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-[#7e7e8a] border-b border-white/5">
                      <th className="text-left py-2">Gun</th>
                      <th className="text-center py-2">Misafir</th>
                      <th className="text-center py-2">Masa Rez.</th>
                      <th className="text-center py-2">Kahvalti</th>
                      <th className="text-center py-2">Ogle</th>
                      <th className="text-center py-2">Aksam</th>
                      <th className="text-center py-2">Toplam</th>
                    </tr>
                  </thead>
                  <tbody>
                    {forecast.map((day, i) => (
                      <tr key={i} className="border-b border-white/3 text-[#e5e5e8]">
                        <td className="py-2"><span className="text-[#C4972A] font-medium">{day.day_name}</span> <span className="text-[#7e7e8a] text-xs">{day.date}</span></td>
                        <td className="text-center">{day.hotel_guests}</td>
                        <td className="text-center">{day.table_reservations}</td>
                        <td className="text-center text-amber-400">{day.breakfast}</td>
                        <td className="text-center">{day.lunch}</td>
                        <td className="text-center">{day.dinner}</td>
                        <td className="text-center font-bold text-[#C4972A]">{day.total_meals}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <div className="glass rounded-xl p-5" data-testid="group-notifications">
          <h3 className="text-base font-semibold text-[#C4972A] mb-3 flex items-center gap-2">
            <MessageSquare className="w-4 h-4" /> WhatsApp Grup Bildirimleri
          </h3>
          {notifications.length === 0 ? (
            <p className="text-[#7e7e8a] text-sm text-center py-8">Henuz bildirim yok. Botlari calistirarak bildirim olusturabilirsiniz.</p>
          ) : (
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {notifications.map((notif, i) => (
                <div key={i} className="bg-white/3 rounded-lg p-3" data-testid={`notification-${i}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-2 flex-1">
                      {getLogIcon(notif.type)}
                      <div className="flex-1">
                        <p className="text-sm text-white whitespace-pre-wrap">{notif.message}</p>
                        <div className="flex items-center gap-2 mt-1.5">
                          <Badge className="bg-[#C4972A]/10 text-[#C4972A] text-[10px]">{notif.type}</Badge>
                          <span className="text-[10px] text-[#5a5a65]">{notif.created_at?.slice(0, 16).replace('T', ' ')}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Logs Tab */}
      {activeTab === 'logs' && (
        <div className="glass rounded-xl p-5" data-testid="automation-logs">
          <h3 className="text-base font-semibold text-[#C4972A] mb-3 flex items-center gap-2">
            <Clock className="w-4 h-4" /> Son Islemler
          </h3>
          {logs.length === 0 ? (
            <p className="text-[#7e7e8a] text-sm text-center py-6">Henuz otomasyon islemi yok</p>
          ) : (
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {logs.map((log, i) => (
                <div key={i} className="flex items-center justify-between p-2.5 bg-white/3 rounded-lg text-sm">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    {getLogIcon(log.type)}
                    <span className="text-[#e5e5e8] truncate">{log.message || log.policy || log.type}</span>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {log.penalty_amount > 0 && <Badge className="bg-red-500/10 text-red-400 text-[10px]">{log.penalty_amount} TL</Badge>}
                    <span className="text-[10px] text-[#5a5a65]">{log.created_at?.slice(0, 16).replace('T', ' ')}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
