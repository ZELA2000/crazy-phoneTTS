# 🚀 QUICKSTART - crazy-phoneTTS Azure Setup

Guida rapida per configurare il sistema TTS con Azure Speech Services per centralini professionali.## Prerequisiti

- Docker e Docker Compose installati

## ⚡ Setup in 5 Minuti- Almeno 4GB di RAM disponibili

- Porte 3000 e 8000 libere

### 1. **Crea Account Azure Speech Services**

## Avvio del Sistema

#### **Portal Azure**

1. Vai su [portal.azure.com](https://portal.azure.com)### 1. Posizionati nella cartella del progetto

2. Click **"Create a resource"**```bash

3. Cerca **"Speech Services"**
4. Click **"Create"**

#### **Configurazione Risorsa**
```bash
Name: tts-centralino-[your-company]
Subscription: [Your subscription]
Resource Group: rg-centralino
Location: West Europe
Pricing Tier: F0 (Free) - 500K chars/month
```

#### **Ottieni Credenziali**
1. Vai alla risorsa creata
2. **Keys and Endpoint** → Copy:
   - **Key 1**: `your_api_key_here`
   - **Location/Region**: `westeurope`

### 2. **Configurazione Progetto**

#### **Clone Repository**
```bash
git clone <repository-url>
cd crazy-phoneTTS
```

#### **File Environment (.env)**
Crea `.env` nella root:
```bash
# Azure Speech Services - OBBLIGATORIO

AZURE_SPEECH_KEY=your_api_key_here### Passo 3: Genera e Scarica

AZURE_SPEECH_REGION=westeurope- Clicca "Genera Audio"

- Attendi la processazione (30-60 secondi)

# Optional configurations- Ascolta l'anteprima e scarica il file finale

BACKEND_PORT=8000

FRONTEND_PORT=3000## 🎯 Ottimizzazioni per Centralini

```

### Volume Consigliati

### 3. **Avvio Sistema**- **Voce**: Volume automatico normalizzato

- **Musica**: 20-40% per messaggi informativi, 10-20% per annunci importanti

#### **Docker (Raccomandato)**

```bash### Durata Ottimale

# Build e avvio- **Messaggi brevi**: 10-30 secondi

docker-compose up --build- **Messaggi di attesa**: 30-60 secondi

- **Annunci**: 15-45 secondi

# In background

docker-compose up -d --build### Tipo di Musica

```- **Attesa**: Musica ambient, jazz soft, classica leggera

- **Informativa**: Musica corporate, soft pop

#### **Verifica Funzionamento**- **Promozionale**: Musica più energica ma non invasiva

```bash

# Health check## 🔧 Risoluzione Problemi

curl http://localhost:8000/health

### Il container backend non si avvia

# Response atteso:- Verifica di avere almeno 4GB RAM disponibili

# {- Controlla che la porta 8000 non sia occupata

#   "status": "healthy",

#   "azure_speech_ready": true,### Il frontend non si carica

#   "region": "westeurope"- Controlla che la porta 3000 non sia occupata

# }- Verifica che il backend sia attivo su localhost:8000

```

### Errore durante la generazione audio

### 4. **Primo Test**- Verifica che il file musicale sia un formato supportato

- Controlla che il testo non superi 1000 caratteri

#### **Web Interface**

1. Apri browser: http://localhost:3000### Performance lente

2. Inserisci testo: `"Benvenuto nel nostro centralino"`- Al primo avvio il modello TTS viene scaricato (normale)

3. Click **"Genera Audio"**- Su sistemi con poca RAM, aumenta lo swap

4. Ascolta e scarica il file WAV

## 🏗️ Struttura del Progetto

## 🎵 Setup Libreria Musicale

```

### **Upload Prima Musica**NEWCCFETTS/

1. Web interface → **"Libreria Musicale"**├── backend/              # FastAPI + Coqui TTS

2. **"Scegli File"** → Seleziona MP3/WAV│   ├── main.py          # API endpoints

3. Nome: `"Background Corporate"`│   ├── requirements.txt  # Dipendenze Python

4. **"Carica nella Libreria"**│   └── Dockerfile       # Container backend

├── frontend/            # React App

### **Test con Musica**│   ├── src/

## 🏗️ Struttura del Progetto

```
crazy-phoneTTS/
├── backend/              # FastAPI + Azure Speech
│   ├── main.py          # API endpoints
│   ├── requirements.txt  # Dipendenze Python
│   └── Dockerfile       # Container backend
├── frontend/            # React App
│   ├── src/
│   │   ├── App.js       # Componente principale
│   │   └── index.css    # Stili CSS
│   ├── package.json     # Dipendenze Node.js
│   └── Dockerfile       # Container frontend
├── docker-compose.yml   # Configurazione Docker
└── README.md           # Documentazione
```



### **Formato Telefonico Standard**## 🔄 Aggiornamenti e Personalizzazioni

```

Output Format: WAV### Cambiare la Voce TTS

Audio Quality: PCMModifica `backend/main.py`, linea del modello TTS:

Sample Rate: 8kHz```python

Bit Depth: 16-bit# Altre voci italiane disponibili:

```tts = TTS("tts_models/it/mai_male/glow-tts")  # Voce maschile

```

### **Formato G.711 (Europa)**

```### Modificare i Limiti

Output Format: GSM- **Lunghezza testo**: Cambia `maxLength` in `frontend/src/App.js`

Audio Quality: A-law- **Dimensione file**: Configura limiti in `backend/main.py`

Sample Rate: 8kHz

Bit Depth: 8-bit### Aggiungere Nuovi Formati

```Estendi la lista `audioTypes` in `frontend/src/App.js`



### **Nomi File Automatici**## 📞 Integrazione con Centralini

```

Pattern: {nome_personalizzato}_{YYMMDD}.{formato}### File Audio Generati

Esempio: centralino_welcome_250930.wav- Formato: WAV, 16-bit, 44.1kHz (compatibile con la maggior parte dei sistemi)

```- Naming: `centralino_audio_[timestamp].wav`



## ⚠️ Troubleshooting Veloce### Automazione

Per automatizzare la generazione, usa direttamente l'API:

### **Errore: API Key Missing**```bash

```bashcurl -X POST "http://localhost:8000/generate-audio" \

# Verifica variabili     -F "text=Il tuo messaggio" \

echo $AZURE_SPEECH_KEY     -F "music_file=@musica.mp3" \

echo $AZURE_SPEECH_REGION     -F "music_volume=0.3"

```

# Docker env check

docker-compose exec backend printenv | grep AZURE---

```

**Il sistema è ora pronto per l'uso!** 🎉

### **Errore: Speech Generation Failed**
```bash
# Test connettività diretta
curl -H "Ocp-Apim-Subscription-Key: $AZURE_SPEECH_KEY" \
     "https://$AZURE_SPEECH_REGION.api.cognitive.microsoft.com/sts/v1.0/issuetoken" \
     -X POST
```

---

**Sistema pronto in 5 minuti - Centralini professionali con Azure Speech Services** 🚀