#!/bin/bash
# Update Watcher - Monitora richieste di aggiornamento dal container
# Questo script deve essere eseguito sull'HOST, non nel container

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${1:-$SCRIPT_DIR}"
CHECK_INTERVAL="${2:-5}"

print_log() {
    local timestamp=$(date '+%H:%M:%S')
    local color=""
    case "$2" in
        "green") color="\033[1;32m" ;;
        "yellow") color="\033[1;33m" ;;
        "red") color="\033[1;31m" ;;
        "cyan") color="\033[1;36m" ;;
        *) color="\033[1;37m" ;;
    esac
    echo -e "${color}[$timestamp] $1\033[0m"
}

update_progress() {
    local step="$1"
    local message="$2"
    local percentage="$3"
    local status="${4:-running}"
    
    local progress_data=$(cat <<EOF
{
    "type": "progress",
    "step": "$step",
    "message": "$message", 
    "percentage": $percentage,
    "status": "$status",
    "timestamp": "$(date -Iseconds)"
}
EOF
)
    
    echo "$progress_data" > "$PROGRESS_FILE"
    print_log "$message" "cyan"
}

REQUEST_FILE="$PROJECT_DIR/update_request.json"
PROGRESS_FILE="$PROJECT_DIR/update_progress.json"

print_log "🔍 Update Watcher avviato" "green"
print_log "📂 Directory progetto: $PROJECT_DIR"
print_log "⏱️ Intervallo controllo: $CHECK_INTERVAL secondi"
echo

while true; do
    if [ -f "$REQUEST_FILE" ]; then
        print_log "🚨 Rilevata richiesta di aggiornamento!" "yellow"
        
        # Leggi richiesta
        if command -v jq >/dev/null 2>&1; then
            VERSION=$(jq -r '.version' "$REQUEST_FILE")
            SCRIPT=$(jq -r '.script' "$REQUEST_FILE")
        else
            # Fallback senza jq
            VERSION=$(grep '"version"' "$REQUEST_FILE" | cut -d'"' -f4)
            SCRIPT=$(grep '"script"' "$REQUEST_FILE" | cut -d'"' -f4)
        fi
        
        print_log "📋 Versione richiesta: $VERSION" "green"
        print_log "📋 Script da eseguire: $SCRIPT" "green"
        
        # Rimuovi file richiesta
        rm -f "$REQUEST_FILE"
        
        # Aggiorna progress
        update_progress "host_takeover" "🔄 Host prende controllo dell'aggiornamento..." 30
        
        # Determina script
        if [ "$SCRIPT" = "update_script.ps1" ]; then
            SCRIPT_PATH="$PROJECT_DIR/update_script.ps1"
        else
            SCRIPT_PATH="$PROJECT_DIR/update_script.sh"
        fi
        
        if [ ! -f "$SCRIPT_PATH" ]; then
            update_progress "error" "❌ Script non trovato: $SCRIPT_PATH" 0 "error"
            continue
        fi
        
        print_log "🚀 Eseguendo script di aggiornamento..." "yellow"
        update_progress "executing_host" "🚀 Esecuzione script su host..." 40
        
        # Esegui script
        cd "$PROJECT_DIR"
        if [ "$SCRIPT" = "update_script.ps1" ]; then
            # PowerShell su sistemi che lo supportano
            if command -v pwsh >/dev/null 2>&1; then
                pwsh -ExecutionPolicy Bypass -File "$SCRIPT_PATH" "$VERSION"
            elif command -v powershell >/dev/null 2>&1; then
                powershell -ExecutionPolicy Bypass -File "$SCRIPT_PATH" "$VERSION"
            else
                update_progress "error" "❌ PowerShell non disponibile per eseguire $SCRIPT" 0 "error"
                continue
            fi
        else
            bash "$SCRIPT_PATH" "$VERSION"
        fi
        
        EXIT_CODE=$?
        
        if [ $EXIT_CODE -eq 0 ]; then
            print_log "✅ Aggiornamento completato con successo!" "green"
            update_progress "completed" "🎉 Aggiornamento host completato!" 100 "completed"
        else
            update_progress "error" "❌ Script terminato con errore: $EXIT_CODE" 0 "error"
        fi
    fi
    
    sleep "$CHECK_INTERVAL"
done