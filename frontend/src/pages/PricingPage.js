import React, { useState, useEffect } from 'react';
import { calculatePrice, getPriceRange, getSeasons, getHolidays, getRooms } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { TrendingUp, Calendar, Sun, Snowflake, Leaf, DollarSign, ArrowRight } from 'lucide-react';

const SEASON_ICONS = { 'Yuksek Sezon': Sun, 'Orta Sezon': Leaf, 'Dusuk Sezon': Snowflake };

export default function PricingPage() {
  const [rooms, setRooms] = useState([]);
  const [seasons, setSeasons] = useState([]);
  const [holidays, setHolidays] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState('double');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [priceResult, setPriceResult] = useState(null);
  const [rangeResult, setRangeResult] = useState(null);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getRooms().then(r => setRooms(r.data.rooms)),
      getSeasons().then(r => setSeasons(r.data.seasons)),
      getHolidays().then(r => setHolidays(r.data.holidays)),
    ]).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (selectedRoom && selectedDate) {
      calculatePrice(selectedRoom, selectedDate).then(r => setPriceResult(r.data)).catch(console.error);
    }
  }, [selectedRoom, selectedDate]);

  const handleRange = async () => {
    if (!startDate || !endDate) return;
    const r = await getPriceRange(selectedRoom, startDate, endDate);
    setRangeResult(r.data);
  };

  if (loading) return <div className="p-8"><div className="h-8 w-64 bg-white/5 rounded animate-pulse" /></div>;

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="pricing-page">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]" data-testid="pricing-title">Dinamik Fiyatlama</h1>
        <p className="text-[#7e7e8a] text-sm mt-1">Sezon, tatil ve doluluga gore otomatik fiyat hesaplama</p>
      </div>

      {/* Quick Calculator */}
      <div className="glass rounded-xl p-5 space-y-4">
        <h3 className="text-base font-semibold text-[#C4972A] flex items-center gap-2">
          <DollarSign className="w-4 h-4" /> Fiyat Hesapla
        </h3>
        <div className="flex gap-3 flex-wrap">
          <select value={selectedRoom} onChange={e => setSelectedRoom(e.target.value)}
            className="h-9 bg-[#0f0f14] border border-white/10 rounded-lg text-sm text-[#e5e5e8] px-3" data-testid="room-select">
            {rooms.map(r => <option key={r.room_id} value={r.room_id}>{r.name_tr} ({r.base_price_try} TL)</option>)}
          </select>
          <Input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)}
            className="w-44 bg-white/5 border-white/10" data-testid="date-input" />
        </div>

        {priceResult && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="price-result">
            <div className="bg-white/5 rounded-lg p-3">
              <p className="text-xs text-[#7e7e8a]">Baz Fiyat</p>
              <p className="text-lg font-bold text-[#a9a9b2]">{priceResult.base_price} TL</p>
            </div>
            <div className="bg-[#C4972A]/10 border border-[#C4972A]/20 rounded-lg p-3">
              <p className="text-xs text-[#C4972A]">Hesaplanan Fiyat</p>
              <p className="text-lg font-bold text-[#C4972A]" data-testid="final-price">{priceResult.final_price} TL</p>
            </div>
            <div className="bg-white/5 rounded-lg p-3">
              <p className="text-xs text-[#7e7e8a]">Sezon</p>
              <p className="text-sm font-medium text-white">{priceResult.season}</p>
              <p className="text-xs text-[#7e7e8a]">x{priceResult.season_multiplier}</p>
            </div>
            <div className="bg-white/5 rounded-lg p-3">
              <p className="text-xs text-[#7e7e8a]">Ozel Gun</p>
              {priceResult.is_holiday ? (
                <><p className="text-sm font-medium text-amber-400">{priceResult.holiday_name}</p>
                <p className="text-xs text-[#7e7e8a]">x{priceResult.holiday_multiplier}</p></>
              ) : priceResult.is_weekend ? (
                <><p className="text-sm font-medium text-blue-400">Hafta Sonu</p>
                <p className="text-xs text-[#7e7e8a]">x{priceResult.weekend_multiplier}</p></>
              ) : <p className="text-sm text-[#7e7e8a]">Normal Gun</p>}
            </div>
          </div>
        )}
      </div>

      {/* Range Calculator */}
      <div className="glass rounded-xl p-5 space-y-4">
        <h3 className="text-base font-semibold text-[#C4972A] flex items-center gap-2">
          <Calendar className="w-4 h-4" /> Konaklama Hesapla
        </h3>
        <div className="flex gap-3 items-end flex-wrap">
          <div>
            <label className="text-xs text-[#7e7e8a] block mb-1">Giris</label>
            <Input type="date" value={startDate} onChange={e => setStartDate(e.target.value)}
              className="w-40 bg-white/5 border-white/10" data-testid="range-start" />
          </div>
          <ArrowRight className="w-4 h-4 text-[#7e7e8a] mb-2" />
          <div>
            <label className="text-xs text-[#7e7e8a] block mb-1">Cikis</label>
            <Input type="date" value={endDate} onChange={e => setEndDate(e.target.value)}
              className="w-40 bg-white/5 border-white/10" data-testid="range-end" />
          </div>
          <Button onClick={handleRange} className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="calc-range-btn">
            Hesapla
          </Button>
        </div>

        {rangeResult && (
          <div className="space-y-3" data-testid="range-result">
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-[#C4972A]/10 border border-[#C4972A]/20 rounded-lg p-3 text-center">
                <p className="text-xs text-[#C4972A]">Toplam</p>
                <p className="text-xl font-bold text-[#C4972A]">{rangeResult.total_price.toLocaleString()} TL</p>
              </div>
              <div className="bg-white/5 rounded-lg p-3 text-center">
                <p className="text-xs text-[#7e7e8a]">Gece Sayisi</p>
                <p className="text-xl font-bold text-white">{rangeResult.nights}</p>
              </div>
              <div className="bg-white/5 rounded-lg p-3 text-center">
                <p className="text-xs text-[#7e7e8a]">Gece Ortalama</p>
                <p className="text-xl font-bold text-white">{rangeResult.average_nightly.toLocaleString()} TL</p>
              </div>
            </div>
            <div className="max-h-48 overflow-y-auto space-y-1">
              {rangeResult.daily_breakdown?.map((day, i) => (
                <div key={i} className="flex items-center justify-between p-2 bg-white/3 rounded text-sm">
                  <span className="text-[#a9a9b2]">{day.date}</span>
                  <div className="flex items-center gap-2">
                    {day.is_holiday && <Badge className="bg-amber-500/10 text-amber-400 text-[10px]">{day.holiday_name}</Badge>}
                    {day.is_weekend && !day.is_holiday && <Badge className="bg-blue-500/10 text-blue-400 text-[10px]">HaftaSonu</Badge>}
                    <span className="text-[#C4972A] font-medium">{day.final_price} TL</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Seasons & Holidays */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass rounded-xl p-5">
          <h3 className="text-base font-semibold text-[#C4972A] mb-3 flex items-center gap-2">
            <Sun className="w-4 h-4" /> Sezon Carpanlari
          </h3>
          <div className="space-y-2">
            {seasons.map(s => {
              const Icon = SEASON_ICONS[s.label] || Leaf;
              return (
                <div key={s.key} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4 text-[#C4972A]" />
                    <span className="text-sm">{s.label}</span>
                    <span className="text-xs text-[#7e7e8a]">({s.months.map(m => ['', 'Oca','Sub','Mar','Nis','May','Haz','Tem','Agu','Eyl','Eki','Kas','Ara'][m]).join(', ')})</span>
                  </div>
                  <Badge className={`${s.multiplier > 1 ? 'bg-amber-500/10 text-amber-400' : s.multiplier < 1 ? 'bg-blue-500/10 text-blue-400' : 'bg-white/10 text-[#a9a9b2]'}`}>
                    x{s.multiplier}
                  </Badge>
                </div>
              );
            })}
          </div>
        </div>
        <div className="glass rounded-xl p-5">
          <h3 className="text-base font-semibold text-[#C4972A] mb-3 flex items-center gap-2">
            <Calendar className="w-4 h-4" /> Tatil Gunleri ({holidays.length})
          </h3>
          <div className="space-y-1 max-h-64 overflow-y-auto">
            {holidays.map((h, i) => (
              <div key={i} className="flex items-center justify-between p-2 bg-white/5 rounded text-sm">
                <div>
                  <span className="text-[#e5e5e8]">{h.name}</span>
                  <span className="text-xs text-[#7e7e8a] ml-2">{h.date}</span>
                </div>
                <Badge className="bg-amber-500/10 text-amber-400 text-[10px]">x{h.multiplier}</Badge>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
