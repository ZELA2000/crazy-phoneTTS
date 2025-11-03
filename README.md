# 🎙️ crazy-phoneTTS

Sistema Text-to-Speech professionale per centralini telefonici con Azure Speech Services e libreria musicale integrata.

## 📑 Indice

- [Caratteristiche Principali](#caratteristiche-principali)
- [🚀 Setup Rapido (5 minuti)](#-setup-rapido-5-minuti)
- [💰 Piano Azure F0](#-piano-azure-f0---perfetto-per-centralini)
- [🗣️ Voci Disponibili](#️-voci-italiane-disponibili)
- [⚙️ Funzionalità Avanzate](#️-funzionalità-avanzate)
- [🌐 Deployment in Rete](#-deployment-in-rete-aziendale)
- [🔧 Configurazione Avanzata](#-configurazione-avanzata)
- [📚 API Reference](#-api-reference)
- [🛠️ Risoluzione Problemi](#️-risoluzione-problemi)
- [📊 Monitoraggio](#-monitoraggio-e-manutenzione)
- [📁 Struttura Progetto](#-struttura-del-progetto)
- [🔗 Link Utili](#-supporto-e-link-utili)
- [💻 Tecnologie Utilizzate](#-tecnologie-utilizzate)

## Caratteristiche Principali

### 🏢 Azure Speech Services - Licenza Commerciale
- Uso commerciale legale per centralini business
- Piano F0 gratuito: 500.000 caratteri/mese
- SLA 99.9% garantito da Microsoft
- Voci Neural Italiane di alta qualità

### 🎵 Libreria Musicale Avanzata
- Upload multipli: MP3, WAV, OGG
- Gestione persistente con metadati
- Controlli audio: volume, fade in/out, timing
- Anteprima integrata prima della generazione

### ⚡ Funzionalità Professionali
- Formati output: WAV, MP3, GSM
- Qualità telefonica: PCM, A-law, μ-law
- Nomi file personalizzati con data
- Interface responsive per tutti i dispositivi

## Setup Rapido (5 minuti)

### 1. Prerequisiti
- Docker e Docker Compose
- Account Azure (gratuito)
- Almeno 4GB di RAM
- Porte 3000 e 8000 disponibili

### 2. Configurazione Azure Speech Services

1. Vai al [Portal Azure](https://portal.azure.com)
2. Crea una risorsa "Speech Services"
3. Ottieni **Key** e **Region** dalla sezione "Keys and Endpoint"

### 3. Configurazione Progetto

```bash
# Clone del repository
git clone <repository-url>
cd crazy-phoneTTS

# Crea file .env
cat > .env << EOF
AZURE_SPEECH_KEY=your_api_key_here
AZURE_SPEECH_REGION=westeurope
EOF
```

### 4. Avvio Sistema

```bash
# Build e avvio
docker-compose up --build

# Oppure in background
docker-compose up -d --build
```

### 5. Verifica Funzionamento

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Dovresti vedere:
```json
{
  "status": "healthy",
  "azure_speech_ready": true,
  "region": "westeurope"
}
```

## 💰 Piano Azure F0 - Perfetto per Centralini

| Caratteristica | Piano F0 Gratuito |
|----------------|------------------|
| **Caratteri/mese** | 500.000 GRATIS |
| **Messaggi centralino** | ~6.600/mese* |
| **Uso commerciale** | ✅ Autorizzato |
| **SLA** | 99.9% |
| **Costo eccedenza** | $1/milione caratteri |

*Basato su 75 caratteri per messaggio medio

## 🗣️ Voci Italiane Disponibili

### Femminili
- **it-IT-ElsaNeural**: Voce professionale per centralini aziendali
- **it-IT-IsabellaNeural**: Voce espressiva per messaggi promozionali
- **it-IT-IrmaNeural**: Voce calda per supporto clienti

### Maschili
- **it-IT-DiegoNeural**: Voce autorevole per annunci ufficiali
- **it-IT-BenignoNeural**: Voce espressiva per guide vocali
- **it-IT-CalimeroNeural**: Voce moderna per comunicazioni dinamiche

### Stili Vocali Supportati
- `customerservice`: Ottimizzato per servizio clienti
- `newscast`: Stile da giornalista/annunciatore
- `assistant`: Stile da assistente virtuale
- `chat`: Conversazionale e amichevole
- `cheerful`: Allegro e positivo

## ⚙️ Funzionalità Avanzate

### Gestione Libreria Musicale

1. **Caricare una canzone**:
   - Click "Libreria Musicale"
   - Inserisci nome canzone
   - Seleziona file audio (MP3/WAV/OGG)
   - Click "Carica"

2. **Controlli Audio Avanzati**:
   - **Volume musica**: 0-100% (slider)
   - **Musica prima del testo**: 0-10 secondi
   - **Musica dopo il testo**: 0-10 secondi
   - **Fade In**: 0-5 secondi
   - **Fade Out**: 0-5 secondi

### Configurazioni Esempio

#### Per Centralino Professionale:
- Musica prima: 3 secondi
- Musica dopo: 2 secondi
- Fade In: 1 secondo
- Fade Out: 2 secondi
- Volume musica: 30%

#### Per Messaggio Pubblicitario:
- Musica prima: 5 secondi
- Musica dopo: 4 secondi
- Fade In: 2 secondi
- Fade Out: 3 secondi
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

## 🔧 Configurazione Avanzata

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
├── backend/                 # FastAPI + Azure Speech
│   ├── main.py             # API endpoints
│   ├── requirements.txt    # Dipendenze Python
│   ├── Dockerfile          # Container backend
│   └── uploads/
│       ├── library/        # Libreria musicale persistente
│       └── README_MUSIC.md
├── frontend/               # React App
│   ├── src/
│   │   ├── App.js         # Componente principale
│   │   ├── index.css      # Stili CSS
│   │   └── index.js
│   ├── package.json       # Dipendenze Node.js
│   ├── Dockerfile         # Container frontend
│   └── public/
├── docker-compose.yml      # Configurazione Docker
├── .env.example           # Template variabili environment
└── README.md             # Documentazione
```

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

## � Tecnologie Utilizzate

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

### Requirements
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