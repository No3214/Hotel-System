import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# ==================== REQUIRED CONFIG ====================
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')

# Validate required variables at import time
_missing = []
if not MONGO_URL:
    _missing.append('MONGO_URL')
if not DB_NAME:
    _missing.append('DB_NAME')

if _missing:
    print(f"KRITIK HATA: Eksik zorunlu environment variable'lar: {', '.join(_missing)}")
    print("Lutfen .env dosyasini olusturun veya environment variable'lari ayarlayin.")
    print("Ornek: cp .env.example .env && nano .env")
    sys.exit(1)

# ==================== ENVIRONMENT ====================
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

# ==================== CORS ====================
_cors_raw = os.environ.get('CORS_ORIGINS', '')
if _cors_raw and _cors_raw.strip() != '*':
    CORS_ORIGINS = [origin.strip() for origin in _cors_raw.split(',') if origin.strip()]
elif ENVIRONMENT == 'production':
    # Frontend served from same origin — allow same-origin by default
    CORS_ORIGINS = ['*']
    logger.info("CORS_ORIGINS not set — defaulting to allow all (frontend same-origin)")
else:
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173', 'http://127.0.0.1:3000']

# ==================== AI / LLM KEYS ====================
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# ==================== WHATSAPP ====================
WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN', '')
WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')
WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN', '')
WHATSAPP_BUSINESS_ACCOUNT_ID = os.environ.get('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
WHATSAPP_APP_SECRET = os.environ.get('WHATSAPP_APP_SECRET', '')

# ==================== INSTAGRAM ====================
INSTAGRAM_ACCESS_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN', '')
INSTAGRAM_PAGE_ID = os.environ.get('INSTAGRAM_PAGE_ID', '')

# ==================== GOOGLE BUSINESS ====================
GOOGLE_BUSINESS_ACCOUNT_ID = os.environ.get('GOOGLE_BUSINESS_ACCOUNT_ID', '')
GOOGLE_BUSINESS_LOCATION_ID = os.environ.get('GOOGLE_BUSINESS_LOCATION_ID', '')
GOOGLE_BUSINESS_ACCESS_TOKEN = os.environ.get('GOOGLE_BUSINESS_ACCESS_TOKEN', '')
GOOGLE_BUSINESS_REFRESH_TOKEN = os.environ.get('GOOGLE_BUSINESS_REFRESH_TOKEN', '')
GOOGLE_BUSINESS_CLIENT_ID = os.environ.get('GOOGLE_BUSINESS_CLIENT_ID', '')
GOOGLE_BUSINESS_CLIENT_SECRET = os.environ.get('GOOGLE_BUSINESS_CLIENT_SECRET', '')

# ==================== HOTELRUNNER ====================
HOTELRUNNER_API_KEY = os.environ.get('HOTELRUNNER_API_KEY', '')
HOTELRUNNER_HOTEL_ID = os.environ.get('HOTELRUNNER_HOTEL_ID', '')
HOTELRUNNER_API_URL = os.environ.get('HOTELRUNNER_API_URL', 'https://app.hotelrunner.com/api/v2')

# ==================== REDIS (optional) ====================
REDIS_URL = os.environ.get('REDIS_URL', '')

# ==================== UPLOAD ====================
UPLOAD_DIR = ROOT_DIR / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)

# ==================== RATE LIMITING ====================
RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() == 'true'

# ==================== LOGGING ====================
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
