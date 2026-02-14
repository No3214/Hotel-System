import logging
import hashlib
import os
from pathlib import Path
from typing import Dict, Any, Optional
import PyPDF2
from PIL import Image
import io

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process different document types and extract text"""
    
    @staticmethod
    def calculate_hash(content: bytes) -> str:
        """Calculate SHA-256 hash of content"""
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    async def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text_content = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text.strip():
                            text_content.append(f"--- Sayfa {page_num + 1} ---\n{text}")
                    except Exception as e:
                        logger.error(f"Error extracting page {page_num}: {e}")
                        continue
            
            return "\n\n".join(text_content) if text_content else "PDF'den metin çıkarılamadı (görsel içerik olabilir)"
            
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return f"PDF işleme hatası: {str(e)}"
    
    @staticmethod
    async def extract_text_from_image(file_path: str) -> str:
        """Extract basic info from image (actual OCR will be done by Gemini)"""
        try:
            with Image.open(file_path) as img:
                # Get image metadata
                info = {
                    "format": img.format,
                    "size": f"{img.width}x{img.height}",
                    "mode": img.mode
                }
                return f"Görsel dosyası: {info['format']}, {info['size']}, {info['mode']}. Gemini ile OCR yapılacak."
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            return f"Görsel işleme hatası: {str(e)}"
    
    @staticmethod
    async def extract_text_from_text_file(file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1254', 'iso-8859-9']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                        return content
                except UnicodeDecodeError:
                    continue
            
            return "Metin dosyası okunamadı (encoding hatası)"
            
        except Exception as e:
            logger.error(f"Text file error: {e}")
            return f"Metin dosyası hatası: {str(e)}"
    
    @staticmethod
    async def process_file(file_path: str, file_type: str) -> Dict[str, Any]:
        """Process file based on type and extract content"""
        try:
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_content = f.read()
                content_hash = DocumentProcessor.calculate_hash(file_content)
            
            # Extract text based on file type
            raw_content = ""
            needs_ocr = False
            
            if file_type == 'application/pdf':
                raw_content = await DocumentProcessor.extract_text_from_pdf(file_path)
                # If extraction failed or very short, mark for OCR
                if len(raw_content) < 100 or "görsel içerik" in raw_content.lower():
                    needs_ocr = True
            
            elif file_type in ['image/jpeg', 'image/png', 'image/heic']:
                raw_content = await DocumentProcessor.extract_text_from_image(file_path)
                needs_ocr = True
            
            elif file_type == 'text/plain':
                raw_content = await DocumentProcessor.extract_text_from_text_file(file_path)
            
            else:
                raw_content = f"Desteklenmeyen dosya tipi: {file_type}"
            
            return {
                "raw_content": raw_content,
                "content_hash": content_hash,
                "needs_ocr": needs_ocr,
                "content_length": len(raw_content),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"File processing error: {e}")
            return {
                "raw_content": "",
                "content_hash": "",
                "needs_ocr": False,
                "content_length": 0,
                "status": "error",
                "error": str(e)
            }
