# 🚨 RISOLUZIONE PROBLEMA AZURE SPEECH SERVICES

## Problema Rilevato
```
ERROR: Azure Speech Services: Connection failed - Azure Speech test failed: ResultReason.Canceled
ERROR: SpeechServiceConnection_SynthesisConnectionTimeoutMs
```

## ✅ SOLUZIONE RAPIDA

### 🔥 PROBLEMA TIMEOUT (Più Comune)
Se vedi errori di timeout, è normale in ambienti aziendali con firewall/proxy.

**Soluzione immediata:**
```bash
# Ferma il servizio
docker-compose down

# Riavvia con timeout estesi
AZURE_CONNECTION_TIMEOUT=60 AZURE_REQUEST_TIMEOUT=120 docker-compose up --build
```

**Soluzione permanente (.env):**
```env
AZURE_SPEECH_KEY=la-tua-chiave-azure
AZURE_SPEECH_REGION=westeurope

# Timeout per ambienti aziendali
AZURE_CONNECTION_TIMEOUT=60
AZURE_REQUEST_TIMEOUT=120
AZURE_MAX_RETRIES=5
AZURE_RETRY_DELAY=3.0
```

### 🔑 PROBLEMA CREDENZIALI

Il problema principale è che la chiave Azure nel codice potrebbe essere scaduta o non valida.

**Passi per risolvere:**

1. **Ottieni una nuova chiave Azure:**
   - Vai su [portale Azure](https://portal.azure.com)
   - Cerca "Speech Services" 
   - Crea una nuova risorsa o usa una esistente
   - Vai su "Keys and Endpoint"
   - Copia **KEY 1**

2. **Configura le variabili d'ambiente:**

   **Opzione A - File .env (Consigliata):**
   ```bash
   # Crea file .env nella cartella root del progetto
   cp .env.example .env
   
   # Modifica .env con le tue credenziali:
   AZURE_SPEECH_KEY=la-tua-chiave-azure-qui
   AZURE_SPEECH_REGION=westeurope
   ```

   **Opzione B - Variabili di sistema:**
   ```powershell
   # In PowerShell
   $env:AZURE_SPEECH_KEY="la-tua-chiave-azure-qui"
   $env:AZURE_SPEECH_REGION="westeurope"
   ```

3. **Riavvia il servizio:**
   ```bash
   docker-compose down
   docker-compose up --build
   ```

### 2. Verifica della Configurazione

Dopo il riavvio, dovresti vedere:
```
✅ Azure Speech Services: Connection verified
```

Se vedi ancora errori, controlla i log dettagliati che ora includono suggerimenti specifici.

### 3. Test del Servizio

```bash
# Verifica health check
curl http://localhost:8000/health

# Testa una voce specifica
curl -X POST http://localhost:8000/test-voice \
  -F "voice_id=it-IT-ElsaNeural" \
  -F "test_text=Test di connessione Azure"
```

## 🔍 DIAGNOSTICA AVANZATA

Se il problema persiste, i log ora includeranno:
- **Diagnostica dettagliata** dell'errore
- **Suggerimenti specifici** basati sul tipo di errore
- **Codici di errore** Azure per debugging avanzato

### Errori Comuni e Soluzioni

| Errore | Causa | Soluzione |
|--------|-------|-----------|
| `authentication failed` | Chiave non valida | Verifica la chiave nel portale Azure |
| `region not found` | Region errata | Usa region breve (es: `westeurope`) |
| `quota exceeded` | Limite gratuito superato | Controlla uso nel portale Azure |
| `connection timeout` | Problemi di rete | Verifica connessione/firewall |

## 📞 SUPPORTO

- **Health Check**: http://localhost:8000/health
- **Documentazione**: Consulta `AZURE_INTEGRATION.md`
- **Log dettagliati**: Ora disponibili per debugging avanzato

---

**Il sistema è ora configurato con:**
- ✅ Gestione sicura delle credenziali (no hardcode)
- ✅ Diagnostica errori avanzata
- ✅ Configurazione tramite file .env
- ✅ Suggerimenti automatici per la risoluzione