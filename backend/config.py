import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')

WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN', '')
WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')
WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'kozbeyli_verify_2026')
INSTAGRAM_ACCESS_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN', '')
INSTAGRAM_PAGE_ID = os.environ.get('INSTAGRAM_PAGE_ID', '')

UPLOAD_DIR = ROOT_DIR / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)
