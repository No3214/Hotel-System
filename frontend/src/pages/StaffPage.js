import React, { useState, useEffect } from 'react';
import { getStaff, createStaff, deleteStaff, getShifts, createShift, deleteShift, getAIShifts, getAIPerformance, getAIHRAnalytics } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Users, Plus, Trash2, Clock, Calendar, Sparkles, AlertCircle, Check, Activity, ShieldAlert, Award, TrendingUp } from 'lucide-react';

const DEPARTMENTS = {
  resepsiyon: 'Resepsiyon',
  mutfak: 'Mutfak',
  kat_hizmetleri: 'Kat Hizmetleri',
  bahce: 'Bahce & Havuz',
  guvenlik: 'Guvenlik',
  yonetim: 'Yonetim',
  general: 'Genel',
};

export default function StaffPage() {
  const [staff, setStaff] = useState([]);
  const [shifts, setShifts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('staff');
  const [openStaff, setOpenStaff] = useState(false);
  const [openShift, setOpenShift] = useState(false);
  const [form, setForm] = useState({ name: '', role: '', phone: '', email: '', department: 'general' });
  const [shiftForm, setShiftForm] = useState({ staff_id: '', staff_name: '', date: '', start_time: '08:00', end_time: '17:00', department: 'general', notes: '' });

  // AI Shifts State
  const [aiLoading, setAiLoading] = useState(false);
  const [aiStartDate, setAiStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [aiResult, setAiResult] = useState(null);

  // AI Performance State
  const [perfLoading, setPerfLoading] = useState(false);
  const [perfResult, setPerfResult] = useState(null);
  const [selectedStaffForPerf, setSelectedStaffForPerf] = useState(null);
  const [openPerf, setOpenPerf] = useState(false);

  // AI HR Analytics State
  const [aiHrLoading, setAiHrLoading] = useState(false);
  const [aiHrResult, setAiHrResult] = useState(null);
  const [openAiHr, setOpenAiHr] = useState(false);

  const loadStaff = () => { getStaff().then(r => setStaff(r.data.staff)).catch(console.error).finally(() => setLoading(false)); };
  const loadShifts = () => { getShifts().then(r => setShifts(r.data.shifts)).catch(console.error); };

  useEffect(() => { loadStaff(); loadShifts(); }, []);

  const handleCreateStaff = async () => {
    if (!form.name || !form.role) return;
    await createStaff(form);
    setForm({ name: '', role: '', phone: '', email: '', department: 'general' });
    setOpenStaff(false);
    loadStaff();
  };

  const handleCreateShift = async () => {
    if (!shiftForm.staff_id || !shiftForm.date) return;
    await createShift(shiftForm);
    setShiftForm({ staff_id: '', staff_name: '', date: '', start_time: '08:00', end_time: '17:00', department: 'general', notes: '' });
    setOpenShift(false);
    loadShifts();
  };
  
  const generateAIShifts = async () => {
    setAiLoading(true);
    setAiResult(null);
    try {
      const res = await getAIShifts(aiStartDate);
      if (res.data.ai_shifts) setAiResult(res.data);
      else if (res.data.error) alert(res.data.error);
    } catch (e) {
      console.error(e);
      alert("AI vardiya üretirken hata olustu.");
    } finally {
      setAiLoading(false);
    }
  };
  
  const applyAIShifts = async () => {
    if (!aiResult) return;
    for (const sh of aiResult.ai_shifts) {
      if (sh.shift !== 'OFF') {
         const parts = sh.shift.split('-');
         const st = parts[0]?.trim() || '08:00';
         const en = parts[1]?.trim() || '16:00';
         const staffMember = staff.find(s => s.id === sh.staff_id);
         await createShift({
             staff_id: sh.staff_id,
             staff_name: sh.staff_name,
             date: sh.date,
             start_time: st,
             end_time: en,
             department: staffMember?.department || 'general',
             notes: `AI: ${sh.reason}`
         });
      }
    }
    setAiResult(null);
    loadShifts();
    setTab('shifts');
  };

  const handleGenerateAIPerformance = async (staffMember) => {
    setSelectedStaffForPerf(staffMember);
    setOpenPerf(true);
    setPerfLoading(true);
    setPerfResult(null);
    try {
      const res = await getAIPerformance(staffMember.id);
      if (res.data.performance) {
        setPerfResult(res.data.performance);
      } else if (res.data.error) {
        alert(res.data.error);
        setOpenPerf(false);
      }
    } catch (e) {
      console.error(e);
      alert("AI Performans Raporu üretirken hata olustu.");
      setOpenPerf(false);
    } finally {
      setPerfLoading(false);
    }
  };

  const handleGenerateAIHRAnalytics = async () => {
    setOpenAiHr(true);
    setAiHrLoading(true);
    setAiHrResult(null);
    try {
      const res = await getAIHRAnalytics();
      if (res.data?.report) setAiHrResult(res.data.report);
      else if (res.data?.error) alert(res.data.error);
    } catch (e) {
      console.error(e);
      alert('HR Analizi üretilirken hata oluştu.');
    } finally {
      setAiHrLoading(false);
    }
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="staff-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Personel & Vardiyalar</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">{staff.length} personel, {shifts.length} vardiya</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleGenerateAIHRAnalytics} className="bg-purple-600 hover:bg-purple-500 text-white shadow-[0_0_15px_rgba(147,51,234,0.3)]">
            <ShieldAlert className="w-4 h-4 mr-2" /> AI HR Radarı
          </Button>
          <Dialog open={openStaff} onOpenChange={setOpenStaff}>
            <DialogTrigger asChild>
              <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-staff-btn">
                <Plus className="w-4 h-4 mr-2" /> Personel Ekle
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
              <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Personel</DialogTitle></DialogHeader>
              <div className="space-y-3">
                <Input placeholder="Ad Soyad *" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} className="bg-white/5 border-white/10" data-testid="staff-name-input" />
                <Input placeholder="Gorev *" value={form.role} onChange={e => setForm({ ...form, role: e.target.value })} className="bg-white/5 border-white/10" />
                <Select value={form.department} onValueChange={v => setForm({ ...form, department: v })}>
                  <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-[#1a1a22] border-[#C4972A]/20">
                    {Object.entries(DEPARTMENTS).map(([k, v]) => <SelectItem key={k} value={k}>{v}</SelectItem>)}
                  </SelectContent>
                </Select>
                <Input placeholder="Telefon" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} className="bg-white/5 border-white/10" />
                <Input placeholder="E-posta" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} className="bg-white/5 border-white/10" />
                <Button onClick={handleCreateStaff} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-staff-btn">Kaydet</Button>
              </div>
            </DialogContent>
          </Dialog>
          <Dialog open={openShift} onOpenChange={setOpenShift}>
            <DialogTrigger asChild>
              <Button variant="outline" className="border-[#C4972A]/30 text-[#C4972A]" data-testid="add-shift-btn">
                <Clock className="w-4 h-4 mr-2" /> Vardiya Ekle
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
              <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Vardiya</DialogTitle></DialogHeader>
              <div className="space-y-3">
                <Select value={shiftForm.staff_id} onValueChange={v => {
                  const s = staff.find(x => x.id === v);
                  setShiftForm({ ...shiftForm, staff_id: v, staff_name: s?.name || '', department: s?.department || 'general' });
                }}>
                  <SelectTrigger className="bg-white/5 border-white/10"><SelectValue placeholder="Personel secin *" /></SelectTrigger>
                  <SelectContent className="bg-[#1a1a22] border-[#C4972A]/20 max-h-48">
                    {staff.map(s => <SelectItem key={s.id} value={s.id}>{s.name} - {s.role}</SelectItem>)}
                  </SelectContent>
                </Select>
                <Input type="date" value={shiftForm.date} onChange={e => setShiftForm({ ...shiftForm, date: e.target.value })} className="bg-white/5 border-white/10" data-testid="shift-date" />
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs text-[#7e7e8a] block mb-1">Baslangic</label>
                    <Input type="time" value={shiftForm.start_time} onChange={e => setShiftForm({ ...shiftForm, start_time: e.target.value })} className="bg-white/5 border-white/10" />
                  </div>
                  <div>
                    <label className="text-xs text-[#7e7e8a] block mb-1">Bitis</label>
                    <Input type="time" value={shiftForm.end_time} onChange={e => setShiftForm({ ...shiftForm, end_time: e.target.value })} className="bg-white/5 border-white/10" />
                  </div>
                </div>
                <Input placeholder="Notlar" value={shiftForm.notes} onChange={e => setShiftForm({ ...shiftForm, notes: e.target.value })} className="bg-white/5 border-white/10" />
                <Button onClick={handleCreateShift} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-shift-btn">Kaydet</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[['staff', 'Personel', Users], ['shifts', 'Vardiyalar', Calendar]].map(([id, label, Icon]) => (
          <button key={id} onClick={() => setTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all ${tab === id ? 'bg-[#C4972A]/20 text-[#C4972A]' : 'bg-white/5 text-[#7e7e8a] hover:bg-white/10'}`}>
            <Icon className="w-4 h-4" /> {label}
          </button>
        ))}
      </div>

      {/* Staff List */}
      {tab === 'staff' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {staff.map(s => (
            <div key={s.id} className="glass rounded-xl p-4 hover:gold-glow transition-all" data-testid={`staff-${s.id}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-[#C4972A]/20 flex items-center justify-center text-[#C4972A] font-bold">
                    {s.name?.[0]}
                  </div>
                  <div>
                    <p className="font-medium">{s.name}</p>
                    <p className="text-xs text-[#C4972A]">{s.role}</p>
                  </div>
                </div>
                <button onClick={() => { deleteStaff(s.id).then(loadStaff); }} className="text-[#7e7e8a] hover:text-red-400">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              <div className="mt-3 flex items-center gap-2 mb-3">
                <Badge className="bg-white/5 text-[#7e7e8a] text-xs">{DEPARTMENTS[s.department] || s.department}</Badge>
                {s.phone && <span className="text-xs text-[#7e7e8a]">{s.phone}</span>}
              </div>
              <div className="border-t border-white/5 pt-3">
                <Button size="sm" onClick={() => handleGenerateAIPerformance(s)} className="w-full bg-blue-500/10 text-blue-400 hover:bg-blue-500/20">
                  <Activity className="w-3 h-3 mr-2" /> AI Performans Raporu
                </Button>
              </div>
            </div>
          ))}
          {staff.length === 0 && <div className="col-span-3 text-center py-12 text-[#7e7e8a]"><Users className="w-12 h-12 mx-auto mb-3 opacity-30" /><p>Henuz personel yok</p></div>}
        </div>
      )}

      {/* AI Performance Modal */}
      <Dialog open={openPerf} onOpenChange={setOpenPerf}>
        <DialogContent className="bg-[#1a1a22] border-blue-500/20 max-w-lg text-white">
          <DialogHeader>
            <DialogTitle className="text-blue-400 flex items-center gap-2">
              <Sparkles className="w-5 h-5" /> AI Personel Performans Raporu
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {perfLoading ? (
              <div className="text-center py-8">
                <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                <p className="text-gray-400 text-sm">Gemini {selectedStaffForPerf?.name} icin 360 derece performans verilerini (Gorev, Yorum, Vardiya) analiz ediyor...</p>
              </div>
            ) : perfResult ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between bg-blue-500/10 p-4 rounded-lg">
                  <div>
                    <h3 className="font-semibold text-white">{selectedStaffForPerf?.name}</h3>
                    <p className="text-xs text-blue-300">{DEPARTMENTS[selectedStaffForPerf?.department]}</p>
                  </div>
                  <div className="text-center">
                    <span className="text-3xl font-bold tracking-tighter text-blue-400">{perfResult.score}</span>
                    <span className="text-xs text-gray-500 block">/ 10</span>
                  </div>
                </div>

                <div className="text-sm text-gray-300 leading-relaxed italic bg-white/5 p-3 rounded">
                  "{perfResult.summary}"
                </div>

                <div className="grid grid-cols-2 gap-3 mt-2">
                  <div className="bg-green-500/10 p-3 rounded border border-green-500/20">
                    <h4 className="text-xs font-semibold text-green-400 mb-2">Güçlü Yönleri</h4>
                    <ul className="list-disc pl-4 text-xs text-gray-300 space-y-1">
                      {perfResult.strengths?.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                  <div className="bg-red-500/10 p-3 rounded border border-red-500/20">
                    <h4 className="text-xs font-semibold text-red-400 mb-2">Gelişim Alanları</h4>
                    <ul className="list-disc pl-4 text-xs text-gray-300 space-y-1">
                      {perfResult.areas_of_improvement?.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                </div>

                <div className="bg-[#C4972A]/10 p-3 rounded border border-[#C4972A]/20">
                  <h4 className="text-xs font-semibold text-[#C4972A] mb-1">Yönetici Tavsiyesi</h4>
                  <p className="text-xs text-gray-300">{perfResult.manager_advice}</p>
                </div>
              </div>
            ) : null}
          </div>
        </DialogContent>
      </Dialog>

      {/* AI HR Analytics Modal */}
      <Dialog open={openAiHr} onOpenChange={setOpenAiHr}>
        <DialogContent className="bg-[#1a1a22] border-purple-500/30 max-w-4xl text-white max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-purple-400 flex items-center gap-2 text-xl">
              <ShieldAlert className="w-6 h-6" /> AI İnsan Kaynakları & Tükenmişlik Radarı
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-6">
            {aiHrLoading ? (
              <div className="text-center py-12">
                <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-400 text-sm">Gemini otel genelindeki is yükünü ve vardiya dökümlerini analiz ediyor...</p>
              </div>
            ) : aiHrResult ? (
              <div className="space-y-6">
                
                {/* Score & Summary */}
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-6 text-center flex-shrink-0 flex flex-col justify-center items-center min-w-[200px]">
                    <Award className="w-8 h-8 text-purple-400 mb-2" />
                    <div className="text-sm text-purple-300 mb-1">HR Sağlık Skoru</div>
                    <div className="text-4xl font-bold text-white">{aiHrResult.hr_health_score}</div>
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-xl p-6 flex-1 flex flex-col justify-center">
                    <h4 className="text-purple-400 font-medium mb-2 flex items-center gap-2"><Sparkles className="w-4 h-4"/> Yönetici Özeti</h4>
                    <p className="text-[#e5e5e8] text-sm leading-relaxed">{aiHrResult.summary}</p>
                  </div>
                </div>

                {/* Burnout Risks */}
                <div>
                  <h4 className="flex items-center gap-2 text-red-400 font-medium mb-3">
                    <AlertCircle className="w-5 h-5" /> Tükenmişlik Riskleri (Kırmızı Bayraklar)
                  </h4>
                  {aiHrResult.burnout_risks?.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {aiHrResult.burnout_risks.map((risk, i) => (
                        <div key={i} className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                           <div className="flex justify-between items-start mb-2">
                              <span className="font-semibold text-white">{risk.staff_name}</span>
                              <Badge className={risk.risk_level === 'high' ? 'bg-red-500 text-white' : 'bg-orange-500 text-white'}>{risk.risk_level.toUpperCase()}</Badge>
                           </div>
                           <p className="text-xs text-red-200 mb-1">Departman: {DEPARTMENTS[risk.department] || risk.department}</p>
                           <p className="text-sm text-gray-300">{risk.reason}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 p-4 rounded-lg flex items-center gap-2 text-sm">
                      <Check className="w-4 h-4" /> Şu an için kritik seviyede tükenmişlik riski taşıyan personel bulunmuyor.
                    </div>
                  )}
                </div>

                {/* Grid for Imbalance and Actions */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="bg-white/5 border border-white/10 rounded-xl p-5">
                      <h4 className="text-orange-400 font-medium mb-3 flex items-center gap-2">
                         <TrendingUp className="w-4 h-4"/> İş Yükü Dengesizliği
                      </h4>
                      <p className="text-sm text-gray-300 leading-relaxed">{aiHrResult.workload_imbalance}</p>
                   </div>
                   
                   <div className="bg-white/5 border border-white/10 rounded-xl p-5">
                      <h4 className="text-[#C4972A] font-medium mb-3 flex items-center gap-2">
                         <Activity className="w-4 h-4"/> Motivasyon Eylem Planı
                      </h4>
                      <ul className="space-y-3">
                         {aiHrResult.motivation_actions?.map((act, i) => (
                           <li key={i} className="text-sm p-3 bg-black/20 rounded">
                             <div className="font-semibold text-[#C4972A] mb-1">{act.target}</div>
                             <div className="text-gray-300 text-xs">{act.action}</div>
                           </li>
                         ))}
                      </ul>
                   </div>
                </div>

              </div>
            ) : null}
          </div>
        </DialogContent>
      </Dialog>

      {/* Shifts List */}
      {tab === 'shifts' && (
        <div className="space-y-6">
          <div className="bg-indigo-500/10 border border-indigo-500/30 p-5 rounded-xl">
             <div className="flex flex-col md:flex-row items-center gap-4 justify-between">
                <div>
                   <h2 className="text-lg font-semibold text-indigo-400 flex items-center gap-2"><Sparkles className="w-5 h-5"/> AI Smart Shift Planner</h2>
                   <p className="text-sm text-indigo-300 mt-1">Gelecek tahminleri (gelir & etkinlik) isiginda haftalik optimize edilmis vardiya cizelgesi uretin.</p>
                </div>
                <div className="flex gap-2 items-center w-full md:w-auto">
                   <Input type="date" value={aiStartDate} onChange={e => setAiStartDate(e.target.value)} className="bg-[#1a1a22] border-indigo-500/30 w-auto" />
                   <Button onClick={generateAIShifts} disabled={aiLoading} className="bg-indigo-600 hover:bg-indigo-700 text-white whitespace-nowrap">
                     {aiLoading ? 'Hesaplaniyor...' : 'AI Çizelgesi Üret'}
                   </Button>
                </div>
             </div>
             
             {aiResult && (
                 <div className="mt-6 pt-6 border-t border-indigo-500/20">
                    <div className="bg-[#1a1a22] p-4 rounded-lg flex items-start gap-3 mb-4">
                       <AlertCircle className="w-5 h-5 text-[#C4972A] flex-shrink-0 mt-0.5" />
                       <div className="text-sm text-gray-300">
                          <p className="font-semibold text-white mb-1">AI Analiz Özeti</p>
                          {aiResult.analysis}
                       </div>
                    </div>
                    
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
                        {aiResult.ai_shifts.map((sh, idx) => (
                           <div key={idx} className="bg-[#1a1a22] p-3 rounded border border-white/5">
                               <div className="flex justify-between font-medium mb-1">
                                  <span>{sh.staff_name}</span>
                                  <Badge className={sh.shift === 'OFF' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}>{sh.shift}</Badge>
                               </div>
                               <div className="text-xs text-[#7e7e8a] flex justify-between">
                                  <span>{sh.date}</span>
                                  <span className="truncate ml-2" title={sh.reason}>{sh.reason}</span>
                               </div>
                           </div>
                        ))}
                    </div>
                    
                    <div className="flex justify-end gap-2">
                       <Button variant="ghost" className="text-gray-400" onClick={() => setAiResult(null)}>Iptal</Button>
                       <Button onClick={applyAIShifts} className="bg-green-600 hover:bg-green-700 text-white">
                         <Check className="w-4 h-4 mr-2" /> Vardiyaları Sisteme Kaydet
                       </Button>
                    </div>
                 </div>
             )}
          </div>
        
          <div className="space-y-3">
          {shifts.map(sh => (
            <div key={sh.id} className="glass rounded-xl p-4 flex items-center gap-4 hover:gold-glow transition-all" data-testid={`shift-${sh.id}`}>
              <div className="w-10 h-10 rounded-lg bg-[#C4972A]/10 flex items-center justify-center">
                <Clock className="w-5 h-5 text-[#C4972A]" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{sh.staff_name}</span>
                  <Badge className="bg-white/5 text-[#7e7e8a] text-xs">{DEPARTMENTS[sh.department] || sh.department}</Badge>
                </div>
                <div className="text-xs text-[#7e7e8a] mt-1">
                  {sh.date} | {sh.start_time} - {sh.end_time}
                  {sh.notes && ` | ${sh.notes}`}
                </div>
              </div>
              <button onClick={() => { deleteShift(sh.id).then(loadShifts); }} className="text-[#7e7e8a] hover:text-red-400">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
          {shifts.length === 0 && <div className="text-center py-12 text-[#7e7e8a]"><Clock className="w-12 h-12 mx-auto mb-3 opacity-30" /><p>Henuz vardiya yok</p></div>}
        </div>
        </div>
      )}
    </div>
  );
}
