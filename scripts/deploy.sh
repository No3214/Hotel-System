#!/bin/bash
# ==========================================
# Kozbeyli Konagi — VPS Deployment Script
# ==========================================
# Kullanim: ./scripts/deploy.sh [production|staging]
# Onkosul: Docker ve docker-compose kurulu olmali

set -e

ENV=${1:-production}
echo "=== Kozbeyli Konagi Deploy — $ENV ==="

# Renklendirme
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# .env kontrolu
if [ ! -f backend/.env ]; then
    echo -e "${RED}HATA: backend/.env dosyasi bulunamadi!${NC}"
    echo "Lutfen .env.example dosyasini kopyalayin:"
    echo "  cp backend/.env.example backend/.env"
    echo "  nano backend/.env"
    exit 1
fi

echo -e "${YELLOW}1. Git pull...${NC}"
git pull origin main

echo -e "${YELLOW}2. Docker imajlarini olusturuyor...${NC}"
docker compose build --no-cache

echo -e "${YELLOW}3. Eski container'lari durduruyor...${NC}"
docker compose down

echo -e "${YELLOW}4. Yeni container'lari baslatıyor...${NC}"
docker compose up -d

echo -e "${YELLOW}5. Health check bekleniyor...${NC}"
sleep 10

# Health check
HEALTH=$(curl -s http://localhost:8000/api/health | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null || echo "unreachable")

if [ "$HEALTH" = "healthy" ]; then
    echo -e "${GREEN}=== Deploy basarili! API saglikli. ===${NC}"
else
    echo -e "${RED}=== UYARI: API durumu: $HEALTH ===${NC}"
    echo "Loglar:"
    docker compose logs --tail=20 backend
fi

echo ""
echo -e "${GREEN}Servisler:${NC}"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/api/docs"
echo ""
echo "Docker loglarini gormek icin: docker compose logs -f"
