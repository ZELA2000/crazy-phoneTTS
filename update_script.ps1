# Script di aggiornamento per Windows
# Parametro: $args[0] = nuova versione
param(
    [string]$NewVersion = "latest"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

# Funzione per salvare il progresso
function Save-UpdateProgress {
    param($Status, $Step, $Percentage, $Message, $Info = "")
    
    $Progress = @{
        status = $Status
        step = $Step
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffffffK")
        percentage = $Percentage
        type = "progress"
        message = $Message
    }
    
    if ($Info) {
        $Progress.info = $Info
    }
    
    $ProgressJson = $Progress | ConvertTo-Json -Depth 10
    $ProgressJson | Out-File -FilePath "update_progress.json" -Encoding UTF8 -Force
}

Write-Host "🚀 Avvio aggiornamento crazy-phoneTTS a versione $NewVersion"
Save-UpdateProgress "running" "start" 0 "🚀 Avvio aggiornamento crazy-phoneTTS a versione $NewVersion"

try {
    # Salva la directory corrente
    $OriginalPath = Get-Location
    $ProjectPath = Split-Path -Parent $MyInvocation.MyCommand.Path

    Set-Location $ProjectPath
    Write-Host "📂 Directory progetto: $ProjectPath"

    # Step 1: Verifica Docker
    Write-Host "🐳 Verifica Docker..."
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker non trovato! Installare Docker Desktop."
    }
    Write-Host "✅ Docker: $dockerVersion"

    # Step 2: Verifica Docker Compose  
    Write-Host "🔧 Verifica Docker Compose..."
    Save-UpdateProgress "running" "compose_check" 10 "🔧 Verifica Docker Compose..."
    $composeVersion = docker-compose --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose non trovato!"
    }
    Write-Host "✅ Docker Compose: $composeVersion"

    # Step 3: Backup configurazione
    Write-Host "💾 Backup configurazione..."
    Save-UpdateProgress "running" "backup" 15 "💾 Creazione backup..."
    $BackupDir = "backup_" + (Get-Date -Format "yyyyMMdd_HHmmss")
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    
    if (Test-Path ".env") {
        Copy-Item ".env" "$BackupDir\" -Force
        Write-Host "✅ Backup .env salvato in $BackupDir"
    }
    
    if (Test-Path "backend/uploads") {
        Copy-Item "backend/uploads" "$BackupDir\" -Recurse -Force
        Write-Host "✅ Backup uploads salvato in $BackupDir"
    }

    if (Test-Path "backend/output") {
        Copy-Item "backend/output" "$BackupDir\" -Recurse -Force
        Write-Host "✅ Backup output salvato in $BackupDir"
    }

    # Step 3.1: Backup completo del progetto per sicurezza
    Write-Host "💾 Backup completo del progetto..."
    $FullBackupDir = "$BackupDir\full_project"
    New-Item -ItemType Directory -Path $FullBackupDir -Force | Out-Null
    
    # Esclude SOLO cartelle git locali, temporanee e di backup
    # INCLUDE: .github (Actions), .gitignore, .gitattributes 
    $ExcludePatterns = @("backup_*", ".git", "node_modules", "__pycache__", "*.tmp")
    
    Write-Host "📋 File esclusi dal backup: .git (solo repo locale), backup_*, node_modules, __pycache__, *.tmp" -ForegroundColor DarkCyan
    Write-Host "📋 File inclusi: .github, .gitignore, .gitattributes, codice sorgente" -ForegroundColor DarkGreen
    
    Get-ChildItem -Path . -Force | Where-Object { 
        $item = $_
        $shouldExclude = $false
        foreach ($pattern in $ExcludePatterns) {
            if ($item.Name -like $pattern) {
                $shouldExclude = $true
                break
            }
        }
        return !$shouldExclude
    } | ForEach-Object {
        $destination = Join-Path $FullBackupDir $_.Name
        try {
            if ($_.PSIsContainer) {
                Copy-Item $_.FullName $destination -Recurse -Force -ErrorAction SilentlyContinue
            } else {
                Copy-Item $_.FullName $destination -Force -ErrorAction SilentlyContinue
            }
            Write-Host "  📁 $($_.Name)" -ForegroundColor DarkGray
        } catch {
            Write-Host "  ⚠️ Errore copia $($_.Name): $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    Write-Host "✅ Backup completo salvato in $FullBackupDir"

    # Step 3.2: Pulizia backup vecchi (mantiene solo i 10 più recenti)
    Write-Host "🧹 Pulizia backup vecchi..."
    
    $AllBackups = Get-ChildItem -Directory -Name "backup_*" | Sort-Object CreationTime
    $BackupCount = $AllBackups.Count
    
    if ($BackupCount -gt 10) {
        Write-Host "⚠️ Trovati $BackupCount backup, rimuovo i più vecchi..." -ForegroundColor Yellow
        
        $BackupsToRemove = $AllBackups | Select-Object -First ($BackupCount - 10)
        
        foreach ($OldBackup in $BackupsToRemove) {
            if (Test-Path $OldBackup) {
                Remove-Item -Path $OldBackup -Recurse -Force
                Write-Host "  🗑️ Rimosso: $OldBackup" -ForegroundColor DarkGray
            }
        }
        
        $NewCount = (Get-ChildItem -Directory -Name "backup_*").Count
        Write-Host "✅ Backup ridotti da $BackupCount a $NewCount (mantenuti i 10 più recenti)"
    } else {
        Write-Host "✅ Backup attuali: $BackupCount (limite: 10) - nessuna pulizia necessaria"
    }

    # Step 4: Stop containers
    Write-Host "🛑 Arresto containers..."
    Save-UpdateProgress "running" "docker_stop" 30 "🛑 Arresto containers..."
    docker-compose down 2>$null
    Write-Host "✅ Containers arrestati"

    # Step 5: Download nuova versione
    Write-Host "📦 Download versione $NewVersion da GitHub..."
    Save-UpdateProgress "running" "download" 40 "📦 Download da GitHub..."
    $TempFile = "$env:TEMP\crazy-phonetts-$NewVersion.zip"
    $DownloadUrl = "https://github.com/ZELA2000/crazy-phoneTTS/archive/refs/heads/main.zip"
    
    if ($NewVersion -ne "latest") {
        $DownloadUrl = "https://github.com/ZELA2000/crazy-phoneTTS/archive/refs/tags/$NewVersion.zip"
    }
    
    Write-Host "📥 Scaricamento da: $DownloadUrl"
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $TempFile -UseBasicParsing
    Write-Host "✅ Download completato"

    # Step 6: Estrazione
    Write-Host "📂 Estrazione archivio..."
    $TempExtract = "$env:TEMP\crazy-phonetts-extract"
    if (Test-Path $TempExtract) {
        Remove-Item $TempExtract -Recurse -Force
    }
    Expand-Archive -Path $TempFile -DestinationPath $TempExtract -Force
    
    # Trova la cartella estratta (può avere nome diverso)
    $ExtractedFolder = Get-ChildItem $TempExtract | Where-Object { $_.PSIsContainer } | Select-Object -First 1
    Write-Host "✅ Estratto in: $($ExtractedFolder.FullName)"

    # Step 7: Aggiornamento file
    Write-Host "🔄 Aggiornamento file progetto..."
    
    # Lista file da aggiornare (esclusi .env e uploads)
    $FilesToUpdate = @(
        "backend\main.py",
        "backend\Dockerfile",
        "backend\requirements.txt",
        "frontend\src\App.js",
        "frontend\src\index.css",
        "frontend\src\index.js", 
        "frontend\Dockerfile",
        "frontend\package.json",
        "frontend\public\index.html",
        "docker-compose.yml",
        "VERSION",
        "README.md",
        "FEATURES.md",
        "QUICKSTART.md",
        "update_script.ps1",
        "update_script.sh"
    )
    
    foreach ($file in $FilesToUpdate) {
        $SourceFile = Join-Path $ExtractedFolder.FullName $file
        if (Test-Path $SourceFile) {
            $DestFile = $file
            $DestDir = Split-Path $DestFile -Parent
            if ($DestDir -and !(Test-Path $DestDir)) {
                New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
            }
            Copy-Item $SourceFile $DestFile -Force
            Write-Host "✅ Aggiornato: $file"
        }
    }

    # Step 8: Ripristino configurazione
    Write-Host "⚙️ Ripristino configurazione..."
    if (Test-Path "$BackupDir\.env") {
        Copy-Item "$BackupDir\.env" "." -Force
        Write-Host "✅ Ripristinato file .env"
    }
    
    if (Test-Path "$BackupDir\uploads") {
        Copy-Item "$BackupDir\uploads\*" "backend\uploads\" -Recurse -Force
        Write-Host "✅ Ripristinati file uploads"
    }

    if (Test-Path "$BackupDir\output") {
        Copy-Item "$BackupDir\output\*" "backend\output\" -Recurse -Force
        Write-Host "✅ Ripristinati file output"
    }

    # Step 9: Rebuild containers
    Write-Host "🔨 Rebuild containers Docker..."
    docker-compose build --no-cache
    if ($LASTEXITCODE -ne 0) {
        throw "Errore durante build containers"
    }
    Write-Host "✅ Build completata"

    # Step 10: Avvio sistema
    Write-Host "🚀 Avvio sistema aggiornato..."
    Save-UpdateProgress "running" "docker_start" 80 "🚀 Avvio sistema aggiornato..."
    docker-compose up -d
    if ($LASTEXITCODE -ne 0) {
        throw "Errore durante avvio containers"
    }

    # Step 11: Verifica salute sistema
    Write-Host "🏥 Verifica salute sistema..."
    Start-Sleep -Seconds 15
    
    $healthOk = $false
    for ($i = 1; $i -le 8; $i++) {
        try {
            Write-Host "⏳ Tentativo $i/8: Controllo health endpoint..." -ForegroundColor Yellow
            $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
            if ($health.status -eq "ok") {
                Write-Host "✅ Backend funzionante!" -ForegroundColor Green
                $healthOk = $true
                break
            }
        } catch {
            if ($i -eq 8) {
                Write-Host "❌ Health check fallito dopo 8 tentativi" -ForegroundColor Red
                Write-Host "⚠️ Il sistema potrebbe essere avviato ma non risponde" -ForegroundColor Yellow
            } else {
                Write-Host "⏳ Backend non ancora pronto, attendo..." -ForegroundColor Yellow
                Start-Sleep -Seconds 8
            }
        }
    }
    
    # Verifica frontend
    if ($healthOk) {
        Write-Host "🌐 Verifica frontend..."
        try {
            $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
            if ($frontendResponse.StatusCode -eq 200) {
                Write-Host "✅ Frontend funzionante!" -ForegroundColor Green
            }
        } catch {
            Write-Host "⚠️ Frontend non risponde, ma backend è OK" -ForegroundColor Yellow
        }
    }

    # Cleanup
    Write-Host "🧹 Pulizia file temporanei..."
    if (Test-Path $TempFile) { Remove-Item $TempFile -Force }
    if (Test-Path $TempExtract) { Remove-Item $TempExtract -Recurse -Force }
    
    # Pulizia finale backup vecchi (doppio controllo)
    Write-Host "🧹 Verifica finale backup..."
    $FinalBackups = Get-ChildItem -Directory -Name "backup_*" | Sort-Object CreationTime
    if ($FinalBackups.Count -gt 10) {
        $ExtraBackups = $FinalBackups | Select-Object -First ($FinalBackups.Count - 10)
        foreach ($ExtraBackup in $ExtraBackups) {
            Remove-Item -Path $ExtraBackup -Recurse -Force -ErrorAction SilentlyContinue
        }
        Write-Host "✅ Pulizia finale backup completata"
    }
    
    Write-Host ""
    Write-Host "🎉 AGGIORNAMENTO COMPLETATO CON SUCCESSO!"
    Write-Host "🌐 Frontend: http://localhost:3000"
    Write-Host "📚 API Docs: http://localhost:8000/docs"
    Write-Host "💾 Backup salvato in: $BackupDir"
    
    Save-UpdateProgress "completed" "completed" 100 "🎉 Aggiornamento completato con successo!" "Sistema aggiornato e riavviato"

} catch {
    Write-Host ""
    Write-Host "❌ ERRORE DURANTE AGGIORNAMENTO:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    
    Save-UpdateProgress "error" "error" 0 "❌ Errore durante aggiornamento: $($_.Exception.Message)"
    
    # Tentativo di ripristino automatico
    Write-Host "🔄 Avvio ripristino automatico..." -ForegroundColor Yellow
    $FullBackupDir = "$BackupDir\full_project"
    
    if (Test-Path $FullBackupDir) {
        try {
            Write-Host "📂 Ripristino da: $FullBackupDir"
            
            # Verifica cosa abbiamo PRIMA del ripristino
            Write-Host "🔍 Stato PRIMA del ripristino:" -ForegroundColor Cyan
            if (Test-Path ".git") { 
                Write-Host "  ✅ .git presente (sarà preservato)" -ForegroundColor Green 
            } else { 
                Write-Host "  ℹ️ .git non presente (normale per download)" -ForegroundColor Cyan 
            }
            if (Test-Path ".env") { 
                Write-Host "  ✅ .env presente (sarà preservato)" -ForegroundColor Green 
            } else { 
                Write-Host "  ℹ️ .env mancante (normale)" -ForegroundColor Cyan 
            }
            
            # Arresta eventuali container in errore
            docker-compose down 2>$null
            
            # Rimuove file attuali (preservando .git locale, .env locale e backup)
            Write-Host "🗑️ Rimozione file corrotti (preservando Git locale)..." -ForegroundColor Yellow
            Get-ChildItem -Path . -Force | Where-Object { 
                !($_.Name -like "backup_*") -and 
                !($_.Name -eq ".git") -and         # Solo repo .git locale  
                !($_.Name -eq ".env")              # .env locale esistente
            } | ForEach-Object {
                try {
                    Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
                    Write-Host "  🗑️ Rimosso: $($_.Name)" -ForegroundColor DarkGray
                } catch {
                    Write-Host "  ⚠️ Non rimosso: $($_.Name)" -ForegroundColor Yellow
                }
            }
            
            # Ripristina dal backup completo
            Write-Host "📋 Ripristino file dal backup..."
            Get-ChildItem -Path $FullBackupDir -Force | ForEach-Object {
                $destination = Join-Path (Get-Location).Path $_.Name
                try {
                    if ($_.PSIsContainer) {
                        Copy-Item $_.FullName $destination -Recurse -Force
                    } else {
                        Copy-Item $_.FullName $destination -Force
                    }
                    Write-Host "  ✅ $($_.Name)" -ForegroundColor Green
                } catch {
                    Write-Host "  ❌ Errore ripristino $($_.Name): $($_.Exception.Message)" -ForegroundColor Red
                }
            }
            
            Write-Host "✅ Ripristino completato!" -ForegroundColor Green
            
            Write-Host "🔍 Stato DOPO il ripristino:" -ForegroundColor Cyan
            if (Test-Path ".git") { 
                Write-Host "  ✅ .git PRESERVATA" -ForegroundColor Green 
            } else { 
                Write-Host "  ℹ️ .git non presente (OK se non c'era prima)" -ForegroundColor Cyan 
            }
            if (Test-Path ".env") { 
                Write-Host "  ✅ .env preservata" -ForegroundColor Green 
            } else { 
                Write-Host "  ℹ️ .env ripristinata dal backup" -ForegroundColor Cyan 
            }
            if (Test-Path "backend/main.py") { 
                Write-Host "  ✅ Backend ripristinato" -ForegroundColor Green 
            } else { 
                Write-Host "  ❌ Backend MANCANTE!" -ForegroundColor Red 
            }
            if (Test-Path ".github") { 
                Write-Host "  ✅ .github (Actions) ripristinata" -ForegroundColor Green 
            } else { 
                Write-Host "  ⚠️ .github mancante" -ForegroundColor Yellow 
            }
            
            Write-Host "📁 Preservati: .git locale, .env locale, cartelle backup" -ForegroundColor Green
            Write-Host "📦 Ripristinati dal backup: codice, .github, .gitignore, config" -ForegroundColor Green
            
            # Tenta di riavviare il sistema ripristinato
            Write-Host "🚀 Riavvio sistema ripristinato..."
            docker-compose up -d 2>$null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Sistema ripristinato e riavviato con successo!" -ForegroundColor Green
                Write-Host "🌐 Controlla: http://localhost:3000" -ForegroundColor Cyan
            } else {
                Write-Host "⚠️ Sistema ripristinato ma riavvio fallito" -ForegroundColor Yellow
                Write-Host "💡 Prova manualmente: docker-compose up -d" -ForegroundColor Cyan
            }
            
        } catch {
            Write-Host "❌ Errore durante ripristino automatico: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "🔧 RIPRISTINO MANUALE NECESSARIO:" -ForegroundColor Yellow
            Write-Host "   1. Copia i file da: $FullBackupDir" -ForegroundColor Cyan
            Write-Host "   2. Esegui: docker-compose up -d" -ForegroundColor Cyan
        }
    } else {
        Write-Host "❌ Backup completo non trovato!" -ForegroundColor Red
        Write-Host "💡 Ripristino manuale da: $BackupDir" -ForegroundColor Cyan
        Write-Host "   1. Copia .env da $BackupDir" -ForegroundColor Cyan
        Write-Host "   2. Copia uploads da $BackupDir" -ForegroundColor Cyan
        Write-Host "   3. Esegui: docker-compose up -d" -ForegroundColor Cyan
    }
    
    exit 1
} finally {
    Set-Location $OriginalPath
}