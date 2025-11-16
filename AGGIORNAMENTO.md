# 🔄 Sistema di Aggiornamento Semplificato

## ⚠️ Importante: Cambiamenti al Sistema di Aggiornamento

Il sistema di aggiornamento è stato **semplificato** per maggiore sicurezza e controllo.

### Cosa è Cambiato

❌ **Rimosso**: Aggiornamento automatico dal backend web  
❌ **Rimosso**: Pulsante "Aggiorna" nell'interfaccia  
❌ **Rimosso**: Progress tracking in tempo reale  

✅ **Mantenuto**: Controllo versione da GitHub  
✅ **Mantenuto**: Notifica aggiornamenti disponibili  
✅ **Aggiunto**: Istruzioni chiare per aggiornamento manuale  

### Perché il Cambiamento

- 🔒 **Sicurezza**: Nessuna esecuzione automatica di script da remoto
- 🎯 **Controllo**: L'amministratore decide quando aggiornare
- 📊 **Trasparenza**: Visibilità completa del processo
- ✅ **Affidabilità**: Meno complessità = meno bug

## Come Verificare Aggiornamenti Disponibili

### Tramite Interfaccia Web

1. Apri l'interfaccia web di crazy-phoneTTS
2. Vai nella sezione **"Informazioni"** o **"Settings"**
3. Cerca la notifica di aggiornamento disponibile
4. Visualizza il changelog e le istruzioni

### Tramite API

```bash
# Controlla versione corrente
curl http://localhost:8000/version/current

# Controlla se disponibile aggiornamento
curl http://localhost:8000/version/check

# Ottieni istruzioni per aggiornare
curl http://localhost:8000/update/instructions
```

## Aggiornamento Manuale

Sono disponibili due script per aggiornare facilmente il progetto:

### Windows (PowerShell)

Apri PowerShell nella cartella del progetto ed esegui:

```powershell
.\update.ps1
```

Per saltare la conferma (utile per automazione):

```powershell
.\update.ps1 -SkipConfirm
```

### Linux/Mac (Bash)

Apri il terminale nella cartella del progetto ed esegui:

```bash
chmod +x update.sh  # Solo la prima volta, per rendere eseguibile lo script
./update.sh
```

Per saltare la conferma:

```bash
./update.sh --skip-confirm
```

## Cosa Fanno gli Script

Gli script di aggiornamento eseguono automaticamente queste operazioni:

1. **Scaricano gli aggiornamenti** da GitHub (`git pull`)
   - Salvano eventuali modifiche locali in stash
   - Scaricano le nuove versioni
   - Ripristinano le modifiche locali

2. **Fermano i container** (`docker compose down`)
   - Arresta temporaneamente i servizi

3. **Riavviano i container** con le nuove modifiche (`docker compose up -d --build`)
   - Ricostruisce le immagini Docker
   - Avvia i servizi aggiornati

## ⚠️ Importante

- Durante l'aggiornamento, **i servizi saranno temporaneamente offline** (solitamente 1-2 minuti)
- Assicurati che **Docker sia in esecuzione** prima di lanciare lo script
- Gli script richiedono **Git** installato sul sistema

## Verificare lo Stato

Dopo l'aggiornamento, puoi verificare che tutto funzioni:

```bash
# Controlla lo stato dei container
docker compose ps

# Visualizza i log se necessario
docker compose logs -f
```

## Accesso ai Servizi

Dopo l'aggiornamento, i servizi saranno disponibili a:

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

## Controllo Versione

Puoi controllare la versione corrente visitando:

- **Frontend**: Clicca sull'icona dell'ingranaggio e controlla la sezione "Aggiornamenti"
- **File VERSION**: Apri il file `VERSION` nella cartella del progetto

---

## Risoluzione Problemi

### Script Bloccato da PowerShell

Se Windows blocca l'esecuzione dello script PowerShell, esegui:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Errore "Git non trovato"

Installa Git da: https://git-scm.com/download/

### Errore "Docker non in esecuzione"

- **Windows**: Avvia Docker Desktop
- **Linux**: `sudo systemctl start docker`
- **Mac**: Avvia Docker Desktop

### Container Non Partono

Se i container non si avviano dopo l'aggiornamento:

```bash
# Controlla i log per gli errori
docker compose logs

# Prova a ricostruire forzando
docker compose down -v
docker compose up -d --build --force-recreate
```
