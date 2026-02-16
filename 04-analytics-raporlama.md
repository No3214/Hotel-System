# Analytics ve Raporlama Sistemi - Teknik Dokümantasyon

## 1. Dashboard Mimarisi

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ANALYTICS DASHBOARD MİMARİSİ                            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    KPI KARTLARI (4 Adet)                            │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │  │
│  │  │ Günlük Gelir │ │   Doluluk    │ │ Ort. Oda     │ │  RevPAR      │ │  │
│  │  │   ₺45,250    │ │    78%       │ │  ₺2,850      │ │  ₺2,223      │ │  │
│  │  │   ↑ 12%      │ │   ↑ 5%       │ │   ↑ 8%       │ │   ↑ 15%      │ │  │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐ │
│  │   GELİR TRENDİ (Line Chart) │  │   REZERVASYON KAYNAKLARI (Pie)      │ │
│  │                             │  │                                     │ │
│  │    ₺                        │  │         ┌─────────┐                 │ │
│  │ 60k│      ╱╲                │  │        /  OTA 35%  \                │ │
│  │ 50k│    ╱    ╲      ╱╲      │  │       /  Direct 40%  \               │ │
│  │ 40k│  ╱        ╲  ╱    ╲    │  │      │   Walk-in 25%   │              │ │
│  │ 30k│╱            ╲          │  │       \                /               │ │
│  │    └─────────────────────── │  │        \              /                │ │
│  │      Oca Şub Mar Nis May   │  │         └───────────┘                 │ │
│  └─────────────────────────────┘  └─────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │              DOLULUK ISI HARİTASI (Heatmap - 365 Gün)               │  │
│  │                                                                     │  │
│  │   Oca  ████████████████████████████████████████████████████████   │  │
│  │   Şub  ████████████████████████████████████████████████████████   │  │
│  │   Mar  ████████████████████████████████████████████████████████   │  │
│  │   Nis  ████████████████████████████████████████████████████████   │  │
│  │   May  ████████████████████████████████████████████████████████   │  │
│  │   Haz  ████████████████████████████████████████████████████████   │  │
│  │   Tem  ████████████████████████████████████████████████████████   │  │
│  │   Ağu  ████████████████████████████████████████████████████████   │  │
│  │   Eyl  ████████████████████████████████████████████████████████   │  │
│  │   Eki  ████████████████████████████████████████████████████████   │  │
│  │   Kas  ████████████████████████████████████████████████████████   │  │
│  │   Ara  ████████████████████████████████████████████████████████   │  │
│  │                                                                     │  │
│  │   🟩 %80-100  🟨 %60-80  🟧 %40-60  🟥 %0-40                       │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. API Endpoints

```python
# api/analytics_routes.py

from fastapi import APIRouter, Query
from datetime import date, timedelta
from typing import Optional, List

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/dashboard/kpi")
async def get_kpi_metrics(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None)
):
    """
    Dashboard KPI metriklerini döndürür
    """
    if not date_from:
        date_from = date.today()
    if not date_to:
        date_to = date.today()
    
    # Günlük gelir
    daily_revenue = await calculate_revenue(date_from, date_to)
    
    # Doluluk oranı
    occupancy_rate = await calculate_occupancy(date_from, date_to)
    
    # Ortalama oda fiyatı (ADR)
    sold_nights = await get_sold_room_nights(date_from, date_to)
    adr = daily_revenue / sold_nights if sold_nights > 0 else 0
    
    # RevPAR
    total_rooms = 16
    total_room_nights = total_rooms * ((date_to - date_from).days + 1)
    revpar = daily_revenue / total_room_nights
    
    # Geçmiş dönem karşılaştırması
    prev_days = (date_to - date_from).days + 1
    prev_from = date_from - timedelta(days=prev_days)
    prev_to = date_from - timedelta(days=1)
    
    prev_revenue = await calculate_revenue(prev_from, prev_to)
    revenue_change = ((daily_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
    
    return {
        "period": {
            "from": date_from.isoformat(),
            "to": date_to.isoformat()
        },
        "daily_revenue": {
            "value": round(daily_revenue, 2),
            "currency": "TRY",
            "change_percent": round(revenue_change, 1),
            "trend": "up" if revenue_change > 0 else "down"
        },
        "occupancy_rate": {
            "value": round(occupancy_rate * 100, 1),
            "change_percent": 5.2,
            "trend": "up"
        },
        "adr": {
            "value": round(adr, 2),
            "currency": "TRY",
            "change_percent": 8.3,
            "trend": "up"
        },
        "revpar": {
            "value": round(revpar, 2),
            "currency": "TRY",
            "change_percent": 15.1,
            "trend": "up"
        }
    }

@router.get("/revenue/trend")
async def get_revenue_trend(
    period: str = Query(default="30d", regex="^(7d|30d|90d|1y)$")
):
    """
    Gelir trend verisini döndürür
    """
    days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}[period]
    
    data = []
    for i in range(days):
        day = date.today() - timedelta(days=days - i - 1)
        revenue = await calculate_revenue(day, day)
        data.append({
            "date": day.isoformat(),
            "revenue": revenue
        })
    
    return {
        "period": period,
        "data": data,
        "total": sum(d["revenue"] for d in data),
        "average": sum(d["revenue"] for d in data) / len(data) if data else 0
    }

@router.get("/bookings/sources")
async def get_booking_sources(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None)
):
    """
    Rezervasyon kaynak dağılımını döndürür
    """
    from models.reservation import Reservation
    
    if not date_from:
        date_from = date.today() - timedelta(days=30)
    if not date_to:
        date_to = date.today()
    
    # Kaynaklara göre grupla
    sources_data = {}
    
    reservations = await Reservation.filter(
        created_at__gte=date_from,
        created_at__lte=date_to
    ).all()
    
    for res in reservations:
        source = res.source or "unknown"
        if source not in sources_data:
            sources_data[source] = {"count": 0, "revenue": 0}
        sources_data[source]["count"] += 1
        sources_data[source]["revenue"] += res.total_price
    
    total_bookings = sum(s["count"] for s in sources_data.values())
    total_revenue = sum(s["revenue"] for s in sources_data.values())
    
    sources = []
    for name, data in sources_data.items():
        sources.append({
            "name": name,
            "bookings": data["count"],
            "bookings_percent": round(data["count"] / total_bookings * 100, 1) if total_bookings > 0 else 0,
            "revenue": data["revenue"],
            "revenue_percent": round(data["revenue"] / total_revenue * 100, 1) if total_revenue > 0 else 0
        })
    
    # Sırala (gelire göre)
    sources.sort(key=lambda x: x["revenue"], reverse=True)
    
    return {
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "sources": sources
    }

@router.get("/occupancy/heatmap")
async def get_occupancy_heatmap(
    year: Optional[int] = Query(default=None)
):
    """
    Yıllık doluluk ısı haritasını döndürür
    """
    if not year:
        year = date.today().year
    
    heatmap = []
    for month in range(1, 13):
        month_data = []
        for day in range(1, 32):
            try:
                current_date = date(year, month, day)
                occupancy = await calculate_occupancy(current_date, current_date)
                month_data.append({
                    "day": day,
                    "occupancy": round(occupancy * 100, 1),
                    "level": get_occupancy_level(occupancy)
                })
            except ValueError:
                break
        
        heatmap.append({
            "month": month,
            "month_name": get_month_name_tr(month),
            "days": month_data
        })
    
    return {"year": year, "heatmap": heatmap}

def get_occupancy_level(occupancy: float) -> str:
    if occupancy >= 0.8:
        return "high"
    elif occupancy >= 0.6:
        return "medium"
    elif occupancy >= 0.4:
        return "low"
    else:
        return "critical"

def get_month_name_tr(month: int) -> str:
    months = ["", "Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
    return months[month]

@router.get("/rooms/performance")
async def get_room_performance(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None)
):
    """
    Oda kategorisi bazlı performans raporu
    """
    from models.room import Room
    from models.reservation import Reservation
    
    if not date_from:
        date_from = date.today() - timedelta(days=30)
    if not date_to:
        date_to = date.today()
    
    rooms = await Room.all()
    performance = []
    
    for room in rooms:
        bookings = await Reservation.filter(
            room_id=room.id,
            check_in__gte=date_from,
            check_out__lte=date_to
        ).all()
        
        total_nights = sum(
            (b.check_out - b.check_in).days for b in bookings
        )
        total_revenue = sum(b.total_price for b in bookings)
        
        available_nights = ((date_to - date_from).days + 1)
        occupancy = total_nights / available_nights if available_nights > 0 else 0
        
        performance.append({
            "room_id": room.id,
            "room_number": room.number,
            "room_type": room.type,
            "bookings_count": len(bookings),
            "total_nights": total_nights,
            "occupancy_rate": round(occupancy * 100, 1),
            "total_revenue": round(total_revenue, 2),
            "adr": round(total_revenue / total_nights, 2) if total_nights > 0 else 0
        })
    
    # Sırala (gelire göre)
    performance.sort(key=lambda x: x["total_revenue"], reverse=True)
    
    return {
        "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
        "rooms": performance
    }

@router.get("/guests/satisfaction")
async def get_guest_satisfaction(
    period: str = Query(default="30d")
):
    """
    Misafir memnuniyet trendini döndürür
    """
    from models.review import GoogleReview
    
    days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}[period]
    
    reviews = await GoogleReview.filter(
        date__gte=date.today() - timedelta(days=days)
    ).all()
    
    if not reviews:
        return {
            "overall_rating": 0,
            "total_reviews": 0,
            "message": "No reviews found for the period"
        }
    
    avg_rating = sum(r.rating for r in reviews) / len(reviews)
    
    # Aylık trend
    monthly_trend = []
    for i in range(min(6, days // 30)):
        month_end = date.today() - timedelta(days=30 * i)
        month_start = month_end - timedelta(days=30)
        
        month_reviews = [r for r in reviews if month_start <= r.date <= month_end]
        if month_reviews:
            month_avg = sum(r.rating for r in month_reviews) / len(month_reviews)
            monthly_trend.append({
                "month": month_start.strftime("%b"),
                "average_rating": round(month_avg, 2),
                "review_count": len(month_reviews)
            })
    
    # Yıldız dağılımı
    rating_distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        rating_distribution[r.rating] = rating_distribution.get(r.rating, 0) + 1
    
    return {
        "overall_rating": round(avg_rating, 2),
        "total_reviews": len(reviews),
        "rating_distribution": rating_distribution,
        "monthly_trend": list(reversed(monthly_trend))
    }

@router.get("/export/excel")
async def export_excel(
    report_type: str = Query(..., regex="^(revenue|bookings|occupancy)$"),
    date_from: date = Query(...),
    date_to: date = Query(...)
):
    """
    Excel raporu indir
    """
    import pandas as pd
    from fastapi.responses import StreamingResponse
    import io
    
    if report_type == "revenue":
        data = await get_revenue_data(date_from, date_to)
        df = pd.DataFrame(data)
        filename = f"revenue_report_{date_from}_{date_to}.xlsx"
    elif report_type == "bookings":
        data = await get_bookings_data(date_from, date_to)
        df = pd.DataFrame(data)
        filename = f"bookings_report_{date_from}_{date_to}.xlsx"
    else:
        data = await get_occupancy_data(date_from, date_to)
        df = pd.DataFrame(data)
        filename = f"occupancy_report_{date_from}_{date_to}.xlsx"
    
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# Yardımcı fonksiyonlar
async def calculate_revenue(date_from: date, date_to: date) -> float:
    from models.reservation import Reservation
    
    reservations = await Reservation.filter(
        check_in__gte=date_from,
        check_out__lte=date_to,
        status__in=["confirmed", "checked_in", "checked_out"]
    ).all()
    
    return sum(r.total_price for r in reservations)

async def calculate_occupancy(date_from: date, date_to: date) -> float:
    from models.reservation import Reservation
    
    total_rooms = 16
    total_nights = ((date_to - date_from).days + 1) * total_rooms
    
    reservations = await Reservation.filter(
        check_in__lte=date_to,
        check_out__gte=date_from,
        status__in=["confirmed", "checked_in", "checked_out"]
    ).all()
    
    occupied_nights = 0
    for res in reservations:
        res_start = max(res.check_in, date_from)
        res_end = min(res.check_out, date_to)
        occupied_nights += (res_end - res_start).days
    
    return occupied_nights / total_nights if total_nights > 0 else 0

async def get_sold_room_nights(date_from: date, date_to: date) -> int:
    from models.reservation import Reservation
    
    reservations = await Reservation.filter(
        check_in__gte=date_from,
        check_out__lte=date_to,
        status__in=["confirmed", "checked_in", "checked_out"]
    ).all()
    
    return sum((r.check_out - r.check_in).days for r in reservations)
```

## 3. Frontend Bileşenleri

```typescript
// components/analytics/KPICard.tsx
import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, Users, Bed, BarChart3 } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string | number;
  changePercent: number;
  trend: 'up' | 'down';
  icon: 'revenue' | 'occupancy' | 'adr' | 'revpar';
  currency?: string;
}

const iconMap = {
  revenue: DollarSign,
  occupancy: Users,
  adr: Bed,
  revpar: BarChart3
};

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  changePercent,
  trend,
  icon,
  currency = '₺'
}) => {
  const Icon = iconMap[icon];
  
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="p-3 bg-green-50 rounded-lg">
          <Icon className="w-6 h-6 text-green-600" />
        </div>
        <div className={`flex items-center gap-1 text-sm font-medium ${
          trend === 'up' ? 'text-green-600' : 'text-red-600'
        }`}>
          {trend === 'up' ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
          <span>{changePercent > 0 ? '+' : ''}{changePercent}%</span>
        </div>
      </div>
      <h3 className="text-gray-500 text-sm font-medium">{title}</h3>
      <p className="text-2xl font-bold text-gray-900 mt-1">
        {typeof value === 'number' && icon === 'revenue' ? `${currency}${value.toLocaleString()}` : 
         typeof value === 'number' && icon === 'occupancy' ? `%${value}` : value}
      </p>
    </div>
  );
};

// components/analytics/RevenueChart.tsx
import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';

interface RevenueData {
  date: string;
  revenue: number;
}

export const RevenueChart: React.FC = () => {
  const [data, setData] = useState<RevenueData[]>([]);
  const [period, setPeriod] = useState<'7d' | '30d' | '90d'>('30d');
  
  useEffect(() => {
    fetch(`/api/analytics/revenue/trend?period=${period}`)
      .then(res => res.json())
      .then(data => setData(data.data));
  }, [period]);
  
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Gelir Trendi
        </h3>
        <div className="flex gap-2">
          {(['7d', '30d', '90d'] as const).map(p => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                period === p 
                  ? 'bg-green-600 text-white' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {p === '7d' ? '7 Gün' : p === '30d' ? '30 Gün' : '90 Gün'}
            </button>
          ))}
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#7A8B6F" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#7A8B6F" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="date" 
            tickFormatter={(date) => new Date(date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })}
            stroke="#9ca3af"
            fontSize={12}
          />
          <YAxis 
            tickFormatter={(value) => `₺${(value / 1000).toFixed(0)}k`}
            stroke="#9ca3af"
            fontSize={12}
          />
          <Tooltip 
            formatter={(value: number) => [`₺${value.toLocaleString()}`, 'Gelir']}
            labelFormatter={(label) => new Date(label).toLocaleDateString('tr-TR')}
            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
          />
          <Area 
            type="monotone" 
            dataKey="revenue" 
            stroke="#7A8B6F" 
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorRevenue)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

// components/analytics/OccupancyHeatmap.tsx
import React from 'react';

interface HeatmapDay {
  day: number;
  occupancy: number;
  level: 'high' | 'medium' | 'low' | 'critical';
}

interface HeatmapMonth {
  month: number;
  month_name: string;
  days: HeatmapDay[];
}

interface HeatmapData {
  year: number;
  heatmap: HeatmapMonth[];
}

interface OccupancyHeatmapProps {
  data: HeatmapData;
}

export const OccupancyHeatmap: React.FC<OccupancyHeatmapProps> = ({ data }) => {
  const getColor = (level: string) => {
    const colors = {
      high: 'bg-green-500',
      medium: 'bg-yellow-400',
      low: 'bg-orange-400',
      critical: 'bg-red-500'
    };
    return colors[level] || 'bg-gray-200';
  };
  
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Doluluk Isı Haritası - {data.year}
      </h3>
      
      <div className="space-y-1">
        {data.heatmap.map((month) => (
          <div key={month.month} className="flex items-center gap-2">
            <span className="w-10 text-xs text-gray-600 font-medium">
              {month.month_name}
            </span>
            <div className="flex gap-0.5 flex-wrap">
              {month.days.map((day) => (
                <div
                  key={day.day}
                  className={`w-3 h-3 rounded-sm ${getColor(day.level)} hover:ring-2 hover:ring-gray-400 cursor-pointer transition-all`}
                  title={`${day.day} ${month.month_name}: %${day.occupancy}`}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
      
      <div className="flex gap-4 mt-4 text-xs text-gray-600">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-green-500 rounded-sm" />
          <span>%80-100</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-yellow-400 rounded-sm" />
          <span>%60-80</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-orange-400 rounded-sm" />
          <span>%40-60</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-red-500 rounded-sm" />
          <span>%0-40</span>
        </div>
      </div>
    </div>
  );
};

// components/analytics/BookingSourcesChart.tsx
import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface SourceData {
  name: string;
  bookings: number;
  bookings_percent: number;
  revenue: number;
  revenue_percent: number;
}

interface BookingSourcesChartProps {
  data: SourceData[];
}

const COLORS = ['#7A8B6F', '#9CA3AF', '#D1D5DB', '#E5E7EB', '#F3F4F6'];

export const BookingSourcesChart: React.FC<BookingSourcesChartProps> = ({ data }) => {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Rezervasyon Kaynakları
      </h3>
      
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey="bookings"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value: number, name: string, props: any) => [
              `${value} rezervasyon (%${props.payload.bookings_percent})`,
              name
            ]}
            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
          />
          <Legend 
            verticalAlign="bottom" 
            height={36}
            formatter={(value: string, entry: any) => `${value} (%${entry.payload.bookings_percent})`}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
```

## 4. Dashboard Sayfası

```typescript
// pages/AnalyticsDashboard.tsx
import React, { useEffect, useState } from 'react';
import { KPICard } from '../components/analytics/KPICard';
import { RevenueChart } from '../components/analytics/RevenueChart';
import { OccupancyHeatmap } from '../components/analytics/OccupancyHeatmap';
import { BookingSourcesChart } from '../components/analytics/BookingSourcesChart';

interface KPIData {
  daily_revenue: { value: number; change_percent: number; trend: 'up' | 'down' };
  occupancy_rate: { value: number; change_percent: number; trend: 'up' | 'down' };
  adr: { value: number; change_percent: number; trend: 'up' | 'down' };
  revpar: { value: number; change_percent: number; trend: 'up' | 'down' };
}

export const AnalyticsDashboard: React.FC = () => {
  const [kpiData, setKpiData] = useState<KPIData | null>(null);
  const [bookingSources, setBookingSources] = useState([]);
  const [heatmapData, setHeatmapData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // KPI verileri
        const kpiRes = await fetch('/api/analytics/dashboard/kpi');
        const kpi = await kpiRes.json();
        setKpiData(kpi);

        // Kaynak dağılımı
        const sourcesRes = await fetch('/api/analytics/bookings/sources');
        const sources = await sourcesRes.json();
        setBookingSources(sources.sources);

        // Isı haritası
        const heatmapRes = await fetch('/api/analytics/occupancy/heatmap');
        const heatmap = await heatmapRes.json();
        setHeatmapData(heatmap);

        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch analytics data:', error);
        setLoading(false);
      }
    };

    fetchData();
    
    // 30 saniyede bir yenile
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span>Canlı</span>
          </div>
        </div>

        {/* KPI Kartları */}
        {kpiData && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <KPICard
              title="Günlük Gelir"
              value={kpiData.daily_revenue.value}
              changePercent={kpiData.daily_revenue.change_percent}
              trend={kpiData.daily_revenue.trend}
              icon="revenue"
            />
            <KPICard
              title="Doluluk Oranı"
              value={kpiData.occupancy_rate.value}
              changePercent={kpiData.occupancy_rate.change_percent}
              trend={kpiData.occupancy_rate.trend}
              icon="occupancy"
            />
            <KPICard
              title="Ort. Oda Fiyatı (ADR)"
              value={kpiData.adr.value}
              changePercent={kpiData.adr.change_percent}
              trend={kpiData.adr.trend}
              icon="adr"
            />
            <KPICard
              title="RevPAR"
              value={kpiData.revpar.value}
              changePercent={kpiData.revpar.change_percent}
              trend={kpiData.revpar.trend}
              icon="revpar"
            />
          </div>
        )}

        {/* Grafikler */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <RevenueChart />
          {bookingSources.length > 0 && (
            <BookingSourcesChart data={bookingSources} />
          )}
        </div>

        {/* Isı Haritası */}
        {heatmapData && (
          <div className="mb-6">
            <OccupancyHeatmap data={heatmapData} />
          </div>
        )}
      </div>
    </div>
  );
};
```

---

**Not:** Dashboard 30 saniyede bir otomatik yenilenir. Tüm grafikler interaktif ve responsive'tir.
