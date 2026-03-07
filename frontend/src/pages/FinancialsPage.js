import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { DollarSign, TrendingUp, TrendingDown, Plus, Trash2, ChevronLeft, ChevronRight, PieChart, BarChart3, ArrowUpRight, ArrowDownRight, Sparkles, Loader2, AlertTriangle, CheckCircle, ShieldAlert, Zap, Award, LineChart, Lightbulb } from 'lucide-react';
import { getFinancialCategories, addIncome, addExpense, getIncomeList, getExpenseList, deleteFinancialRecord, getDailySummary, getMonthlySummary, getFinancialAudit, getFinancialForecast, getVendorROIAnalysis } from '../api';

const TABS = [
  { key: 'overview', label: 'Genel Bakis' },
  { key: 'income', label: 'Gelir' },
  { key: 'expense', label: 'Gider' },
];

function formatMoney(val) {
  return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY', minimumFractionDigits: 0 }).format(val || 0);
}

export default function FinancialsPage() {
  const [tab, setTab] = useState('overview');
  const [categories, setCategories] = useState({ income_categories: [], expense_categories: [] });
  const [monthly, setMonthly] = useState(null);
  const [daily, setDaily] = useState(null);
  const [incomeRecords, setIncomeRecords] = useState([]);
  const [expenseRecords, setExpenseRecords] = useState([]);
  const [showForm, setShowForm] = useState(null); // 'income' | 'expense' | null
  const [formData, setFormData] = useState({ date: new Date().toISOString().split('T')[0], category: '', description: '', amount: '', source: 'direct', commission_rate: 0, vendor: '' });
  const [loading, setLoading] = useState(true);

  // Phase 9: AI Audit
  const [aiAudit, setAiAudit] = useState(null);
  const [auditLoading, setAuditLoading] = useState(false);

  // Phase 16: AI Forecast
  const [aiForecast, setAiForecast] = useState(null);
  const [forecastLoading, setForecastLoading] = useState(false);

  // Phase 23: AI Vendor ROI
  const [vendorRoi, setVendorRoi] = useState(null);
  const [vendorRoiLoading, setVendorRoiLoading] = useState(false);

  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [selectedDay, setSelectedDay] = useState(now.toISOString().split('T')[0]);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [catRes, monthRes, dayRes] = await Promise.all([
        getFinancialCategories(),
        getMonthlySummary(year, month),
        getDailySummary(selectedDay),
      ]);
      setCategories(catRes.data);
      setMonthly(monthRes.data);
      setDaily(dayRes.data);
    } catch (e) { console.error(e); }

    try {
      const [incRes, expRes] = await Promise.all([
        getIncomeList({ date_from: `${year}-${String(month).padStart(2,'0')}-01`, date_to: `${year}-${String(month).padStart(2,'0')}-31` }),
        getExpenseList({ date_from: `${year}-${String(month).padStart(2,'0')}-01`, date_to: `${year}-${String(month).padStart(2,'0')}-31` }),
      ]);
      setIncomeRecords(incRes.data.records || []);
      setExpenseRecords(expRes.data.records || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [year, month, selectedDay]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleSubmit = async (type) => {
    try {
      if (type === 'income') {
        await addIncome({ ...formData, amount: parseFloat(formData.amount), commission_rate: parseFloat(formData.commission_rate || 0) });
      } else {
        await addExpense({ ...formData, amount: parseFloat(formData.amount) });
      }
      setShowForm(null);
      setFormData({ date: selectedDay, category: '', description: '', amount: '', source: 'direct', commission_rate: 0, vendor: '' });
      loadData();
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id) => {
    try { await deleteFinancialRecord(id); loadData(); } catch (e) { console.error(e); }
  };

  const changeMonth = (delta) => {
    let m = month + delta;
    let y = year;
    if (m > 12) { m = 1; y++; }
    if (m < 1) { m = 12; y--; }
    setMonth(m); setYear(y);
    setSelectedDay(`${y}-${String(m).padStart(2,'0')}-01`);
  };

  const MONTHS_TR = ['Ocak','Subat','Mart','Nisan','Mayis','Haziran','Temmuz','Agustos','Eylul','Ekim','Kasim','Aralik'];

  const profit = (monthly?.profit || 0);
  const profitColor = profit >= 0 ? 'text-emerald-400' : 'text-red-400';

  // Compute max bar for daily trend chart
  const maxTrend = Math.max(...(monthly?.daily_trend || []).map(d => Math.max(d.income, d.expense)), 1);

  return (
    <div className="p-6 space-y-6" data-testid="financials-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Gelir / Gider Takibi</h1>
          <p className="text-sm text-[#a9a9b2]">Finansal raporlar ve KPI'lar</p>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={async () => {
              setForecastLoading(true);
              try {
                const res = await getFinancialForecast();
                if (res.data?.success) setAiForecast(res.data.forecast);
              } catch(e) { console.error(e); alert('Tahmin calistirilamadi.'); }
              setForecastLoading(false);
            }} 
            disabled={forecastLoading}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium transition-all text-sm mr-2 shadow-[0_0_15px_rgba(79,70,229,0.3)]"
          >
            {forecastLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <LineChart className="w-4 h-4" />}
            AI Gelecek Ay Tahmini
          </button>

          <button 
            onClick={async () => {
              setVendorRoiLoading(true);
              try {
                const res = await getVendorROIAnalysis(6);
                if (res.data?.success) setVendorRoi(res.data.report);
                else {
                  alert(res.data?.message || 'Yeterli veri bulunamadi.');
                  setVendorRoi(null);
                }
              } catch(e) { console.error(e); alert('Tedarikci Analizi calistirilamadi.'); }
              setVendorRoiLoading(false);
            }} 
            disabled={vendorRoiLoading}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-medium transition-all text-sm mr-2 shadow-[0_0_15px_rgba(147,51,234,0.3)]"
          >
            {vendorRoiLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <TrendingDown className="w-4 h-4" />}
            AI TedarikCFO Raporu
          </button>

          <button 
            onClick={async () => {
              setAuditLoading(true);
              try {
                const res = await getFinancialAudit(year, month);
                if (res.data?.success) setAiAudit(res.data.audit);
              } catch(e) { console.error(e); alert('Denetim calistirilamadi.'); }
              setAuditLoading(false);
            }} 
            disabled={auditLoading}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium transition-all text-sm mr-4"
          >
            {auditLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            Gemini CFO Denetimi
          </button>
          
          <button onClick={() => changeMonth(-1)} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-white" data-testid="prev-month-btn"><ChevronLeft className="w-4 h-4" /></button>
          <span className="text-white font-medium min-w-[140px] text-center">{MONTHS_TR[month-1]} {year}</span>
          <button onClick={() => changeMonth(1)} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-white" data-testid="next-month-btn"><ChevronRight className="w-4 h-4" /></button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-white/5 p-1 rounded-lg w-fit" data-testid="financials-tabs">
        {TABS.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)} data-testid={`tab-${t.key}`}
            className={`px-4 py-1.5 rounded-md text-sm transition-all ${tab === t.key ? 'bg-[#C4972A] text-[#0a0a0f] font-medium' : 'text-[#a9a9b2] hover:text-white'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-20"><div className="w-8 h-8 border-2 border-[#C4972A] border-t-transparent rounded-full animate-spin" /></div>
      ) : (
        <>
          {/* OVERVIEW TAB */}
          {tab === 'overview' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              {/* KPI Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <KPICard icon={<ArrowUpRight className="w-5 h-5 text-emerald-400" />} label="Toplam Gelir (Net)" value={formatMoney(monthly?.income?.net)} sub={`Brut: ${formatMoney(monthly?.income?.gross)}`} color="emerald" testId="total-income" />
                <KPICard icon={<ArrowDownRight className="w-5 h-5 text-red-400" />} label="Toplam Gider" value={formatMoney(monthly?.expense?.total)} sub={`${monthly?.expense?.count || 0} kayit`} color="red" testId="total-expense" />
                <KPICard icon={<TrendingUp className="w-5 h-5 text-[#C4972A]" />} label="Kar / Zarar" value={formatMoney(profit)} sub={`Kar Marji: %${monthly?.profit_margin || 0}`} color={profit >= 0 ? 'emerald' : 'red'} testId="profit" />
                <KPICard icon={<PieChart className="w-5 h-5 text-blue-400" />} label="Doluluk Orani" value={`%${monthly?.kpis?.occupancy_rate || 0}`} sub={`ADR: ${formatMoney(monthly?.kpis?.adr)}`} color="blue" testId="occupancy" />
              </div>

              {/* Daily Trend Mini Chart */}
              <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                <h3 className="text-white font-medium mb-3 flex items-center gap-2"><BarChart3 className="w-4 h-4 text-[#C4972A]" /> Gunluk Trend</h3>
                <div className="flex items-end gap-[2px] h-32" data-testid="daily-trend-chart">
                  {(monthly?.daily_trend || []).map((d, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center gap-[1px]" title={`${d.date}\nGelir: ${formatMoney(d.income)}\nGider: ${formatMoney(d.expense)}`}>
                      <div className="w-full bg-emerald-500/60 rounded-t-sm" style={{ height: `${(d.income / maxTrend) * 100}%`, minHeight: d.income > 0 ? 2 : 0 }} />
                      <div className="w-full bg-red-400/60 rounded-b-sm" style={{ height: `${(d.expense / maxTrend) * 100}%`, minHeight: d.expense > 0 ? 2 : 0 }} />
                    </div>
                  ))}
                </div>
                <div className="flex justify-between mt-1 text-[10px] text-[#a9a9b2]">
                  <span>1</span><span>{Math.ceil((monthly?.daily_trend || []).length / 2)}</span><span>{(monthly?.daily_trend || []).length}</span>
                </div>
                <div className="flex gap-4 mt-2 text-xs text-[#a9a9b2]">
                  <span className="flex items-center gap-1"><span className="w-3 h-2 bg-emerald-500/60 rounded-sm" /> Gelir</span>
                  <span className="flex items-center gap-1"><span className="w-3 h-2 bg-red-400/60 rounded-sm" /> Gider</span>
                </div>
              </div>

              {/* Category Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <CategoryBreakdown title="Gelir Kategorileri" data={monthly?.income?.by_category || {}} color="emerald" categories={categories.income_categories} />
                <CategoryBreakdown title="Gider Kategorileri" data={monthly?.expense?.by_category || {}} color="red" categories={categories.expense_categories} />
              </div>

              {/* Commission / Source Breakdown */}
              {monthly?.income?.by_source && Object.keys(monthly.income.by_source).length > 0 && (
                <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                  <h3 className="text-white font-medium mb-3">Kanal Bazli Gelir</h3>
                  <div className="space-y-2">
                    {Object.entries(monthly.income.by_source).map(([src, data]) => (
                      <div key={src} className="flex items-center justify-between p-2 bg-white/5 rounded-lg">
                        <span className="text-white capitalize text-sm">{src}</span>
                        <div className="flex gap-4 text-xs">
                          <span className="text-[#a9a9b2]">Brut: {formatMoney(data.gross)}</span>
                          <span className="text-red-400">Komisyon: {formatMoney(data.commission)}</span>
                          <span className="text-emerald-400 font-medium">Net: {formatMoney(data.net)}</span>
                          <span className="text-[#a9a9b2]">{data.count} islem</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Phase 16: AI Forecast Panel */}
              {aiForecast && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-indigo-950/20 border border-indigo-500/30 rounded-xl p-6 relative overflow-hidden mt-6">
                  <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
                  <div className="flex justify-between items-start mb-6 relative z-10">
                    <div>
                      <h3 className="font-bold text-xl text-indigo-400 flex items-center gap-2">
                        <LineChart className="w-6 h-6" /> AI Finansal Öngörü & Projeksiyon
                      </h3>
                      <p className="text-indigo-300 text-sm mt-1">Gelecek ay için beklenen nakit akışı ve öneriler</p>
                    </div>
                    <button onClick={() => setAiForecast(null)} className="text-[#a9a9b2] hover:text-white px-3 py-1 bg-white/5 rounded-lg text-sm">Paneli Kapat</button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative z-10 mb-6">
                     <div className="bg-[#12121a] border border-white/5 rounded-xl p-4 text-center">
                        <div className="text-xs text-[#a9a9b2] mb-1">Tahmini Gelir</div>
                        <div className="text-xl font-bold text-emerald-400">{formatMoney(aiForecast.projected_revenue_try)}</div>
                     </div>
                     <div className="bg-[#12121a] border border-white/5 rounded-xl p-4 text-center">
                        <div className="text-xs text-[#a9a9b2] mb-1">Tahmini Gider</div>
                        <div className="text-xl font-bold text-red-400">{formatMoney(aiForecast.projected_expense_try)}</div>
                     </div>
                     <div className="bg-[#12121a] border border-white/5 rounded-xl p-4 text-center">
                        <div className="text-xs text-[#a9a9b2] mb-1">Beklenen Net Kâr</div>
                        <div className="text-xl font-bold text-[#C4972A]">{formatMoney(aiForecast.projected_profit_try)}</div>
                     </div>
                     <div className="bg-[#12121a] border border-white/5 rounded-xl p-4 text-center">
                        <div className="text-xs text-[#a9a9b2] mb-1">Beklenen Doluluk</div>
                        <div className="text-xl font-bold text-blue-400">%{aiForecast.expected_occupancy_percent}</div>
                     </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative z-10">
                    <div className="bg-[#0a0a0f] p-4 rounded-xl border border-white/5">
                       <h4 className="flex items-center gap-2 font-medium text-white mb-3 text-sm">
                          <BarChart3 className="w-4 h-4 text-indigo-400" /> Tahmin Notları & Gerekçeler
                       </h4>
                       <ul className="space-y-2">
                          {aiForecast.forecast_notes?.map((note, idx) => (
                             <li key={idx} className="text-xs text-[#c8c8d0] flex items-start gap-2">
                                <span className="text-indigo-400 mt-0.5">•</span> {note}
                             </li>
                          ))}
                       </ul>
                    </div>
                    <div className="bg-[#0a0a0f] p-4 rounded-xl border border-white/5">
                       <h4 className="flex items-center gap-2 font-medium text-white mb-3 text-sm">
                          <Lightbulb className="w-4 h-4 text-amber-400" /> Yönetim Tavsiyeleri
                       </h4>
                       <ul className="space-y-2">
                          {aiForecast.actionable_advice?.map((adv, idx) => (
                             <li key={idx} className="text-xs text-[#c8c8d0] flex items-start gap-2">
                                <span className="text-amber-400 mt-0.5">•</span> {adv}
                             </li>
                          ))}
                       </ul>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Phase 23: AI Vendor ROI Detailed Panel */}
              {vendorRoi && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-purple-950/20 border border-purple-500/30 rounded-xl p-6 relative overflow-hidden mt-6">
                  <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
                  <div className="flex justify-between items-start mb-6 relative z-10">
                    <div>
                      <h3 className="font-bold text-xl text-purple-400 flex items-center gap-2">
                        <TrendingDown className="w-6 h-6" /> Yapay Zeka Satin Alma & Tedarikci Analizi (ROI)
                      </h3>
                      <p className="text-purple-300 text-sm mt-1">Son 6 Aylik Verilere Dayali Tasarruf Odakli CFO Raporu</p>
                    </div>
                    <div className="flex items-center gap-4">
                      {vendorRoi.procurement_health_score !== undefined && (
                        <div className="flex items-center gap-2 bg-purple-500/10 px-3 py-1.5 rounded-lg border border-purple-500/20">
                          <Award className="w-5 h-5 text-purple-400" />
                          <span className="text-purple-400 font-bold">Saglik: {vendorRoi.procurement_health_score}/100</span>
                        </div>
                      )}
                      <button onClick={() => setVendorRoi(null)} className="text-[#a9a9b2] hover:text-white px-3 py-1 bg-white/5 rounded-lg text-sm">Paneli Kapat</button>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 relative z-10 mb-6">
                    {/* Red Flags */}
                    <div className="bg-[#0a0a0f] rounded-xl p-5 border border-white/5">
                      <h4 className="flex items-center gap-2 font-medium text-white mb-4">
                        <AlertTriangle className="w-5 h-5 text-red-500" /> Kirmizi Bayraklar & Fiyat Sismeleri
                      </h4>
                      {vendorRoi.red_flags?.length > 0 ? (
                          <div className="space-y-3">
                            {vendorRoi.red_flags.map((f, i) => (
                              <div key={i} className="p-3 rounded-lg border bg-red-500/10 border-red-500/20 flex gap-3">
                                <AlertTriangle className="w-5 h-5 flex-shrink-0 text-red-400" />
                                <div>
                                  <h5 className="text-sm font-semibold mb-1 text-red-300">{f.vendor}</h5>
                                  <p className="text-[#e5e5e8] text-sm">{f.issue}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                      ) : (
                          <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-lg flex items-center gap-3 text-emerald-400">
                            <CheckCircle className="w-5 h-5" />
                            Aciklanamayan fiyat artisi tespit edilmedi.
                          </div>
                      )}
                    </div>
                    
                    {/* Savings Opportunities */}
                    <div className="bg-[#0a0a0f] rounded-xl p-5 border border-white/5">
                      <h4 className="flex items-center gap-2 font-medium text-white mb-4">
                        <TrendingDown className="w-5 h-5 text-emerald-400" /> Tasarruf Firsatlari
                      </h4>
                      {vendorRoi.savings_opportunities?.length > 0 ? (
                        <div className="space-y-4">
                          {vendorRoi.savings_opportunities.map((s, i) => (
                            <div key={i} className="bg-emerald-500/5 border border-emerald-500/20 rounded-lg p-4">
                              <div className="flex justify-between items-start mb-2">
                                <h5 className="font-medium text-emerald-400">{s.opportunity}</h5>
                                <span className="text-xs bg-emerald-500/20 text-emerald-300 px-2 py-1 rounded-full font-bold">
                                  {formatMoney(s.estimated_monthly_saving_try)} / Ay
                                </span>
                              </div>
                              <p className="text-sm text-[#e5e5e8] leading-relaxed">{s.action}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-[#a9a9b2]">Su an icin belirgin bir tasarruf firsati bulunamadi.</p>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 relative z-10">
                    <div className="bg-[#0a0a0f] rounded-xl p-5 border border-purple-500/30">
                      <h4 className="flex items-center gap-2 font-medium text-purple-400 mb-4 border-b border-purple-500/20 pb-3">
                        Genel CFO Satin Alma Ozeti
                      </h4>
                      <p className="text-sm text-[#e5e5e8] leading-relaxed whitespace-pre-line">{vendorRoi.summary_message}</p>
                    </div>

                    <div className="bg-[#0a0a0f] rounded-xl p-5 border border-white/5">
                      <h4 className="flex items-center gap-2 font-medium text-white mb-4">
                        <Lightbulb className="w-5 h-5 text-amber-400" /> En Cok Harcama Yapilan Tedarikciler
                      </h4>
                      <div className="space-y-3">
                        {vendorRoi.vendor_insights?.map((v, i) => (
                          <div key={i} className="p-3 bg-white/5 border border-white/10 rounded-lg">
                            <div className="flex justify-between items-center mb-1">
                              <span className="font-semibold text-white">{v.vendor}</span>
                              <span className={`text-[10px] uppercase font-bold px-2 py-1 rounded ${
                                v.status === 'renegotiate' ? 'bg-orange-500/20 text-orange-400' : 
                                v.status === 'replace' ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'
                              }`}>{v.status}</span>
                            </div>
                            <p className="text-xs text-[#a9a9b2]">{v.note}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
              
              {/* Phase 9: AI Audit Detailed Panel */}
              {aiAudit && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-emerald-950/20 border border-emerald-500/30 rounded-xl p-6 relative overflow-hidden mt-6">
                  <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
                  <div className="flex justify-between items-start mb-6 relative z-10">
                    <div>
                      <h3 className="font-bold text-xl text-emerald-400 flex items-center gap-2">
                        <ShieldAlert className="w-6 h-6" /> CFO Düzeyinde Yapay Zeka Denetim Raporu
                      </h3>
                      <p className="text-emerald-500/80 text-sm mt-1">{year}-{month} Donemi Icin Finansal Analiz ve Anomaliler</p>
                    </div>
                    <div className="flex items-center gap-4">
                      {aiAudit.financial_score && (
                        <div className="flex items-center gap-2 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/20">
                          <Award className="w-5 h-5 text-emerald-400" />
                          <span className="text-emerald-400 font-bold">Skor: {aiAudit.financial_score}/100</span>
                        </div>
                      )}
                      <button onClick={() => setAiAudit(null)} className="text-[#a9a9b2] hover:text-white px-3 py-1 bg-white/5 rounded-lg text-sm">Raporu Kapat</button>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 relative z-10">
                    <div className="lg:col-span-2 space-y-6">
                      {/* Anomalies */}
                      <div className="bg-[#0a0a0f] rounded-xl p-5 border border-white/5">
                        <h4 className="flex items-center gap-2 font-medium text-white mb-4">
                          <AlertTriangle className="w-5 h-5 text-red-400" /> Tespit Edilen Anomaliler & Riskler
                        </h4>
                        {aiAudit.anomalies?.length > 0 ? (
                           <div className="space-y-3">
                             {aiAudit.anomalies.map((a, i) => (
                               <div key={i} className={`p-3 rounded-lg border flex gap-3 ${a.severity === 'high' ? 'bg-red-500/10 border-red-500/20' : 'bg-orange-500/10 border-orange-500/20'}`}>
                                  <AlertTriangle className={`w-5 h-5 flex-shrink-0 ${a.severity === 'high' ? 'text-red-400' : 'text-orange-400'}`} />
                                  <div>
                                    <h5 className={`text-sm font-semibold mb-1 ${a.severity === 'high' ? 'text-red-300' : 'text-orange-300'}`}>{a.type}</h5>
                                    <p className="text-[#e5e5e8] text-sm">{a.description}</p>
                                  </div>
                               </div>
                             ))}
                           </div>
                        ) : (
                           <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-lg flex items-center gap-3 text-emerald-400">
                             <CheckCircle className="w-5 h-5" />
                             Bu donemde supheli bir finansal islem (anomali) tespit edilmedi.
                           </div>
                        )}
                      </div>
                      
                      {/* Savings & ROI */}
                      <div className="bg-[#0a0a0f] rounded-xl p-5 border border-white/5">
                        <h4 className="flex items-center gap-2 font-medium text-white mb-4">
                          <TrendingUp className="w-5 h-5 text-[#C4972A]" /> Tedarikci ROI & Tasarruf Tavsiyeleri
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                          {aiAudit.savings_recommendations?.map((r, i) => (
                             <div key={i} className="bg-white/5 border border-white/10 rounded-lg p-4">
                               <h5 className="font-medium text-[#C4972A] mb-2">{r.title}</h5>
                               <p className="text-sm text-[#e5e5e8] leading-relaxed mb-3">{r.detail}</p>
                               <span className="text-xs px-2 py-1 bg-white/10 rounded text-[#a9a9b2]">Etki: {r.impact?.toUpperCase()}</span>
                             </div>
                          ))}
                        </div>
                        
                        {aiAudit.revenue_insights && aiAudit.revenue_insights.length > 0 && (
                           <>
                              <h4 className="flex items-center gap-2 font-medium text-white mb-4 pt-4 border-t border-white/5">
                                <Zap className="w-5 h-5 text-blue-400" /> Gelir Artirma Stratejileri
                              </h4>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {aiAudit.revenue_insights.map((r, i) => (
                                   <div key={i} className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-4">
                                     <h5 className="font-medium text-blue-400 mb-2">{r.title}</h5>
                                     <p className="text-sm text-[#e5e5e8] leading-relaxed mb-3">{r.detail}</p>
                                   </div>
                                ))}
                              </div>
                           </>
                        )}
                      </div>
                    </div>
                    
                    {/* General Summary Sidebar */}
                    <div className="bg-[#0a0a0f] rounded-xl p-5 border border-emerald-500/30 shadow-[0_0_30px_rgba(16,185,129,0.05)]">
                       <h4 className="flex items-center gap-2 font-medium text-emerald-400 mb-4 border-b border-emerald-500/20 pb-3">
                         Yapay Zeka CFO Ozeti
                       </h4>
                       <p className="text-sm text-[#e5e5e8] leading-relaxed whitespace-pre-line">{aiAudit.summary}</p>
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}

          {/* INCOME / EXPENSE TABS */}
          {(tab === 'income' || tab === 'expense') && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="text-white font-medium">{tab === 'income' ? 'Gelir Kayitlari' : 'Gider Kayitlari'}</h2>
                <button onClick={() => { setShowForm(tab); setFormData(p => ({ ...p, date: selectedDay, category: '' })); }}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-[#C4972A] text-[#0a0a0f] rounded-lg text-sm font-medium hover:bg-[#d4a73a] transition-all"
                  data-testid={`add-${tab}-btn`}>
                  <Plus className="w-4 h-4" /> {tab === 'income' ? 'Gelir Ekle' : 'Gider Ekle'}
                </button>
              </div>

              {/* Form Modal */}
              {showForm && (
                <div className="bg-white/5 rounded-xl p-4 border border-[#C4972A]/30 space-y-3" data-testid="financial-form">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <input type="date" value={formData.date} onChange={e => setFormData(p => ({...p, date: e.target.value}))}
                      className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm" data-testid="form-date" />
                    <select value={formData.category} onChange={e => setFormData(p => ({...p, category: e.target.value}))}
                      className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm" data-testid="form-category">
                      <option value="">Kategori Sec</option>
                      {(showForm === 'income' ? categories.income_categories : categories.expense_categories).map(c => (
                        <option key={c.key} value={c.key}>{c.label}</option>
                      ))}
                    </select>
                    <input type="number" placeholder="Tutar (TL)" value={formData.amount} onChange={e => setFormData(p => ({...p, amount: e.target.value}))}
                      className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm" data-testid="form-amount" />
                    <input type="text" placeholder="Aciklama" value={formData.description} onChange={e => setFormData(p => ({...p, description: e.target.value}))}
                      className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm" data-testid="form-description" />
                  </div>
                  {showForm === 'income' && (
                    <div className="grid grid-cols-2 gap-3">
                      <select value={formData.source} onChange={e => setFormData(p => ({...p, source: e.target.value}))}
                        className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm" data-testid="form-source">
                        <option value="direct">Direkt</option>
                        <option value="booking">Booking.com</option>
                        <option value="expedia">Expedia</option>
                        <option value="airbnb">Airbnb</option>
                        <option value="google">Google Hotel</option>
                        <option value="other">Diger</option>
                      </select>
                      <input type="number" placeholder="Komisyon %" value={formData.commission_rate} onChange={e => setFormData(p => ({...p, commission_rate: e.target.value}))}
                        className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm" data-testid="form-commission" />
                    </div>
                  )}
                  {showForm === 'expense' && (
                    <input type="text" placeholder="Tedarikci" value={formData.vendor} onChange={e => setFormData(p => ({...p, vendor: e.target.value}))}
                      className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm w-full" data-testid="form-vendor" />
                  )}
                  <div className="flex gap-2">
                    <button onClick={() => handleSubmit(showForm)} data-testid="form-submit"
                      className="px-4 py-2 bg-[#C4972A] text-[#0a0a0f] rounded-lg text-sm font-medium hover:bg-[#d4a73a]">Kaydet</button>
                    <button onClick={() => setShowForm(null)} className="px-4 py-2 bg-white/5 text-[#a9a9b2] rounded-lg text-sm hover:bg-white/10">Iptal</button>
                  </div>
                </div>
              )}

              {/* Records List */}
              <div className="space-y-2" data-testid={`${tab}-list`}>
                {(tab === 'income' ? incomeRecords : expenseRecords).map(rec => (
                  <div key={rec.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/5 hover:border-white/10 transition-all">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${tab === 'income' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-400/20 text-red-400'}`}>
                          {rec.category}
                        </span>
                        <span className="text-white text-sm">{rec.description || '-'}</span>
                        {rec.source && rec.source !== 'direct' && (
                          <span className="text-xs text-blue-400 bg-blue-400/10 px-1.5 py-0.5 rounded">{rec.source}</span>
                        )}
                      </div>
                      <span className="text-xs text-[#a9a9b2]">{rec.date}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <span className={`font-medium text-sm ${tab === 'income' ? 'text-emerald-400' : 'text-red-400'}`}>
                          {formatMoney(rec.amount)}
                        </span>
                        {rec.commission_amount > 0 && (
                          <div className="text-xs text-[#a9a9b2]">Net: {formatMoney(rec.net_amount)}</div>
                        )}
                      </div>
                      <button onClick={() => handleDelete(rec.id)} className="p-1.5 rounded-lg hover:bg-red-400/10 text-red-400/60 hover:text-red-400 transition-all" data-testid={`delete-${rec.id}`}>
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
                {(tab === 'income' ? incomeRecords : expenseRecords).length === 0 && (
                  <div className="text-center py-8 text-[#a9a9b2] text-sm">Bu ay icin kayit bulunamadi</div>
                )}
              </div>
            </motion.div>
          )}
        </>
      )}
    </div>
  );
}

function KPICard({ icon, label, value, sub, color, testId }) {
  const borderColor = { emerald: 'border-emerald-500/20', red: 'border-red-400/20', blue: 'border-blue-400/20' }[color] || 'border-white/5';
  return (
    <div className={`bg-white/5 rounded-xl p-4 border ${borderColor}`} data-testid={testId}>
      <div className="flex items-center gap-2 mb-2">{icon}<span className="text-xs text-[#a9a9b2]">{label}</span></div>
      <div className="text-xl font-bold text-white">{value}</div>
      {sub && <div className="text-xs text-[#a9a9b2] mt-1">{sub}</div>}
    </div>
  );
}

function CategoryBreakdown({ title, data, color, categories }) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const total = entries.reduce((s, [, v]) => s + v, 0);
  const bgColor = color === 'emerald' ? 'bg-emerald-500/40' : 'bg-red-400/40';

  const getLabel = (key) => {
    const cat = categories.find(c => c.key === key);
    return cat ? cat.label : key;
  };

  return (
    <div className="bg-white/5 rounded-xl p-4 border border-white/5">
      <h3 className="text-white font-medium mb-3">{title}</h3>
      {entries.length === 0 ? (
        <p className="text-[#a9a9b2] text-sm">Kayit yok</p>
      ) : (
        <div className="space-y-2">
          {entries.map(([key, val]) => (
            <div key={key}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-[#a9a9b2]">{getLabel(key)}</span>
                <span className="text-white">{formatMoney(val)} ({total > 0 ? Math.round(val / total * 100) : 0}%)</span>
              </div>
              <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                <div className={`h-full ${bgColor} rounded-full`} style={{ width: `${total > 0 ? (val / total) * 100 : 0}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
