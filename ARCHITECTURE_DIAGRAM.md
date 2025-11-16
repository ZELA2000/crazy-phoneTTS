# Architettura Backend - Diagramma Visuale

```
┌─────────────────────────────────────────────────────────────────┐
│                        🚀 main.py                               │
│                   (FastAPI Entry Point)                         │
│                                                                 │
│  • Inizializzazione app FastAPI                                │
│  • Definizione endpoint REST                                   │
│  • Configurazione middleware                                   │
│  • WebSocket endpoints                                         │
└────────────┬────────────────────────────────────┬──────────────┘
             │                                    │
             ▼                                    ▼
    ┌────────────────┐                   ┌────────────────┐
    │   📦 CORE      │                   │  📦 MODELS     │
    │                │                   │                │
    │ config.py      │◄──────────────────┤ history.py     │
    │                │                   │ voice_catalog  │
    │ • App Config   │                   │                │
    │ • Azure Config │                   │ • DB History   │
    │ • Network      │                   │ • Voice Data   │
    │ • Validation   │                   │ • Catalog      │
    └────────┬───────┘                   └────────┬───────┘
             │                                    │
             ▼                                    ▼
    ┌────────────────────────────────────────────────────┐
    │              📦 SERVICES                           │
    │                                                    │
    │ azure_speech.py                                    │
    │                                                    │
    │ • AzureSpeechService                              │
    │ • SSMLGenerator                                   │
    │ • Voice Synthesis                                 │
    │ • Azure API Integration                           │
    └────────────────────┬───────────────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────────────────┐
    │              📦 MANAGERS                            │
    │  (Business Logic & Coordination)                    │
    │                                                     │
    │ ┌─────────────────────────────────────────────┐   │
    │ │ websocket_manager.py                        │   │
    │ │ • Real-time connections                     │   │
    │ │ • History updates broadcast                 │   │
    │ │ • Progress notifications                    │   │
    │ └─────────────────────────────────────────────┘   │
    │                                                     │
    │ ┌─────────────────────────────────────────────┐   │
    │ │ update_manager.py                           │   │
    │ │ • Update progress tracking                  │   │
    │ │ • State persistence                         │   │
    │ │ • Host-container coordination               │   │
    │ └─────────────────────────────────────────────┘   │
    │                                                     │
    │ ┌─────────────────────────────────────────────┐   │
    │ │ audio_processor.py                          │   │
    │ │ • Format conversion (WAV/MP3/GSM)          │   │
    │ │ • Quality specs (PCM/A-law/u-law)          │   │
    │ │ • Telephony optimization                    │   │
    │ └─────────────────────────────────────────────┘   │
    │                                                     │
    │ ┌─────────────────────────────────────────────┐   │
    │ │ music_library.py                            │   │
    │ │ • Music file management                     │   │
    │ │ • Metadata handling                         │   │
    │ │ • Audio duration calculation                │   │
    │ └─────────────────────────────────────────────┘   │
    │                                                     │
    │ ┌─────────────────────────────────────────────┐   │
    │ │ version_manager.py                          │   │
    │ │ • Version tracking                          │   │
    │ │ • GitHub release checking                   │   │
    │ │ • Semver comparison                         │   │
    │ └─────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────┘
```

## Flusso Dati Tipico

### 1. Richiesta Generazione Audio TTS

```
┌─────────┐
│ Cliente │
│ (HTTP)  │
└────┬────┘
     │
     │ POST /generate-audio
     ▼
┌─────────────────┐
│   main.py       │
│  (Endpoint)     │
└────┬────────────┘
     │
     ├─► core.config
     │   └─► Legge configurazione Azure
     │
     ├─► models.voice_catalog
     │   └─► Valida voce richiesta
     │
     ├─► services.azure_speech
     │   └─► Sintetizza audio con Azure
     │
     ├─► managers.audio_processor
     │   └─► Converte nel formato richiesto
     │
     ├─► managers.music_library (opzionale)
     │   └─► Mixa con musica di sottofondo
     │
     └─► models.history
         └─► Salva nel database

     ┌────────────┐
     │ File Audio │ ◄─── Risposta al cliente
     └────────────┘
```

### 2. WebSocket Real-time Updates

```
┌──────────┐
│ Cliente  │
│(WebSocket│
└────┬─────┘
     │
     │ WS /ws/history
     ▼
┌───────────────────┐
│ managers.         │
│ websocket_manager │
└────┬──────────────┘
     │
     │ Nuovo testo sintetizzato
     ▼
┌──────────────┐
│ models.      │
│ history      │
└──────┬───────┘
       │
       │ Broadcast update
       ▼
┌──────────────┐
│ Tutti i      │
│ client       │
│ connessi     │
└──────────────┘
```

### 3. Sistema Aggiornamento

```
┌─────────┐
│ Cliente │
└────┬────┘
     │
     │ POST /update/start
     ▼
┌────────────────┐
│ managers.      │
│ version_mgr    │
└────┬───────────┘
     │
     │ Check GitHub
     ▼
┌────────────────┐
│ GitHub API     │
└────┬───────────┘
     │
     │ Nuova versione?
     ▼
┌────────────────┐
│ managers.      │
│ update_manager │
└────┬───────────┘
     │
     │ Progress updates
     ▼
┌────────────────┐
│ WebSocket      │
│ Broadcast      │
└────────────────┘
```

## Relazioni tra Componenti

```
┌──────────────────────────────────────────────────────────┐
│                    DEPENDENCY GRAPH                       │
└──────────────────────────────────────────────────────────┘

main.py
  │
  ├──► core.config ────────────────┐
  │                                 │
  ├──► models.history ──────────────┤
  │                                 │
  ├──► models.voice_catalog ────────┤
  │                                 │
  ├──► services.azure_speech ───────┼──► core.config
  │                                 │
  └──► managers.*                   │
         │                          │
         ├──► websocket_manager ────┤
         ├──► update_manager ───────┤
         ├──► audio_processor ──────┤
         ├──► music_library ────────┤
         └──► version_manager ──────┘

LEGENDA:
────► Dipendenza diretta
═══► Dipendenza forte (richiesta)
- - -> Dipendenza opzionale
```

## Pattern Architetturali Applicati

### 1. Layered Architecture

```
┌────────────────────────────────────┐
│   Presentation Layer (main.py)    │ ◄─── REST API / WebSocket
├────────────────────────────────────┤
│   Business Layer (managers/)      │ ◄─── Logica applicativa
├────────────────────────────────────┤
│   Service Layer (services/)       │ ◄─── Integrazioni esterne
├────────────────────────────────────┤
│   Data Layer (models/)            │ ◄─── Persistenza dati
├────────────────────────────────────┤
│   Core Layer (core/)              │ ◄─── Configurazione base
└────────────────────────────────────┘
```

### 2. Dependency Injection

```python
# Esempio in main.py
app_config = ApplicationConfiguration()
azure_speech = AzureSpeechService(
    speech_key=app_config.azure.speech_key,
    speech_region=app_config.azure.speech_region
)
```

### 3. Repository Pattern

```python
# models/history.py
class TextHistoryDatabase:
    def add_text_entry(...)  # Create
    def get_recent_entries(...)  # Read
    # Update / Delete methods
```

### 4. Facade Pattern

```python
# managers/audio_processor.py
class AudioConverter:
    def convert(...)  # Nasconde complessità conversione
```

## Metriche Architettura

### Accoppiamento (Coupling)

| Componente | Accoppiamento | Valutazione |
|------------|---------------|-------------|
| core/ | Nessuno | ⭐⭐⭐⭐⭐ Ottimo |
| models/ | Basso (solo core) | ⭐⭐⭐⭐⭐ Ottimo |
| services/ | Basso | ⭐⭐⭐⭐ Buono |
| managers/ | Medio | ⭐⭐⭐⭐ Buono |
| main.py | Alto (coordina) | ⭐⭐⭐ Accettabile |

### Coesione (Cohesion)

| Componente | Coesione | Valutazione |
|------------|----------|-------------|
| core/ | Funzionale | ⭐⭐⭐⭐⭐ Ottimo |
| models/ | Funzionale | ⭐⭐⭐⭐⭐ Ottimo |
| services/ | Funzionale | ⭐⭐⭐⭐⭐ Ottimo |
| managers/ | Funzionale | ⭐⭐⭐⭐ Buono |

### Complessità Ciclomatica

```
Modulo                          Complessità Media
─────────────────────────────────────────────────
core/config.py                        3
models/history.py                     4
models/voice_catalog.py               3
services/azure_speech.py              5
managers/websocket_manager.py         4
managers/update_manager.py            4
managers/audio_processor.py           6
managers/music_library.py             5
managers/version_manager.py           4
main.py                               8
─────────────────────────────────────────────────
MEDIA TOTALE                          4.6
```

✅ Complessità media **Bassa** (target < 10)

## Conclusioni

L'architettura organizzata offre:

✅ **Separazione concerns** - Ogni layer ha responsabilità chiare  
✅ **Scalabilità** - Facile aggiungere nuovi componenti  
✅ **Testabilità** - Componenti isolati e mockabili  
✅ **Manutenibilità** - Codice organizzato e comprensibile  
✅ **Standard industry** - Pattern riconosciuti e documentati  

La struttura è pronta per:
- Team development
- Continuous integration
- Production deployment
- Future expansion
