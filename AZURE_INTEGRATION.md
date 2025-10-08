# Azure Speech Services Integration Guide

## Panoramica

crazy-phoneTTS è ora completamente integrato con **Azure Speech Services** per fornire sintesi vocale di qualità commerciale professionale per centralini telefonici.

## Configurazione Azure

### 1. Ottenere le Credenziali Azure

1. Vai al [portale Azure](https://portal.azure.com)
2. Crea una risorsa "Speech Services" 
3. Ottieni la **chiave** e la **region** dal pannello "Keys and Endpoint"

### 2. Configurazione Variabili d'Ambiente

```bash
# Obbligatorie
export AZURE_SPEECH_KEY="your-azure-speech-key-here"
export AZURE_SPEECH_REGION="westeurope"

# Opzionali - Configurazioni avanzate
export AZURE_SPEECH_ENDPOINT="your-custom-endpoint"  # Solo se usi endpoint personalizzato
export AZURE_CONNECTION_TIMEOUT="10"                 # Timeout connessione (secondi)
export AZURE_REQUEST_TIMEOUT="30"                    # Timeout richiesta (secondi)
export AZURE_MAX_RETRIES="3"                        # Numero massimo di retry
export AZURE_RETRY_DELAY="1.0"                      # Delay tra retry (secondi)
```

### 3. Docker Configuration

Nel `docker-compose.yml`, aggiungi le variabili d'ambiente:

```yaml
services:
  backend:
    environment:
      - AZURE_SPEECH_KEY=${AZURE_SPEECH_KEY}
      - AZURE_SPEECH_REGION=${AZURE_SPEECH_REGION}
```

## Voci Disponibili

### Voci Neural (Consigliate)

#### Femminili
- **it-IT-ElsaNeural**: Voce professionale per centralini aziendali
- **it-IT-IsabellaNeural**: Voce espressiva per messaggi promozionali
- **it-IT-IrmaNeural**: Voce calda per supporto clienti

#### Maschili  
- **it-IT-DiegoNeural**: Voce autorevole per annunci ufficiali
- **it-IT-BenignoNeural**: Voce espressiva per guide vocali
- **it-IT-CalimeroNeural**: Voce moderna per comunicazioni dinamiche

### Stili Vocali Supportati

- `customerservice`: Ottimizzato per servizio clienti
- `newscast`: Stile da giornalista/annunciatore
- `assistant`: Stile da assistente virtuale
- `chat`: Conversazionale e amichevole
- `cheerful`: Allegro e positivo
- `friendly`: Amichevole e accogliente
- `excited`: Entusiasta ed energico

## Funzionalità Avanzate

### 1. Controlli SSML

```python
# Esempio di opzioni SSML personalizzate
ssml_options = {
    'rate': 'medium',           # Velocità: x-slow, slow, medium, fast, x-fast
    'pitch': 'medium',          # Tono: x-low, low, medium, high, x-high  
    'volume': 'loud',           # Volume: silent, x-soft, soft, medium, loud, x-loud
    'style': 'customerservice', # Stile vocale (solo Neural)
    'emphasis': 'strong',       # Enfasi: strong, moderate, reduced
    'break_time': 1.0          # Pausa iniziale in secondi
}
```

### 2. Gestione Errori e Retry

Il sistema implementa automaticamente:
- **Timeout configurabili** per connessioni e richieste
- **Retry con backoff esponenziale** in caso di errori temporanei
- **Logging dettagliato** per debugging
- **Validazione della configurazione** all'avvio

### 3. Monitoraggio e Health Check

```bash
# Verifica stato del servizio
GET /health

# Testa una voce specifica
POST /test-voice
```

## API Endpoints

### Sintesi Vocale Principale

```bash
POST /generate-audio
```

**Parametri principali:**
- `text`: Testo da sintetizzare
- `edge_voice`: ID della voce Azure (es. "it-IT-ElsaNeural")
- `music_file`: File musicale opzionale
- `music_volume`: Volume musica (0.0-1.0)
- `output_format`: wav, mp3, gsm
- `audio_quality`: pcm, alaw, ulaw

### Gestione Voci

```bash
GET /available-voices    # Lista tutte le voci disponibili
GET /speakers           # Lista dettagliata con stili
POST /test-voice        # Testa una voce specifica
```

### Libreria Musicale

```bash
POST /music-library/upload    # Carica musica
GET /music-library/list       # Lista musica disponibile
DELETE /music-library/{id}    # Elimina musica
```

## Best Practices per Centralini

### 1. Selezione Voci
- **Centralini aziendali**: `it-IT-ElsaNeural` con stile `customerservice`
- **Messaggi promozionali**: `it-IT-IsabellaNeural` con stile `cheerful`
- **Supporto tecnico**: `it-IT-DiegoNeural` con stile `assistant`

### 2. Parametri Audio
- **Formato**: WAV per qualità massima, MP3 per dimensioni ridotte
- **Qualità**: PCM (16bit) per sistema digitali, A-law/μ-law per analogici
- **Volume voce**: Sempre prioritario sulla musica di sottofondo

### 3. Ottimizzazioni SSML
```xml
<!-- Esempio per centralino -->
<speak version="1.0" xml:lang="it-IT">
    <voice name="it-IT-ElsaNeural">
        <mstts:express-as style="customerservice" styledegree="1.2">
            <prosody rate="medium" volume="loud">
                Benvenuti in Azienda XYZ.
                <break time="0.5s"/>
                Per parlare con un operatore, premete 0.
            </prosody>
        </mstts:express-as>
    </voice>
</speak>
```

## Risoluzione Problemi

### Errori Comuni

1. **"Azure Speech Key not configured"**
   - Verifica che `AZURE_SPEECH_KEY` sia impostata correttamente

2. **"Connection timeout"** 
   - Verifica connessione internet
   - Aumenta `AZURE_CONNECTION_TIMEOUT`

3. **"Voice not found"**
   - Usa `/available-voices` per vedere le voci disponibili
   - Verifica che la region supporti la voce scelta

### Logging

Configura il livello di log per debugging:
```bash
export LOG_LEVEL=DEBUG
```

## Pricing Azure

- **Standard**: ~€4 per 1M caratteri
- **Neural**: ~€16 per 1M caratteri  
- **Primo milione di caratteri gratis ogni mese**

Consulta [Azure Pricing](https://azure.microsoft.com/pricing/details/cognitive-services/speech-services/) per dettagli aggiornati.

## Supporto

- **Documentazione Azure**: https://docs.microsoft.com/azure/cognitive-services/speech-service/
- **Issues GitHub**: Apri un issue per problemi specifici
- **Support Azure**: Per problemi con l'account Azure

---

**crazy-phoneTTS** - TTS professionale per centralini con Azure Speech Services