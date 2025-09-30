# 🎙️ crazy-phoneTTS - Azure Speech Services

Sistema Text-to-Speech professionale per centralini telefonici con Azure Speech Services e libreria musicale integrata.

## ⭐ Caratteristiche Principali

### 🏢 **Azure Speech Services** - Licenza Commerciale
- ✅ **Uso Commerciale Legale** per centralini business
- ✅ **Piano F0 Gratuito**: 500.000 caratteri/mese
- ✅ **SLA 99.9%** garantito da Microsoft
- ✅ **Voci Neural Italiane** di alta qualità

### 🎵 **Libreria Musicale Avanzata**
- ✅ **Upload Multipli**: MP3, WAV, OGG
- ✅ **Gestione Persistente** con metadati
- ✅ **Controlli Audio**: Volume, fade in/out, timing
- ✅ **Anteprima Integrata** prima della generazione

### 🔧 **Funzionalità Professionali**
- ✅ **Formati Output**: WAV, MP3, GSM
- ✅ **Qualità Telefonica**: PCM, A-law, μ-law
- ✅ **Nomi File Personalizzati** con data
- ✅ **Interface Responsive** per tutti i dispositivi

## 🚀 Avvio Rapido

### 1. **Setup Azure Speech Services**

1. **Crea risorsa Speech** nel [Portal Azure](https://portal.azure.com)
2. **Copia le credenziali**:
   - API Key
   - Region (es. `westeurope`)

### 2. **Configurazione Environment**

Crea file `.env` nella root del progetto:

```bash
# Azure Speech Services
AZURE_SPEECH_KEY=your_api_key_here
AZURE_SPEECH_REGION=westeurope
```

### 3. **Avvio con Docker**

```bash
# Clone del repository
git clone <repository-url>
cd crazy-phoneTTS

# Build e avvio
docker-compose up --build
```

### 4. **Accesso Web**

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📊 Piano Azure F0 - Perfetto per Centralini

| Caratteristica | Piano F0 Gratuito |
|----------------|------------------|
| **Caratteri/mese** | 500.000 GRATIS |
| **Messaggi centralino** | ~6.600/mese* |
| **Uso commerciale** | ✅ Autorizzato |
| **SLA** | 99.9% |
| **Costo eccedenza** | $1/milione caratteri |

*Basato su 75 caratteri per messaggio medio

## 🎙️ Voci Italiane Disponibili

| Voce | Tipo | Descrizione |
|------|------|-------------|
| `it-IT-ElsaNeural` | Femmina | Naturale, professionale |
| `it-IT-IsabellaNeural` | Femmina | Espressiva, dinamica |
| `it-IT-DiegoNeural` | Maschio | Naturale, autorevole |
| `it-IT-BenignoNeural` | Maschio | Espressivo, caloroso |

## 🎵 Gestione Libreria Musicale

### **Upload Musiche**
1. Sezione "Libreria Musicale"
2. Click "Scegli File" → Seleziona MP3/WAV/OGG
3. Inserisci nome descrittivo
4. Click "Carica"

### **Controlli Audio Avanzati**
- **Volume Musica**: 0-100% regolabile
- **Timing**: Musica prima/dopo il parlato
- **Fade Effects**: In/Out con durata personalizzabile
- **Anteprima**: Player integrato per test

### **Formati Output**
- **WAV**: Qualità massima per centralini
- **MP3**: Compresso per storage
- **GSM**: Ottimizzato per telefonia

## 📁 Struttura File Output

```
output/
├── {nome_personalizzato}_{YYMMDD}.wav
├── {nome_personalizzato}_{YYMMDD}.mp3
└── {nome_personalizzato}_{YYMMDD}.gsm
```

Esempio: `centralino_welcome_250930.wav`

## 🛠️ Configurazione Avanzata

### **Variables Environment Complete**

```bash
# Azure Speech Services (OBBLIGATORIO)
AZURE_SPEECH_KEY=your_subscription_key
AZURE_SPEECH_REGION=westeurope

# Server Configuration (OPZIONALE)
BACKEND_PORT=8000
FRONTEND_PORT=3000
CORS_ORIGINS=http://localhost:3000

# Storage Paths (OPZIONALE)
UPLOAD_PATH=./uploads
OUTPUT_PATH=./output
MUSIC_LIBRARY_PATH=./uploads/library
```

## 🔍 Monitoring e Diagnostica

### **Health Check API**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "azure_speech_ready": true,
  "region": "westeurope"
}
```

## 🆘 Troubleshooting

### **Errore: "Azure Speech generation failed"**
```bash
# Verifica configurazione
echo $AZURE_SPEECH_KEY
echo $AZURE_SPEECH_REGION

# Test connettività Azure
curl -H "Ocp-Apim-Subscription-Key: $AZURE_SPEECH_KEY" \
     "https://$AZURE_SPEECH_REGION.api.cognitive.microsoft.com/sts/v1.0/issuetoken" -X POST
```

### **Problema Upload Musica**
```bash
# Verifica permissions
docker exec crazy-phonetts-backend ls -la uploads/library/

# Cleanup storage
docker-compose exec backend rm -rf uploads/library/*
```

## 📚 API Reference

### **Genera Audio**
```http
POST /generate-audio
Content-Type: multipart/form-data

text: "Benvenuto in azienda"
tts_service: "azure" 
edge_voice: "it-IT-ElsaNeural"
music_volume: 0.3
output_format: "wav"
audio_quality: "pcm"
custom_filename: "welcome_message"
```

### **Gestione Libreria**
```http
GET /music-library/list
POST /music-library/upload
DELETE /music-library/{song_id}
```

## 🔗 Link Utili

- [Azure Speech Services Portal](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices)
- [Documentazione Ufficiale](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/)
- [Prezzi Azure Speech](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/)
- [Supporto Microsoft](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/support)

---

**Sviluppato per centralini professionali con Azure Speech Services F0 - Legale e Scalabile** 🏢