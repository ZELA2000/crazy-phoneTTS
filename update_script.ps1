# Script di aggiornamento per Windows
# Parametro: $args[0] = nuova versione
param(
    [string]$NewVersion = "latest"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

Write-Host "🚀 Avvio aggiornamento crazy-phoneTTS a versione $NewVersion"

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
    $composeVersion = docker-compose --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose non trovato!"
    }
    Write-Host "✅ Docker Compose: $composeVersion"

    # Step 3: Backup configurazione
    Write-Host "💾 Backup configurazione..."
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

    # Step 4: Stop containers
    Write-Host "🛑 Arresto containers..."
    docker-compose down 2>$null
    Write-Host "✅ Containers arrestati"

    # Step 5: Download nuova versione
    Write-Host "📦 Download versione $NewVersion da GitHub..."
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
        "QUICKSTART.md"
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
    docker-compose up -d
    if ($LASTEXITCODE -ne 0) {
        throw "Errore durante avvio containers"
    }

    # Step 11: Verifica salute
    Write-Host "🏥 Verifica salute sistema..."
    Start-Sleep -Seconds 10
    
    for ($i = 1; $i -le 6; $i++) {
        try {
            $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
            if ($health.status -eq "ok") {
                Write-Host "✅ Sistema aggiornato e funzionante!"
                break
            }
        } catch {
            if ($i -eq 6) {
                Write-Host "⚠️ Sistema avviato ma health check fallito"
            } else {
                Write-Host "⏳ Attendo avvio sistema... ($i/6)"
                Start-Sleep -Seconds 5
            }
        }
    }

    # Cleanup
    Write-Host "🧹 Pulizia file temporanei..."
    if (Test-Path $TempFile) { Remove-Item $TempFile -Force }
    if (Test-Path $TempExtract) { Remove-Item $TempExtract -Recurse -Force }
    
    Write-Host ""
    Write-Host "🎉 AGGIORNAMENTO COMPLETATO CON SUCCESSO!"
    Write-Host "🌐 Frontend: http://localhost:3000"
    Write-Host "📚 API Docs: http://localhost:8000/docs"
    Write-Host "💾 Backup salvato in: $BackupDir"

} catch {
    Write-Host ""
    Write-Host "❌ ERRORE DURANTE AGGIORNAMENTO:"
    Write-Host $_.Exception.Message
    Write-Host ""
    Write-Host "🔄 Per ripristino, copia i file da $BackupDir"
    exit 1
} finally {
    Set-Location $OriginalPath
}