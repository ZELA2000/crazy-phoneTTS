# Update Watcher - Monitora richieste di aggiornamento dal container
# Questo script deve essere eseguito sull'HOST, non nel container

param(
    [string]$ProjectDir = (Split-Path -Parent $MyInvocation.MyCommand.Path),
    [int]$CheckInterval = 5
)

Write-Host "🔍 Update Watcher avviato"
Write-Host "📂 Directory progetto: $ProjectDir"
Write-Host "⏱️ Intervallo controllo: $CheckInterval secondi"
Write-Host ""

$RequestFile = Join-Path $ProjectDir "update_request.json"
$ProgressFile = Join-Path $ProjectDir "update_progress.json"

function Write-ColorHost($message, $color = "White") {
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $message" -ForegroundColor $color
}

function Update-Progress($step, $message, $percentage, $status = "running") {
    $progress = @{
        type = "progress"
        step = $step
        message = $message
        percentage = $percentage
        status = $status
        timestamp = (Get-Date).ToString("o")
    }
    
    $progress | ConvertTo-Json -Depth 3 | Out-File -FilePath $ProgressFile -Encoding UTF8
    Write-ColorHost $message "Cyan"
}

try {
    while ($true) {
        if (Test-Path $RequestFile) {
            Write-ColorHost "🚨 Rilevata richiesta di aggiornamento!" "Yellow"
            
            try {
                # Leggi richiesta
                $request = Get-Content $RequestFile | ConvertFrom-Json
                Write-ColorHost "📋 Versione richiesta: $($request.version)" "Green"
                Write-ColorHost "📋 Script da eseguire: $($request.script)" "Green"
                
                # Rimuovi file richiesta per evitare loop
                Remove-Item $RequestFile -Force
                
                # Aggiorna progress
                Update-Progress "host_takeover" "🔄 Host prende controllo dell'aggiornamento..." 30
                
                # Su Windows, forza l'uso di PowerShell per compatibilità
                $ScriptPath = Join-Path $ProjectDir "update_script.ps1"
                
                if (-not (Test-Path $ScriptPath)) {
                    throw "Script PowerShell non trovato: $ScriptPath"
                }
                
                Write-ColorHost "🚀 Eseguendo script PowerShell (Windows)..." "Yellow"
                Update-Progress "executing_host" "🚀 Esecuzione script PowerShell su host..." 40
                
                # Esegui sempre script PowerShell su Windows
                & powershell -ExecutionPolicy Bypass -File $ScriptPath $request.version
                
                $exitCode = $LASTEXITCODE
                
                if ($exitCode -eq 0) {
                    Write-ColorHost "✅ Aggiornamento completato con successo!" "Green"
                    Update-Progress "completed" "🎉 Aggiornamento host completato!" 100 "completed"
                } else {
                    throw "Script terminato con codice di errore: $exitCode"
                }
                
            } catch {
                $errorMsg = "❌ Errore durante aggiornamento: $($_.Exception.Message)"
                Write-ColorHost $errorMsg "Red"
                Update-Progress "error" $errorMsg 0 "error"
            }
        }
        
        Start-Sleep -Seconds $CheckInterval
    }
} catch {
    Write-ColorHost "❌ Errore critico watcher: $($_.Exception.Message)" "Red"
} finally {
    Write-ColorHost "🔚 Update Watcher terminato" "Gray"
}