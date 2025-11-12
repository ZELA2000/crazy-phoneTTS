#!/bin/bash
# Script di aggiornamento per Linux/Mac
# Parametro: $1 = nuova versione

set -e  # Exit on any error

NEW_VERSION=${1:-latest}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "🚀 Avvio aggiornamento crazy-phoneTTS a versione $NEW_VERSION"

# Function per output colorato
print_step() {
    echo -e "\n\033[1;34m$1\033[0m"
}
print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}
print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}
print_warning() {
    echo -e "\033[1;33m⚠️ $1\033[0m"
}

cd "$PROJECT_DIR"

# Step 1: Verifica Docker
print_step "🐳 Verifica Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker non trovato! Installare Docker."
    exit 1
fi
DOCKER_VERSION=$(docker --version)
print_success "Docker: $DOCKER_VERSION"

# Step 2: Verifica Docker Compose
print_step "🔧 Verifica Docker Compose..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    print_error "Docker Compose non trovato!"
    exit 1
fi
COMPOSE_VERSION=$($COMPOSE_CMD --version)
print_success "Docker Compose: $COMPOSE_VERSION"

# Step 3: Backup configurazione
print_step "💾 Backup configurazione..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f ".env" ]; then
    cp ".env" "$BACKUP_DIR/"
    print_success "Backup .env salvato in $BACKUP_DIR"
fi

if [ -d "backend/uploads" ]; then
    cp -r "backend/uploads" "$BACKUP_DIR/"
    print_success "Backup uploads salvato in $BACKUP_DIR"
fi

# Step 4: Stop containers
print_step "🛑 Arresto containers..."
$COMPOSE_CMD down || true
print_success "Containers arrestati"

# Step 5: Download nuova versione
print_step "📦 Download versione $NEW_VERSION da GitHub..."
TEMP_FILE="/tmp/crazy-phonetts-$NEW_VERSION.tar.gz"
DOWNLOAD_URL="https://github.com/ZELA2000/crazy-phoneTTS/archive/refs/heads/main.tar.gz"

if [ "$NEW_VERSION" != "latest" ]; then
    DOWNLOAD_URL="https://github.com/ZELA2000/crazy-phoneTTS/archive/refs/tags/$NEW_VERSION.tar.gz"
fi

echo "📥 Scaricamento da: $DOWNLOAD_URL"
curl -L "$DOWNLOAD_URL" -o "$TEMP_FILE"
print_success "Download completato"

# Step 6: Estrazione
print_step "📂 Estrazione archivio..."
TEMP_EXTRACT="/tmp/crazy-phonetts-extract"
rm -rf "$TEMP_EXTRACT"
mkdir -p "$TEMP_EXTRACT"
tar -xzf "$TEMP_FILE" -C "$TEMP_EXTRACT" --strip-components=1
print_success "Estratto in: $TEMP_EXTRACT"

# Step 7: Aggiornamento file
print_step "🔄 Aggiornamento file progetto..."

# Lista file da aggiornare (esclusi .env e uploads)
FILES_TO_UPDATE=(
    "backend/main.py"
    "backend/Dockerfile" 
    "backend/requirements.txt"
    "frontend/src/App.js"
    "frontend/src/index.css"
    "frontend/src/index.js"
    "frontend/Dockerfile"
    "frontend/package.json"
    "frontend/public/index.html"
    "docker-compose.yml"
    "VERSION"
    "README.md"
    "FEATURES.md"
    "QUICKSTART.md"
    "update_script.sh"
    "update_script.ps1"
)

for file in "${FILES_TO_UPDATE[@]}"; do
    if [ -f "$TEMP_EXTRACT/$file" ]; then
        # Crea directory se non esiste
        mkdir -p "$(dirname "$file")"
        cp "$TEMP_EXTRACT/$file" "$file"
        print_success "Aggiornato: $file"
    fi
done

# Step 8: Ripristino configurazione
print_step "⚙️ Ripristino configurazione..."
if [ -f "$BACKUP_DIR/.env" ]; then
    cp "$BACKUP_DIR/.env" "."
    print_success "Ripristinato file .env"
fi

if [ -d "$BACKUP_DIR/uploads" ]; then
    cp -r "$BACKUP_DIR/uploads/"* "backend/uploads/" 2>/dev/null || true
    print_success "Ripristinati file uploads"
fi

# Step 9: Rebuild containers
print_step "🔨 Rebuild containers Docker..."
$COMPOSE_CMD build --no-cache
print_success "Build completata"

# Step 10: Avvio sistema
print_step "🚀 Avvio sistema aggiornato..."
$COMPOSE_CMD up -d
print_success "Containers avviati"

# Step 11: Verifica salute
print_step "🏥 Verifica salute sistema..."
sleep 10

for i in {1..6}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Sistema aggiornato e funzionante!"
        break
    else
        if [ $i -eq 6 ]; then
            print_warning "Sistema avviato ma health check fallito"
        else
            echo "⏳ Attendo avvio sistema... ($i/6)"
            sleep 5
        fi
    fi
done

# Cleanup
print_step "🧹 Pulizia file temporanei..."
rm -f "$TEMP_FILE"
rm -rf "$TEMP_EXTRACT"

echo ""
print_success "🎉 AGGIORNAMENTO COMPLETATO CON SUCCESSO!"
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "💾 Backup salvato in: $BACKUP_DIR"