#!/bin/bash
set -e

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

if ! command -v git &> /dev/null; then
    echo -e "${RED}ERRORE: Git non e installato.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERRORE: Docker non e installato.${NC}"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo -e "${RED}ERRORE: Docker non e in esecuzione.${NC}"
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
    rm -rf "$CURRENT_DIR"/*
    rm -rf "$CURRENT_DIR"/.*  2>/dev/null || true
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

echo -e "  ${GREEN}- Aggiornamenti scaricati con successo${NC}"

echo ""
echo -e "${CYAN}[3/5] Arresto dei container...${NC}"
if ! docker compose down; then
    echo -e "${RED}ERRORE: Impossibile fermare i container.${NC}"
    restore_backup
    exit 1
fi
echo -e "  ${GREEN}- Container fermati con successo${NC}"

echo ""
echo -e "${CYAN}[4/5] Build delle nuove immagini...${NC}"
if ! docker compose build; then
    echo -e "${RED}ERRORE: Build fallita.${NC}"
    restore_backup
    echo -e "  ${YELLOW}- Riavvio dei container con la versione precedente...${NC}"
    docker compose up -d
    exit 1
fi
echo -e "  ${GREEN}- Build completata con successo${NC}"

echo ""
echo -e "${CYAN}[5/5] Avvio dei container...${NC}"
if ! docker compose up -d; then
    echo -e "${RED}ERRORE: Impossibile avviare i container.${NC}"
    docker compose down
    restore_backup
    echo -e "  ${YELLOW}- Riavvio dei container con la versione precedente...${NC}"
    docker compose up -d
    exit 1
fi

echo -e "  ${GRAY}- Attendo avvio dei container...${NC}"
sleep 5

RUNNING_CONTAINERS=$(docker compose ps --status running --quiet | wc -l)
if [ "$RUNNING_CONTAINERS" -lt 2 ]; then
    echo -e "${RED}ERRORE: Non tutti i container sono in esecuzione.${NC}"
    docker compose down
    restore_backup
    echo -e "  ${YELLOW}- Riavvio dei container con la versione precedente...${NC}"
    docker compose up -d
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
echo -e "${GRAY}Controlla lo stato dei container con: docker compose ps${NC}"
