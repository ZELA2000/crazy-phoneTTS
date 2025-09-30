# 🎵 crazy-phoneTTS - Funzionalità Avanzate per la Musica

## ✨ Nuove Funzionalità Implementate

### 🎛️ Controlli Audio Avanzati

- **Timing Musicale Personalizzabile**:
  - Impostare durata musica prima del testo (0-10 secondi)
  - Impostare durata musica dopo il testo (0-10 secondi)
  
- **Effetti Audio Professionali**:
  - Fade In regolabile (0-5 secondi)
  - Fade Out regolabile (0-5 secondi)
  - Volume musica indipendente dal volume voce
  - Riduzione automatica volume musica durante la voce (-6dB)

### 📚 Libreria Musicale Persistente

- **Gestione Canzoni**:
  - Upload canzoni con nome personalizzabile
  - Visualizzazione durata e dimensione file
  - Eliminazione canzoni dalla libreria
  - Selezione rapida dalla libreria per riutilizzo

- **Interfaccia Intuitiva**:
  - Lista visuale delle canzoni caricate
  - Indicatore visivo canzone selezionata
  - Anteprima informazioni audio (durata, dimensione)
  - Upload drag & drop per nuove canzoni

### 🎚️ Mixaggio Audio Intelligente

- **Struttura Audio Professionale**:
  1. **Intro musicale** (solo musica con fade in)
  2. **Voce + sottofondo** (musica ridotta durante parlato)
  3. **Outro musicale** (solo musica con fade out)

- **Ottimizzazioni Audio**:
  - Normalizzazione automatica
  - Filtro passa-basso per voce più naturale
  - Loop automatico musica se più corta del testo
  - Bilanciamento dinamico voce/musica

## 🚀 Come Utilizzare le Nuove Funzionalità

### 1. Libreria Musicale

```bash
# Avvia il sistema
docker-compose up --build

# Accedi all'interfaccia web
http://localhost:3000
```

1. **Caricare una canzone**:
   - Clicca "📚 Apri Libreria Musicale"
   - Inserisci nome canzone
   - Seleziona file audio (MP3/WAV/OGG)
   - Clicca "📤 Carica"

2. **Usare una canzone dalla libreria**:
   - Scegli dalla lista delle canzoni caricate
   - La canzone selezionata sarà evidenziata
   - Procedi con la generazione audio

### 2. Controlli Audio Avanzati

Quando hai selezionato una musica (libreria o upload), appariranno i controlli:

- **Volume musica**: 0-100% (slider)
- **Musica prima del testo**: 0-10 secondi
- **Musica dopo il testo**: 0-10 secondi  
- **Fade In**: 0-5 secondi
- **Fade Out**: 0-5 secondi

### 3. Esempi di Configurazione

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

## 🔧 API Endpoints Aggiornati

### Nuovi Endpoint Libreria Musicale

```http
# Upload canzone alla libreria
POST /music-library/upload
Content-Type: multipart/form-data
- name: string (nome canzone)
- music_file: file (audio file)

# Lista canzoni in libreria
GET /music-library/list
Response: {"songs": [...]}

# Elimina canzone dalla libreria
DELETE /music-library/{song_id}
```

### Endpoint Generate-Audio Esteso

```http
POST /generate-audio
Content-Type: multipart/form-data

# Parametri esistenti
- text: string
- music_file: file (opzionale)
- music_volume: float (0.0-1.0)
- tts_service: string
- edge_voice: string
- language: string

# NUOVI parametri
- library_song_id: string (ID canzone da libreria)
- music_before_seconds: float (0-10)
- music_after_seconds: float (0-10)
- fade_in_duration: float (0-5)
- fade_out_duration: float (0-5)
```

## 📁 Struttura Directory Aggiornata

```
backend/
├── uploads/
│   ├── library/          # 📚 NUOVO: Libreria musicale persistente
│   │   ├── {uuid}.mp3    # File audio canzoni
│   │   └── {uuid}.json   # Metadata canzoni
│   └── README_MUSIC.md
├── output/               # File audio generati
└── voices/              # Campioni voice cloning
```

## 🎯 Vantaggi per Centralini

1. **Efficienza**: Riutilizzo canzoni senza ri-upload
2. **Professionalità**: Controllo preciso timing e fade
3. **Consistency**: Stessa musica per tutti i messaggi aziendali
4. **Flessibilità**: Diverse configurazioni per diversi scopi
5. **Qualità**: Mixaggio automatico professionale

## 🔍 Monitoraggio e Debug

- **Logs Backend**: Controllare container logs per upload/eliminazioni
- **Storage**: Canzoni salvate in volume Docker persistente
- **Performance**: Cache automatic delle canzoni caricate
- **Errori**: Gestione errori completa con messaggi informativi

Le nuove funzionalità sono **fully backward compatible** - il sistema funziona esattamente come prima se non si usano le nuove opzioni.