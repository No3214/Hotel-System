import asyncio
import logging
from typing import Dict, List, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType
from config import LLM_MODELS, GOOGLE_API_KEY, GROQ_API_KEY, DEEPSEEK_API_KEY, OPENROUTER_API_KEY, EMERGENT_LLM_KEY
import json
import httpx

logger = logging.getLogger(__name__)

class LLMCouncil:
    """Multi-LLM orchestration for document intelligence"""
    
    def __init__(self):
        # Initialize different LLM agents
        self.fast_analyzer = None
        self.deep_reasoner = None
        self.multimodal_agent = None
        self.quality_controller = None
        
        # Initialize Emergent LLM for embeddings
        if EMERGENT_LLM_KEY:
            try:
                self.embeddings_chat = LlmChat(
                    api_key=EMERGENT_LLM_KEY,
                    session_id="embeddings-session",
                    system_message="You are an embedding generator."
                ).with_model("openai", "gpt-5.1")
            except Exception as e:
                logger.error(f"Failed to initialize embeddings: {e}")
                self.embeddings_chat = None
    
    async def analyze_document_fast(self, content: str, file_type: str) -> Dict[str, Any]:
        """Fast initial analysis using Groq (Llama 3.1)"""
        try:
            if not GROQ_API_KEY:
                return {"error": "GROQ API key not configured"}
            
            # Use Groq API directly for speed
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-70b-versatile",
                        "messages": [
                            {
                                "role": "system",
                                "content": "Sen bir otel yönetim dokuman analisti olarak çalışıyorsun. Dokümanları hızlıca analiz edip kategori ve içerik tipini belirle."
                            },
                            {
                                "role": "user",
                                "content": f"""Bu dokümanı analiz et ve kategorize et:

Dosya Tipi: {file_type}
İçerik:
{content[:3000]}

JSON formatında şu bilgileri ver:
{{
  "category": "menu/checklist/sop/policy/invoice/other",
  "title": "Doküman başlığı",
  "summary": "Kısa özet",
  "keywords": ["anahtar", "kelimeler"],
  "language": "tr/en",
  "confidence": 0.0-1.0
}}"""
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 500
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content_text = result['choices'][0]['message']['content']
                    # Try to parse JSON from response
                    try:
                        # Extract JSON from markdown code blocks if present
                        if '```json' in content_text:
                            json_str = content_text.split('```json')[1].split('```')[0].strip()
                        elif '```' in content_text:
                            json_str = content_text.split('```')[1].split('```')[0].strip()
                        else:
                            json_str = content_text.strip()
                        
                        return json.loads(json_str)
                    except:
                        return {
                            "category": "other",
                            "title": "Analiz Edildi",
                            "summary": content_text[:200],
                            "keywords": [],
                            "language": "tr",
                            "confidence": 0.5
                        }
                else:
                    logger.error(f"Groq API error: {response.status_code}")
                    return {"error": f"API error: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Fast analysis error: {e}")
            return {"error": str(e)}
    
    async def extract_knowledge_deep(self, content: str, category: str) -> Dict[str, Any]:
        """Deep extraction using DeepSeek for detailed analysis"""
        try:
            if not DEEPSEEK_API_KEY:
                return {"error": "DeepSeek API key not configured"}
            
            # Use DeepSeek via OpenRouter
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {
                                "role": "system",
                                "content": """Sen bir otel operasyonu uzmanısın. Dokümanlardan:
1. SOP (Standard Operating Procedure) adımlarını çıkar
2. Checklist maddelerini listele
3. Standartları ve politikaları belirle
4. Envanter bilgilerini çıkar
5. Aksiyon gerektiren görevleri tespit et

Her bilgi için başlık, içerik, uygulama alanı (mutfak/resepsiyon/oda) ve öncelik belirt."""
                            },
                            {
                                "role": "user",
                                "content": f"""Kategori: {category}

İçerik:
{content}

JSON formatında yapılandırılmış bilgi çıkar:
{{
  "knowledge_items": [
    {{
      "type": "sop/checklist/standard/policy/inventory",
      "title": "...",
      "content": "...",
      "applicable_to": ["mutfak", "resepsiyon"],
      "priority": 1-10
    }}
  ],
  "tasks": [
    {{
      "title": "...",
      "description": "...",
      "assignee_role": "mutfak/resepsiyon/kat",
      "priority": "low/normal/high/urgent",
      "due_days": 1
    }}
  ]
}}"""
                            }
                        ],
                        "temperature": 0.2
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content_text = result['choices'][0]['message']['content']
                    try:
                        if '```json' in content_text:
                            json_str = content_text.split('```json')[1].split('```')[0].strip()
                        elif '```' in content_text:
                            json_str = content_text.split('```')[1].split('```')[0].strip()
                        else:
                            json_str = content_text.strip()
                        
                        return json.loads(json_str)
                    except:
                        return {
                            "knowledge_items": [],
                            "tasks": [],
                            "raw_response": content_text[:500]
                        }
                else:
                    return {"error": f"DeepSeek API error: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Deep extraction error: {e}")
            return {"error": str(e)}
    
    async def process_image_with_gemini(self, file_path: str) -> str:
        """Process image/PDF with Gemini for multimodal analysis"""
        try:
            if not GOOGLE_API_KEY:
                return "Google API key not configured"
            
            # Initialize Gemini chat for file processing
            gemini_chat = LlmChat(
                api_key=GOOGLE_API_KEY,
                session_id=f"multimodal-{file_path}",
                system_message="Sen bir görsel ve PDF analiz uzmanısın. Otel dokümanlarından metin çıkar."
            ).with_model("gemini", "gemini-2.5-flash")
            
            # Determine mime type
            mime_type = "image/jpeg"
            if file_path.lower().endswith('.pdf'):
                mime_type = "application/pdf"
            elif file_path.lower().endswith('.png'):
                mime_type = "image/png"
            
            # Create file content
            file_content = FileContentWithMimeType(
                file_path=file_path,
                mime_type=mime_type
            )
            
            # Send to Gemini
            user_message = UserMessage(
                text="Bu dokümanı/görseli analiz et. Tüm metni çıkar ve içeriği Türkçe özetle.",
                file_contents=[file_content]
            )
            
            response = await gemini_chat.send_message(user_message)
            return response
            
        except Exception as e:
            logger.error(f"Gemini multimodal error: {e}")
            return f"Görsel işleme hatası: {str(e)}"
    
    async def quality_check(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Quality control using OpenRouter GPT-4o"""
        try:
            if not OPENROUTER_API_KEY:
                return {"status": "skipped", "quality_score": 0.7}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "openai/gpt-4o",
                        "messages": [
                            {
                                "role": "system",
                                "content": "Sen bir kalite kontrol uzmanısın. Çıkarılan bilgileri kontrol et: tutarlılık, eksiklik, hata tespit et."
                            },
                            {
                                "role": "user",
                                "content": f"""Bu çıkarılmış bilgiyi kontrol et:

{json.dumps(extracted_data, ensure_ascii=False, indent=2)}

JSON formatında döndür:
{{
  "is_valid": true/false,
  "quality_score": 0.0-1.0,
  "issues": ["sorun1", "sorun2"],
  "suggestions": ["öneri1"],
  "confidence": 0.0-1.0
}}"""
                            }
                        ],
                        "temperature": 0.1
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content_text = result['choices'][0]['message']['content']
                    try:
                        if '```json' in content_text:
                            json_str = content_text.split('```json')[1].split('```')[0].strip()
                        else:
                            json_str = content_text.strip()
                        return json.loads(json_str)
                    except:
                        return {
                            "is_valid": True,
                            "quality_score": 0.75,
                            "issues": [],
                            "suggestions": [],
                            "confidence": 0.7
                        }
                else:
                    return {"status": "error", "quality_score": 0.5}
                    
        except Exception as e:
            logger.error(f"Quality check error: {e}")
            return {"status": "error", "quality_score": 0.5, "error": str(e)}
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for semantic search"""
        try:
            if not EMERGENT_LLM_KEY:
                return None
            
            # Use OpenAI embeddings API via Emergent key
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {EMERGENT_LLM_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "text-embedding-3-small",
                        "input": text[:8000]  # Limit text length
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['data'][0]['embedding']
                else:
                    logger.error(f"Embedding API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return None
    
    async def orchestrate_full_analysis(self, content: str, file_type: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Full multi-agent analysis orchestration"""
        results = {
            "fast_analysis": None,
            "deep_extraction": None,
            "multimodal_ocr": None,
            "quality_check": None,
            "embedding": None,
            "final_confidence": 0.0
        }
        
        try:
            # Step 1: Fast analysis for categorization
            logger.info("Step 1: Fast analysis with Groq...")
            fast_result = await self.analyze_document_fast(content, file_type)
            results["fast_analysis"] = fast_result
            
            # If image/PDF, use Gemini for OCR
            if file_path and file_type in ['application/pdf', 'image/jpeg', 'image/png']:
                logger.info("Step 1.5: Multimodal OCR with Gemini...")
                ocr_text = await self.process_image_with_gemini(file_path)
                results["multimodal_ocr"] = ocr_text
                content = content + "\n\n" + ocr_text  # Append OCR text
            
            # Step 2: Deep extraction with DeepSeek
            category = fast_result.get('category', 'other')
            logger.info(f"Step 2: Deep extraction for category '{category}'...")
            deep_result = await self.extract_knowledge_deep(content, category)
            results["deep_extraction"] = deep_result
            
            # Step 3: Quality check with GPT-4o
            logger.info("Step 3: Quality check...")
            quality_result = await self.quality_check(deep_result)
            results["quality_check"] = quality_result
            
            # Step 4: Generate embedding
            logger.info("Step 4: Generating embedding...")
            embedding = await self.generate_embedding(content[:5000])
            results["embedding"] = embedding
            
            # Calculate final confidence
            fast_conf = fast_result.get('confidence', 0.5)
            quality_conf = quality_result.get('confidence', 0.5)
            quality_score = quality_result.get('quality_score', 0.5)
            
            results["final_confidence"] = (fast_conf + quality_conf + quality_score) / 3
            
            logger.info(f"Analysis complete. Final confidence: {results['final_confidence']:.2f}")
            return results
            
        except Exception as e:
            logger.error(f"Orchestration error: {e}")
            results["error"] = str(e)
            return results

# Global instance
llm_council = LLMCouncil()
