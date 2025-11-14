# 🔄 Sistema Auto-Aggiornamento Host-Side

## 📋 Come Funziona

Il sistema di auto-aggiornamento ora funziona correttamente perché:

1. **Backend (Container)** crea una richiesta di aggiornamento
2. **Host Watcher** rileva la richiesta ed esegue lo script
3. **Script Host** aggiorna Docker e riavvia tutto
4. **Frontend** monitora il progress via file persistente

## 🚀 Avvio Sistema Completo

### Windows:
```powershell
# 1. Avvia Docker Compose
docker-compose up -d

# 2. Avvia Host Watcher (in una finestra separata)
.\update_watcher.ps1
```

### Linux/Mac:
```bash
# 1. Avvia Docker Compose  
docker-compose up -d

# 2. Avvia Host Watcher (in un terminale separato)
chmod +x update_watcher.sh
./update_watcher.sh
```

## 📊 Flusso Aggiornamento

```
Frontend → Richiesta Aggiornamento
    ↓
Backend → Crea update_request.json
    ↓  
Host Watcher → Rileva richiesta
    ↓
Host Watcher → Esegue update_script.ps1/sh
    ↓
Script Host → Ferma Docker → Aggiorna → Riavvia
    ↓
Frontend → Riconnette automaticamente → Mostra completamento
```

## 🔧 File Coinvolti

- `update_watcher.ps1` - Watcher PowerShell (Windows)  
- `update_watcher.sh` - Watcher Bash (Linux/Mac)
- `update_request.json` - File richiesta (creato dal backend)
- `update_progress.json` - File progress (aggiornato da host + backend)
- `update_script.ps1` - Script aggiornamento PowerShell
- `update_script.sh` - Script aggiornamento Bash

## ⚠️ Importante

- **Host Watcher deve essere sempre attivo** per ricevere richieste di aggiornamento
- Il watcher monitora ogni 5 secondi la presenza di richieste
- Durante l'aggiornamento Docker si ferma (normale)
- Frontend continua a monitorare via polling e riconnette automaticamente

## 🎯 Test del Sistema

1. Avvia sistema completo (Docker + Host Watcher)
2. Vai su http://localhost:3000  
3. Se disponibile, clicca "Aggiorna Ora"
4. Osserva:
   - Progress bar continua (anche con Docker spento)
   - Host Watcher esegue aggiornamento
   - Sistema si riavvia automaticamente
   - Frontend riconnette e mostra completamento

## 🐛 Troubleshooting

**Host Watcher non rileva richieste:**
- Verifica che il watcher sia avviato
- Controlla che la directory sia corretta  
- Verifica permessi file update_request.json

**Script non esegue:**
- Windows: Verifica ExecutionPolicy PowerShell
- Linux/Mac: Verifica permessi esecuzione chmod +x

**Docker non riavvia:**
- Verifica che Docker Desktop sia avviato
- Controlla che docker-compose.yml sia valido