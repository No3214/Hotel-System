# Revenue Management Sistemi - Teknik Dokümantasyon

## 1. Genel Bakış

Revenue Management (Gelir Yönetimi), otelcilik sektöründe talep ve arz dinamiklerine göre fiyatları optimize ederek geliri maksimize eden stratejik bir yaklaşımdır.

## 2. Dinamik Fiyatlandırma Formülü

```
DİNAMİK FİYAT = BAZ FİYAT × MEVSİM × DOLULUK × TALEP × GÜN × ÖZEL GÜN

Örnek Hesaplama:
─────────────────────────────────────────────────────────
Baz Fiyat:                    2,500₺
Mevsim Faktörü (Temmuz):      × 1.50  = 3,750₺
Doluluk Faktörü (%95):        × 1.30  = 4,875₺
Talep Faktörü (Yüksek):       × 1.10  = 5,363₺
Gün Faktörü (Cumartesi):      × 1.15  = 6,167₺
Özel Gün (Yok):               × 1.00  = 6,167₺
─────────────────────────────────────────────────────────
SON FİYAT:                    6,170₺ (İndirimli: 6,000₺)
```

## 3. Konfigürasyon

```python
# config/revenue_management.py

from pydantic_settings import BaseSettings
from typing import Dict

class RevenueManagementConfig(BaseSettings):
    # Dinamik fiyatlandırma ayarları
    DYNAMIC_PRICING_ENABLED: bool = True
    MIN_PRICE_MULTIPLIER: float = 0.7   # Minimum -30%
    MAX_PRICE_MULTIPLIER: float = 2.0   # Maximum +100%
    
    # Faktör ağırlıkları
    SEASON_WEIGHT: float = 1.0
    OCCUPANCY_WEIGHT: float = 1.0
    DEMAND_WEIGHT: float = 0.8
    DAY_WEIGHT: float = 0.6
    SPECIAL_DAY_WEIGHT: float = 1.2
    
    # Otomatik güncelleme
    AUTO_UPDATE_ENABLED: bool = True
    UPDATE_INTERVAL_HOURS: int = 6
    DAYS_AHEAD: int = 90
    
    # Baz fiyatlar (oda tipine göre)
    BASE_RATES: Dict[str, float] = {
        "standart_deniz": 2500,
        "standart_kara": 2200,
        "superior": 3200,
        "uc_kisilik": 3500,
        "dort_kisilik": 4200
    }
    
    class Config:
        env_prefix = "RM_"

settings = RevenueManagementConfig()
```

## 4. Veri Modelleri

```python
# models/revenue_management.py

from datetime import date, datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from enum import Enum

class DemandLevel(str, Enum):
    VERY_LOW = "very_low"      # -30%
    LOW = "low"                # -15%
    NORMAL = "normal"          # 0%
    HIGH = "high"              # +15%
    VERY_HIGH = "very_high"    # +30%
    EXTREME = "extreme"        # +50%

class Season(str, Enum):
    LOW = "low"                # -15%
    SHOULDER = "shoulder"      # 0%
    HIGH = "high"              # +25%
    PEAK = "peak"              # +50%

class DynamicPrice(BaseModel):
    id: str
    room_type: str
    date: date
    base_price: float
    dynamic_price: float
    currency: str = "TRY"
    factors: Dict[str, float]  # Her faktörün çarpanı
    total_multiplier: float
    is_auto_generated: bool = True
    created_at: datetime
    updated_at: datetime
    
class PricingRule(BaseModel):
    id: str
    name: str
    room_type: Optional[str]  # None = tüm odalar
    date_from: Optional[date]
    date_to: Optional[date]
    day_of_week: Optional[List[int]]  # 0=Monday, 6=Sunday
    adjustment_type: str  # percentage, fixed_amount
    adjustment_value: float  # +10 = +%10, -500 = -500₺
    min_stay: int = 1
    priority: int = 0  # Yüksek öncelik önce uygulanır
    is_active: bool = True
    
class CompetitorPrice(BaseModel):
    id: str
    competitor_name: str
    room_type: str
    date: date
    price: float
    currency: str = "TRY"
    source: str  # manual, scraping, api
    captured_at: datetime
    
class RevenueForecast(BaseModel):
    id: str
    date_from: date
    date_to: date
    room_type: Optional[str]
    predicted_occupancy: float
    predicted_revenue: float
    predicted_adr: float
    predicted_revpar: float
    confidence_score: float  # 0-1
    created_at: datetime

class PricingFactors(BaseModel):
    """
    Fiyatlandırma faktörleri
    """
    season_factor: float = Field(default=1.0, ge=0.5, le=2.0)
    occupancy_factor: float = Field(default=1.0, ge=0.5, le=2.0)
    demand_factor: float = Field(default=1.0, ge=0.5, le=2.0)
    day_factor: float = Field(default=1.0, ge=0.5, le=2.0)
    special_day_factor: float = Field(default=1.0, ge=0.5, le=2.0)
    
    @property
    def total_multiplier(self) -> float:
        return (
            self.season_factor *
            self.occupancy_factor *
            self.demand_factor *
            self.day_factor *
            self.special_day_factor
        )
```

## 5. Pricing Engine

```python
# services/pricing_engine.py

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

from config.revenue_management import settings
from models.revenue_management import (
    DynamicPrice, PricingFactors, DemandLevel, Season, PricingRule
)

logger = logging.getLogger(__name__)

class PricingEngine:
    def __init__(self):
        self.base_rates = settings.BASE_RATES
        self.min_multiplier = settings.MIN_PRICE_MULTIPLIER
        self.max_multiplier = settings.MAX_PRICE_MULTIPLIER
    
    async def calculate_dynamic_price(
        self,
        room_type: str,
        target_date: date,
        base_price: Optional[float] = None,
        apply_rules: bool = True
    ) -> Dict:
        """
        Belirli tarih için dinamik fiyat hesaplar
        """
        if base_price is None:
            base_price = self.base_rates.get(room_type, 2500)
        
        # Faktörleri hesapla
        factors = PricingFactors(
            season_factor=self._get_season_factor(target_date),
            occupancy_factor=await self._get_occupancy_factor(target_date),
            demand_factor=await self._get_demand_factor(target_date),
            day_factor=self._get_day_factor(target_date),
            special_day_factor=self._get_special_day_factor(target_date)
        )
        
        # Temel dinamik fiyat
        raw_price = base_price * factors.total_multiplier
        
        # Manuel kuralları uygula
        if apply_rules:
            rule_adjustment = await self._apply_pricing_rules(
                room_type, target_date, raw_price
            )
            raw_price = rule_adjustment
        
        # Min/max sınırları uygula
        min_price = base_price * self.min_multiplier
        max_price = base_price * self.max_multiplier
        dynamic_price = max(min_price, min(raw_price, max_price))
        
        # Yuvarlama (50₺'lik adımlar)
        dynamic_price = round(dynamic_price / 50) * 50
        
        return {
            "room_type": room_type,
            "date": target_date.isoformat(),
            "base_price": base_price,
            "dynamic_price": dynamic_price,
            "factors": {
                "season": factors.season_factor,
                "occupancy": factors.occupancy_factor,
                "demand": factors.demand_factor,
                "day": factors.day_factor,
                "special_day": factors.special_day_factor
            },
            "total_multiplier": round(factors.total_multiplier, 2),
            "applied_limits": {
                "min": min_price,
                "max": max_price
            }
        }
    
    def _get_season_factor(self, target_date: date) -> float:
        """
        Mevsim faktörünü belirler
        """
        month = target_date.month
        
        # Yüksek sezon: Haziran-Ağustos
        if month in [6, 7, 8]:
            return 1.50  # PEAK
        # Shoulder: Mayıs, Eylül
        elif month in [5, 9]:
            return 1.25  # HIGH
        # Düşük: Kasım-Mart
        elif month in [11, 12, 1, 2, 3]:
            return 0.85  # LOW
        # Normal: Nisan, Ekim
        else:
            return 1.0  # SHOULDER
    
    async def _get_occupancy_factor(self, target_date: date) -> float:
        """
        Doluluk faktörünü belirler
        """
        from models.reservation import Reservation
        
        # O gün ve sonraki 7 günün doluluğunu kontrol et
        occupancy_rates = []
        for i in range(8):
            check_date = target_date + timedelta(days=i)
            
            total_rooms = 16
            booked_rooms = await Reservation.filter(
                check_in__lte=check_date,
                check_out__gt=check_date,
                status__in=["confirmed", "checked_in"]
            ).count()
            
            occupancy = booked_rooms / total_rooms
            occupancy_rates.append(occupancy)
        
        avg_occupancy = sum(occupancy_rates) / len(occupancy_rates)
        
        # Doluluk seviyesine göre faktör
        if avg_occupancy >= 0.95:
            return 1.50  # EXTREME
        elif avg_occupancy >= 0.85:
            return 1.30  # VERY_HIGH
        elif avg_occupancy >= 0.70:
            return 1.15  # HIGH
        elif avg_occupancy >= 0.50:
            return 1.0   # NORMAL
        elif avg_occupancy >= 0.30:
            return 0.85  # LOW
        else:
            return 0.70  # VERY_LOW
    
    async def _get_demand_factor(self, target_date: date) -> float:
        """
        Talep faktörünü belirler (rezervasyon hızı)
        """
        from models.reservation import Reservation
        
        days_until = (target_date - date.today()).days
        
        if days_until <= 0:
            return 1.0
        
        # Son 7 günde bu tarih için kaç rezervasyon yapıldı
        recent_bookings = await Reservation.filter(
            check_in=target_date,
            created_at__gte=datetime.now() - timedelta(days=7)
        ).count()
        
        # Hızlı rezervasyon = yüksek talep
        if recent_bookings >= 5:
            return 1.20
        elif recent_bookings >= 3:
            return 1.10
        elif recent_bookings >= 1:
            return 1.0
        else:
            return 0.95
    
    def _get_day_factor(self, target_date: date) -> float:
        """
        Gün faktörünü belirler
        """
        weekday = target_date.weekday()
        
        # Cuma, Cumartesi = hafta sonu fiyatı
        if weekday in [4, 5]:  # Friday, Saturday
            return 1.15
        # Pazar akşamı = normal
        elif weekday == 6:
            return 1.0
        # Hafta içi
        else:
            return 0.95
    
    def _get_special_day_factor(self, target_date: date) -> float:
        """
        Özel gün faktörünü belirler
        """
        special_days = {
            # Yılbaşı
            (1, 1): 1.50,
            # 14 Şubat
            (2, 14): 1.30,
            # 23 Nisan
            (4, 23): 1.20,
            # 1 Mayıs
            (5, 1): 1.20,
            # 19 Mayıs
            (5, 19): 1.20,
            # 30 Ağustos
            (8, 30): 1.30,
            # 29 Ekim
            (10, 29): 1.20,
        }
        
        # Ramazan ve Kurban bayramları (değişken tarihler)
        # Bu kısım veritabanından veya harici API'den alınabilir
        
        key = (target_date.month, target_date.day)
        return special_days.get(key, 1.0)
    
    async def _apply_pricing_rules(
        self,
        room_type: str,
        target_date: date,
        current_price: float
    ) -> float:
        """
        Manuel fiyatlandırma kurallarını uygular
        """
        rules = await PricingRule.filter(
            is_active=True
        ).order_by("-priority").all()
        
        final_price = current_price
        
        for rule in rules:
            # Kuralın geçerli olup olmadığını kontrol et
            if not self._is_rule_applicable(rule, room_type, target_date):
                continue
            
            # Kuralı uygula
            if rule.adjustment_type == "percentage":
                final_price *= (1 + rule.adjustment_value / 100)
            elif rule.adjustment_type == "fixed_amount":
                final_price += rule.adjustment_value
        
        return final_price
    
    def _is_rule_applicable(
        self,
        rule: PricingRule,
        room_type: str,
        target_date: date
    ) -> bool:
        """
        Kuralın geçerli olup olmadığını kontrol eder
        """
        # Oda tipi kontrolü
        if rule.room_type and rule.room_type != room_type:
            return False
        
        # Tarih aralığı kontrolü
        if rule.date_from and target_date < rule.date_from:
            return False
        if rule.date_to and target_date > rule.date_to:
            return False
        
        # Gün kontrolü
        if rule.day_of_week is not None:
            if target_date.weekday() not in rule.day_of_week:
                return False
        
        return True
    
    async def update_all_prices(self, days_ahead: int = 90) -> Dict:
        """
        Gelecek X gün için tüm fiyatları günceller
        """
        results = []
        updated_count = 0
        
        for i in range(days_ahead):
            target_date = date.today() + timedelta(days=i)
            
            for room_type in self.base_rates.keys():
                try:
                    price_data = await self.calculate_dynamic_price(
                        room_type, target_date
                    )
                    
                    # Veritabanına kaydet
                    await DynamicPrice.update_or_create(
                        room_type=room_type,
                        date=target_date,
                        defaults={
                            "base_price": price_data["base_price"],
                            "dynamic_price": price_data["dynamic_price"],
                            "factors": price_data["factors"],
                            "total_multiplier": price_data["total_multiplier"],
                            "is_auto_generated": True,
                            "updated_at": datetime.now()
                        }
                    )
                    
                    results.append(price_data)
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to update price for {room_type} on {target_date}: {e}")
        
        # HotelRunner'a senkronize et
        await self._sync_to_hotelrunner(results)
        
        logger.info(f"Updated {updated_count} prices")
        
        return {
            "updated": updated_count,
            "days_ahead": days_ahead,
            "room_types": len(self.base_rates)
        }
    
    async def _sync_to_hotelrunner(self, price_data: List[Dict]):
        """
        Dinamik fiyatları HotelRunner'a gönderir
        """
        from services.hotelrunner_service import HotelRunnerService
        from models.hotelrunner import RateUpdateRequest
        
        try:
            async with HotelRunnerService() as service:
                # Grupta gönder (rate limit için)
                batch_size = 50
                for i in range(0, len(price_data), batch_size):
                    batch = price_data[i:i + batch_size]
                    
                    rate_updates = [
                        RateUpdateRequest(
                            room_type=price["room_type"],
                            start_date=datetime.fromisoformat(price["date"]).date(),
                            end_date=datetime.fromisoformat(price["date"]).date(),
                            price=price["dynamic_price"]
                        )
                        for price in batch
                    ]
                    
                    await service.update_rates_bulk(rate_updates)
                    
            logger.info(f"Synced {len(price_data)} prices to HotelRunner")
            
        except Exception as e:
            logger.error(f"Failed to sync to HotelRunner: {e}")
    
    async def get_price_recommendation(
        self,
        room_type: str,
        target_date: date
    ) -> Dict:
        """
        Fiyat önerisi sunar (geçmiş verilere dayalı)
        """
        # Geçmiş yılın aynı dönemindeki fiyatları al
        last_year = target_date.replace(year=target_date.year - 1)
        
        historical_prices = await DynamicPrice.filter(
            room_type=room_type,
            date=last_year
        ).all()
        
        if historical_prices:
            avg_price = sum(p.dynamic_price for p in historical_prices) / len(historical_prices)
            recommendation = "Geçmiş yıl ortalamasına göre fiyatlandır"
        else:
            avg_price = None
            recommendation = "Geçmiş veri yok, mevcut faktörlere göre hesapla"
        
        current = await self.calculate_dynamic_price(room_type, target_date)
        
        return {
            "room_type": room_type,
            "date": target_date.isoformat(),
            "recommended_price": current["dynamic_price"],
            "historical_average": avg_price,
            "recommendation": recommendation,
            "factors": current["factors"]
        }
```

## 6. Revenue Forecast

```python
# services/revenue_forecast.py

from datetime import date, timedelta
from typing import Dict, List
import logging

from models.revenue_management import RevenueForecast
from models.reservation import Reservation
from models.room import Room

logger = logging.getLogger(__name__)

class RevenueForecastService:
    async def generate_forecast(
        self,
        date_from: date,
        date_to: date,
        room_type: Optional[str] = None
    ) -> Dict:
        """
        Belirli dönem için gelir tahmini oluşturur
        """
        forecasts = []
        total_predicted_revenue = 0
        
        current = date_from
        while current <= date_to:
            daily_forecast = await self._forecast_day(current, room_type)
            forecasts.append(daily_forecast)
            total_predicted_revenue += daily_forecast["predicted_revenue"]
            current += timedelta(days=1)
        
        # KPI hesapla
        total_days = (date_to - date_from).days + 1
        avg_daily_revenue = total_predicted_revenue / total_days
        
        return {
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            },
            "total_predicted_revenue": round(total_predicted_revenue, 2),
            "average_daily_revenue": round(avg_daily_revenue, 2),
            "daily_forecasts": forecasts
        }
    
    async def _forecast_day(
        self,
        target_date: date,
        room_type: Optional[str] = None
    ) -> Dict:
        """
        Tek günlük tahmin oluşturur
        """
        # Mevcut rezervasyonları al
        reservations = await Reservation.filter(
            check_in__lte=target_date,
            check_out__gt=target_date,
            status__in=["confirmed", "checked_in"]
        )
        
        if room_type:
            reservations = reservations.filter(room__type=room_type)
        
        confirmed_revenue = sum(
            r.total_price / (r.check_out - r.check_in).days
            for r in reservations
        )
        
        occupied_rooms = len(reservations)
        total_rooms = 16 if not room_type else await Room.filter(type=room_type).count()
        available_rooms = total_rooms - occupied_rooms
        
        # Dinamik fiyatı al
        from services.pricing_engine import PricingEngine
        engine = PricingEngine()
        
        if room_type:
            price_data = await engine.calculate_dynamic_price(room_type, target_date)
            avg_rate = price_data["dynamic_price"]
        else:
            # Tüm oda tiplerinin ortalaması
            rates = []
            for rt in engine.base_rates.keys():
                pd = await engine.calculate_dynamic_price(rt, target_date)
                rates.append(pd["dynamic_price"])
            avg_rate = sum(rates) / len(rates) if rates else 2500
        
        # Boş odalar için tahmini doluluk (%40 varsayımı)
        expected_additional_occupancy = available_rooms * 0.4
        potential_revenue = expected_additional_occupancy * avg_rate
        
        total_predicted = confirmed_revenue + potential_revenue
        predicted_occupancy = (occupied_rooms + expected_additional_occupancy) / total_rooms
        
        return {
            "date": target_date.isoformat(),
            "confirmed_revenue": round(confirmed_revenue, 2),
            "potential_revenue": round(potential_revenue, 2),
            "predicted_revenue": round(total_predicted, 2),
            "predicted_occupancy": round(predicted_occupancy * 100, 1),
            "predicted_adr": round(avg_rate, 2),
            "predicted_revpar": round(total_predicted / total_rooms, 2),
            "occupied_rooms": occupied_rooms,
            "available_rooms": available_rooms
        }
    
    async def compare_forecast_vs_actual(
        self,
        date_from: date,
        date_to: date
    ) -> Dict:
        """
        Tahmin ile gerçekleşen değerleri karşılaştırır
        """
        # Tahminleri al
        forecast = await self.generate_forecast(date_from, date_to)
        
        # Gerçek değerleri hesapla
        actual_revenue = 0
        actual_nights = 0
        
        reservations = await Reservation.filter(
            check_in__gte=date_from,
            check_out__lte=date_to,
            status__in=["checked_out", "checked_in"]
        ).all()
        
        for r in reservations:
            nights = (r.check_out - r.check_in).days
            actual_revenue += r.total_price
            actual_nights += nights
        
        total_days = (date_to - date_from).days + 1
        total_room_nights = 16 * total_days
        
        actual_adr = actual_revenue / actual_nights if actual_nights > 0 else 0
        actual_revpar = actual_revenue / total_room_nights
        actual_occupancy = (actual_nights / total_room_nights) * 100
        
        predicted_revenue = forecast["total_predicted_revenue"]
        
        return {
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            },
            "forecast": {
                "revenue": predicted_revenue,
                "adr": sum(d["predicted_adr"] for d in forecast["daily_forecasts"]) / len(forecast["daily_forecasts"]),
                "revpar": sum(d["predicted_revpar"] for d in forecast["daily_forecasts"]) / len(forecast["daily_forecasts"]),
                "occupancy": sum(d["predicted_occupancy"] for d in forecast["daily_forecasts"]) / len(forecast["daily_forecasts"])
            },
            "actual": {
                "revenue": round(actual_revenue, 2),
                "adr": round(actual_adr, 2),
                "revpar": round(actual_revpar, 2),
                "occupancy": round(actual_occupancy, 1)
            },
            "variance": {
                "revenue": round(actual_revenue - predicted_revenue, 2),
                "revenue_percent": round((actual_revenue - predicted_revenue) / predicted_revenue * 100, 1) if predicted_revenue > 0 else 0
            }
        }
```

## 7. API Endpoint'leri

```python
# api/revenue_routes.py

from fastapi import APIRouter, Query, HTTPException
from datetime import date
from typing import Optional, List

from services.pricing_engine import PricingEngine
from services.revenue_forecast import RevenueForecastService
from models.revenue_management import PricingRule

router = APIRouter(prefix="/api/revenue", tags=["Revenue Management"])

@router.get("/pricing/calculate")
async def calculate_price(
    room_type: str,
    target_date: date,
    base_price: Optional[float] = Query(default=None)
):
    """
    Belirli tarih için dinamik fiyat hesaplar
    """
    engine = PricingEngine()
    result = await engine.calculate_dynamic_price(room_type, target_date, base_price)
    return result

@router.post("/pricing/update-all")
async def update_all_prices(days_ahead: int = Query(default=90)):
    """
    Gelecek X gün için tüm fiyatları günceller
    """
    engine = PricingEngine()
    result = await engine.update_all_prices(days_ahead)
    return result

@router.get("/pricing/calendar")
async def get_pricing_calendar(
    room_type: str,
    date_from: date,
    date_to: date
):
    """
    Fiyat takvimi döndürür
    """
    from models.revenue_management import DynamicPrice
    
    prices = await DynamicPrice.filter(
        room_type=room_type,
        date__gte=date_from,
        date__lte=date_to
    ).order_by("date").all()
    
    return {
        "room_type": room_type,
        "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
        "prices": [
            {
                "date": p.date.isoformat(),
                "base_price": p.base_price,
                "dynamic_price": p.dynamic_price,
                "factors": p.factors,
                "total_multiplier": p.total_multiplier
            }
            for p in prices
        ]
    }

@router.get("/forecast")
async def get_revenue_forecast(
    date_from: date,
    date_to: date,
    room_type: Optional[str] = Query(default=None)
):
    """
    Gelir tahmini döndürür
    """
    service = RevenueForecastService()
    forecast = await service.generate_forecast(date_from, date_to, room_type)
    return forecast

@router.get("/forecast/compare")
async def compare_forecast_actual(
    date_from: date,
    date_to: date
):
    """
    Tahmin ile gerçekleşen değerleri karşılaştırır
    """
    service = RevenueForecastService()
    comparison = await service.compare_forecast_vs_actual(date_from, date_to)
    return comparison

@router.post("/rules")
async def create_pricing_rule(rule: PricingRule):
    """
    Yeni fiyatlandırma kuralı oluşturur
    """
    await rule.save()
    return rule

@router.get("/rules")
async def get_pricing_rules(
    is_active: Optional[bool] = Query(default=None)
):
    """
    Fiyatlandırma kurallarını listeler
    """
    query = PricingRule.all().order_by("-priority")
    
    if is_active is not None:
        query = query.filter(is_active=is_active)
    
    rules = await query.all()
    return {"rules": rules}

@router.get("/kpi")
async def get_revenue_kpi(
    date_from: date = Query(default=None),
    date_to: date = Query(default=None)
):
    """
    Gelir yönetimi KPI'larını döndürür
    """
    from models.reservation import Reservation
    
    if not date_from:
        date_from = date.today()
    if not date_to:
        date_to = date.today()
    
    # Rezervasyonları al
    reservations = await Reservation.filter(
        check_in__gte=date_from,
        check_out__lte=date_to,
        status__in=["checked_out", "checked_in"]
    ).all()
    
    total_revenue = sum(r.total_price for r in reservations)
    total_nights = sum((r.check_out - r.check_in).days for r in reservations)
    
    # ADR (Average Daily Rate)
    adr = total_revenue / total_nights if total_nights > 0 else 0
    
    # RevPAR (Revenue Per Available Room)
    total_days = (date_to - date_from).days + 1
    total_available_room_nights = 16 * total_days
    revpar = total_revenue / total_available_room_nights
    
    # Doluluk oranı
    occupied_room_nights = total_nights
    occupancy_rate = (occupied_room_nights / total_available_room_nights) * 100
    
    return {
        "period": {
            "from": date_from.isoformat(),
            "to": date_to.isoformat()
        },
        "total_revenue": round(total_revenue, 2),
        "total_nights": total_nights,
        "adr": round(adr, 2),
        "revpar": round(revpar, 2),
        "occupancy_rate": round(occupancy_rate, 1),
        "reservation_count": len(reservations)
    }
```

## 8. Cron Job'lar

```python
# scheduler/revenue_jobs.py

from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from services.pricing_engine import PricingEngine

logger = logging.getLogger(__name__)

def register_revenue_jobs(scheduler):
    """
    Revenue Management job'larını scheduler'a kaydeder
    """
    # Fiyat güncelleme - Her 6 saatte bir
    scheduler.add_job(
        update_prices_job,
        CronTrigger(hour="0,6,12,18"),
        id="revenue_update_prices",
        replace_existing=True
    )
    
    # Günlük tahmin - Her gece 01:00
    scheduler.add_job(
        generate_daily_forecast_job,
        CronTrigger(hour=1, minute=0),
        id="revenue_daily_forecast",
        replace_existing=True
    )
    
    logger.info("Revenue Management jobs registered")

async def update_prices_job():
    """
    Fiyatları günceller
    """
    try:
        engine = PricingEngine()
        result = await engine.update_all_prices(days_ahead=90)
        
        logger.info(f"Price update completed: {result['updated']} prices updated")
        
    except Exception as e:
        logger.error(f"Price update failed: {e}")

async def generate_daily_forecast_job():
    """
    Günlük gelir tahmini oluşturur
    """
    try:
        from services.revenue_forecast import RevenueForecastService
        
        service = RevenueForecastService()
        
        # Gelecek 30 gün için tahmin
        from datetime import date, timedelta
        date_from = date.today()
        date_to = date_from + timedelta(days=30)
        
        forecast = await service.generate_forecast(date_from, date_to)
        
        logger.info(f"Daily forecast generated: {forecast['total_predicted_revenue']}₺ predicted")
        
    except Exception as e:
        logger.error(f"Daily forecast failed: {e}")
```

---

**Not:** Bu sistem dinamik fiyatlandırma ile %10-15 arası gelir artışı sağlayabilir. Faktör ağırlıkları ve çarpanlar işletme stratejinize göre ayarlanmalıdır.
