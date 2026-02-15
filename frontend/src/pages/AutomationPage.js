import React, { useState, useEffect } from 'react';
import { runPaymentReminder, runCancellationCheck, getKitchenForecast, getAutomationLogs, getAutomationSummary } from '../api';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Bot, CreditCard, XCircle, UtensilsCrossed, Play, Clock, AlertTriangle, TrendingUp } from 'lucide-react';

const BOTS = [
  { id: 'payment', name: 'Odeme Hatirlatma', desc: 'Cumartesi check-in: on odeme kontrolu', icon: CreditCard, color: 'amber' },
  { id: 'cancellation', name: 'Iptal Denetcisi', desc: 'Iptal ceza hesaplama otomasyonu', icon: XCircle, color: 'red' },
  { id: 'kitchen', name: 'Mutfak Tahmini', desc: '7 gunluk yemek planlama', icon: UtensilsCrossed, color: 'green' },
];

export default function AutomationPage() {
  const [summary, setSummary] = useState(null);
  const [logs, setLogs] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [running, setRunning] = useState(null);
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getAutomationSummary().then(r => setSummary(r.data)),
      getAutomationLogs({ limit: 20 }).then(r => setLogs(r.data.logs)),
    ]).finally(() => setLoading(false));
  }, []);

  const runBot = async (botId) => {
    setRunning(botId);
    try {
      let res;
      if (botId === 'payment') {
        res = await runPaymentReminder();
      } else if (botId === 'cancellation') {
        res = await runCancellationCheck();
      } else if (botId === 'kitchen') {
        res = await getKitchenForecast(7);
        setForecast(res.data.forecast);
      }
      setResults(prev => ({ ...prev, [botId]: res.data }));
      // Refresh logs
      getAutomationLogs({ limit: 20 }).then(r => setLogs(r.data.logs));
      getAutomationSummary().then(r => setSummary(r.data));
    } catch (err) {
      console.error(err);
    }
    setRunning(null);
  };

  if (loading) return <div className="p-8"><div className="h-8 w-64 bg-white/5 rounded animate-pulse" /></div>;

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="automation-page">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]" data-testid="automation-title">Otomasyon</h1>
        <p className="text-[#7e7e8a] text-sm mt-1">Otomatik islemler ve akilli botlar</p>
      </div>

      {/* Summary */}
      {summary && (
        <div className="grid grid-cols-3 gap-3" data-testid="automation-summary">
          <div className="glass rounded-xl p-4 flex items-center gap-3">
            <Bot className="w-5 h-5 text-[#C4972A]" />
            <div><p className="text-xs text-[#7e7e8a]">Toplam Islem</p><p className="text-xl font-bold text-white">{summary.total_logs}</p></div>
          </div>
          <div className="glass rounded-xl p-4 flex items-center gap-3">
            <CreditCard className="w-5 h-5 text-amber-400" />
            <div><p className="text-xs text-[#7e7e8a]">Odeme Hatirlatma</p><p className="text-xl font-bold text-white">{summary.payment_reminders}</p></div>
          </div>
          <div className="glass rounded-xl p-4 flex items-center gap-3">
            <XCircle className="w-5 h-5 text-red-400" />
            <div><p className="text-xs text-[#7e7e8a]">Iptal Denetimi</p><p className="text-xl font-bold text-white">{summary.cancellation_checks}</p></div>
          </div>
        </div>
      )}

      {/* Bots */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {BOTS.map(bot => {
          const Icon = bot.icon;
          const result = results[bot.id];
          return (
            <div key={bot.id} className="glass rounded-xl p-5 space-y-3" data-testid={`bot-${bot.id}`}>
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg bg-${bot.color}-500/10 flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 text-${bot.color}-400`} />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">{bot.name}</h3>
                  <p className="text-xs text-[#7e7e8a]">{bot.desc}</p>
                </div>
              </div>
              <Button onClick={() => runBot(bot.id)} disabled={running === bot.id}
                className="w-full bg-[#C4972A]/15 hover:bg-[#C4972A]/25 text-[#C4972A] border border-[#C4972A]/20" data-testid={`run-${bot.id}`}>
                {running === bot.id ? (
                  <><Clock className="w-4 h-4 mr-2 animate-spin" /> Calisiyor...</>
                ) : (
                  <><Play className="w-4 h-4 mr-2" /> Calistir</>
                )}
              </Button>
              {result && (
                <div className="bg-white/5 rounded-lg p-3 text-xs space-y-1">
                  {bot.id === 'payment' && <p className="text-amber-400">{result.reminders_created} hatirlatma olusturuldu</p>}
                  {bot.id === 'cancellation' && <p className="text-red-400">{result.processed} iptal islendi</p>}
                  {bot.id === 'kitchen' && <p className="text-green-400">{result.forecast_days} gunluk tahmin hazir</p>}
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

      {/* Recent Logs */}
      <div className="glass rounded-xl p-5">
        <h3 className="text-base font-semibold text-[#C4972A] mb-3 flex items-center gap-2">
          <Clock className="w-4 h-4" /> Son Islemler
        </h3>
        {logs.length === 0 ? (
          <p className="text-[#7e7e8a] text-sm text-center py-6">Henuz otomasyon islemi yok</p>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {logs.map((log, i) => (
              <div key={i} className="flex items-center justify-between p-2.5 bg-white/3 rounded-lg text-sm">
                <div className="flex items-center gap-2">
                  {log.type === 'payment_reminder' && <CreditCard className="w-3.5 h-3.5 text-amber-400" />}
                  {log.type === 'cancellation_penalty' && <XCircle className="w-3.5 h-3.5 text-red-400" />}
                  <span className="text-[#e5e5e8]">{log.message || log.policy || log.type}</span>
                </div>
                <div className="flex items-center gap-2">
                  {log.penalty_amount > 0 && <Badge className="bg-red-500/10 text-red-400 text-[10px]">{log.penalty_amount} TL</Badge>}
                  <span className="text-[10px] text-[#5a5a65]">{log.created_at?.slice(0, 16).replace('T', ' ')}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
