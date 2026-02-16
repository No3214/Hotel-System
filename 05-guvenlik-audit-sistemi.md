# Güvenlik ve Audit Sistemi - Teknik Dokümantasyon

## 1. Genel Bakış

Audit log sistemi, tüm kritik işlemlerin kaydını tutarak güvenlik, uyumluluk ve sorun giderme amacıyla kullanılır. KVKK uyumluluğu için hassas veriler maskeleme ile korunur.

## 2. Audit Log Mimarisi

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUDIT LOG MİMARİSİ                                 │
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                │
│  │   Kullanıcı  │───▶│   İşlem      │───▶│  Audit Log   │                │
│  │   İşlemi     │    │   Decorator  │    │  Kaydet      │                │
│  └──────────────┘    └──────────────┘    └──────────────┘                │
│                                                   │                        │
│                                                   ▼                        │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                     AUDIT LOG VERİTABANI                            │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐               │ │
│  │  │ timestamp│ │ action   │ │ user_id  │ │ changes  │               │ │
│  │  │ entity   │ │ entity_id│ │ ip_addr  │ │ metadata │               │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘               │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                   │                        │
│                                                   ▼                        │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    GÜVENLİK ANALİZİ                                 │ │
│  │  • Şüpheli aktivite tespiti                                        │ │
│  • Anomali algılama                                                  │ │
│  • Gerçek zamanlı uyarılar                                           │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3. Veri Modelleri

```python
# models/audit.py

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum

class AuditAction(str, Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    LOGIN_FAILED = "LOGIN_FAILED"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"

class AuditLog(BaseModel):
    id: str
    timestamp: datetime
    action: str  # AuditAction değeri
    entity_type: str  # "reservation", "guest", "room", etc.
    entity_id: Optional[str]
    user_id: str
    user_email: str
    user_role: Optional[str]
    old_values: Optional[Dict[str, Any]]  # UPDATE için
    new_values: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_id: Optional[str]
    session_id: Optional[str]
    metadata: Optional[Dict[str, Any]]
    success: bool = True
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None

class SecurityAlert(BaseModel):
    id: str
    timestamp: datetime
    alert_type: str  # FAILED_LOGIN, UNUSUAL_HOURS, BULK_DELETION, etc.
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    message: str
    user_id: Optional[str]
    user_email: Optional[str]
    ip_address: Optional[str]
    details: Optional[Dict[str, Any]]
    resolved: bool = False
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]

class SecurityRule(BaseModel):
    id: str
    name: str
    rule_type: str
    threshold: int
    time_window_minutes: int
    severity: str
    is_active: bool = True
    created_at: datetime

class DataRetentionPolicy(BaseModel):
    id: str
    log_type: str
    retention_days: int
    auto_delete: bool = True
    last_cleanup: Optional[datetime]
```

## 4. Audit Logger

```python
# security/audit_logger.py

from datetime import datetime
from typing import Optional, Dict, Any, Callable
from functools import wraps
import logging
import copy

from models.audit import AuditLog, AuditAction

logger = logging.getLogger(__name__)

# Hassas alanlar (KVKK uyumluluğu için)
SENSITIVE_FIELDS = {
    "password", "credit_card", "cvv", "card_number", 
    "phone", "email", "tc_kimlik", "passport", "id_number",
    "bank_account", "iban"
}

class AuditLogger:
    @staticmethod
    def mask_sensitive_data(data: Optional[Dict]) -> Optional[Dict]:
        """
        Hassas bilgileri maskele (KVKK uyumluluğu)
        """
        if not data:
            return None
        
        masked = copy.deepcopy(data)
        
        def mask_value(value: Any) -> Any:
            if isinstance(value, str):
                if len(value) > 6:
                    return value[:2] + "***" + value[-2:]
                return "***"
            elif isinstance(value, dict):
                return {k: mask_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [mask_value(item) for item in value]
            return value
        
        for field in SENSITIVE_FIELDS:
            if field in masked:
                masked[field] = mask_value(masked[field])
        
        # İç içe dict'leri de maskele
        for key, value in masked.items():
            if isinstance(value, dict):
                masked[key] = AuditLogger.mask_sensitive_data(value)
        
        return masked
    
    @staticmethod
    async def log(
        action: AuditAction,
        entity_type: str,
        entity_id: Optional[str],
        user_id: str,
        user_email: str,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None
    ):
        """
        Her işlemi audit log olarak kaydeder
        """
        # Hassas bilgileri maskele
        masked_old = AuditLogger.mask_sensitive_data(old_values)
        masked_new = AuditLogger.mask_sensitive_data(new_values)
        masked_metadata = AuditLogger.mask_sensitive_data(metadata)
        
        try:
            await AuditLog.create(
                timestamp=datetime.now(),
                action=action.value,
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                user_email=user_email,
                old_values=masked_old,
                new_values=masked_new,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                metadata=masked_metadata,
                success=success,
                error_message=error_message,
                duration_ms=duration_ms
            )
            
            logger.debug(f"Audit log created: {action.value} on {entity_type}")
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            # Audit log hatası işlemi durdurmamalı
    
    @staticmethod
    def get_changes_summary(old_values: Optional[Dict], new_values: Optional[Dict]) -> Dict:
        """
        Değişiklik özetini oluşturur
        """
        if not old_values and not new_values:
            return {}
        
        if not old_values:
            return {"type": "created", "fields": list(new_values.keys())}
        
        if not new_values:
            return {"type": "deleted", "fields": list(old_values.keys())}
        
        # Değişen alanları bul
        changed_fields = []
        for key in set(old_values.keys()) | set(new_values.keys()):
            old_val = old_values.get(key)
            new_val = new_values.get(key)
            if old_val != new_val:
                changed_fields.append({
                    "field": key,
                    "old": old_val if key not in SENSITIVE_FIELDS else "***",
                    "new": new_val if key not in SENSITIVE_FIELDS else "***"
                })
        
        return {
            "type": "updated",
            "changed_fields": changed_fields
        }

# Decorator olarak kullanım
def audit_log(
    action: AuditAction,
    entity_type: str,
    get_entity_id: Optional[Callable] = None
):
    """
    Fonksiyon decorator'ı olarak audit log
    
    Kullanım:
        @audit_log(AuditAction.CREATE, "reservation")
        async def create_reservation(data: ReservationCreate):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from fastapi import Request
            
            start_time = datetime.now()
            old_values = None
            entity_id = None
            
            # Entity ID'yi belirle
            if get_entity_id:
                entity_id = get_entity_id(*args, **kwargs)
            elif "id" in kwargs:
                entity_id = kwargs["id"]
            elif "entity_id" in kwargs:
                entity_id = kwargs["entity_id"]
            
            # UPDATE için mevcut değerleri al
            if action == AuditAction.UPDATE and entity_id:
                old_values = await get_current_entity_values(entity_type, entity_id)
            
            # Fonksiyonu çalıştır
            try:
                result = await func(*args, **kwargs)
                success = True
                error_msg = None
                
                # Yeni değerleri al
                new_values = extract_entity_values(result) if result else None
                
                # Entity ID'yi sonuçtan al (CREATE için)
                if not entity_id and result and hasattr(result, 'id'):
                    entity_id = result.id
                
            except Exception as e:
                success = False
                error_msg = str(e)
                new_values = None
                raise
            
            finally:
                # Süreyi hesapla
                duration = int((datetime.now() - start_time).total_seconds() * 1000)
                
                # Request bilgilerini al
                request = get_current_request()
                ip_address = get_client_ip(request) if request else None
                user_agent = request.headers.get("user-agent") if request else None
                
                # Log kaydet
                await AuditLogger.log(
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    user_id=get_current_user_id(),
                    user_email=get_current_user_email(),
                    old_values=old_values,
                    new_values=new_values,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=success,
                    error_message=error_msg,
                    duration_ms=duration
                )
            
            return result
        
        return wrapper
    return decorator

# Yardımcı fonksiyonlar
async def get_current_entity_values(entity_type: str, entity_id: str) -> Optional[Dict]:
    """
    Mevcut entity değerlerini alır
    """
    model_map = {
        "reservation": "models.reservation.Reservation",
        "guest": "models.guest.Guest",
        "room": "models.room.Room",
        "user": "models.user.User"
    }
    
    model_path = model_map.get(entity_type)
    if not model_path:
        return None
    
    try:
        module_name, class_name = model_path.rsplit(".", 1)
        module = __import__(module_name, fromlist=[class_name])
        model_class = getattr(module, class_name)
        
        entity = await model_class.get(id=entity_id)
        return entity.dict() if entity else None
        
    except Exception as e:
        logger.error(f"Failed to get entity values: {e}")
        return None

def extract_entity_values(result: Any) -> Optional[Dict]:
    """
    Sonuçtan entity değerlerini çıkarır
    """
    if hasattr(result, 'dict'):
        return result.dict()
    elif isinstance(result, dict):
        return result
    return None

# FastAPI request context
def get_current_request() -> Optional[Any]:
    """
    Mevcut request'i alır
    """
    from contextvars import ContextVar
    request_var: ContextVar = ContextVar('request', default=None)
    return request_var.get()

def get_current_user_id() -> str:
    """
    Mevcut kullanıcı ID'sini alır
    """
    # JWT token'dan veya session'dan al
    return "anonymous"  # Placeholder

def get_current_user_email() -> str:
    """
    Mevcut kullanıcı email'ini alır
    """
    return "anonymous@example.com"  # Placeholder

def get_client_ip(request: Any) -> Optional[str]:
    """
    Client IP adresini alır
    """
    if not request:
        return None
    
    # X-Forwarded-For header'ını kontrol et (proxy arkasındaysa)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    return request.client.host if hasattr(request, 'client') else None
```

## 5. Şüpheli Aktivite Tespiti

```python
# security/fraud_detection.py

from datetime import datetime, timedelta
from typing import List, Dict
import logging

from models.audit import AuditLog, SecurityAlert, SecurityRule

logger = logging.getLogger(__name__)

class FraudDetectionService:
    def __init__(self):
        self.rules = [
            SecurityRule(
                id="failed_login",
                name="Failed Login Attempts",
                rule_type="FAILED_LOGIN",
                threshold=5,
                time_window_minutes=60,
                severity="HIGH"
            ),
            SecurityRule(
                id="unusual_hours",
                name="Unusual Hours Activity",
                rule_type="UNUSUAL_HOURS",
                threshold=10,
                time_window_minutes=1440,  # 24 saat
                severity="MEDIUM"
            ),
            SecurityRule(
                id="bulk_deletion",
                name="Bulk Deletion",
                rule_type="BULK_DELETION",
                threshold=10,
                time_window_minutes=60,
                severity="HIGH"
            ),
            SecurityRule(
                id="multiple_ips",
                name="Multiple IP Addresses",
                rule_type="MULTIPLE_IPS",
                threshold=3,
                time_window_minutes=60,
                severity="MEDIUM"
            ),
            SecurityRule(
                id="high_value_change",
                name="High Value Changes",
                rule_type="HIGH_VALUE_CHANGE",
                threshold=3,
                time_window_minutes=60,
                severity="MEDIUM"
            )
        ]
    
    async def check_user_activity(self, user_id: str) -> List[Dict]:
        """
        Kullanıcının şüpheli aktivitelerini kontrol eder
        """
        alerts = []
        
        for rule in self.rules:
            alert = await self._check_rule(rule, user_id)
            if alert:
                alerts.append(alert)
        
        return alerts
    
    async def _check_rule(self, rule: SecurityRule, user_id: str) -> Optional[Dict]:
        """
        Belirli bir kuralı kontrol eder
        """
        time_threshold = datetime.now() - timedelta(minutes=rule.time_window_minutes)
        
        if rule.rule_type == "FAILED_LOGIN":
            return await self._check_failed_logins(user_id, rule, time_threshold)
        
        elif rule.rule_type == "UNUSUAL_HOURS":
            return await self._check_unusual_hours(user_id, rule, time_threshold)
        
        elif rule.rule_type == "BULK_DELETION":
            return await self._check_bulk_deletions(user_id, rule, time_threshold)
        
        elif rule.rule_type == "MULTIPLE_IPS":
            return await self._check_multiple_ips(user_id, rule, time_threshold)
        
        elif rule.rule_type == "HIGH_VALUE_CHANGE":
            return await self._check_high_value_changes(user_id, rule, time_threshold)
        
        return None
    
    async def _check_failed_logins(
        self,
        user_id: str,
        rule: SecurityRule,
        time_threshold: datetime
    ) -> Optional[Dict]:
        """
        Başarısız login denemelerini kontrol eder
        """
        failed_logins = await AuditLog.filter(
            user_id=user_id,
            action="LOGIN_FAILED",
            timestamp__gte=time_threshold
        ).count()
        
        if failed_logins >= rule.threshold:
            return {
                "type": rule.rule_type,
                "severity": rule.severity,
                "message": f"{rule.time_window_minutes} dakikada {failed_logins} başarısız giriş denemesi",
                "count": failed_logins,
                "threshold": rule.threshold
            }
        
        return None
    
    async def _check_unusual_hours(
        self,
        user_id: str,
        rule: SecurityRule,
        time_threshold: datetime
    ) -> Optional[Dict]:
        """
        Olağandışı saatlerde işlem kontrolü
        """
        unusual_hours_logs = await AuditLog.filter(
            user_id=user_id,
            timestamp__gte=time_threshold,
            timestamp__hour__lt=6  # 00:00 - 06:00 arası
        ).count()
        
        if unusual_hours_logs >= rule.threshold:
            return {
                "type": rule.rule_type,
                "severity": rule.severity,
                "message": f"Son {rule.time_window_minutes // 60} saatte {unusual_hours_logs} işlem (gece saatlerinde)",
                "count": unusual_hours_logs,
                "threshold": rule.threshold
            }
        
        return None
    
    async def _check_bulk_deletions(
        self,
        user_id: str,
        rule: SecurityRule,
        time_threshold: datetime
    ) -> Optional[Dict]:
        """
        Toplu silme işlemlerini kontrol eder
        """
        deletions = await AuditLog.filter(
            user_id=user_id,
            action="DELETE",
            timestamp__gte=time_threshold
        ).count()
        
        if deletions >= rule.threshold:
            return {
                "type": rule.rule_type,
                "severity": rule.severity,
                "message": f"{rule.time_window_minutes} dakikada {deletions} silme işlemi",
                "count": deletions,
                "threshold": rule.threshold
            }
        
        return None
    
    async def _check_multiple_ips(
        self,
        user_id: str,
        rule: SecurityRule,
        time_threshold: datetime
    ) -> Optional[Dict]:
        """
        Farklı IP adreslerinden giriş kontrolü
        """
        unique_ips = await AuditLog.filter(
            user_id=user_id,
            timestamp__gte=time_threshold
        ).distinct().values("ip_address")
        
        ip_count = len([ip for ip in unique_ips if ip["ip_address"]])
        
        if ip_count >= rule.threshold:
            return {
                "type": rule.rule_type,
                "severity": rule.severity,
                "message": f"{rule.time_window_minutes} dakikada {ip_count} farklı IP adresi",
                "count": ip_count,
                "threshold": rule.threshold,
                "ips": [ip["ip_address"] for ip in unique_ips if ip["ip_address"]]
            }
        
        return None
    
    async def _check_high_value_changes(
        self,
        user_id: str,
        rule: SecurityRule,
        time_threshold: datetime
    ) -> Optional[Dict]:
        """
        Yüksek değerli değişiklikleri kontrol eder
        """
        high_value_updates = await AuditLog.filter(
            user_id=user_id,
            action="UPDATE",
            entity_type="reservation",
            timestamp__gte=time_threshold
        ).all()
        
        # 5000₺ üzeri değişiklikleri say
        count = 0
        for log in high_value_updates:
            metadata = log.metadata or {}
            if metadata.get("price_change", 0) > 5000:
                count += 1
        
        if count >= rule.threshold:
            return {
                "type": rule.rule_type,
                "severity": rule.severity,
                "message": f"{rule.time_window_minutes} dakikada {count} yüksek değerli değişiklik",
                "count": count,
                "threshold": rule.threshold
            }
        
        return None
    
    async def create_alert(self, alert_data: Dict, user_id: str):
        """
        Güvenlik alert'i oluşturur
        """
        # Kullanıcı bilgilerini al
        user = await AuditLog.filter(user_id=user_id).first()
        user_email = user.user_email if user else None
        
        # Son log'dan IP al
        last_log = await AuditLog.filter(
            user_id=user_id
        ).order_by("-timestamp").first()
        ip_address = last_log.ip_address if last_log else None
        
        alert = await SecurityAlert.create(
            timestamp=datetime.now(),
            alert_type=alert_data["type"],
            severity=alert_data["severity"],
            message=alert_data["message"],
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            details={
                "count": alert_data.get("count"),
                "threshold": alert_data.get("threshold"),
                "ips": alert_data.get("ips")
            }
        )
        
        logger.warning(f"Security alert created: {alert.alert_type} - {alert.message}")
        
        # Yüksek öncelikli alert'ler için bildirim gönder
        if alert.severity in ["HIGH", "CRITICAL"]:
            await self._send_security_notification(alert)
        
        return alert
    
    async def _send_security_notification(self, alert: SecurityAlert):
        """
        Güvenlik bildirimi gönderir
        """
        from services.notification_service import notification_service
        
        await notification_service.send_notification(
            type="SECURITY_ALERT",
            title=f"Güvenlik Uyarısı: {alert.alert_type}",
            message=alert.message,
            priority="high",
            metadata={
                "alert_id": alert.id,
                "severity": alert.severity,
                "user_id": alert.user_id
            }
        )
```

## 6. API Endpoint'leri

```python
# api/audit_routes.py

from fastapi import APIRouter, Query, Depends, HTTPException
from datetime import date
from typing import Optional, List

from models.audit import AuditLog, SecurityAlert
from models.user import User

router = APIRouter(prefix="/api/audit", tags=["Audit & Security"])

async def get_current_admin_user():
    """
    Sadece admin kullanıcıları kontrol eder
    """
    # JWT token'dan kullanıcı bilgisini al
    user = await get_current_user()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.get("/logs")
async def get_audit_logs(
    entity_type: Optional[str] = Query(default=None),
    action: Optional[str] = Query(default=None),
    user_id: Optional[str] = Query(default=None),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Audit log kayıtlarını döndürür (sadece admin)
    """
    query = AuditLog.all()
    
    if entity_type:
        query = query.filter(entity_type=entity_type)
    if action:
        query = query.filter(action=action)
    if user_id:
        query = query.filter(user_id=user_id)
    if date_from:
        query = query.filter(timestamp__date__gte=date_from)
    if date_to:
        query = query.filter(timestamp__date__lte=date_to)
    
    total = await query.count()
    logs = await query.order_by("-timestamp").offset((page - 1) * limit).limit(limit).all()
    
    return {
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "user_email": log.user_email,
                "ip_address": log.ip_address,
                "success": log.success,
                "changes": AuditLogger.get_changes_summary(log.old_values, log.new_values)
            }
            for log in logs
        ]
    }

@router.get("/logs/{entity_type}/{entity_id}")
async def get_entity_history(
    entity_type: str,
    entity_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Belirli bir entity'nin değişiklik geçmişini döndürür
    """
    logs = await AuditLog.filter(
        entity_type=entity_type,
        entity_id=entity_id
    ).order_by("timestamp").all()
    
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "history": [
            {
                "timestamp": log.timestamp.isoformat(),
                "action": log.action,
                "user": log.user_email,
                "ip_address": log.ip_address,
                "changes": AuditLogger.get_changes_summary(log.old_values, log.new_values)
            }
            for log in logs
        ]
    }

@router.get("/alerts")
async def get_security_alerts(
    severity: Optional[str] = Query(default=None),
    resolved: Optional[bool] = Query(default=None),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Güvenlik alert'lerini döndürür
    """
    query = SecurityAlert.all().order_by("-timestamp")
    
    if severity:
        query = query.filter(severity=severity)
    if resolved is not None:
        query = query.filter(resolved=resolved)
    
    alerts = await query.limit(100).all()
    
    return {
        "alerts": [
            {
                "id": alert.id,
                "type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "user_id": alert.user_id,
                "user_email": alert.user_email,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            }
            for alert in alerts
        ]
    }

@router.post("/alerts/{alert_id}/resolve")
async def resolve_security_alert(
    alert_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Güvenlik alert'ini çözümlendi olarak işaretler
    """
    alert = await SecurityAlert.get(id=alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.resolved = True
    alert.resolved_at = datetime.now()
    alert.resolved_by = current_user.email
    await alert.save()
    
    return {"status": "resolved", "alert_id": alert_id}

@router.get("/stats")
async def get_audit_stats(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Audit istatistiklerini döndürür
    """
    if not date_from:
        date_from = date.today() - timedelta(days=30)
    if not date_to:
        date_to = date.today()
    
    logs = await AuditLog.filter(
        timestamp__date__gte=date_from,
        timestamp__date__lte=date_to
    ).all()
    
    # Action bazlı sayılar
    action_counts = {}
    for log in logs:
        action_counts[log.action] = action_counts.get(log.action, 0) + 1
    
    # Entity bazlı sayılar
    entity_counts = {}
    for log in logs:
        entity_counts[log.entity_type] = entity_counts.get(log.entity_type, 0) + 1
    
    # Başarısız işlemler
    failed_count = len([l for l in logs if not l.success])
    
    return {
        "period": {
            "from": date_from.isoformat(),
            "to": date_to.isoformat()
        },
        "total_logs": len(logs),
        "action_counts": action_counts,
        "entity_counts": entity_counts,
        "failed_operations": failed_count,
        "success_rate": round((len(logs) - failed_count) / len(logs) * 100, 1) if logs else 100
    }
```

## 7. Veri Tutma Politikası (Data Retention)

```python
# scheduler/audit_cleanup.py

from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging

from models.audit import AuditLog, DataRetentionPolicy

logger = logging.getLogger(__name__)

async def cleanup_old_logs():
    """
    Eski audit loglarını temizler
    """
    policies = await DataRetentionPolicy.filter(auto_delete=True).all()
    
    total_deleted = 0
    
    for policy in policies:
        cutoff_date = datetime.now() - timedelta(days=policy.retention_days)
        
        # Eski logları sil
        deleted = await AuditLog.filter(
            timestamp__lt=cutoff_date
        ).delete()
        
        total_deleted += deleted
        
        logger.info(f"Cleaned up {deleted} old {policy.log_type} logs")
        
        # Son temizlik zamanını güncelle
        policy.last_cleanup = datetime.now()
        await policy.save()
    
    logger.info(f"Total deleted logs: {total_deleted}")

def register_cleanup_job(scheduler):
    """
    Temizlik job'unu scheduler'a kaydeder
    """
    # Her gece 02:00'da çalıştır
    scheduler.add_job(
        cleanup_old_logs,
        CronTrigger(hour=2, minute=0),
        id="audit_cleanup",
        replace_existing=True
    )
    
    logger.info("Audit cleanup job registered")
```

---

**Not:** Tüm audit logları KVKK uyumlu olarak hassas veriler maskeleme ile saklanır. Varsayılan saklama süresi 2 yıldır.
