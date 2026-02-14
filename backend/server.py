from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import shutil

# Import our modules
from config import MONGO_URL, DB_NAME, CORS_ORIGINS, UPLOAD_DIR, MAX_UPLOAD_SIZE, SUPPORTED_FILE_TYPES
from models import (
    Document, DocumentCreate, DocumentStatus,
    KnowledgeItem, KnowledgeItemCreate, KnowledgeItemType,
    Task, TaskCreate, TaskStatus, TaskPriority,
    ProcessingJob, DashboardStats
)
from llm_council import llm_council
from document_processor import DocumentProcessor
from whatsapp_parser import WhatsAppParser

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
try:
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    logger.info(f"Connected to MongoDB: {DB_NAME}")
except Exception as e:
    logger.error(f"MongoDB connection error: {e}")
    raise

# Create FastAPI app
app = FastAPI(title="VeriÇevir Hotel Management API")
api_router = APIRouter(prefix="/api")

# ==================== BACKGROUND TASKS ====================

async def process_document_background(document_id: str, file_path: str, file_type: str):
    """Background task to process uploaded document"""
    try:
        logger.info(f"Processing document {document_id}...")
        
        # Update status to processing
        await db.documents.update_one(
            {"id": document_id},
            {"$set": {"status": DocumentStatus.PROCESSING, "updated_at": datetime.now(timezone.utc)}}
        )
        
        # Step 1: Extract text from file
        logger.info("Step 1: Extracting text...")
        extracted = await DocumentProcessor.process_file(file_path, file_type)
        
        if extracted["status"] == "error":
            raise Exception(extracted.get("error", "Extraction failed"))
        
        raw_content = extracted["raw_content"]
        content_hash = extracted["content_hash"]
        needs_ocr = extracted["needs_ocr"]
        
        # Update document with raw content
        await db.documents.update_one(
            {"id": document_id},
            {"$set": {
                "raw_content": raw_content,
                "content_hash": content_hash,
                "metadata.needs_ocr": needs_ocr,
                "metadata.content_length": extracted["content_length"]
            }}
        )
        
        # Step 2: LLM Council Analysis
        logger.info("Step 2: Running LLM Council analysis...")
        analysis_results = await llm_council.orchestrate_full_analysis(
            content=raw_content,
            file_type=file_type,
            file_path=file_path if needs_ocr else None
        )
        
        # Step 3: Save extracted knowledge items
        logger.info("Step 3: Saving knowledge items...")
        knowledge_items = []
        deep_extraction = analysis_results.get("deep_extraction", {})
        
        if "knowledge_items" in deep_extraction:
            for item_data in deep_extraction["knowledge_items"]:
                knowledge_item = KnowledgeItem(
                    document_id=document_id,
                    item_type=KnowledgeItemType(item_data.get("type", "standard")),
                    title=item_data.get("title", "Başlıksız"),
                    content=item_data.get("content", ""),
                    applicable_to=item_data.get("applicable_to", []),
                    priority=item_data.get("priority", 5),
                    embedding=analysis_results.get("embedding")
                )
                
                result = await db.knowledge_items.insert_one(knowledge_item.model_dump())
                knowledge_items.append(str(result.inserted_id))
        
        # Step 4: Create tasks
        logger.info("Step 4: Creating tasks...")
        created_tasks = []
        
        if "tasks" in deep_extraction:
            for task_data in deep_extraction["tasks"]:
                due_date = None
                if "due_days" in task_data:
                    due_date = datetime.now(timezone.utc) + timedelta(days=task_data["due_days"])
                
                task = Task(
                    document_id=document_id,
                    title=task_data.get("title", "Görev"),
                    description=task_data.get("description"),
                    assignee_role=task_data.get("assignee_role"),
                    priority=TaskPriority(task_data.get("priority", "normal")),
                    due_date=due_date,
                    source="ai"
                )
                
                result = await db.tasks.insert_one(task.model_dump())
                created_tasks.append(str(result.inserted_id))
        
        # Step 5: Update document with final results
        logger.info("Step 5: Finalizing...")
        fast_analysis = analysis_results.get("fast_analysis", {})
        quality_check = analysis_results.get("quality_check", {})
        
        await db.documents.update_one(
            {"id": document_id},
            {"$set": {
                "status": DocumentStatus.COMPLETED,
                "processed_at": datetime.now(timezone.utc),
                "extracted_data": {
                    "category": fast_analysis.get("category"),
                    "title": fast_analysis.get("title"),
                    "summary": fast_analysis.get("summary"),
                    "keywords": fast_analysis.get("keywords", []),
                    "knowledge_items_count": len(knowledge_items),
                    "tasks_count": len(created_tasks)
                },
                "confidence_score": analysis_results.get("final_confidence", 0.5),
                "embedding": analysis_results.get("embedding"),
                "metadata.quality_check": quality_check,
                "metadata.knowledge_item_ids": knowledge_items,
                "metadata.task_ids": created_tasks
            }}
        )
        
        logger.info(f"Document {document_id} processed successfully!")
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}")
        # Mark as failed
        await db.documents.update_one(
            {"id": document_id},
            {"$set": {
                "status": DocumentStatus.FAILED,
                "metadata.error": str(e),
                "updated_at": datetime.now(timezone.utc)
            }}
        )

# ==================== API ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "VeriÇevir API - Otel Yönetim Zeka Sistemi", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    try:
        # Check MongoDB connection
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# ==================== DASHBOARD ====================

@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Count documents
        total_documents = await db.documents.count_documents({})
        documents_processed = await db.documents.count_documents({"status": DocumentStatus.COMPLETED})
        pending_documents = await db.documents.count_documents({"status": DocumentStatus.PENDING})
        
        # Count knowledge items
        total_knowledge_items = await db.knowledge_items.count_documents({"status": "active"})
        
        # Count tasks
        total_tasks = await db.tasks.count_documents({})
        pending_tasks = await db.tasks.count_documents({"status": TaskStatus.PENDING})
        
        # Calculate average quality score
        pipeline = [
            {"$match": {"status": DocumentStatus.COMPLETED, "confidence_score": {"$exists": True}}},
            {"$group": {"_id": None, "avg_quality": {"$avg": "$confidence_score"}}}
        ]
        quality_result = await db.documents.aggregate(pipeline).to_list(1)
        quality_score = quality_result[0]["avg_quality"] if quality_result else 0.7
        
        # Get recent activities (last 10 documents)
        recent_docs = await db.documents.find(
            {},
            {"_id": 0, "id": 1, "filename": 1, "status": 1, "created_at": 1}
        ).sort("created_at", -1).limit(10).to_list(10)
        
        return DashboardStats(
            total_documents=total_documents,
            documents_processed=documents_processed,
            pending_documents=pending_documents,
            total_knowledge_items=total_knowledge_items,
            total_tasks=total_tasks,
            pending_tasks=pending_tasks,
            quality_score=round(quality_score, 2),
            recent_activities=recent_docs
        )
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DOCUMENTS ====================

@api_router.post("/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and process a document"""
    try:
        # Validate file type
        if file.content_type not in SUPPORTED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Desteklenmeyen dosya tipi: {file.content_type}"
            )
        
        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset
        
        if file_size > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Dosya çok büyük. Maksimum: {MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )
        
        # Create document record
        document = Document(
            filename=file.filename,
            file_type=file.content_type,
            file_size=file_size,
            file_url="",
            status=DocumentStatus.PENDING
        )
        
        # Save file
        file_path = UPLOAD_DIR / f"{document.id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        document.file_url = str(file_path)
        
        # Insert to database
        await db.documents.insert_one(document.model_dump())
        
        # Schedule background processing
        background_tasks.add_task(
            process_document_background,
            document.id,
            str(file_path),
            file.content_type
        )
        
        return {
            "success": True,
            "document_id": document.id,
            "filename": file.filename,
            "status": "processing",
            "message": "Dosya yüklendi ve işleniyor..."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/documents")
async def list_documents(
    status: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """List documents"""
    try:
        query = {}
        if status:
            query["status"] = status
        
        documents = await db.documents.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        total = await db.documents.count_documents(query)
        
        return {
            "documents": documents,
            "total": total,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """Get document details"""
    try:
        document = await db.documents.find_one({"id": document_id}, {"_id": 0})
        
        if not document:
            raise HTTPException(status_code=404, detail="Doküman bulunamadı")
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== KNOWLEDGE BASE ====================

@api_router.get("/knowledge")
async def list_knowledge_items(
    item_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """List knowledge items"""
    try:
        query = {"status": "active"}
        
        if item_type:
            query["item_type"] = item_type
        
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"content": {"$regex": search, "$options": "i"}}
            ]
        
        items = await db.knowledge_items.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        total = await db.knowledge_items.count_documents(query)
        
        return {
            "items": items,
            "total": total,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        logger.error(f"List knowledge error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/knowledge/{item_id}")
async def get_knowledge_item(item_id: str):
    """Get knowledge item details"""
    try:
        item = await db.knowledge_items.find_one({"id": item_id}, {"_id": 0})
        
        if not item:
            raise HTTPException(status_code=404, detail="Bilgi öğesi bulunamadı")
        
        return item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get knowledge item error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== TASKS ====================

@api_router.get("/tasks")
async def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """List tasks"""
    try:
        query = {}
        
        if status:
            query["status"] = status
        
        if priority:
            query["priority"] = priority
        
        tasks = await db.tasks.find(
            query,
            {"_id": 0}
        ).sort("due_date", 1).skip(skip).limit(limit).to_list(limit)
        
        total = await db.tasks.count_documents(query)
        
        return {
            "tasks": tasks,
            "total": total,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        logger.error(f"List tasks error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.patch("/tasks/{task_id}/status")
async def update_task_status(task_id: str, status: str):
    """Update task status"""
    try:
        update_data = {
            "status": status,
            "updated_at": datetime.now(timezone.utc)
        }
        
        if status == TaskStatus.COMPLETED:
            update_data["completed_at"] = datetime.now(timezone.utc)
        
        result = await db.tasks.update_one(
            {"id": task_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Görev bulunamadı")
        
        return {"success": True, "message": "Görev durumu güncellendi"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update task error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== WHATSAPP PROCESSING ====================

@api_router.post("/whatsapp/parse")
async def parse_whatsapp_export(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Parse WhatsApp export file and create tasks"""
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Parse WhatsApp messages
        parser = WhatsAppParser()
        parsed_data = parser.parse_export_file(text_content)
        
        # Create tasks from messages
        whatsapp_tasks = parser.create_tasks_from_whatsapp(parsed_data)
        
        # Save to database
        created_task_ids = []
        for task_data in whatsapp_tasks:
            task = Task(
                title=task_data['title'],
                description=task_data['description'],
                priority=TaskPriority(task_data['priority']),
                source='whatsapp',
                metadata=task_data.get('metadata', {})
            )
            result = await db.tasks.insert_one(task.model_dump())
            created_task_ids.append(str(result.inserted_id))
        
        return {
            "success": True,
            "message": "WhatsApp mesajları işlendi",
            "statistics": {
                "total_messages": parsed_data['total_messages'],
                "unique_senders": len(parsed_data['unique_senders']),
                "tasks_created": len(created_task_ids)
            },
            "senders": parsed_data['unique_senders'],
            "task_ids": created_task_ids
        }
        
    except Exception as e:
        logger.error(f"WhatsApp parse error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SEMANTIC SEARCH ====================

@api_router.post("/search/semantic")
async def semantic_search(query: str, limit: int = 10):
    """Semantic search using embeddings"""
    try:
        # Generate query embedding
        query_embedding = await llm_council.generate_embedding(query)
        
        if not query_embedding:
            # Fallback to text search
            items = await db.knowledge_items.find(
                {
                    "status": "active",
                    "$or": [
                        {"title": {"$regex": query, "$options": "i"}},
                        {"content": {"$regex": query, "$options": "i"}}
                    ]
                },
                {"_id": 0}
            ).limit(limit).to_list(limit)
            
            return {"results": items, "method": "text_search"}
        
        # Find similar items (simple cosine similarity)
        # In production, use vector database or MongoDB Atlas Vector Search
        all_items = await db.knowledge_items.find(
            {"status": "active", "embedding": {"$exists": True, "$ne": None}},
            {"_id": 0}
        ).to_list(1000)
        
        # Calculate cosine similarity
        from numpy import dot
        from numpy.linalg import norm
        
        results = []
        for item in all_items:
            if item.get("embedding"):
                similarity = dot(query_embedding, item["embedding"]) / (
                    norm(query_embedding) * norm(item["embedding"])
                )
                item["similarity"] = float(similarity)
                results.append(item)
        
        # Sort by similarity
        results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        
        return {"results": results[:limit], "method": "semantic_search"}
        
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        # Fallback to text search
        items = await db.knowledge_items.find(
            {
                "status": "active",
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"content": {"$regex": query, "$options": "i"}}
                ]
            },
            {"_id": 0}
        ).limit(limit).to_list(limit)
        
        return {"results": items, "method": "text_search_fallback", "error": str(e)}

# ==================== INCLUDE ROUTER ====================

app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ['*'] else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("MongoDB connection closed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
