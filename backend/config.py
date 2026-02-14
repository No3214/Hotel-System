import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB Configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'vericevir_hotel')

# CORS
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

# LLM API Keys
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# Upload Configuration
UPLOAD_DIR = ROOT_DIR / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB

# Processing Configuration
SUPPORTED_FILE_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/heic',
    'text/plain',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
]

# LLM Models Configuration
LLM_MODELS = {
    'fast_analysis': {
        'provider': 'groq',
        'model': 'llama-3.1-70b-versatile',
        'api_key': GROQ_API_KEY
    },
    'deep_reasoning': {
        'provider': 'openrouter',
        'model': 'deepseek/deepseek-chat',
        'api_key': DEEPSEEK_API_KEY
    },
    'multimodal': {
        'provider': 'google',
        'model': 'gemini-2.5-flash',
        'api_key': GOOGLE_API_KEY
    },
    'quality_control': {
        'provider': 'openrouter',
        'model': 'openai/gpt-4o',
        'api_key': OPENROUTER_API_KEY
    },
    'embeddings': {
        'provider': 'emergent',
        'model': 'gpt-5.1',
        'api_key': EMERGENT_LLM_KEY
    }
}
