# 🏢 CONFIGURAZIONE AMBIENTI AZIENDALI

## Problema: Timeout di Connessione Azure

Se vedi questo errore:
```
ERROR: SpeechServiceConnection_SynthesisConnectionTimeoutMs
```

**È normale in ambienti aziendali** con firewall/proxy che rallentano le connessioni esterne.

## ✅ SOLUZIONE RAPIDA

### Opzione 1: Riavvio con timeout estesi
```bash
# Ferma il servizio
docker-compose down

# Riavvia con timeout maggiori
AZURE_CONNECTION_TIMEOUT=60 AZURE_REQUEST_TIMEOUT=120 docker-compose up --build
```

### Opzione 2: Configurazione permanente .env
```bash
# Crea/modifica file .env
AZURE_SPEECH_KEY=la-tua-chiave-azure
AZURE_SPEECH_REGION=westeurope

# Timeout estesi per ambienti aziendali
AZURE_CONNECTION_TIMEOUT=60
AZURE_REQUEST_TIMEOUT=120  
AZURE_MAX_RETRIES=5
AZURE_RETRY_DELAY=3.0
```

### Opzione 3: Configurazione ultra-conservativa
```bash
# Per reti molto lente o con proxy complessi
AZURE_CONNECTION_TIMEOUT=120
AZURE_REQUEST_TIMEOUT=180
AZURE_MAX_RETRIES=10
AZURE_RETRY_DELAY=5.0
```

## 🔧 Configurazioni per Tipo di Ambiente

### Rete Domestica/Veloce
```env
AZURE_CONNECTION_TIMEOUT=10
AZURE_REQUEST_TIMEOUT=30
AZURE_MAX_RETRIES=3
```

### Ufficio/Aziendale Standard  
```env
AZURE_CONNECTION_TIMEOUT=30
AZURE_REQUEST_TIMEOUT=60
AZURE_MAX_RETRIES=3
```

### Aziendale con Firewall/Proxy
```env
AZURE_CONNECTION_TIMEOUT=60
AZURE_REQUEST_TIMEOUT=120
AZURE_MAX_RETRIES=5
```

### Rete Molto Lenta/Complessa
```env
AZURE_CONNECTION_TIMEOUT=120
AZURE_REQUEST_TIMEOUT=180
AZURE_MAX_RETRIES=10
```

## 🌐 Configurazioni di Rete Specifiche

### Proxy Aziendale
Se la tua azienda usa un proxy, potrebbero servire configurazioni aggiuntive nel Docker:
```yaml
# In docker-compose.yml, aggiungi:
environment:
  - HTTP_PROXY=http://proxy.company.com:8080
  - HTTPS_PROXY=http://proxy.company.com:8080
  - NO_PROXY=localhost,127.0.0.1
```

### Firewall con Whitelist
Assicurati che questi domini siano abilitati:
- `*.cognitiveservices.azure.com`
- `*.speech.microsoft.com`
- `westeurope.api.cognitive.microsoft.com` (o la tua region)

### VPN Aziendali
Le VPN possono rallentare significativamente le connessioni:
- Usa timeout estesi (120s+)
- Aumenta i retry (5-10)
- Considera region Azure più vicine al server VPN

## 🚀 Test di Connettività

Dopo la configurazione, verifica:

```bash
# 1. Riavvia con nuove configurazioni
docker-compose down
docker-compose up --build

# 2. Controlla i log per:
✅ Azure Speech Services: ✓ Connection verified

# 3. Testa manualmente
curl http://localhost:8000/health
```

## ⏱️ Monitoraggio Performance

I log ora mostrano:
- Tempo di connessione effettivo
- Tipo di errore specifico (timeout vs auth vs network)
- Suggerimenti automatici basati sull'ambiente

## 🆘 Se Continua a Non Funzionare

1. **Verifica connettività di base:**
   ```bash
   # Test ping verso Azure
   ping westeurope.api.cognitive.microsoft.com
   ```

2. **Bypass temporaneo del test di startup:**
   Nel `main.py`, commenta la riga di test nella funzione `startup_event()` per saltare il test iniziale.

3. **Test manuale dal browser:**
   Vai su http://localhost:8000/test-voice dopo l'avvio

4. **Contatta IT aziendale:**
   - Richiedi whitelist per `*.cognitiveservices.azure.com`
   - Verifica configurazioni proxy/firewall per traffico HTTPS verso Azure

---

**Il servizio ora include:**
- ✅ Timeout configurabili per ogni ambiente
- ✅ Fallback automatico su voci standard (più veloci)
- ✅ Diagnostica automatica problemi di rete
- ✅ Suggerimenti specifici per ambienti aziendali