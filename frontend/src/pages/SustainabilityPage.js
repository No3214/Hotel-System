import React, { useState, useEffect } from 'react';
import { getEnergyAIReport } from '../api';
import { Button } from '../components/ui/button';
import { Leaf, Zap, CloudLightning, Thermometer, Wind, AlertTriangle, CheckCircle, Droplets, Loader2, Sparkles } from 'lucide-react';

export default function SustainabilityPage() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getEnergyAIReport();
      if (res.data.success) {
        setReport(res.data);
      } else {
        setError('Rapor alinamadi.');
      }
    } catch (err) {
      console.error(err);
      setError('Bir hata olustu.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  if (loading && !report) {
    return (
      <div className="flex flex-col items-center justify-center p-24 text-[#8FAA86]">
        <Loader2 className="w-12 h-12 animate-spin mb-4 opacity-50" />
        <p className="text-sm font-medium">Yapay Zeka Karbon & Enerji Raporu Hazirlaniriyor...</p>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="sustainability-page">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold flex items-center gap-2 text-[#8FAA86]">
            <Leaf className="w-7 h-7" /> Green Hotel AI
          </h1>
          <p className="text-[#a9a9b2] text-sm mt-1">Yapay Zeka Destekli Enerji & Surdurulebilirlik Yoneticisi</p>
        </div>
        <Button 
          onClick={fetchReport} 
          disabled={loading}
          className="bg-[#8FAA86] hover:bg-[#78966e] text-white"
        >
          {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
          Raporu Guncelle
        </Button>
      </div>

      {error ? (
        <div className="glass rounded-xl p-8 text-center text-red-400">
          <AlertTriangle className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>{error}</p>
        </div>
      ) : report ? (
        <div className="grid grid-cols-12 gap-6">
          
          {/* Sol Kolon: Ozet & Hava Durumu */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            
            <div className="glass rounded-xl p-6 relative overflow-hidden group border border-[#8FAA86]/30">
              <div className="absolute -right-6 -top-6 text-[#8FAA86] opacity-10 group-hover:scale-110 transition-transform">
                <Leaf className="w-32 h-32" />
              </div>
              <h3 className="text-sm text-[#7e7e8a] font-medium mb-1 relative z-10">Tahmini Karbon Tasarrufu</h3>
              <div className="flex items-end gap-2 mb-4 relative z-10">
                <span className="text-4xl font-bold text-[#8FAA86]">{report.report?.carbon_saving_estimate_kg || '0'}</span>
                <span className="text-sm text-[#8FAA86]/80 mb-1">kg CO²</span>
              </div>
              <p className="text-xs text-[#a9a9b2] bg-white/5 p-3 rounded-lg relative z-10">
                Belirtilen aksiyonlari alarak dogaya <b>{(report.report?.carbon_saving_estimate_kg / 2).toFixed(1)} agaclik</b> katki saglayabilirsiniz.
              </p>
            </div>

            <div className="glass rounded-xl p-6">
              <h3 className="text-sm font-medium text-[#C4972A] mb-4 flex items-center gap-2">
                <CloudLightning className="w-4 h-4" /> Hava Durumu & Genel Baglam
              </h3>
              <div className="flex items-center gap-4 mb-4 bg-white/5 p-4 rounded-lg">
                <Thermometer className="w-8 h-8 text-[#C4972A]" />
                <div>
                  <p className="text-sm text-[#7e7e8a]">Foca, bugun:</p>
                  <p className="text-lg font-semibold text-[#e5e5e8]">{report.weather}</p>
                </div>
              </div>
              <p className="text-sm text-[#a9a9b2] leading-relaxed">
                {report.report?.weather_context}
              </p>
            </div>

            <div className="glass rounded-xl p-6">
              <h3 className="text-sm font-medium text-[#e5e5e8] mb-4 flex items-center gap-2">
                <Building2 className="w-4 h-4" /> Kat Bazli Doluluk
              </h3>
              <div className="space-y-3">
                {Object.entries(report.floor_occupancy || {}).map(([floor, data]) => {
                  const occupancyRate = (data.occupied / data.total) * 100;
                  return (
                    <div key={floor} className="bg-white/5 p-3 rounded-lg">
                      <div className="flex justify-between items-center mb-1.5">
                        <span className="text-sm font-medium text-[#e5e5e8]">{floor}. Kat</span>
                        <span className="text-xs text-[#7e7e8a]">{data.occupied} / {data.total} Oda</span>
                      </div>
                      <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-blue-500 rounded-full" 
                          style={{ width: `${occupancyRate}%`, background: occupancyRate > 0 ? '#3b82f6' : '#7e7e8a' }}
                        />
                      </div>
                      <p className="text-[10px] text-[#7e7e8a] mt-1.5">
                        {occupancyRate === 0 ? "Tamamen bos - İklimlendirme kapatilabilir." : "Aktif iklimlendirme gerektiriyor."}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>

          </div>

          {/* Sag Kolon: Aksiyon Plani */}
          <div className="col-span-12 lg:col-span-8">
            <div className="glass rounded-xl p-6">
              <h3 className="text-lg font-bold text-[#e5e5e8] mb-6 flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-500" /> Yapay Zeka Tasarruf Aksiyonlari
              </h3>

              <div className="space-y-4">
                {report.report?.actions?.length > 0 ? (
                  report.report.actions.map((action, idx) => (
                    <div key={idx} className="flex gap-4 p-4 rounded-xl border border-white/5 bg-[#1a1a22] hover:bg-white/5 transition-all">
                      <div className="mt-1">
                        {action.department === 'teknik' ? (
                          <div className="p-2 bg-yellow-500/20 rounded-lg text-yellow-500"><Zap className="w-4 h-4" /></div>
                        ) : action.department === 'housekeeping' ? (
                          <div className="p-2 bg-blue-500/20 rounded-lg text-blue-500"><Droplets className="w-4 h-4" /></div>
                        ) : (
                          <div className="p-2 bg-[#8FAA86]/20 rounded-lg text-[#8FAA86]"><Leaf className="w-4 h-4" /></div>
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between items-start mb-1">
                          <h4 className="text-sm font-semibold text-[#e5e5e8]">{action.title}</h4>
                          <span className="text-[10px] uppercase font-bold text-[#7e7e8a] bg-white/5 px-2 py-1 rounded">
                            {action.department}
                          </span>
                        </div>
                        <p className="text-sm text-[#a9a9b2] leading-relaxed">
                          {action.description}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center p-8 text-[#7e7e8a]">
                    <CheckCircle className="w-8 h-8 mx-auto mb-2 opacity-50 text-[#8FAA86]" />
                    <p>Su an icin oteliniz maksimum verimlilikte calisiyor!</p>
                  </div>
                )}
              </div>
            </div>
            
            <div className="mt-6 glass rounded-xl p-6 bg-gradient-to-br from-[#8FAA86]/10 to-transparent border border-[#8FAA86]/20">
              <h3 className="text-sm font-medium text-[#8FAA86] mb-2 flex items-center gap-2">
                <Sparkles className="w-4 h-4" /> Gemini Enerji Optimizasyonu Nasil Calisir?
              </h3>
              <p className="text-xs text-[#a9a9b2] leading-relaxed">
                Bu rapor gercek zamanli olarak otelinizin PMS verilerinizi (kat bazli anlik doluluk), mutfak siparis yogunlugunuzu ve lokal hava durumunu inceler. 
                Yapısal bir enerji denetimcisi mantigiyla, tamamen bos olan katlardaki "hayalet enerji tuketimini" minimalize edecek taktikler bulur ve karbon ayak izinizi azaltmaniza yardimci olur.
              </p>
            </div>
          </div>

        </div>
      ) : null}
    </div>
  );
}
