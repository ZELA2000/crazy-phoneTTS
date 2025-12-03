#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m'

SKIP_CONFIRM=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-confirm) SKIP_CONFIRM=true; shift ;;
        *) echo -e "${RED}Opzione sconosciuta: $1${NC}"; exit 1 ;;
    esac
done

echo -e "${CYAN}=== crazy-phoneTTS Update Script ===${NC}"
echo ""

GIT_AVAILABLE=false
if command -v git &> /dev/null; then
    GIT_AVAILABLE=true
    echo -e "${GREEN}Git disponibile: utilizzo git per l'aggiornamento${NC}"
else
    echo -e "${YELLOW}Git non disponibile: utilizzo download ZIP manuale${NC}"
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERRORE: Docker non e installato.${NC}"
    exit 1
fi

# Rileva se è necessario sudo per docker
DOCKER_CMD="docker"
NEEDS_SUDO=false

if ! docker ps &> /dev/null; then
    if sudo docker ps &> /dev/null 2>&1; then
        DOCKER_CMD="sudo docker"
        NEEDS_SUDO=true
        echo -e "${YELLOW}Utilizzo sudo per i comandi Docker${NC}"
    else
        echo -e "${RED}ERRORE: Docker non e in esecuzione.${NC}"
        exit 1
    fi
fi

# Rileva se usare docker compose o docker-compose
COMPOSE_CMD=""
if $DOCKER_CMD compose version &> /dev/null; then
    COMPOSE_CMD="compose"
    echo -e "${GREEN}Utilizzo docker compose (nuovo)${NC}"
elif command -v docker-compose &> /dev/null; then
    # docker-compose legacy - se docker richiede sudo, anche docker-compose lo richiederà
    if [ "$NEEDS_SUDO" = true ]; then
        COMPOSE_CMD="sudo docker-compose"
        DOCKER_CMD=""
        echo -e "${YELLOW}Utilizzo sudo docker-compose (legacy)${NC}"
    else
        COMPOSE_CMD="docker-compose"
        DOCKER_CMD=""
        echo -e "${YELLOW}Utilizzo docker-compose (legacy)${NC}"
    fi
else
    echo -e "${RED}ERRORE: Né 'docker compose' né 'docker-compose' sono disponibili.${NC}"
    exit 1
fi

echo -e "${CYAN}Controllo ultima release disponibile...${NC}"
if command -v curl &> /dev/null; then
    LATEST_RELEASE=$(curl -s https://api.github.com/repos/ZELA2000/crazy-phoneTTS/releases/latest)
    LATEST_VERSION=$(echo $LATEST_RELEASE | grep -o '"tag_name": "[^"]*' | cut -d'"' -f4)
elif command -v wget &> /dev/null; then
    LATEST_RELEASE=$(wget -qO- https://api.github.com/repos/ZELA2000/crazy-phoneTTS/releases/latest)
    LATEST_VERSION=$(echo $LATEST_RELEASE | grep -o '"tag_name": "[^"]*' | cut -d'"' -f4)
else
    echo -e "${YELLOW}ATTENZIONE: curl o wget non trovati.${NC}"
    LATEST_VERSION="unknown"
fi

if [ -f VERSION ]; then
    CURRENT_VERSION=$(cat VERSION | tr -d '\r\n')
else
    CURRENT_VERSION="unknown"
fi

if [ "$LATEST_VERSION" != "unknown" ]; then
    echo -e "  ${YELLOW}Versione corrente: $CURRENT_VERSION${NC}"
    echo -e "  ${GREEN}Ultima versione:   $LATEST_VERSION${NC}"
    
    if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
        echo ""
        echo -e "${GREEN}Sei gia aggiornato all ultima versione!${NC}"
        read -p "Vuoi forzare l aggiornamento comunque? (s/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
            exit 0
        fi
    fi
fi

if [ "$SKIP_CONFIRM" = false ]; then
    echo ""
    echo -e "${YELLOW}Questo script effettuera le seguenti operazioni:${NC}"
    echo -e "${YELLOW}  1. Crea un backup completo del progetto (incluso .git)${NC}"
    echo -e "${YELLOW}  2. Scarica l ultima release da GitHub ($LATEST_VERSION)${NC}"
    echo -e "${YELLOW}  3. Ferma i container in esecuzione${NC}"
    echo -e "${YELLOW}  4. Riavvia i container con le nuove modifiche${NC}"
    echo -e "${YELLOW}  5. In caso di errore, ripristina il backup automaticamente${NC}"
    echo ""
    echo -e "${RED}ATTENZIONE: Il servizio sara temporaneamente offline durante l aggiornamento.${NC}"
    echo ""
    
    read -p "Vuoi continuare? (s/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
        echo -e "${YELLOW}Aggiornamento annullato.${NC}"
        exit 0
    fi
fi

CURRENT_DIR=$(pwd)
PARENT_DIR=$(dirname "$CURRENT_DIR")
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="$PARENT_DIR/crazy-phoneTTS_backup_$TIMESTAMP"

restore_backup() {
    echo -e "${YELLOW}  - Ripristino del backup...${NC}"
    cd "$PARENT_DIR"
    
    # Rimuovi file e directory con attenzione per evitare errori "Device or resource busy"
    find "$CURRENT_DIR" -mindepth 1 -maxdepth 1 ! -name 'uploads' ! -name 'output' -exec rm -rf {} + 2>/dev/null || true
    
    # Copia il backup
    cp -rf "$BACKUP_PATH"/. "$CURRENT_DIR"/
    cd "$CURRENT_DIR"
    echo -e "${GREEN}  - Backup ripristinato con successo${NC}"
}

echo ""
echo -e "${CYAN}Pulizia vecchi backup...${NC}"
OLD_BACKUPS=$(find "$PARENT_DIR" -maxdepth 1 -type d -name "crazy-phoneTTS_backup_*" | sort -r | tail -n +3)
if [ -n "$OLD_BACKUPS" ]; then
    echo "$OLD_BACKUPS" | while read backup; do
        echo -e "  ${GRAY}- Rimozione vecchio backup: $(basename $backup)${NC}"
        rm -rf "$backup" 2>/dev/null || true
    done
fi

echo ""
echo -e "${CYAN}[1/5] Creazione backup completo...${NC}"
echo -e "  ${GRAY}- Backup in corso: $BACKUP_PATH${NC}"

mkdir -p "$BACKUP_PATH"

if ! cp -rf "$CURRENT_DIR"/. "$BACKUP_PATH"/; then
    echo -e "${RED}ERRORE: Impossibile creare il backup.${NC}"
    exit 1
fi
echo -e "  ${GREEN}- Backup creato con successo (incluso .git)${NC}"

echo ""
echo -e "${CYAN}[2/5] Scaricamento ultima release da GitHub...${NC}"

if [ "$GIT_AVAILABLE" = true ]; then
    # Metodo 1: Usa Git (preferito)
    echo -e "  ${GRAY}- Utilizzo Git per l'aggiornamento...${NC}"
    
    if [[ -n $(git status --porcelain) ]]; then
        echo -e "  ${YELLOW}- Trovate modifiche locali, salvataggio in stash...${NC}"
        git stash push -m "Auto-stash before update"
        HAS_CHANGES=true
    else
        HAS_CHANGES=false
    fi

    echo -e "  ${GRAY}- Download delle release...${NC}"
    if ! git fetch --tags --force; then
        echo -e "${RED}ERRORE: Impossibile scaricare gli aggiornamenti.${NC}"
        restore_backup
        exit 1
    fi

    if [ "$LATEST_VERSION" != "unknown" ]; then
        echo -e "  ${GRAY}- Checkout della versione $LATEST_VERSION...${NC}"
        if ! git checkout "$LATEST_VERSION" -f; then
            echo -e "${RED}ERRORE: Impossibile fare checkout della release.${NC}"
            restore_backup
            exit 1
        fi
    else
        echo -e "  ${GRAY}- Eseguo git pull...${NC}"
        if ! git pull; then
            echo -e "${RED}ERRORE: Git pull fallito.${NC}"
            restore_backup
            exit 1
        fi
    fi

    if [ "$HAS_CHANGES" = true ]; then
        echo -e "  ${YELLOW}- Tentativo ripristino modifiche locali...${NC}"
        if ! git stash pop 2>/dev/null; then
            echo -e "  ${YELLOW}- ATTENZIONE: Alcune modifiche locali potrebbero essere in conflitto${NC}"
            echo -e "  ${YELLOW}- Le modifiche sono salvate in: git stash list${NC}"
        fi
    fi
else
    # Metodo 2: Download ZIP manuale (fallback)
    echo -e "  ${GRAY}- Download ZIP dalla release GitHub...${NC}"
    
    ZIP_URL="https://github.com/ZELA2000/crazy-phoneTTS/archive/refs/heads/main.zip"
    ZIP_PATH="/tmp/crazy-phoneTTS-update.zip"
    EXTRACT_PATH="/tmp/crazy-phoneTTS-extract"
    
    # Download ZIP
    echo -e "  ${GRAY}- Download in corso da GitHub...${NC}"
    if command -v curl &> /dev/null; then
        if ! curl -L "$ZIP_URL" -o "$ZIP_PATH"; then
            echo -e "${RED}ERRORE: Download fallito.${NC}"
            restore_backup
            exit 1
        fi
    elif command -v wget &> /dev/null; then
        if ! wget "$ZIP_URL" -O "$ZIP_PATH"; then
            echo -e "${RED}ERRORE: Download fallito.${NC}"
            restore_backup
            exit 1
        fi
    else
        echo -e "${RED}ERRORE: curl o wget non disponibili.${NC}"
        restore_backup
        exit 1
    fi
    
    # Estrazione
    echo -e "  ${GRAY}- Estrazione archivio...${NC}"
    rm -rf "$EXTRACT_PATH" 2>/dev/null || true
    mkdir -p "$EXTRACT_PATH"
    
    # Prova diversi metodi di estrazione
    if command -v unzip &> /dev/null; then
        if ! unzip -q "$ZIP_PATH" -d "$EXTRACT_PATH"; then
            echo -e "${RED}ERRORE: Estrazione fallita.${NC}"
            restore_backup
            exit 1
        fi
    elif command -v 7z &> /dev/null; then
        if ! 7z x "$ZIP_PATH" -o"$EXTRACT_PATH" -y > /dev/null; then
            echo -e "${RED}ERRORE: Estrazione fallita.${NC}"
            restore_backup
            exit 1
        fi
    elif command -v python3 &> /dev/null; then
        if ! python3 -m zipfile -e "$ZIP_PATH" "$EXTRACT_PATH"; then
            echo -e "${RED}ERRORE: Estrazione fallita.${NC}"
            restore_backup
            exit 1
        fi
    elif command -v python &> /dev/null; then
        if ! python -m zipfile -e "$ZIP_PATH" "$EXTRACT_PATH"; then
            echo -e "${RED}ERRORE: Estrazione fallita.${NC}"
            restore_backup
            exit 1
        fi
    else
        echo -e "${RED}ERRORE: Nessun tool di estrazione ZIP disponibile (unzip/7z/python).${NC}"
        restore_backup
        exit 1
    fi
    
    # Trova la cartella estratta
    EXTRACTED_FOLDER=$(ls -1 "$EXTRACT_PATH" | head -n 1)
    
    # Copia solo i file necessari (escludi .git, .env, uploads, output)
    echo -e "  ${GRAY}- Aggiornamento file di sistema...${NC}"
    
    cd "$EXTRACT_PATH/$EXTRACTED_FOLDER"
    
    # Metodo semplificato: usa rsync se disponibile, altrimenti cp con esclusioni
    if command -v rsync &> /dev/null; then
        rsync -av --exclude='.git' --exclude='uploads/' --exclude='output/' --exclude='backup*/' --exclude='node_modules/' --exclude='.env' --exclude='.env.local' ./ "$CURRENT_DIR/" > /dev/null
    else
        # Copia tutti i file escludendo le directory sensibili
        for item in *; do
            if [ "$item" != ".git" ] && [ "$item" != "uploads" ] && [ "$item" != "output" ] && [ "$item" != "node_modules" ]; then
                cp -rf "$item" "$CURRENT_DIR/" 2>/dev/null || true
            fi
        done
        
        # Copia i file nascosti escludendo .git e .env
        for item in .[^.]*; do
            if [ -e "$item" ] && [ "$item" != ".git" ] && [ "$item" != ".env" ] && [ "$item" != ".env.local" ]; then
                cp -rf "$item" "$CURRENT_DIR/" 2>/dev/null || true
            fi
        done
    fi
    
    cd "$CURRENT_DIR"
    
    # Pulizia
    rm -f "$ZIP_PATH" 2>/dev/null || true
    rm -rf "$EXTRACT_PATH" 2>/dev/null || true
fi

echo -e "  ${GREEN}- Aggiornamenti scaricati con successo${NC}"

echo ""
echo -e "${CYAN}[3/5] Arresto dei container...${NC}"
# Aumenta il timeout per sistemi lenti (es. NAS)
export COMPOSE_HTTP_TIMEOUT=300
if [ -n "$DOCKER_CMD" ]; then
    FULL_CMD="$DOCKER_CMD $COMPOSE_CMD down --timeout 120"
else
    FULL_CMD="$COMPOSE_CMD down --timeout 120"
fi
if ! $FULL_CMD; then
    echo -e "${RED}ERRORE: Impossibile fermare i container.${NC}"
    restore_backup
    exit 1
fi
echo -e "  ${GREEN}- Container fermati con successo${NC}"

echo ""
echo -e "${CYAN}[4/5] Build delle nuove immagini...${NC}"
if [ -n "$DOCKER_CMD" ]; then
    FULL_CMD_BUILD="$DOCKER_CMD $COMPOSE_CMD build"
    FULL_CMD_UP="$DOCKER_CMD $COMPOSE_CMD up -d"
else
    FULL_CMD_BUILD="$COMPOSE_CMD build"
    FULL_CMD_UP="$COMPOSE_CMD up -d"
fi
if ! $FULL_CMD_BUILD; then
    echo -e "${RED}ERRORE: Build fallita.${NC}"
    restore_backup
    echo -e "  ${YELLOW}- Riavvio dei container con la versione precedente...${NC}"
    $FULL_CMD_UP
    exit 1
fi
echo -e "  ${GREEN}- Build completata con successo${NC}"

echo ""
echo -e "${CYAN}[5/5] Avvio dei container...${NC}"
if [ -n "$DOCKER_CMD" ]; then
    FULL_CMD_UP="$DOCKER_CMD $COMPOSE_CMD up -d"
    FULL_CMD_DOWN="$DOCKER_CMD $COMPOSE_CMD down"
    FULL_CMD_PS="$DOCKER_CMD $COMPOSE_CMD ps -q"
else
    FULL_CMD_UP="$COMPOSE_CMD up -d"
    FULL_CMD_DOWN="$COMPOSE_CMD down"
    FULL_CMD_PS="$COMPOSE_CMD ps -q"
fi

if ! $FULL_CMD_UP; then
    echo -e "${RED}ERRORE: Impossibile avviare i container.${NC}"
    $FULL_CMD_DOWN
    restore_backup
    echo -e "  ${YELLOW}- Riavvio dei container con la versione precedente...${NC}"
    $FULL_CMD_UP
    exit 1
fi

echo -e "  ${GRAY}- Attendo avvio dei container...${NC}"
sleep 10

# Verifica che i container siano in esecuzione usando docker ps
RUNNING_CONTAINERS=$($FULL_CMD_PS | wc -l)
if [ "$RUNNING_CONTAINERS" -lt 2 ]; then
    echo -e "${RED}ERRORE: Non tutti i container sono in esecuzione.${NC}"
    $FULL_CMD_DOWN
    restore_backup
    echo -e "  ${YELLOW}- Riavvio dei container con la versione precedente...${NC}"
    $FULL_CMD_UP
    exit 1
fi

echo -e "  ${GREEN}- Container avviati con successo${NC}"

echo ""
echo -e "${GREEN}=== Aggiornamento completato con successo! ===${NC}"
echo ""
echo -e "${CYAN}Versione aggiornata: $LATEST_VERSION${NC}"
echo ""
echo -e "${CYAN}I servizi sono ora disponibili:${NC}"
echo -e "${CYAN}  - Frontend: http://localhost:3000${NC}"
echo -e "${CYAN}  - Backend:  http://localhost:8000${NC}"
echo ""
echo -e "${GRAY}Backup salvato in: $BACKUP_PATH${NC}"
echo -e "${GRAY}Puoi eliminarlo manualmente se tutto funziona correttamente.${NC}"
echo ""
if [ -n "$DOCKER_CMD" ]; then
    echo -e "${GRAY}Controlla lo stato dei container con: $DOCKER_CMD $COMPOSE_CMD ps${NC}"
else
    echo -e "${GRAY}Controlla lo stato dei container con: $COMPOSE_CMD ps${NC}"
fi
