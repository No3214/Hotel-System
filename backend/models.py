from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from enum import Enum

# Enums
class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class KnowledgeItemType(str, Enum):
    SOP = "sop"
    CHECKLIST = "checklist"
    STANDARD = "standard"
    POLICY = "policy"
    INVENTORY = "inventory"
    TASK = "task"

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

# Base Models
class TimestampModel(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Document Models
class DocumentCreate(BaseModel):
    filename: str
    file_type: str
    file_size: int

class Document(TimestampModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    file_type: str
    file_size: int
    file_url: str
    status: DocumentStatus = DocumentStatus.PENDING
    raw_content: Optional[str] = None
    content_hash: Optional[str] = None
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: Optional[float] = None
    embedding: Optional[List[float]] = None
    processed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Knowledge Item Models
class KnowledgeItemCreate(BaseModel):
    item_type: KnowledgeItemType
    title: str
    content: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    applicable_to: List[str] = Field(default_factory=list)

class KnowledgeItem(TimestampModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: Optional[str] = None
    item_type: KnowledgeItemType
    title: str
    content: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    applicable_to: List[str] = Field(default_factory=list)
    status: str = "active"
    priority: int = 5
    version: int = 1
    parent_id: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = None
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Task Models
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_role: Optional[str] = None
    priority: TaskPriority = TaskPriority.NORMAL
    due_date: Optional[datetime] = None

class Task(TimestampModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    knowledge_item_id: Optional[str] = None
    document_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    assignee_role: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    notes: Optional[str] = None
    source: str = "ai"
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Processing Job Models
class ProcessingJob(TimestampModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    job_type: str
    status: str = "queued"
    progress: int = 0
    total_steps: int = 100
    current_step: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Dashboard Stats
class DashboardStats(BaseModel):
    total_documents: int
    documents_processed: int
    pending_documents: int
    total_knowledge_items: int
    total_tasks: int
    pending_tasks: int
    quality_score: float
    recent_activities: List[Dict[str, Any]]
