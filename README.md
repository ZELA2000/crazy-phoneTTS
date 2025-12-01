
# crazy-phoneTTS

Sistema Text-to-Speech professionale per centralini telefonici, con supporto per Azure Speech Services, Google Cloud TTS, Edge TTS e libreria musicale integrata.


## Indice
- [Introduzione](#introduzione)
- [Requisiti](#requisiti)
- [Setup Rapido](#setup-rapido)
- [Configurazione Servizi TTS](#configurazione-servizi-tts)
- [Configurazione Libreria Musicale](#configurazione-libreria-musicale)
- [Utilizzo API](#utilizzo-api)
- [Aggiornamenti e Backup](#aggiornamenti-e-backup)
- [Risoluzione Problemi](#risoluzione-problemi)
- [Struttura Progetto](#struttura-progetto)
- [Linee Guida per le Voci](#linee-guida-per-le-voci)
- [Risorse Utili](#risorse-utili)

---

## Introduzione

crazy-phoneTTS è un sistema Text-to-Speech professionale per centralini telefonici, con sintesi vocale di alta qualità, mixaggio audio avanzato e interfaccia web moderna.

---

## Requisiti

- Docker + Docker Compose
- Account per almeno un servizio TTS (Azure, Google, Edge)
- 4GB RAM minimi (consigliati 8GB+)
- Porte 3000 (frontend) e 8000 (backend) disponibili

---

## Setup Rapido

1. **Clona il repository**
  ```bash
  git clone <repository-url>
  cd crazy-phoneTTS
  ```

2. **Configura il file `.env`**
  - Copia `.env.example` in `.env`
  - Inserisci le credenziali per almeno un servizio TTS (vedi sezione successiva)

3. **Avvia il sistema**
  ```bash
  docker-compose up --build
  ```

4. **Accedi**
  - Frontend: [http://localhost:3000](http://localhost:3000)
  - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Healthcheck: [http://localhost:8000/health](http://localhost:8000/health)

---


## Configurazione Servizi TTS

### Azure Speech Services
- Ottieni chiave e region dal portale Azure
- Imposta in `.env`:
  ```
  AZURE_SPEECH_KEY=your-key
  AZURE_SPEECH_REGION=your-region
  ```

### Google Cloud Text-to-Speech

#### 1. Prerequisiti
- Account Google Cloud
- Progetto Google Cloud attivo
- API "Cloud Text-to-Speech" abilitata

#### 2. Configurazione Credenziali

**Opzione 1: File JSON (raccomandato)**
1. Vai su: https://console.cloud.google.com/
2. Crea nuovo progetto o seleziona esistente
3. Abilita "Cloud Text-to-Speech API"
4. Vai su "IAM & Admin" > "Service Accounts"
5. Crea Service Account con ruolo "Text-to-Speech User"
6. Scarica il file JSON delle credenziali
7. Imposta la variabile d'ambiente:
   - Linux/macOS: `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"`
   - Windows: `set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\credentials.json`

**Opzione 2: Credenziali automatiche (Google Cloud)**
Se l'app gira su Google Cloud (Cloud Run, Compute Engine), le credenziali vengono rilevate automaticamente.

#### 3. Test rapido
1. Configura le credenziali come sopra
2. Riavvia: `docker-compose down && docker-compose up --build`
3. Vai su: http://localhost:3000
4. Seleziona "Google" come servizio TTS
5. Testa con frasi brevi

#### 4. Troubleshooting
- Errore "credenziali non trovate": verifica il path del file JSON e i permessi
- Errore "API non abilitata": abilita "Cloud Text-to-Speech API" nel progetto
- Errore "quota superata": verifica l'utilizzo nel Google Cloud Console
- Il servizio non appare: controlla i log Docker e la configurazione

#### 5. Setup delle voci
- Consulta la lista delle voci disponibili tramite API o interfaccia web
- Scegli voci italiane per centralini (es. Neural2, WaveNet)
- Testa la voce con un breve messaggio prima di generare file definitivi

### Edge TTS
- Non richiede configurazione, sempre disponibile

---

## Configurazione Libreria Musicale

- Carica file musicali tramite interfaccia web (MP3, WAV, OGG)
- I file vengono analizzati e ottimizzati automaticamente
- Puoi gestire volume, fade in/out, timing e preview

---

## Utilizzo API

### Sintesi Vocale
```http
POST /generate-audio
Content-Type: multipart/form-data
text: "Messaggio di benvenuto"
tts_service: "azure" | "google" | "edge"
voice_id: "it-IT-ElsaNeural"
music_file: file.mp3
music_volume: 0.3
output_format: "wav"
```

### Libreria Musicale
```http
POST /music-library/upload
GET /music-library/list
DELETE /music-library/{song_id}
```

### Gestione Voci
```http
GET /available-voices
POST /test-voice
```

---

## Aggiornamenti e Backup

- Aggiornamento automatico tramite interfaccia web o script (`update.ps1`/`update.sh`)
- Backup automatico di configurazioni e file upload
- Rollback disponibile tramite cartella backup

---

## Risoluzione Problemi

- Verifica credenziali e region in `.env`
- Riavvia Docker dopo modifiche
- Consulta i log con `docker-compose logs -f backend`
- Testa la connessione con `curl http://localhost:8000/health`
- Per ambienti aziendali, aumenta timeout e verifica proxy/firewall

---

## Struttura Progetto

```
crazy-phoneTTS/
├── backend/        # FastAPI + servizi TTS
├── frontend/       # React web app
├── docker-compose.yml
├── .env.example    # Template configurazione
├── update.ps1/.sh  # Script aggiornamento
├── output/         # File audio generati
├── uploads/        # Libreria musicale
```

---

## Linee Guida per le Voci

- Scegli voci italiane professionali per centralini (es. ElsaNeural, DiegoNeural)
- Utilizza stili vocali appropriati: `customerservice`, `newscast`, `assistant`
- Per Google TTS, seleziona voci italiane disponibili tramite API
- Testa sempre la voce con un breve messaggio prima di generare file definitivi

---

## Risorse Utili

- [Documentazione Azure Speech](https://docs.microsoft.com/azure/cognitive-services/speech-service/)
- [Documentazione Google Cloud TTS](https://cloud.google.com/text-to-speech/docs)
- [API Reference FastAPI](http://localhost:8000/docs)
- [Guida Docker](https://docs.docker.com/get-started/)

---

## Note Finali

Questa documentazione è pensata per guidare l’utente in modo chiaro e professionale, dalla configurazione iniziale all’utilizzo avanzato, senza riferimenti commerciali o promozionali.  
Per dettagli tecnici sulle architetture, consulta i file di progetto e la documentazione tecnica inclusa.

---

Sistema TTS professionale per centralini con Azure Speech Services, Google Cloud TTS, Edge TTS e libreria musicale integrata.
...existing code...
- Volume musica: 40%

### Formati Output

- **WAV**: Qualità massima per centralini digitali
- **MP3**: Compresso per storage e web
- **GSM**: Ottimizzato per telefonia tradizionale

### Struttura File Output

```
output/
├── {nome_personalizzato}_{YYMMDD}.wav
├── {nome_personalizzato}_{YYMMDD}.mp3
└── {nome_personalizzato}_{YYMMDD}.gsm
```

Esempio: `centralino_welcome_031125.wav`

## 🌐 Deployment in Rete Aziendale

### Configurazione per Accesso Multi-Utente

Il sistema supporta automaticamente:
- **Rilevamento IP automatico** per accesso in rete
- **Accesso simultaneo** da più dispositivi
- **Cronologia condivisa** in tempo reale
- **Interface responsive** per desktop, tablet, mobile

### Per l'Amministratore (sul server):
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

### Per gli Utenti in Rete:
- **Web Interface**: http://[IP-SERVER]:3000
- **API**: http://[IP-SERVER]:8000

### Configurazione Firewall

```bash
# Windows
New-NetFirewallRule -DisplayName "TTS Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
New-NetFirewallRule -DisplayName "TTS Frontend" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow
```

## � Sistema Auto-Aggiornamento

### Funzionalità Automatiche

Il sistema include un **sistema di aggiornamento automatico** completo:

- ✅ **Controllo automatico** nuove release GitHub ogni ora
- ✅ **Notifiche in-app** con changelog dettagliato 
- ✅ **Aggiornamento one-click** dall'interfaccia web
- ✅ **Progress bar in tempo reale** durante l'aggiornamento
- ✅ **Backup automatico** di configurazioni e upload
- ✅ **Riavvio zero-downtime** dopo completamento

### Come Funziona

1. **Rilevamento**: Il sistema controlla GitHub ogni ora per nuove release
2. **Notifica**: Compare una notifica in alto a destra nell'interfaccia
3. **Conferma**: L'utente può vedere il changelog e confermare l'aggiornamento
4. **Download**: Il sistema scarica automaticamente la nuova versione
5. **Backup**: Salva configurazioni (.env) e file upload
6. **Aggiornamento**: Sostituisce i file di sistema mantenendo i dati
7. **Riavvio**: Ricompila e riavvia i container Docker
8. **Verifica**: Controlla che tutto funzioni correttamente
9. **Completamento**: Ricarica automaticamente la pagina

### API Aggiornamenti

```bash
# Controlla versione attuale
GET /version/current

# Controlla aggiornamenti disponibili  
GET /version/check

# Avvia aggiornamento
POST /update/start

# WebSocket progress aggiornamento
WS /ws/update-progress
```

### Aggiornamento Manuale

Se preferisci aggiornare manualmente:

```bash
# Windows
.\update_script.ps1

# Linux/Mac
./update_script.sh

# Con versione specifica
.\update_script.ps1 v1.2.0
./update_script.sh v1.2.0
```

### Sicurezza

- ✅ Download solo da repository GitHub ufficiale
- ✅ Backup automatico prima di ogni aggiornamento
- ✅ Rollback disponibile da cartella backup
- ✅ Verifica integrità post-aggiornamento
- ✅ Nessuna perdita di configurazioni o upload

## �🔧 Configurazione Avanzata

### Variabili Environment Complete

```bash
# Azure Speech Services (OBBLIGATORIO)
AZURE_SPEECH_KEY=your_subscription_key
AZURE_SPEECH_REGION=westeurope

# Timeout per ambienti aziendali (OPZIONALE)
AZURE_CONNECTION_TIMEOUT=60
AZURE_REQUEST_TIMEOUT=120
AZURE_MAX_RETRIES=5
AZURE_RETRY_DELAY=3.0

# Server Configuration (OPZIONALE)
BACKEND_PORT=8000
FRONTEND_PORT=3000
BACKEND_HOST=0.0.0.0

# Storage Paths (OPZIONALE)
UPLOAD_PATH=./uploads
OUTPUT_PATH=./output
MUSIC_LIBRARY_PATH=./uploads/library
```

### Configurazioni per Tipo di Ambiente

#### Rete Domestica/Veloce
```env
AZURE_CONNECTION_TIMEOUT=10
AZURE_REQUEST_TIMEOUT=30
AZURE_MAX_RETRIES=3
```

#### Ufficio/Aziendale Standard
```env
AZURE_CONNECTION_TIMEOUT=30
AZURE_REQUEST_TIMEOUT=60
AZURE_MAX_RETRIES=3
```

#### Aziendale con Firewall/Proxy
```env
AZURE_CONNECTION_TIMEOUT=60
AZURE_REQUEST_TIMEOUT=120
AZURE_MAX_RETRIES=5
```

### Proxy Aziendale

Se la tua azienda usa un proxy, aggiungi in `docker-compose.yml`:

```yaml
environment:
  - HTTP_PROXY=http://proxy.company.com:8080
  - HTTPS_PROXY=http://proxy.company.com:8080
  - NO_PROXY=localhost,127.0.0.1
```

## 📚 API Reference

### Sintesi Vocale Principale

```http
POST /generate-audio
Content-Type: multipart/form-data

# Parametri principali
text: "Benvenuto in azienda"
tts_service: "azure"
edge_voice: "it-IT-ElsaNeural"
music_volume: 0.3
output_format: "wav"
audio_quality: "pcm"
custom_filename: "welcome_message"

# Nuovi parametri per controlli avanzati
library_song_id: "uuid-song"
music_before_seconds: 3.0
music_after_seconds: 2.0
fade_in_duration: 1.0
fade_out_duration: 2.0
```

### Gestione Libreria Musicale

```http
# Carica musica
POST /music-library/upload
Content-Type: multipart/form-data
- name: "Background Corporate"
- music_file: file.mp3

# Lista musica
GET /music-library/list

# Elimina musica
DELETE /music-library/{song_id}
```

### Gestione Voci

```http
GET /available-voices    # Lista tutte le voci disponibili
GET /speakers           # Lista dettagliata con stili
POST /test-voice        # Testa una voce specifica
```

## 🛠️ Risoluzione Problemi

### Errori Comuni

#### Problema: "Azure Speech Services: Connection failed"
```bash
# Verifica credenziali
echo $AZURE_SPEECH_KEY
echo $AZURE_SPEECH_REGION

# Riavvia con timeout estesi (ambienti aziendali)
AZURE_CONNECTION_TIMEOUT=60 AZURE_REQUEST_TIMEOUT=120 docker-compose up --build
```

#### Problema: Timeout di Connessione (Ambienti Aziendali)

È normale in ambienti con firewall/proxy. **Soluzione rapida**:

```bash
# Ferma il servizio
docker-compose down

# Riavvia con timeout estesi
AZURE_CONNECTION_TIMEOUT=60 AZURE_REQUEST_TIMEOUT=120 docker-compose up --build
```

#### Problema: "Authentication failed"
- Verifica la chiave nel portale Azure
- Assicurati di usare la region corretta (es: `westeurope`)

#### Problema: "Quota exceeded"
- Controlla l'uso nel portale Azure
- Il piano F0 ha limite di 500K caratteri/mese

### Test di Connettività

```bash
# Test health check
curl http://localhost:8000/health

# Test voice specifico
curl -X POST http://localhost:8000/test-voice \
  -F "voice_id=it-IT-ElsaNeural" \
  -F "test_text=Test di connessione Azure"

# Test connettività Azure diretta
curl -H "Ocp-Apim-Subscription-Key: $AZURE_SPEECH_KEY" \
     "https://$AZURE_SPEECH_REGION.api.cognitive.microsoft.com/sts/v1.0/issuetoken" \
     -X POST
```

### Firewall Aziendale

Assicurati che questi domini siano abilitati:
- `*.cognitiveservices.azure.com`
- `*.speech.microsoft.com`
- `westeurope.api.cognitive.microsoft.com` (o la tua region)

## 📊 Monitoraggio e Manutenzione

### Controllo Stato Sistema

```bash
# Status completo
docker-compose ps

# Logs in tempo reale
docker-compose logs -f backend
docker-compose logs -f frontend

# Statistiche risorse
docker stats
```

### Backup Database Cronologia

```bash
# Backup database
docker-compose exec backend cp /app/text_history.db /app/output/backup_$(date +%Y%m%d).db

# Copia backup su host
docker cp $(docker-compose ps -q backend):/app/output/backup_*.db ./backups/
```

## 📁 Struttura del Progetto

```
crazy-phoneTTS/
├── backend/                        # FastAPI + Azure Speech
│   ├── main.py                     # Entry point API
│   ├── requirements.txt            # Dipendenze Python
│   ├── Dockerfile                  # Container backend
│   │
│   ├── core/                       # ⚙️ Configurazione base
│   │   ├── __init__.py
│   │   └── config.py               # Configurazione centralizzata
│   │
│   ├── services/                   # 🔌 Integrazioni esterne
│   │   ├── __init__.py
│   │   └── azure_speech.py         # Azure Speech Services
│   │
│   ├── managers/                   # 🎯 Business logic
│   │   ├── __init__.py
│   │   ├── websocket_manager.py    # WebSocket real-time
│   │   ├── update_manager.py       # Sistema aggiornamenti
│   │   ├── audio_processor.py      # Elaborazione audio
│   │   ├── music_library.py        # Gestione libreria
│   │   └── version_manager.py      # Versioning GitHub
│   │
│   ├── models/                     # 📊 Modelli dati
│   │   ├── __init__.py
│   │   ├── history.py              # Database cronologia
│   │   └── voice_catalog.py        # Catalogo voci Azure
│   │
│   └── uploads/
│       ├── library/                # Libreria musicale
│       └── README_MUSIC.md
│
├── frontend/                       # React App
│   ├── src/
│   │   ├── App.js                 # Componente principale
│   │   ├── index.css              # Stili CSS
│   │   └── index.js
│   ├── package.json               # Dipendenze Node.js
│   ├── Dockerfile                 # Container frontend
│   └── public/
│
├── docker-compose.yml              # Orchestrazione container
├── .env.example                    # Template variabili env
├── VERSION                         # Versione corrente
├── update.ps1 / update.sh          # Script aggiornamento
│
└── 📚 Documentazione
    ├── README.md                   # Questo file
    ├── BACKEND_STRUCTURE.md        # Architettura backend
    ├── ARCHITECTURE_DIAGRAM.md     # Diagrammi visuali
    ├── TECHNICAL_DOCUMENTATION.md  # Documentazione tecnica
    ├── REFACTORING_GUIDE.md        # Guida refactoring
    └── REFACTORING_SUMMARY.md      # Riepilogo modifiche
```

### Architettura Backend

Il backend segue il pattern **Layered Architecture** con separazione delle responsabilità:

- **core/** - Configurazione e componenti fondamentali
- **services/** - Integrazione con API esterne (Azure)
- **managers/** - Logica business e coordinamento
- **models/** - Modelli dati e persistenza

📖 **Documentazione completa**: Vedi [BACKEND_STRUCTURE.md](BACKEND_STRUCTURE.md) e [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)

## Performance e Ottimizzazioni

### Raccomandazioni Hardware
- **CPU**: 4+ cores per uso intensivo
- **RAM**: 8GB+ per Azure Speech caching
- **Rete**: Minimo 10 Mbps per audio HD
- **Storage**: SSD consigliato per performance I/O

### Ottimizzazioni per Centralini
- **Volume voce**: Sempre prioritario sulla musica
- **Formato**: WAV per qualità, MP3 per storage
- **Lunghezza**: 15-45 secondi per messaggi ottimali
- **Musica**: Ambient, jazz soft, corporate per attesa

## Integrazione con Centralini

### File Audio Generati
- **Formato**: WAV, 16-bit, 44.1kHz (compatibile con maggior parte sistemi)
- **Naming**: `centralino_audio_[timestamp].wav`
- **Qualità**: PCM per digitali, A-law/μ-law per analogici

### Automazione via API

```bash
# Generazione automatica via script
curl -X POST "http://localhost:8000/generate-audio" \
     -F "text=Il tuo messaggio automatico" \
     -F "music_file=@musica_aziendale.mp3" \
     -F "music_volume=0.3" \
     -F "edge_voice=it-IT-ElsaNeural"
```
## 💻 Tecnologie Utilizzate

### Backend
- **Python 3.9+** - Linguaggio principale
- **FastAPI** - Framework web moderno e veloce
- **Azure Speech Services** - Servizio TTS Microsoft
- **Pydantic** - Validazione dati e serializzazione
- **python-multipart** - Gestione upload file multipart
- **uvicorn** - Server ASGI per FastAPI

### Frontend
- **React 18** - Framework JavaScript per UI
- **JavaScript ES6+** - Linguaggio frontend
- **HTML5** - Markup semantico
- **CSS3** - Styling e responsive design
- **Fetch API** - Comunicazione con backend
- **WebAudio API** - Gestione audio nel browser

### Audio Processing
- **Azure Speech SDK** - Sintesi vocale cloud
- **Web Audio API** - Manipolazione audio lato client
- **Supporto formati**: WAV, MP3, OGG, GSM
- **Audio Codec**: PCM, A-law, μ-law

### DevOps & Deployment
- **Docker** - Containerizzazione applicazione
- **Docker Compose** - Orchestrazione multi-container
- **Linux Alpine** - Immagine base leggera
- **Node.js 18** - Runtime JavaScript
- **Nginx** (opzionale) - Reverse proxy per produzione

### Database & Storage
- **File System** - Storage locale per file audio
- **JSON** - Configurazione e metadati
- **Volumi Docker** - Persistenza dati

### Networking & Security
- **CORS** - Cross-Origin Resource Sharing
- **Environment Variables** - Gestione sicura credenziali
- **HTTPS Ready** - Supporto SSL/TLS per produzione
- **Firewall Configuration** - Setup rete aziendale

### Cloud Services
- **Microsoft Azure** - Cloud provider
- **Azure Cognitive Services** - Servizi AI/ML
- **Azure Speech Services** - TTS con voci neurali
- **Endpoint REST** - API Azure per sintesi vocale

### Formati Supportati

#### Input Audio
- **MP3** - Compressione con perdita
- **WAV** - Audio non compresso
- **OGG** - Codec open source

#### Output Audio
- **WAV** - 16-bit PCM, 44.1kHz (centralini digitali)
- **MP3** - Compresso per web e storage
- **GSM** - Ottimizzato per telefonia (8kHz)

#### Qualità Audio
- **PCM** - Pulse Code Modulation (digitale)
- **A-law** - Compressione europea telefonica
- **μ-law** - Compressione americana telefonica

### Compatibilità
- **OS**: Linux, Windows, macOS
- **Browser**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **Mobile**: iOS Safari, Android Chrome
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Requirements Hardware
```
Minime:
- CPU: 2 cores
- RAM: 4GB
- Storage: 10GB
- Network: 5 Mbps

Consigliate:
- CPU: 4+ cores
- RAM: 8GB+
- Storage: SSD 50GB+
- Network: 10+ Mbps
```

---

## 🔗 Supporto e Link Utili

- **Azure Speech Portal**: [portal.azure.com](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices)
- **Documentazione Azure**: [docs.microsoft.com/azure/cognitive-services/speech-service](https://docs.microsoft.com/azure/cognitive-services/speech-service/)
- **Prezzi Azure Speech**: [azure.microsoft.com/pricing/details/cognitive-services/speech-services](https://azure.microsoft.com/pricing/details/cognitive-services/speech-services/)
- **Issues GitHub**: Apri un issue per problemi specifici

## 📄 Licenza

Questo progetto utilizza Azure Speech Services con licenza commerciale autorizzata per uso business.

---

**Sistema TTS professionale per centralini con Azure Speech Services - Legale, Scalabile, Pronto per Produzione**