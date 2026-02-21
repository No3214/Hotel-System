#!/bin/bash
# ==========================================
# Kozbeyli Konagi — Ilk Kurulum Scripti
# ==========================================
# Bu script gelistirme ortamini kurar

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=== Kozbeyli Konagi — Gelistirme Ortami Kurulumu ==="
echo ""

# 1. Backend .env
if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}backend/.env olusturuluyor...${NC}"
    cp backend/.env.example backend/.env
    # Rastgele JWT secret uret
    JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/BURAYA-GUCLU-BIR-SECRET-KOYUN/$JWT_SECRET/" backend/.env
    else
        sed -i "s/BURAYA-GUCLU-BIR-SECRET-KOYUN/$JWT_SECRET/" backend/.env
    fi
    echo -e "${GREEN}.env olusturuldu ve JWT secret ayarlandi${NC}"
else
    echo -e "${GREEN}backend/.env zaten mevcut${NC}"
fi

# 2. Backend dependencies
echo -e "${YELLOW}Backend bagimliliklari kuruluyor...${NC}"
cd backend
if [ -d "venv" ] || [ -d ".venv" ]; then
    echo "Virtual environment zaten mevcut"
else
    python3 -m venv venv
    echo "Virtual environment olusturuldu"
fi
source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null || true
pip install -r requirements.txt -q
cd ..

# 3. Frontend dependencies
echo -e "${YELLOW}Frontend bagimliliklari kuruluyor...${NC}"
cd frontend
yarn install 2>/dev/null || npm install
cd ..

echo ""
echo -e "${GREEN}=== Kurulum tamamlandi! ===${NC}"
echo ""
echo "Baslatma:"
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn server:app --reload --port 8000"
echo "  Frontend: cd frontend && yarn start"
echo ""
echo "Docker ile:"
echo "  docker compose up -d"
echo ""
echo "Ilk admin olusturma:"
echo "  curl -X POST http://localhost:8000/api/auth/setup"
