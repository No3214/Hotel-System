import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { DollarSign, TrendingUp, TrendingDown, Plus, Trash2, ChevronLeft, ChevronRight, PieChart, BarChart3, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { getFinancialCategories, addIncome, addExpense, getIncomeList, getExpenseList, deleteFinancialRecord, getDailySummary, getMonthlySummary } from '../api';

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
