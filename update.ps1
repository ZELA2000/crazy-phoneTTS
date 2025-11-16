param([switch]$SkipConfirm = $false)

$ErrorActionPreference = "Stop"

Write-Host "=== crazy-phoneTTS Update Script ===" -ForegroundColor Cyan
Write-Host ""

# Verifica che git sia installato
try {
    git --version | Out-Null
}
catch {
    Write-Host "ERRORE: Git non e installato. Installa Git per continuare." -ForegroundColor Red
    exit 1
}

# Verifica che docker sia in esecuzione
try {
    docker ps | Out-Null
}
catch {
    Write-Host "ERRORE: Docker non e in esecuzione. Avvia Docker Desktop." -ForegroundColor Red
    exit 1
}

# Ottieni ultima release da GitHub
Write-Host "Controllo ultima release disponibile..." -ForegroundColor Cyan
try {
    $latestRelease = Invoke-RestMethod -Uri "https://api.github.com/repos/ZELA2000/crazy-phoneTTS/releases/latest" -ErrorAction Stop
    $latestVersion = $latestRelease.tag_name
    $currentVersion = (Get-Content VERSION -ErrorAction SilentlyContinue) -replace "`r|`n", ""
    
    Write-Host "  Versione corrente: $currentVersion" -ForegroundColor Yellow
    Write-Host "  Ultima versione:   $latestVersion" -ForegroundColor Green
    
    if ($currentVersion -eq $latestVersion) {
        Write-Host ""
        Write-Host "Sei gia aggiornato all ultima versione!" -ForegroundColor Green
        $response = Read-Host "Vuoi forzare l aggiornamento comunque? (s/N)"
        if ($response -ne "s" -and $response -ne "S") {
            exit 0
        }
    }
}
catch {
    Write-Host "ATTENZIONE: Impossibile verificare l ultima release. Continuo comunque..." -ForegroundColor Yellow
    $latestVersion = "unknown"
}

# Chiedi conferma se non e specificato -SkipConfirm
if (-not $SkipConfirm) {
    Write-Host ""
    Write-Host "Questo script effettuera le seguenti operazioni:" -ForegroundColor Yellow
    Write-Host "  1. Crea un backup completo del progetto (incluso .git)" -ForegroundColor Yellow
    Write-Host "  2. Scarica l ultima release da GitHub ($latestVersion)" -ForegroundColor Yellow
    Write-Host "  3. Ferma i container in esecuzione" -ForegroundColor Yellow
    Write-Host "  4. Riavvia i container con le nuove modifiche" -ForegroundColor Yellow
    Write-Host "  5. In caso di errore, ripristina il backup automaticamente" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "ATTENZIONE: Il servizio sara temporaneamente offline durante l aggiornamento." -ForegroundColor Red
    Write-Host ""
    
    $response = Read-Host "Vuoi continuare? (s/N)"
    if ($response -ne "s" -and $response -ne "S" -and $response -ne "si" -and $response -ne "Si" -and $response -ne "SI") {
        Write-Host "Aggiornamento annullato." -ForegroundColor Yellow
        exit 0
    }
}

# Salva la directory corrente e definisci il percorso del backup
$currentDir = Get-Location
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$parentDir = Split-Path -Parent $currentDir
$backupPath = Join-Path $parentDir "crazy-phoneTTS_backup_$timestamp"

# Funzione per ripristinare il backup
function Restore-Backup {
    Write-Host "  - Ripristino del backup..." -ForegroundColor Yellow
    
    try {
        Set-Location $parentDir
        Get-ChildItem -Path $currentDir -Force -Recurse | Remove-Item -Force -Recurse -ErrorAction Stop
        Get-ChildItem -Path $backupPath -Force | ForEach-Object {
            Copy-Item -Path $_.FullName -Destination $currentDir -Recurse -Force -ErrorAction Stop
        }
        Set-Location $currentDir
        Write-Host "  - Backup ripristinato con successo" -ForegroundColor Green
    }
    catch {
        Write-Host "  - ERRORE nel ripristino del backup!" -ForegroundColor Red
        Write-Host "  - Backup manuale richiesto da: $backupPath" -ForegroundColor Red
    }
}

# Pulisci vecchi backup (mantieni solo i 2 piu recenti)
Write-Host ""
Write-Host "Pulizia vecchi backup..." -ForegroundColor Cyan
try {
    $oldBackups = Get-ChildItem -Path $parentDir -Directory -Filter "crazy-phoneTTS_backup_*" | 
    Sort-Object Name -Descending | 
    Select-Object -Skip 2
    
    if ($oldBackups) {
        foreach ($backup in $oldBackups) {
            Write-Host "  - Rimozione vecchio backup: $($backup.Name)" -ForegroundColor Gray
            Remove-Item -Path $backup.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}
catch {
    Write-Host "  - Impossibile pulire vecchi backup (non critico)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[1/5] Creazione backup completo..." -ForegroundColor Cyan
try {
    Write-Host "  - Backup in corso: $backupPath" -ForegroundColor Gray
    New-Item -Path $backupPath -ItemType Directory -Force | Out-Null
    Get-ChildItem -Path $currentDir -Force | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $backupPath -Recurse -Force -ErrorAction Stop
    }
    Write-Host "  - Backup creato con successo (incluso .git)" -ForegroundColor Green
}
catch {
    Write-Host "ERRORE: Impossibile creare il backup." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/5] Scaricamento ultima release da GitHub..." -ForegroundColor Cyan
try {
    $hasChanges = git status --porcelain
    if ($hasChanges) {
        Write-Host "  - Trovate modifiche locali, salvataggio in stash..." -ForegroundColor Yellow
        git stash push -m "Auto-stash before update"
    }
    
    Write-Host "  - Download delle release..." -ForegroundColor Gray
    git fetch --tags --force
    
    if ($latestVersion -ne "unknown") {
        Write-Host "  - Checkout della versione $latestVersion..." -ForegroundColor Gray
        git checkout $latestVersion -f
    }
    else {
        Write-Host "  - Eseguo git pull..." -ForegroundColor Gray
        git pull
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Git checkout/pull fallito"
    }
    
    if ($hasChanges) {
        Write-Host "  - Tentativo ripristino modifiche locali..." -ForegroundColor Yellow
        git stash pop 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  - ATTENZIONE: Alcune modifiche locali potrebbero essere in conflitto" -ForegroundColor Yellow
            Write-Host "  - Le modifiche sono salvate in: git stash list" -ForegroundColor Yellow
        }
    }
    
    Write-Host "  - Aggiornamenti scaricati con successo" -ForegroundColor Green
}
catch {
    Write-Host "ERRORE: Impossibile scaricare gli aggiornamenti." -ForegroundColor Red
    Restore-Backup
    exit 1
}

Write-Host ""
Write-Host "[3/5] Arresto dei container..." -ForegroundColor Cyan
try {
    docker compose down
    if ($LASTEXITCODE -ne 0) {
        throw "Docker compose down fallito"
    }
    Write-Host "  - Container fermati con successo" -ForegroundColor Green
}
catch {
    Write-Host "ERRORE: Impossibile fermare i container." -ForegroundColor Red
    Restore-Backup
    exit 1
}

Write-Host ""
Write-Host "[4/5] Build delle nuove immagini..." -ForegroundColor Cyan
try {
    docker compose build
    if ($LASTEXITCODE -ne 0) {
        throw "Docker compose build fallito"
    }
    Write-Host "  - Build completata con successo" -ForegroundColor Green
}
catch {
    Write-Host "ERRORE: Build fallita." -ForegroundColor Red
    Restore-Backup
    Write-Host "  - Riavvio dei container con la versione precedente..." -ForegroundColor Yellow
    docker compose up -d
    exit 1
}

Write-Host ""
Write-Host "[5/5] Avvio dei container..." -ForegroundColor Cyan
try {
    docker compose up -d
    if ($LASTEXITCODE -ne 0) {
        throw "Docker compose up fallito"
    }
    
    Write-Host "  - Attendo avvio dei container..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
    
    $runningContainers = docker compose ps --status running --format json | ConvertFrom-Json
    if ($runningContainers.Count -lt 2) {
        throw "Non tutti i container sono in esecuzione"
    }
    
    Write-Host "  - Container avviati con successo" -ForegroundColor Green
}
catch {
    Write-Host "ERRORE: Impossibile avviare i container." -ForegroundColor Red
    docker compose down -ErrorAction SilentlyContinue
    Restore-Backup
    Write-Host "  - Riavvio dei container con la versione precedente..." -ForegroundColor Yellow
    docker compose up -d
    exit 1
}

Write-Host ""
Write-Host "=== Aggiornamento completato con successo! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Versione aggiornata: $latestVersion" -ForegroundColor Cyan
Write-Host ""
Write-Host "I servizi sono ora disponibili:" -ForegroundColor Cyan
Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  - Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backup salvato in: $backupPath" -ForegroundColor Gray
Write-Host "Puoi eliminarlo manualmente se tutto funziona correttamente." -ForegroundColor Gray
Write-Host ""
Write-Host "Controlla lo stato dei container con: docker compose ps" -ForegroundColor Gray
