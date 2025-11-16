# Documentazione Tecnica - crazy-phoneTTS

## Panoramica del Sistema

crazy-phoneTTS è un sistema di sintesi vocale (Text-to-Speech) progettato per centralini telefonici, che utilizza Azure Speech Services per generare audio di alta qualità in italiano con supporto per musica di sottofondo e controlli avanzati.

## Architettura del Sistema

### Componenti Principali

1. **Backend (FastAPI)**
   - API REST per la generazione di audio TTS
   - Gestione cronologia testi sintetizzati
   - Sistema di aggiornamento automatico
   - Integrazione con Azure Speech Services

2. **Frontend (React)**
   - Interfaccia utente per la generazione di audio
   - Cronologia real-time tramite WebSocket
   - Gestione libreria musicale
   - Notifiche di aggiornamento software

3. **Sistema di Aggiornamento**
   - Script PowerShell (Windows)
   - Script Bash (Linux/Mac)
   - Backup automatico con rotazione
   - Ripristino automatico in caso di errore

## Backend - Struttura e Funzionalità

### Configurazione

#### Variabili d'Ambiente
```
AZURE_SPEECH_KEY          - Chiave API Azure Speech Services (obbligatoria)
AZURE_SPEECH_REGION       - Regione Azure (default: westeurope)
AZURE_SPEECH_ENDPOINT     - Endpoint personalizzato (opzionale)
BACKEND_HOST              - IP di ascolto (default: 0.0.0.0)
BACKEND_PORT              - Porta di ascolto (default: 8000)
```

#### Percorsi File
```
output/                   - File audio generati
uploads/                  - File caricati dagli utenti
uploads/library/          - Libreria musicale
voices/                   - Voci personalizzate (training)
text_history.db           - Database cronologia SQLite
update_progress.json      - Stato aggiornamenti
```

### API Endpoints

#### Generazione Audio
**POST /generate-audio**

Genera audio TTS con opzionale musica di sottofondo.

Parametri:
- `text` (str): Testo da sintetizzare
- `edge_voice` (str): ID voce Azure (default: it-IT-ElsaNeural)
- `music_file` (file): File musicale opzionale
- `library_song_id` (str): ID canzone dalla libreria
- `music_volume` (float): Volume musica 0.0-1.0 (default: 0.3)
- `music_before` (float): Secondi musica prima del testo (default: 2.0)
- `music_after` (float): Secondi musica dopo il testo (default: 3.0)
- `fade_in` (bool): Applica fade in (default: true)
- `fade_out` (bool): Applica fade out (default: true)
- `fade_in_duration` (float): Durata fade in secondi (default: 1.0)
- `fade_out_duration` (float): Durata fade out secondi (default: 2.0)
- `output_format` (str): Formato output (wav, mp3, gsm)
- `audio_quality` (str): Qualità audio (pcm, alaw, ulaw)
- `custom_filename` (str): Nome file personalizzato

Risposta: File audio nel formato richiesto

#### Voci Disponibili
**GET /available-voices**

Restituisce la lista completa delle voci Azure disponibili, organizzate per tipo e genere.

Risposta:
```json
{
  "voices": {
    "neural_voices": {
      "female": {...},
      "male": {...}
    },
    "standard_voices": {
      "female": {...},
      "male": {...}
    }
  },
  "total_count": 8,
  "neural_count": 6
}
```

#### Test Voce
**POST /test-voice**

Testa una voce specifica con testo di prova.

Parametri:
- `voice_id` (str): ID della voce da testare
- `test_text` (str): Testo di prova (opzionale)

Risposta: File audio di test

#### Cronologia
**GET /api/history**

Recupera la cronologia recente dei testi sintetizzati.

Parametri:
- `limit` (int): Numero massimo di voci (default: 10)

Risposta:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "text": "Testo sintetizzato...",
      "voice": "it-IT-ElsaNeural",
      "timestamp": "2025-11-16T10:30:00",
      "user_ip": "...xxx.xxx"
    }
  ],
  "total": 10
}
```

#### Libreria Musicale
**POST /music-library/upload**

Carica una canzone nella libreria musicale.

Parametri:
- `name` (str): Nome della canzone
- `music_file` (file): File audio (MP3, WAV, OGG)

**GET /music-library/list**

Lista tutte le canzoni nella libreria.

**DELETE /music-library/{song_id}**

Elimina una canzone dalla libreria.

#### Sistema di Aggiornamento
**GET /version/check**

Controlla se sono disponibili aggiornamenti.

Risposta:
```json
{
  "current_version": "1.0.0",
  "latest_version": "1.0.1",
  "update_available": true,
  "update_instructions": {
    "windows": {
      "command": ".\\update.ps1",
      "description": "..."
    },
    "linux": {...},
    "mac": {...}
  }
}
```

**GET /health**

Verifica lo stato di salute del servizio.

### WebSocket Endpoints

#### Cronologia Real-Time
**WS /ws**

WebSocket per aggiornamenti real-time della cronologia.

Messaggi ricevuti:
```json
{
  "type": "new_text",
  "data": {
    "id": 123,
    "text": "...",
    "voice": "it-IT-ElsaNeural",
    "timestamp": "2025-11-16T10:30:00"
  }
}
```

#### Progresso Aggiornamenti
**WS /ws/update-progress**

WebSocket per il progresso degli aggiornamenti di sistema.

### Database

#### Tabella text_history
```sql
CREATE TABLE text_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    voice TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_ip TEXT,
    audio_generated BOOLEAN DEFAULT FALSE
)
```

## Specifiche Qualità Audio

### Formati Supportati

#### PCM (Alta Qualità)
- Sample Rate: 8kHz
- Sample Width: 16bit
- Bitrate: 128kbps
- Uso: Qualità massima per centralini VoIP

#### A-law (G.711)
- Sample Rate: 8kHz
- Sample Width: 8bit
- Bitrate: 64kbps
- Codec: pcm_alaw
- Uso: Standard europeo per telefonia

#### u-law (G.711)
- Sample Rate: 8kHz
- Sample Width: 8bit
- Bitrate: 64kbps
- Codec: pcm_mulaw
- Uso: Standard americano per telefonia

## Voci Azure Speech Services

### Voci Neurali Femminili

#### it-IT-ElsaNeural
- **Descrizione**: Voce femminile naturale e professionale
- **Stili**: customerservice, newscast, assistant, chat
- **Uso consigliato**: Centralini aziendali, servizio clienti

#### it-IT-IsabellaNeural
- **Descrizione**: Voce femminile espressiva e accogliente
- **Stili**: chat, cheerful, newscast, assistant
- **Uso consigliato**: Messaggi di benvenuto, annunci pubblicitari

#### it-IT-IrmaNeural
- **Descrizione**: Voce femminile calda e rassicurante
- **Stili**: chat, friendly, assistant
- **Uso consigliato**: Supporto clienti, messaggi informativi

### Voci Neurali Maschili

#### it-IT-DiegoNeural
- **Descrizione**: Voce maschile autorevole e chiara
- **Stili**: customerservice, newscast, assistant
- **Uso consigliato**: Annunci ufficiali, messaggi istituzionali

#### it-IT-BenignoNeural
- **Descrizione**: Voce maschile espressiva e coinvolgente
- **Stili**: chat, friendly, assistant
- **Uso consigliato**: Messaggi promozionali, guide vocali

#### it-IT-CalimeroNeural
- **Descrizione**: Voce maschile moderna e dinamica
- **Stili**: chat, excited, friendly
- **Uso consigliato**: Messaggi giovani, comunicazioni dinamiche

## Elaborazione Audio

### Pipeline di Generazione

1. **Sintesi Vocale**
   - Generazione audio tramite Azure Speech Services
   - Applicazione parametri SSML per controllo avanzato
   - Normalizzazione audio con headroom 2.0dB

2. **Ottimizzazione Audio**
   - Filtro passa-basso a 8kHz per ridurre suono metallico
   - Riduzione volume -3dB per suono più caldo
   - Conversione a mono per compatibilità telefonica

3. **Mixaggio Musicale (opzionale)**
   - Riduzione volume musica secondo parametro utente
   - Loop automatico se musica più corta del necessario
   - Fade in/out configurabili
   - Riduzione -6dB musica durante voce per chiarezza

4. **Conversione Formato**
   - Applicazione specifiche qualità richiesta
   - Conversione nel formato output scelto
   - Naming automatico con data YYMMDD

### Parametri SSML

Il sistema supporta controllo avanzato tramite SSML:

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="it-IT">
  <voice name="it-IT-ElsaNeural">
    <mstts:express-as style="customerservice" styledegree="1.0">
      <prosody rate="medium" pitch="medium" volume="loud">
        <emphasis level="moderate">Testo da sintetizzare</emphasis>
      </prosody>
    </mstts:express-as>
  </voice>
</speak>
```

## Sistema di Aggiornamento

### Funzionalità

- Controllo automatico nuove release da GitHub
- Backup completo prima dell'aggiornamento
- Rotazione backup (massimo 2 conservati)
- Ripristino automatico in caso di errore
- Supporto multipiattaforma (Windows/Linux/Mac)

### Processo di Aggiornamento

#### Fase 1: Backup
- Creazione directory backup con timestamp
- Copia completa progetto (incluso .git e file nascosti)
- Pulizia backup vecchi oltre i 2 più recenti

#### Fase 2: Download
- Controllo ultima release da GitHub API
- Git stash per modifiche locali
- Git fetch --tags per scaricare release
- Git checkout sulla versione specifica

#### Fase 3: Arresto Container
- Docker compose down per fermare tutti i servizi

#### Fase 4: Build
- Docker compose build per ricostruire le immagini
- Ripristino backup in caso di errore

#### Fase 5: Avvio
- Docker compose up -d per riavviare i servizi
- Verifica che almeno 2 container siano running
- Attesa 5 secondi per stabilizzazione
- Ripristino backup in caso di fallimento

### Script di Aggiornamento

#### Windows (update.ps1)
```powershell
# Esecuzione standard con conferma
.\update.ps1

# Esecuzione automatica senza conferma
.\update.ps1 -SkipConfirm
```

#### Linux/Mac (update.sh)
```bash
# Rendi eseguibile (prima esecuzione)
chmod +x update.sh

# Esecuzione standard con conferma
./update.sh

# Esecuzione automatica senza conferma
./update.sh --skip-confirm
```

## Frontend

### Componenti Principali

1. **Generatore Audio**
   - Form per input testo
   - Selezione voce
   - Controlli musica di sottofondo
   - Configurazione qualità output

2. **Cronologia Real-Time**
   - Lista testi sintetizzati
   - Aggiornamento automatico tramite WebSocket
   - Visualizzazione compatta con scroll

3. **Libreria Musicale**
   - Upload file audio
   - Lista canzoni disponibili
   - Eliminazione canzoni
   - Selezione per mixaggio

4. **Sistema Notifiche Aggiornamenti**
   - Dialog modale con istruzioni aggiornamento
   - Comandi specifici per piattaforma
   - Pulsante copia negli appunti

### Rilevamento Automatico API

Il frontend rileva automaticamente l'URL corretto del backend:

```javascript
const getApiUrl = () => {
  // Variabile d'ambiente ha priorità
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // Rileva se localhost o IP di rete
  const currentHost = window.location.hostname;
  
  if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  
  return `http://${currentHost}:8000`;
};
```

## Best Practices Implementate

### Principi Clean Code

1. **Single Responsibility Principle**
   - Ogni funzione ha una responsabilità ben definita
   - Moduli separati per configurazione, database, WebSocket

2. **Nomi Significativi**
   - Variabili e funzioni con nomi descrittivi
   - Costanti in UPPER_CASE
   - Funzioni con verbi (get, set, create, delete)

3. **Funzioni Piccole**
   - Massimo 20-30 righe per funzione
   - Logica complessa suddivisa in funzioni helper
   - Un livello di astrazione per funzione

4. **Gestione Errori Consistente**
   - Try-catch con logging dettagliato
   - HTTPException con messaggi chiari
   - Cleanup risorse in caso di errore

5. **Documentazione Completa**
   - Docstring per ogni classe e funzione
   - Commenti inline solo dove necessario
   - Type hints per parametri e return values

### Sicurezza

1. **Input Validation**
   - Validazione range per parametri numerici
   - Sanitizzazione nomi file
   - Controllo tipi MIME per upload

2. **Privacy**
   - Anonimizzazione IP (solo ultimi 8 caratteri)
   - Troncamento testi lunghi in cronologia
   - Nessun logging di dati sensibili

3. **Resource Management**
   - Cleanup automatico file temporanei
   - Chiusura esplicita connessioni database
   - Gestione connessioni WebSocket morte

## Deployment

### Requisiti

- Docker e Docker Compose
- Git
- PowerShell 5.1+ (Windows) o Bash (Linux/Mac)
- Azure Speech Services subscription

### Configurazione Iniziale

1. Clona il repository
2. Copia `.env.example` in `.env`
3. Configura `AZURE_SPEECH_KEY` nel `.env`
4. Esegui `docker compose up -d`

### Accesso Servizi

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentazione API: http://localhost:8000/docs

## Troubleshooting

### Problemi Comuni

#### Azure Speech Timeout
- Causa: Connessione lenta o firewall
- Soluzione: Verifica connessione internet, controlla firewall/proxy

#### Container Non Partono
- Causa: Porte occupate
- Soluzione: Verifica che 3000 e 8000 siano libere

#### Audio Metallico
- Causa: Normalizzazione troppo aggressiva
- Soluzione: Sistema applica automaticamente filtro passa-basso

#### Aggiornamento Fallito
- Causa: Errore durante build o deployment
- Soluzione: Sistema ripristina automaticamente backup precedente

## Manutenzione

### Backup Database
```bash
# Copia manuale database cronologia
cp text_history.db text_history.db.backup
```

### Pulizia File Temporanei
```bash
# Rimuovi file output vecchi
find output/ -type f -mtime +30 -delete
```

### Log Analysis
```bash
# Visualizza log container
docker compose logs backend --tail=100 --follow
docker compose logs frontend --tail=100 --follow
```

## Licenza

Vedi file LICENSE per dettagli sulla licenza del progetto.

## Supporto

Per problemi o domande, consultare la documentazione Azure Speech Services:
https://docs.microsoft.com/azure/cognitive-services/speech-service/
