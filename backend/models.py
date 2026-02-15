from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from enum import Enum


def utcnow():
    return datetime.now(timezone.utc)


def new_id():
    return str(uuid.uuid4())


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class RoomStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    CLEANING = "cleaning"
    MAINTENANCE = "maintenance"


class ReservationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class HousekeepingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    INSPECTED = "inspected"


# --- Request Models ---

class ChatRequest(BaseModel):
    message: str
    session_id: str = Field(default_factory=new_id)


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_role: Optional[str] = None
    priority: TaskPriority = TaskPriority.NORMAL
    due_date: Optional[str] = None
    source: str = "manual"


class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_role: Optional[str] = None
    notes: Optional[str] = None


class GuestCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    nationality: Optional[str] = None
    notes: Optional[str] = None
    language: str = "tr"


class ReservationCreate(BaseModel):
    guest_id: str
    room_type: str
    check_in: str
    check_out: str
    guests_count: int = 1
    notes: Optional[str] = None
    total_price: Optional[float] = None


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: str = "general"
    event_date: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    capacity: Optional[int] = None
    price_per_person: Optional[float] = None
    is_active: bool = True


class HousekeepingCreate(BaseModel):
    room_number: str
    task_type: str = "standard_clean"
    priority: TaskPriority = TaskPriority.NORMAL
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class KnowledgeCreate(BaseModel):
    title: str
    content: str
    category: str = "general"
    tags: List[str] = Field(default_factory=list)


class StaffCreate(BaseModel):
    name: str
    role: str
    phone: Optional[str] = None
    email: Optional[str] = None
    department: str = "general"
    is_active: bool = True


class WhatsAppMessage(BaseModel):
    from_number: str
    message: str
    sender_name: Optional[str] = None
    timestamp: Optional[str] = None
