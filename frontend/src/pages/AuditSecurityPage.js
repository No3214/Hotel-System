import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, AlertTriangle, CheckCircle, Clock, FileText, Eye, Loader2, RefreshCw } from 'lucide-react';
import { getAuditLogs, getAuditStats, getSecurityAlerts, resolveSecurityAlert, runSecurityCheck } from '../api';

function fmt(n) { return n?.toLocaleString('tr-TR') ?? '0'; }

const ACTION_COLORS = {
  CREATE: 'text-emerald-400', UPDATE: 'text-[#C4972A]', DELETE: 'text-red-400',
  LOGIN: 'text-blue-400', LOGIN_FAILED: 'text-red-500', EXPORT: 'text-purple-400',
};
const SEVERITY_COLORS = {
  LOW: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  MEDIUM: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  HIGH: 'bg-red-500/10 text-red-400 border-red-500/20',
  CRITICAL: 'bg-red-600/20 text-red-500 border-red-600/30',
};

export default function AuditSecurityPage() {
  const [tab, setTab] = useState('logs');
  const [logs, setLogs] = useState(null);
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [checking, setChecking] = useState(false);

  useEffect(() => { loadAll(); }, []);
  useEffect(() => { if (tab === 'logs') loadLogs(); }, [page]);

  const loadAll = async () => {
    setLoading(true);
    try {
      await Promise.all([loadLogs(), loadStats(), loadAlerts()]);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const loadLogs = async () => {
    try {
      const res = await getAuditLogs({ page, limit: 30 });
      setLogs(res.data);
    } catch (e) { console.error(e); }
  };

  const loadStats = async () => {
    try {
      const res = await getAuditStats();
      setStats(res.data);
    } catch (e) { console.error(e); }
  };

  const loadAlerts = async () => {
    try {
      const res = await getSecurityAlerts({});
      setAlerts(res.data);
    } catch (e) { console.error(e); }
  };

  const handleResolve = async (id) => {
    await resolveSecurityAlert(id);
    await loadAlerts();
  };

  const handleSecurityCheck = async () => {
    setChecking(true);
    try {
      await runSecurityCheck();
      await loadAlerts();
    } catch (e) { console.error(e); }
    setChecking(false);
  };

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <Loader2 className="w-8 h-8 animate-spin text-[#C4972A]" />
    </div>
  );

  return (
    <div className="p-6 space-y-6" data-testid="audit-security-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Guvenlik & Denetim</h1>
          <p className="text-sm text-[#7e7e8a] mt-1">Audit loglar, guvenlik uyarilari ve aktivite takibi</p>
        </div>
        <button onClick={handleSecurityCheck} disabled={checking}
          className="flex items-center gap-2 px-4 py-2 bg-[#C4972A] text-black rounded-lg font-medium hover:bg-[#d4a73a] transition-colors disabled:opacity-50"
          data-testid="run-security-check-btn">
          <Shield className={`w-4 h-4 ${checking ? 'animate-pulse' : ''}`} />
          {checking ? 'Kontrol ediliyor...' : 'Guvenlik Kontrolu'}
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4" data-testid="audit-stats">
          <StatCard icon={FileText} title="Toplam Log" value={fmt(stats.total_logs)} />
          <StatCard icon={CheckCircle} title="Basari Orani" value={`%${stats.success_rate}`} color="text-emerald-400" />
          <StatCard icon={AlertTriangle} title="Basarisiz Islem" value={fmt(stats.failed_operations)} color="text-red-400" />
          <StatCard icon={Shield} title="Aktif Uyari" value={fmt(alerts?.alerts?.filter(a => !a.resolved)?.length || 0)} color="text-yellow-400" />
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-[#C4972A]/10 pb-2">
        {[
          { key: 'logs', label: 'Audit Loglar', icon: FileText },
          { key: 'alerts', label: 'Guvenlik Uyarilari', icon: AlertTriangle },
          { key: 'overview', label: 'Genel Bakis', icon: Eye },
        ].map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === t.key ? 'bg-[#C4972A]/15 text-[#C4972A]' : 'text-[#a9a9b2] hover:bg-white/5'
            }`}
            data-testid={`tab-${t.key}`}>
            <t.icon className="w-4 h-4" />{t.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === 'logs' && logs && (
        <div className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl overflow-hidden" data-testid="audit-logs-table">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#C4972A]/10">
                  <th className="px-4 py-3 text-left text-xs text-[#7e7e8a] font-medium">Zaman</th>
                  <th className="px-4 py-3 text-left text-xs text-[#7e7e8a] font-medium">Islem</th>
                  <th className="px-4 py-3 text-left text-xs text-[#7e7e8a] font-medium">Varlik</th>
                  <th className="px-4 py-3 text-left text-xs text-[#7e7e8a] font-medium">Kullanici</th>
                  <th className="px-4 py-3 text-left text-xs text-[#7e7e8a] font-medium">IP</th>
                  <th className="px-4 py-3 text-left text-xs text-[#7e7e8a] font-medium">Durum</th>
                </tr>
              </thead>
              <tbody>
                {(logs.logs || []).map(log => (
                  <tr key={log.id} className="border-b border-white/[0.03] hover:bg-white/[0.02]">
                    <td className="px-4 py-2.5 text-xs text-[#7e7e8a]">{log.timestamp ? new Date(log.timestamp).toLocaleString('tr-TR') : '-'}</td>
                    <td className="px-4 py-2.5"><span className={`text-xs font-medium ${ACTION_COLORS[log.action] || 'text-white'}`}>{log.action}</span></td>
                    <td className="px-4 py-2.5 text-xs text-white">{log.entity_type}{log.entity_id ? ` #${log.entity_id?.slice(0, 8)}` : ''}</td>
                    <td className="px-4 py-2.5 text-xs text-[#a9a9b2]">{log.user_email || log.user_id}</td>
                    <td className="px-4 py-2.5 text-xs text-[#7e7e8a]">{log.ip_address || '-'}</td>
                    <td className="px-4 py-2.5">
                      {log.success !== false
                        ? <span className="text-xs text-emerald-400">Basarili</span>
                        : <span className="text-xs text-red-400">Basarisiz</span>
                      }
                    </td>
                  </tr>
                ))}
                {(!logs.logs || logs.logs.length === 0) && (
                  <tr><td colSpan={6} className="px-4 py-8 text-center text-[#7e7e8a]">Henuz audit log bulunmuyor</td></tr>
                )}
              </tbody>
            </table>
          </div>
          {/* Pagination */}
          {logs.pages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-[#C4972A]/10">
              <span className="text-xs text-[#7e7e8a]">Sayfa {logs.page} / {logs.pages} (Toplam {logs.total})</span>
              <div className="flex gap-2">
                <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page <= 1}
                  className="px-3 py-1 text-xs bg-white/5 text-[#a9a9b2] rounded disabled:opacity-30">Onceki</button>
                <button onClick={() => setPage(Math.min(logs.pages, page + 1))} disabled={page >= logs.pages}
                  className="px-3 py-1 text-xs bg-white/5 text-[#a9a9b2] rounded disabled:opacity-30">Sonraki</button>
              </div>
            </div>
          )}
        </div>
      )}

      {tab === 'alerts' && alerts && (
        <div className="space-y-3" data-testid="security-alerts">
          {(alerts.alerts || []).length === 0 && (
            <div className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-8 text-center">
              <Shield className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
              <p className="text-white font-medium">Aktif guvenlik uyarisi yok</p>
              <p className="text-xs text-[#7e7e8a] mt-1">Sistem guvenli gorunuyor</p>
            </div>
          )}
          {(alerts.alerts || []).map(alert => (
            <motion.div key={alert.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className={`bg-[#12121a] border rounded-xl p-4 ${alert.resolved ? 'border-white/5 opacity-60' : 'border-[#C4972A]/20'}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <AlertTriangle className={`w-5 h-5 mt-0.5 ${alert.severity === 'HIGH' || alert.severity === 'CRITICAL' ? 'text-red-400' : 'text-yellow-400'}`} />
                  <div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded border ${SEVERITY_COLORS[alert.severity] || SEVERITY_COLORS.MEDIUM}`}>
                        {alert.severity}
                      </span>
                      <span className="text-xs text-[#7e7e8a]">{alert.alert_type || alert.type}</span>
                    </div>
                    <p className="text-sm text-white mt-1">{alert.message}</p>
                    <p className="text-xs text-[#7e7e8a] mt-1">{alert.timestamp ? new Date(alert.timestamp).toLocaleString('tr-TR') : ''}</p>
                  </div>
                </div>
                {!alert.resolved && (
                  <button onClick={() => handleResolve(alert.id)}
                    className="text-xs text-emerald-400 hover:text-emerald-300 px-3 py-1 bg-emerald-500/10 rounded-lg"
                    data-testid={`resolve-alert-${alert.id}`}>
                    Cozumle
                  </button>
                )}
                {alert.resolved && <span className="text-xs text-emerald-400">Cozumlendi</span>}
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {tab === 'overview' && stats && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6" data-testid="audit-overview">
          {/* Action Distribution */}
          <div className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-6">
            <h3 className="text-white font-semibold mb-4">Islem Dagilimi</h3>
            <div className="space-y-2">
              {Object.entries(stats.action_counts || {}).map(([action, count]) => {
                const total = Math.max(stats.total_logs, 1);
                const pct = Math.round(count / total * 100);
                return (
                  <div key={action} className="flex items-center gap-3">
                    <span className={`text-xs font-medium w-20 ${ACTION_COLORS[action] || 'text-white'}`}>{action}</span>
                    <div className="flex-1 bg-white/5 rounded-full h-2">
                      <div className="h-2 rounded-full bg-[#C4972A]/60" style={{ width: `${pct}%` }} />
                    </div>
                    <span className="text-xs text-[#7e7e8a] w-12 text-right">{count}</span>
                  </div>
                );
              })}
              {Object.keys(stats.action_counts || {}).length === 0 && (
                <p className="text-sm text-[#7e7e8a]">Henuz islem kaydedilmedi</p>
              )}
            </div>
          </div>

          {/* Entity Distribution */}
          <div className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-6">
            <h3 className="text-white font-semibold mb-4">Varlik Dagilimi</h3>
            <div className="space-y-2">
              {Object.entries(stats.entity_counts || {}).map(([entity, count]) => {
                const total = Math.max(stats.total_logs, 1);
                const pct = Math.round(count / total * 100);
                return (
                  <div key={entity} className="flex items-center gap-3">
                    <span className="text-xs font-medium text-white w-24 capitalize">{entity}</span>
                    <div className="flex-1 bg-white/5 rounded-full h-2">
                      <div className="h-2 rounded-full bg-emerald-500/60" style={{ width: `${pct}%` }} />
                    </div>
                    <span className="text-xs text-[#7e7e8a] w-12 text-right">{count}</span>
                  </div>
                );
              })}
              {Object.keys(stats.entity_counts || {}).length === 0 && (
                <p className="text-sm text-[#7e7e8a]">Henuz varlik kaydedilmedi</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ icon: Icon, title, value, color }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      className="bg-[#12121a] border border-[#C4972A]/10 rounded-xl p-4">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-[#C4972A]/10 rounded-lg"><Icon className={`w-5 h-5 ${color || 'text-[#C4972A]'}`} /></div>
        <div>
          <p className="text-xs text-[#7e7e8a]">{title}</p>
          <p className={`text-lg font-bold ${color || 'text-white'}`}>{value}</p>
        </div>
      </div>
    </motion.div>
  );
}
