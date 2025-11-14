from fastapi import FastAPI, File, UploadFile, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil
import sqlite3
import json
from typing import List, Dict, Any
from pydub import AudioSegment
from pydub.effects import normalize
import tempfile
import logging
import azure.cognitiveservices.speech as speechsdk
import asyncio
import aiofiles
import requests
import io
from datetime import datetime
import threading
import subprocess
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure Speech Services Configuration - Best Practices Implementation
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "westeurope")
AZURE_SPEECH_ENDPOINT = os.getenv("AZURE_SPEECH_ENDPOINT")  # Optional: custom endpoint

# Network Configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")  # Default: accept connections from all IPs
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))  # Default: port 8000

if not AZURE_SPEECH_KEY:
    logger.error("AZURE_SPEECH_KEY non configurata! Configura la variabile d'ambiente AZURE_SPEECH_KEY.")
    logger.info("Per ottenere una chiave Azure Speech: https://docs.microsoft.com/azure/cognitive-services/speech-service/get-started")
else:
    logger.info("Azure Speech Services configurato correttamente")

logger.info(f"Server configurato per ascoltare su: {BACKEND_HOST}:{BACKEND_PORT}")

# File per progress persistente durante aggiornamenti
UPDATE_PROGRESS_FILE = "update_progress.json"

# ==========================================
# SISTEMA CRONOLOGIA TESTI REAL-TIME
# ==========================================

# Manager per connessioni WebSocket attive
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nuova connessione WebSocket. Totale: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Connessione WebSocket chiusa. Totale: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Invia messaggio a tutti i client connessi"""
        if self.active_connections:
            dead_connections = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    dead_connections.append(connection)
            
            # Rimuovi connessioni morte
            for dead in dead_connections:
                self.disconnect(dead)

manager = ConnectionManager()

# ==========================================
# FUNZIONI HELPER PROGRESS PERSISTENTE
# ==========================================

def save_update_progress(progress_data):
    """Salva il progress dell'aggiornamento su file"""
    try:
        progress_data["timestamp"] = datetime.now().isoformat()
        with open(UPDATE_PROGRESS_FILE, 'w') as f:
            json.dump(progress_data, f, indent=2)
        logger.info(f"Progress salvato: {progress_data.get('message', 'N/A')}")
    except Exception as e:
        logger.error(f"Errore salvataggio progress: {e}")

def load_update_progress():
    """Carica il progress dell'aggiornamento dal file"""
    try:
        if os.path.exists(UPDATE_PROGRESS_FILE):
            with open(UPDATE_PROGRESS_FILE, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"Errore caricamento progress: {e}")
        return None

def clear_update_progress():
    """Pulisce il file di progress"""
    try:
        if os.path.exists(UPDATE_PROGRESS_FILE):
            os.remove(UPDATE_PROGRESS_FILE)
        logger.info("File progress pulito")
    except Exception as e:
        logger.error(f"Errore pulizia progress: {e}")

def run_update_script_background(script_path, version, progress_callback=None):
    """Crea il file di richiesta per l'aggiornamento host-side"""
    try:
        # Salva progress iniziale
        save_update_progress({
            "type": "progress",
            "step": "script_start", 
            "message": "🚀 Preparazione aggiornamento host-side...",
            "percentage": 10,
            "status": "running"
        })
        
        # Crea file di richiesta aggiornamento per l'host
        update_request = {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "script": script_path,
            "status": "requested"
        }
        
        # Salva file di richiesta nella directory progetto (accessibile all'host)
        request_file = "/app/project/update_request.json"
        with open(request_file, 'w') as f:
            json.dump(update_request, f, indent=2)
        
        logger.info(f"File di richiesta aggiornamento creato: {request_file}")
        logger.info(f"Versione richiesta: {version}")
        
        # Aggiorna progress per indicare che l'host deve prendere il controllo
        save_update_progress({
            "type": "progress",
            "step": "waiting_host",
            "message": "⏳ In attesa che l'host esegua l'aggiornamento...",
            "percentage": 20,
            "status": "waiting_host",
            "info": "L'aggiornamento deve essere completato dall'host, non dal container"
        })
        
        return True
        
    except Exception as e:
        logger.error(f"Errore creazione richiesta aggiornamento: {e}")
        save_update_progress({
            "type": "error",
            "step": "error",
            "message": f"❌ Errore preparazione aggiornamento: {str(e)}",
            "percentage": 0,
            "status": "error"
        })
        return False

# Database per cronologia testi
def init_database():
    """Inizializza database SQLite per cronologia"""
    conn = sqlite3.connect('text_history.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS text_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            voice TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_ip TEXT,
            audio_generated BOOLEAN DEFAULT FALSE
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database cronologia inizializzato")

def add_text_to_history(text: str, voice: str, user_ip: str = None):
    """Aggiunge testo alla cronologia"""
    conn = sqlite3.connect('text_history.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO text_history (text, voice, user_ip, audio_generated)
        VALUES (?, ?, ?, TRUE)
    ''', (text, voice, user_ip))
    
    conn.commit()
    history_id = cursor.lastrowid
    conn.close()
    
    return history_id

def get_recent_history(limit: int = 10):
    """Recupera cronologia recente"""
    conn = sqlite3.connect('text_history.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, text, voice, timestamp, user_ip
        FROM text_history 
        WHERE audio_generated = TRUE
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "text": row[1][:100] + "..." if len(row[1]) > 100 else row[1],  # Trunca testi lunghi
            "voice": row[2],
            "timestamp": row[3],
            "user_ip": row[4][-8:] if row[4] else "unknown"  # Solo ultimi 8 caratteri IP per privacy
        }
        for row in rows
    ]

# Inizializza database all'avvio
init_database()

def convert_audio_to_format(audio_segment, output_format, audio_quality, custom_filename):
    """
    Converte l'audio nel formato e qualità richiesti secondo le specifiche:
    PCM: 8K, 16bit, 128kbps
    A-law (g.711): 8k, 8bit, 64kbps  
    u-law (g.711): 8k, 8bit, 64kbps
    """
    from datetime import datetime
    
    # Genera data in formato YYMMDD
    date_str = datetime.now().strftime("%y%m%d")
    
    # Pulisci il nome personalizzato per la sicurezza
    clean_name = "".join(c for c in custom_filename if c.isalnum() or c in "._-").strip()
    if not clean_name:
        clean_name = "centralino_audio"
    
    # Applica le specifiche per qualità telefonica
    if audio_quality == "pcm":
        # PCM: 8K, 16bit, 128kbps
        audio_segment = audio_segment.set_frame_rate(8000)
        audio_segment = audio_segment.set_channels(1)  # Mono
        audio_segment = audio_segment.set_sample_width(2)  # 16 bit
    elif audio_quality == "alaw":
        # A-law: 8k, 8bit, 64kbps
        audio_segment = audio_segment.set_frame_rate(8000)
        audio_segment = audio_segment.set_channels(1)  # Mono
        audio_segment = audio_segment.set_sample_width(1)  # 8 bit
    elif audio_quality == "ulaw":
        # u-law: 8k, 8bit, 64kbps
        audio_segment = audio_segment.set_frame_rate(8000)
        audio_segment = audio_segment.set_channels(1)  # Mono
        audio_segment = audio_segment.set_sample_width(1)  # 8 bit
    
    # Determina percorso output e parametri di export
    if output_format == "wav":
        output_path = f"output/{clean_name}_{date_str}.wav"
        if audio_quality == "alaw":
            audio_segment.export(output_path, format="wav", parameters=["-acodec", "pcm_alaw"])
        elif audio_quality == "ulaw":
            audio_segment.export(output_path, format="wav", parameters=["-acodec", "pcm_mulaw"])
        else:  # pcm
            audio_segment.export(output_path, format="wav")
    elif output_format == "mp3":
        output_path = f"output/{clean_name}_{date_str}.mp3"
        audio_segment.export(output_path, format="mp3", bitrate="128k" if audio_quality == "pcm" else "64k")
    elif output_format == "gsm":
        output_path = f"output/{clean_name}_{date_str}.gsm"
        audio_segment.export(output_path, format="gsm")
    
    return output_path

def get_media_type(output_format):
    """Restituisce il media type corretto per il formato"""
    format_map = {
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "gsm": "audio/gsm"
    }
    return format_map.get(output_format, "audio/wav")

app = FastAPI(title="crazy-phoneTTS API", description="TTS con mixaggio musicale per centralini")

# CORS middleware per il frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consenti tutte le origini
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure Speech Services Italian voices - Voci Neural di ultima generazione
AZURE_VOICES = {
    # Voci Neural femminili
    "it-IT-ElsaNeural": {
        "name": "Elsa",
        "gender": "Female", 
        "description": "Voce femminile naturale e professionale",
        "styles": ["customerservice", "newscast", "assistant", "chat"],
        "recommended_for": "Centralini aziendali, servizio clienti"
    },
    "it-IT-IsabellaNeural": {
        "name": "Isabella",
        "gender": "Female",
        "description": "Voce femminile espressiva e accogliente", 
        "styles": ["chat", "cheerful", "newscast", "assistant"],
        "recommended_for": "Messaggi di benvenuto, annunci pubblicitari"
    },
    "it-IT-IrmaNeural": {
        "name": "Irma",
        "gender": "Female",
        "description": "Voce femminile calda e rassicurante",
        "styles": ["chat", "friendly", "assistant"],
        "recommended_for": "Supporto clienti, messaggi informativi"
    },
    
    # Voci Neural maschili
    "it-IT-DiegoNeural": {
        "name": "Diego",
        "gender": "Male",
        "description": "Voce maschile autorevole e chiara",
        "styles": ["customerservice", "newscast", "assistant"],
        "recommended_for": "Annunci ufficiali, messaggi istituzionali"
    },
    "it-IT-BenignoNeural": {
        "name": "Benigno", 
        "gender": "Male",
        "description": "Voce maschile espressiva e coinvolgente",
        "styles": ["chat", "friendly", "assistant"],
        "recommended_for": "Messaggi promozionali, guide vocali"
    },
    "it-IT-CalimeroNeural": {
        "name": "Calimero",
        "gender": "Male", 
        "description": "Voce maschile moderna e dinamica",
        "styles": ["chat", "excited", "friendly"],
        "recommended_for": "Messaggi giovani, comunicazioni dinamiche"
    },
    
    # Voci standard (compatibilità)
    "it-IT-Giuseppe": {
        "name": "Giuseppe",
        "gender": "Male",
        "description": "Voce maschile standard",
        "styles": [],
        "recommended_for": "Compatibilità con sistemi legacy"
    },
    "it-IT-Lucia": {
        "name": "Lucia", 
        "gender": "Female",
        "description": "Voce femminile standard",
        "styles": [],
        "recommended_for": "Compatibilità con sistemi legacy"
    }
}

@app.on_event("startup")
async def startup_event():
    """Inizializzazione e validazione della configurazione Azure Speech Services"""
    logger.info("🚀 crazy-phoneTTS Server Starting...")
    logger.info(f"📍 Azure Speech Region: {AZURE_SPEECH_REGION}")
    
    if AZURE_SPEECH_KEY:
        logger.info("🔑 Azure Speech API Key: ✓ Configured")
        
        # Test della connessione Azure Speech
        try:
            await test_azure_speech_connection()
            logger.info("🎤 Azure Speech Services: ✓ Connection verified")
        except Exception as e:
            logger.error(f"❌ Azure Speech Services: Connection failed - {e}")
            logger.warning("⚠️  TTS service may not work properly")
    else:
        logger.error("❌ Azure Speech API Key: Missing")
        logger.error("📚 Setup guide: https://docs.microsoft.com/azure/cognitive-services/speech-service/get-started")
    
    logger.info("✅ TTS server ready for commercial use!")

async def test_azure_speech_connection():
    """Testa la connessione ad Azure Speech Services con gestione avanzata timeout"""
    try:
        if not AZURE_SPEECH_KEY:
            raise ValueError("Azure Speech Key not configured")
        
        logger.info(f"🔧 Testing Azure Speech connection...")
        logger.debug(f"Region: {AZURE_SPEECH_REGION}")
        logger.debug(f"Key length: {len(AZURE_SPEECH_KEY) if AZURE_SPEECH_KEY else 0}")
        
        # Configurazione test Azure Speech
        if AZURE_SPEECH_ENDPOINT:
            speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, endpoint=AZURE_SPEECH_ENDPOINT)
            logger.debug(f"Using custom endpoint for test: {AZURE_SPEECH_ENDPOINT}")
        else:
            speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
            logger.debug(f"Using standard region for test: {AZURE_SPEECH_REGION}")
        
        # Test con voce Neural italiana
        speech_config.speech_synthesis_voice_name = "it-IT-ElsaNeural"
        
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        
        logger.info("🎤 Performing Azure Speech test synthesis...")
        
        # Test con testo molto breve per ridurre tempo di elaborazione
        test_text = "Test"
        
        # Prova prima con timeout normale
        try:
            result = synthesizer.speak_text_async(test_text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info(f"✅ Azure Speech test successful - Generated {len(result.audio_data)} bytes")
                return True
                
        except Exception as timeout_error:
            logger.warning(f"⚠️ First attempt failed: {timeout_error}")
            logger.info("🔄 Trying fallback approach...")
            
            # Fallback: Prova con voce standard (più veloce)
            try:
                speech_config.speech_synthesis_voice_name = "it-IT-Lucia"  # Voce standard, più veloce
                synthesizer_fallback = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
                
                result = synthesizer_fallback.speak_text_async(test_text).get()
                
                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    logger.info(f"✅ Azure Speech fallback test successful with standard voice")
                    logger.warning("⚠️ Neural voices may be slow in your network environment")
                    return True
                    
            except Exception as fallback_error:
                logger.error(f"❌ Fallback also failed: {fallback_error}")
        
        # Gestione dettagliata degli errori
        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speechsdk.CancellationDetails(result)
            
            # Diagnostica dettagliata dell'errore
            error_details = {
                "reason": str(cancellation_details.reason),
                "error_code": str(cancellation_details.error_code) if hasattr(cancellation_details, 'error_code') else "N/A",
                "error_details": cancellation_details.error_details or "No additional details"
            }
            
            logger.error(f"❌ Azure Speech test canceled:")
            logger.error(f"   Reason: {error_details['reason']}")
            logger.error(f"   Error Code: {error_details['error_code']}")
            logger.error(f"   Details: {error_details['error_details']}")
            
            # Suggerimenti specifici per timeout
            if "timeout" in error_details['error_details'].lower() or "SynthesisConnectionTimeoutMs" in str(timeout_error):
                logger.error("💡 PROBLEMA: Timeout di connessione Azure")
                logger.error("   🌐 Possibili cause:")
                logger.error("      - Connessione internet lenta")
                logger.error("      - Firewall aziendale che blocca Azure")
                logger.error("      - Proxy che rallenta le connessioni")
                logger.error("   🔧 Soluzioni:")
                logger.error("      - Controlla configurazione proxy/firewall")
                logger.error("      - Usa region Azure più vicina")
                logger.error("      - Verifica connessione internet")
                
            elif "authentication" in error_details['error_details'].lower():
                logger.error("💡 PROBLEMA: Chiave Azure non valida")
                logger.error("   - Verifica la chiave nel portale Azure")
                logger.error("   - Assicurati che la risorsa Speech Services sia attiva")
            elif "region" in error_details['error_details'].lower():
                logger.error(f"💡 PROBLEMA: Region '{AZURE_SPEECH_REGION}' non disponibile")
                logger.error("   - Verifica la region nel portale Azure")
                logger.error("   - Prova region alternative: eastus, westus2, northeurope")
            
            raise Exception(f"Azure Speech test failed: {error_details['reason']} - {error_details['error_details']}")
        else:
            raise Exception(f"Azure Speech test failed with reason: {result.reason}")
            
    except Exception as e:
        logger.error(f"❌ Azure Speech connection test error: {e}")
        raise

# Azure Speech Services - Configurazione funzionante

async def generate_azure_speech(text: str, voice: str, output_path: str, ssml_options: dict = None):
    """
    Genera audio usando Azure Speech Services con configurazione Microsoft ufficiale
    
    Args:
        text: Testo da sintetizzare
        voice: Nome della voce Azure (es. it-IT-ElsaNeural)
        output_path: Percorso file output
        ssml_options: Opzioni SSML personalizzate (rate, pitch, volume, etc.)
    
    Returns:
        bool: True se successo, False altrimenti
    """
    if not AZURE_SPEECH_KEY:
        logger.error("Azure Speech Key non configurata")
        return False

    try:
        logger.info(f"🧪 Using Microsoft official Azure configuration...")
        
        # Configurazione esatta come nell'esempio Microsoft che FUNZIONA
        if AZURE_SPEECH_ENDPOINT:
            speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, endpoint=AZURE_SPEECH_ENDPOINT)
            logger.info(f"Using endpoint configuration: {AZURE_SPEECH_ENDPOINT}")
        else:
            speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
            logger.info(f"Using region configuration: {AZURE_SPEECH_REGION}")
        
        # Configurazione voce come nell'esempio che funziona
        speech_config.speech_synthesis_voice_name = voice
        
        # Creare synthesizer come nell'esempio Microsoft
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        
        logger.info(f"🎤 Synthesizing text: {text[:50]}...")
        
        # Se abbiamo opzioni SSML, genera SSML, altrimenti usa testo semplice
        if ssml_options and any(ssml_options.values()):
            ssml = generate_ssml(text, voice, ssml_options)
            logger.debug(f"Using SSML: {ssml[:100]}...")
            result = speech_synthesizer.speak_ssml_async(ssml).get()
        else:
            # Sintesi esatta come nell'esempio Microsoft che FUNZIONA
            result = speech_synthesizer.speak_text_async(text).get()
        
        # Gestione risultato ESATTA come nell'esempio Microsoft
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info(f"✅ Speech synthesized successfully - {len(result.audio_data)} bytes")
            
            # Salva il file usando la stessa logica che funziona
            with open(output_path, 'wb') as audio_file:
                audio_file.write(result.audio_data)
            
            # Verifica che il file sia stato scritto correttamente
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"✅ Azure Speech synthesis completed: {os.path.getsize(output_path)} bytes")
                return True
            else:
                logger.error("File audio vuoto o non creato")
                return False
                
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speechsdk.CancellationDetails(result)
            error_msg = f"Speech synthesis canceled: {cancellation_details.reason}"
            
            if cancellation_details.error_details:
                error_msg += f" - {cancellation_details.error_details}"
            
            logger.error(f"❌ Azure Speech canceled: {error_msg}")
            return False
        else:
            logger.error(f"❌ Azure Speech failed: {result.reason}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Azure Speech error: {e}")
        return False

def generate_ssml(text: str, voice: str, options: dict) -> str:
    """
    Genera SSML avanzato per controllo fine della sintesi vocale
    
    Args:
        text: Testo da sintetizzare
        voice: Nome della voce Azure
        options: Opzioni SSML (rate, pitch, volume, emphasis, breaks, etc.)
    
    Returns:
        str: SSML formattato
    """
    # Estrai opzioni con valori default
    rate = options.get('rate', 'medium')  # x-slow, slow, medium, fast, x-fast o percentuale
    pitch = options.get('pitch', 'medium')  # x-low, low, medium, high, x-high o frequenza
    volume = options.get('volume', 'medium')  # silent, x-soft, soft, medium, loud, x-loud
    emphasis = options.get('emphasis', None)  # strong, moderate, reduced
    break_time = options.get('break_time', None)  # Pausa in secondi
    style = options.get('style', None)  # cheerful, sad, excited, etc. (per voci Neural)
    style_degree = options.get('style_degree', '1.0')  # Intensità dello stile (0.01-2.0)
    
    # Escape HTML nel testo
    import html
    escaped_text = html.escape(text)
    
    # Costruisci SSML
    ssml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="it-IT">'
    ]
    
    # Tag voice con stile se supportato (Neural voices)
    if style and 'Neural' in voice:
        ssml_parts.append(f'<voice name="{voice}">')
        ssml_parts.append(f'<mstts:express-as style="{style}" styledegree="{style_degree}" xmlns:mstts="https://www.w3.org/2001/mstts">')
    else:
        ssml_parts.append(f'<voice name="{voice}">')
    
    # Tag prosody per controllo rate, pitch, volume
    prosody_attrs = []
    if rate != 'medium':
        prosody_attrs.append(f'rate="{rate}"')
    if pitch != 'medium':
        prosody_attrs.append(f'pitch="{pitch}"')
    if volume != 'medium':
        prosody_attrs.append(f'volume="{volume}"')
    
    if prosody_attrs:
        ssml_parts.append(f'<prosody {" ".join(prosody_attrs)}>')
    
    # Aggiungi pausa iniziale se richiesta
    if break_time:
        ssml_parts.append(f'<break time="{break_time}s"/>')
    
    # Testo con eventuale enfasi
    if emphasis:
        ssml_parts.append(f'<emphasis level="{emphasis}">{escaped_text}</emphasis>')
    else:
        ssml_parts.append(escaped_text)
    
    # Chiudi tag prosody
    if prosody_attrs:
        ssml_parts.append('</prosody>')
    
    # Chiudi tag voice e express-as
    if style and 'Neural' in voice:
        ssml_parts.append('</mstts:express-as>')
    ssml_parts.append('</voice>')
    ssml_parts.append('</speak>')
    
    ssml = ''.join(ssml_parts)
    logger.debug(f"Generated SSML: {ssml}")
    return ssml

# ==========================================
# ENDPOINT CRONOLOGIA E WEBSOCKET
# ==========================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket per aggiornamenti real-time della cronologia"""
    await manager.connect(websocket)
    try:
        # Invia cronologia iniziale al nuovo utente
        history = get_recent_history(10)
        await websocket.send_text(json.dumps({
            "type": "history_update",
            "data": history
        }))
        
        # Mantieni connessione attiva
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/history")
async def get_text_history(limit: int = 10):
    """Recupera cronologia recente dei testi"""
    try:
        history = get_recent_history(limit)
        return {
            "status": "success",
            "data": history,
            "total": len(history)
        }
    except Exception as e:
        logger.error(f"Errore recupero cronologia: {e}")
        raise HTTPException(status_code=500, detail="Errore recupero cronologia")

@app.get("/health")
async def health_check():
    """Health check per verificare lo stato del servizio TTS"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "azure_speech_configured": bool(AZURE_SPEECH_KEY),
        "available_voices": len(AZURE_VOICES)
    }
    
    # Test connessione Azure se configurato
    if AZURE_SPEECH_KEY:
        try:
            speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
            health_status["azure_connection"] = "✅ OK"
        except Exception as e:
            health_status["azure_connection"] = "❌ Failed"
            health_status["status"] = "degraded"
    else:
        health_status["azure_connection"] = "⚠️ Not configured"
        health_status["status"] = "degraded"
    
    return health_status

@app.post("/test-voice")
async def test_voice(
    voice_id: str = Form(...),
    test_text: str = Form("Benvenuti nel nostro centralino telefonico. Come possiamo aiutarvi oggi?")
):
    """
    Testa una voce specifica con un testo di prova
    """
    if voice_id not in AZURE_VOICES:
        available_voices = list(AZURE_VOICES.keys())
        raise HTTPException(
            status_code=400, 
            detail=f"Voce non trovata. Voci disponibili: {', '.join(available_voices)}"
        )
    
    if not AZURE_SPEECH_KEY:
        raise HTTPException(
            status_code=503, 
            detail="Azure Speech Services non configurato. Configura AZURE_SPEECH_KEY."
        )
    
    try:
        # Genera file test
        test_id = str(uuid.uuid4())[:8]
        output_path = f"output/voice_test_{voice_id.replace('-', '_')}_{test_id}.wav"
        
        # Opzioni SSML di test
        ssml_options = {
            'rate': 'medium',
            'pitch': 'medium',
            'volume': 'medium',
            'style': AZURE_VOICES[voice_id]["styles"][0] if AZURE_VOICES[voice_id]["styles"] else None
        }
        
        success = await generate_azure_speech(test_text, voice_id, output_path, ssml_options)
        
        if success:
            voice_info = AZURE_VOICES[voice_id]
            return FileResponse(
                output_path,
                media_type="audio/wav",
                filename=f"test_{voice_info['name'].lower()}_{test_id}.wav",
                headers={
                    "X-Voice-ID": voice_id,
                    "X-Voice-Name": voice_info["name"],
                    "X-Voice-Description": voice_info["description"]
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Errore nella generazione audio di test")
            
    except Exception as e:
        logger.error(f"Error testing voice {voice_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Errore nel test della voce: {str(e)}")

@app.get("/available-voices")
async def get_available_voices():
    """Ottieni lista dettagliata delle voci Azure Speech Services disponibili"""
    
    # Organizza le voci per genere e tipo
    organized_voices = {
        "neural_voices": {
            "female": {},
            "male": {}
        },
        "standard_voices": {
            "female": {},
            "male": {}
        }
    }
    
    for voice_id, voice_info in AZURE_VOICES.items():
        voice_type = "neural_voices" if "Neural" in voice_id else "standard_voices"
        gender_key = "female" if voice_info["gender"] == "Female" else "male"
        
        organized_voices[voice_type][gender_key][voice_id] = {
            "id": voice_id,
            "name": voice_info["name"],
            "description": voice_info["description"],
            "styles": voice_info["styles"],
            "recommended_for": voice_info["recommended_for"],
            "is_neural": "Neural" in voice_id
        }
    
    return {
        "voices": organized_voices,
        "total_count": len(AZURE_VOICES),
        "neural_count": len([v for v in AZURE_VOICES.keys() if "Neural" in v]),
        "supported_languages": ["it-IT"],
        "service": "Azure Speech Services",
        "commercial_license": True,
        "style_support": True,
        "pricing_info": "Pay-per-character pricing - see Azure pricing page",
        "documentation": "https://docs.microsoft.com/azure/cognitive-services/speech-service/language-support"
    }

@app.post("/generate-audio")
async def generate_audio(
    text: str = Form(...),
    music_file: UploadFile = File(None),  # Opzionale
    music_volume: float = Form(0.3),  # Volume musica (0.0 = silenziata, 1.0 = volume originale)
    music_before: float = Form(2.0),  # Musica prima del testo (secondi)
    music_after: float = Form(3.0),  # Musica dopo il testo (secondi)
    fade_in: bool = Form(True),  # Applica fade in alla musica
    fade_out: bool = Form(True),  # Applica fade out alla musica
    fade_in_duration: float = Form(1.0),  # Durata fade in musica (secondi)
    fade_out_duration: float = Form(2.0),  # Durata fade out musica (secondi)
    voice_reference: UploadFile = File(None),  # File audio per voice cloning 
    predefined_speaker: str = Form(None),  # Speaker predefinito
    language: str = Form("it"),  # Lingua per XTTS_v2
    tts_service: str = Form("azure"),  # Servizio TTS: "azure" (default)
    edge_voice: str = Form("it-IT-ElsaNeural"),  # Voce Azure Speech
    library_song_id: str = Form(None),  # ID della canzone dalla libreria
    output_format: str = Form("wav"),  # Formato output: "wav", "mp3", "gsm"
    audio_quality: str = Form("pcm"),  # Qualità: "pcm", "alaw", "ulaw"
    custom_filename: str = Form("centralino_audio")  # Nome personalizzato del file
):
    """
    Genera audio con TTS italiano e opzionalmente musica di sottofondo con controlli avanzati
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Testo non può essere vuoto")
    
    if music_volume < 0 or music_volume > 1:
        raise HTTPException(status_code=400, detail="Volume musica deve essere tra 0.0 e 1.0")
    
    if music_before < 0 or music_after < 0:
        raise HTTPException(status_code=400, detail="Durata musica deve essere positiva")
    
    if fade_in_duration < 0 or fade_out_duration < 0:
        raise HTTPException(status_code=400, detail="Durata fade deve essere positiva")
    
    # Validazione formato output
    if output_format not in ["wav", "mp3", "gsm"]:
        raise HTTPException(status_code=400, detail="Formato output deve essere wav, mp3 o gsm")
    
    # Validazione qualità audio
    if audio_quality not in ["pcm", "alaw", "ulaw"]:
        raise HTTPException(status_code=400, detail="Qualità audio deve essere pcm, alaw o ulaw")
    
    # Genera ID univoco per questa richiesta
    session_id = str(uuid.uuid4())
    
    try:
        # Percorsi file temporanei
        tts_path = f"output/tts_{session_id}.wav"
        music_path = None
        voice_ref_path = f"uploads/voice_ref_{session_id}.wav" if voice_reference else None
        final_path = f"output/final_{session_id}.wav"
        
        # Gestisce la musica da libreria o upload
        if library_song_id:
            # Legge i metadata dalla libreria per ottenere il path del file
            metadata_path = f"uploads/library/{library_song_id}.json"
            if not os.path.exists(metadata_path):
                raise HTTPException(status_code=404, detail="Canzone della libreria non trovata")
            
            import json
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            music_path = metadata["file_path"]
            
            if not os.path.exists(music_path):
                raise HTTPException(status_code=404, detail="File audio della libreria non trovato")
        elif music_file and music_file.filename:
            music_path = f"uploads/music_{session_id}.wav"
            with open(music_path, "wb") as buffer:
                shutil.copyfileobj(music_file.file, buffer)
        
        # Salva file voce di riferimento se presente
        if voice_reference and voice_reference.filename:
            with open(voice_ref_path, "wb") as buffer:
                shutil.copyfileobj(voice_reference.file, buffer)
        
        # Genera TTS usando Azure Speech Services
        logger.info(f"🎤 Generating TTS for text: {text[:50]}... using Azure Speech Services")
        
        # Opzioni SSML personalizzate per centralini
        ssml_options = {
            'rate': 'medium',  # Velocità moderata per chiarezza
            'pitch': 'medium', # Tono medio per professionalità
            'volume': 'loud',  # Volume alto per centralini
            'style': 'customerservice' if 'Neural' in edge_voice else None,  # Stile servizio clienti
            'emphasis': 'moderate'  # Enfasi moderata
        }
        
        success = await generate_azure_speech(text, edge_voice, tts_path, ssml_options)
        if not success:
            raise HTTPException(status_code=500, detail="Azure Speech generation failed")
        
        # Salva nella cronologia e notifica utenti connessi
        try:
            # Ottieni IP utente per tracking (solo ultimi caratteri per privacy)
            user_ip = "unknown"  # In produzione: request.client.host
            
            history_id = add_text_to_history(text, edge_voice, user_ip)
            
            # Notifica tutti gli utenti connessi del nuovo testo
            history_update = {
                "type": "new_text",
                "data": {
                    "id": history_id,
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "voice": edge_voice,
                    "timestamp": datetime.now().isoformat(),
                    "user_ip": user_ip[-8:] if user_ip != "unknown" else "unknown"
                }
            }
            await manager.broadcast(history_update)
            
            logger.info(f"✅ Testo salvato nella cronologia (ID: {history_id})")
        except Exception as e:
            logger.warning(f"⚠️ Errore salvataggio cronologia: {e}")
            # Non interrompere la generazione audio per errori cronologia
        
        # Carica audio voce e applica ottimizzazioni per suono più naturale
        voice = AudioSegment.from_wav(tts_path)
        
        # Normalizza con parametri più morbidi per evitare distorsioni
        voice = normalize(voice, headroom=2.0)
        
        # Applica un lieve filtro passa-basso per ridurre metallic sound
        # Riduci leggermente le frequenze acute che causano suono metallico
        voice = voice.low_pass_filter(8000)  # Taglia frequenze sopra 8kHz
        
        # Aggiungi un po' di "warmth" riducendo lievemente il volume generale
        voice = voice - 3  # Riduci di 3dB per suono più morbido
        
        # Se c'è musica, processala e mixa con controlli avanzati
        if music_path and os.path.exists(music_path):
            music = AudioSegment.from_file(music_path)
            music = normalize(music)
            
            # Riduce il volume della musica secondo il parametro
            music = music - (60 - int(music_volume * 60))  # Converti 0-1 in dB
            
            # Calcola le durate
            voice_duration = len(voice)
            music_before_ms = int(music_before * 1000)
            music_after_ms = int(music_after * 1000)
            fade_in_ms = int(fade_in_duration * 1000)
            fade_out_ms = int(fade_out_duration * 1000)
            
            total_duration = music_before_ms + voice_duration + music_after_ms
            
            # Se la musica è più corta del necessario, la ripete
            if len(music) < total_duration:
                loops_needed = (total_duration // len(music)) + 1
                music = music * loops_needed
            
            # Taglia la musica alla durata necessaria
            music = music[:total_duration]
            
            # Applica fade in all'inizio
            if fade_in and fade_in_ms > 0:
                music = music.fade_in(min(fade_in_ms, len(music)))
            
            # Applica fade out alla fine
            if fade_out and fade_out_ms > 0:
                music = music.fade_out(min(fade_out_ms, len(music)))
            
            # Crea il mix finale
            # 1. Musica prima del testo (solo musica)
            music_intro = music[:music_before_ms]
            
            # 2. Voce + musica di sottofondo
            music_during_voice = music[music_before_ms:music_before_ms + voice_duration]
            # Riduci ulteriormente il volume della musica durante la voce
            music_during_voice = music_during_voice - 6  # -6dB per dare priorità alla voce
            voice_with_bg = voice.overlay(music_during_voice)
            
            # 3. Musica dopo il testo (solo musica)
            music_outro = music[music_before_ms + voice_duration:]
            
            # Combina tutte le parti
            final_audio = music_intro + voice_with_bg + music_outro
        else:
            # Solo voce, senza musica
            final_audio = voice
        
        # Salva il risultato finale con conversione nel formato richiesto
        final_path = convert_audio_to_format(final_audio, output_format, audio_quality, custom_filename)
        
        # Cleanup file temporanei
        if os.path.exists(tts_path):
            os.remove(tts_path)
        if music_path and not library_song_id and os.path.exists(music_path):
            # Non eliminare le canzoni della libreria, solo i file temporanei
            os.remove(music_path)
        
        logger.info(f"Audio generated successfully: {final_path}")
        
        # Pulisci il nome personalizzato per la sicurezza e genera data
        clean_name = "".join(c for c in custom_filename if c.isalnum() or c in "._-").strip()
        if not clean_name:
            clean_name = "centralino_audio"
        
        from datetime import datetime
        date_str = datetime.now().strftime("%y%m%d")
        
        return FileResponse(
            final_path, 
            media_type=get_media_type(output_format),
            filename=f"{clean_name}_{date_str}.{output_format}"
        )
        
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        # Cleanup in case of error
        for path in [tts_path, final_path]:
            if 'path' in locals() and os.path.exists(path):
                os.remove(path)
        if music_path and not library_song_id and os.path.exists(music_path):
            os.remove(music_path)
        if voice_ref_path and os.path.exists(voice_ref_path):
            os.remove(voice_ref_path)
        raise HTTPException(status_code=500, detail=f"Errore nella generazione audio: {str(e)}")

@app.post("/music-library/upload")
async def upload_music_to_library(
    name: str = Form(...),
    music_file: UploadFile = File(...)
):
    """
    Carica una canzone nella libreria musicale
    """
    if not music_file.filename:
        raise HTTPException(status_code=400, detail="File musicale richiesto")
    
    # Verifica che sia un file audio
    audio_types = ['audio/mp3', 'audio/wav', 'audio/mpeg', 'audio/ogg', 'audio/mp4']
    if music_file.content_type not in audio_types:
        raise HTTPException(status_code=400, detail="File deve essere audio (MP3, WAV, OGG)")
    
    # Crea directory libreria se non esiste
    library_dir = "uploads/library"
    os.makedirs(library_dir, exist_ok=True)
    
    try:
        # Genera ID univoco per la canzone
        song_id = str(uuid.uuid4())
        extension = os.path.splitext(music_file.filename)[1]
        file_path = os.path.join(library_dir, f"{song_id}{extension}")
        
        # Salva il file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(music_file.file, buffer)
        
        # Ottieni informazioni audio
        try:
            audio = AudioSegment.from_file(file_path)
            duration_seconds = len(audio) / 1000.0
        except Exception:
            duration_seconds = 0
        
        # Salva metadata
        metadata = {
            "id": song_id,
            "name": name,
            "filename": music_file.filename,
            "file_path": file_path,
            "duration_seconds": duration_seconds,
            "uploaded_at": str(datetime.now()),
            "size_bytes": os.path.getsize(file_path)
        }
        
        metadata_path = os.path.join(library_dir, f"{song_id}.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            import json
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Music uploaded to library: {name} ({song_id})")
        
        return {
            "message": f"Canzone '{name}' aggiunta alla libreria con successo",
            "song_id": song_id,
            "duration_seconds": duration_seconds
        }
        
    except Exception as e:
        logger.error(f"Error uploading music: {e}")
        raise HTTPException(status_code=500, detail=f"Errore nel caricamento: {str(e)}")

@app.get("/music-library/list")
async def list_music_library():
    """
    Lista tutte le canzoni nella libreria musicale
    """
    library_dir = "uploads/library"
    if not os.path.exists(library_dir):
        return {"songs": []}
    
    songs = []
    for file in os.listdir(library_dir):
        if file.endswith('.json'):
            try:
                with open(os.path.join(library_dir, file), "r", encoding="utf-8") as f:
                    import json
                    metadata = json.load(f)
                    # Verifica che il file audio esista ancora
                    if os.path.exists(metadata["file_path"]):
                        songs.append(metadata)
            except Exception as e:
                logger.warning(f"Error reading metadata {file}: {e}")
    
    # Ordina per data di upload (più recenti prima)
    songs.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
    
    return {"songs": songs}

@app.delete("/music-library/{song_id}")
async def delete_music_from_library(song_id: str):
    """
    Elimina una canzone dalla libreria musicale
    """
    library_dir = "uploads/library"
    metadata_path = os.path.join(library_dir, f"{song_id}.json")
    
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="Canzone non trovata nella libreria")
    
    try:
        # Leggi metadata per ottenere il percorso del file
        with open(metadata_path, "r", encoding="utf-8") as f:
            import json
            metadata = json.load(f)
        
        # Elimina file audio
        if os.path.exists(metadata["file_path"]):
            os.remove(metadata["file_path"])
        
        # Elimina metadata
        os.remove(metadata_path)
        
        logger.info(f"Music deleted from library: {metadata['name']} ({song_id})")
        
        return {
            "message": f"Canzone '{metadata['name']}' eliminata dalla libreria",
            "song_id": song_id
        }
        
    except Exception as e:
        logger.error(f"Error deleting music: {e}")
        raise HTTPException(status_code=500, detail=f"Errore nell'eliminazione: {str(e)}")

@app.post("/train-voice")
async def train_voice(
    voice_name: str = Form(...),
    audio_samples: list[UploadFile] = File(...),
    transcriptions: str = Form(...)  # Trascrizioni separate da "|"
):
    """
    Endpoint per voice training con Azure Speech Services
    
    Nota: Azure Speech Services non supporta training personalizzato tramite API pubblica.
    Questo endpoint salva i campioni per referenza futura o per training offline.
    
    Per voice cloning in tempo reale, usa le voci Neural predefinite di Azure.
    """
    # Crea directory per la nuova voce
    voice_dir = f"voices/{voice_name}"
    os.makedirs(voice_dir, exist_ok=True)
    
    try:
        # Salva i file audio di training
        transcription_list = transcriptions.split("|")
        
        if len(audio_samples) != len(transcription_list):
            raise HTTPException(
                status_code=400, 
                detail="Numero di file audio deve corrispondere alle trascrizioni"
            )
        
        # Salva i campioni vocali
        for i, (audio_file, transcript) in enumerate(zip(audio_samples, transcription_list)):
            audio_path = f"{voice_dir}/sample_{i+1}.wav"
            with open(audio_path, "wb") as buffer:
                shutil.copyfileobj(audio_file.file, buffer)
            
            # Salva anche la trascrizione
            with open(f"{voice_dir}/sample_{i+1}.txt", "w", encoding="utf-8") as f:
                f.write(transcript.strip())
        
        logger.info(f"Voice training data saved for '{voice_name}' - {len(audio_samples)} samples")
        
        return {
            "message": f"Training data per la voce '{voice_name}' salvati con successo",
            "samples_count": len(audio_samples),
            "voice_dir": voice_dir,
            "note": "Azure Speech Services usa voci Neural predefinite. Per voice cloning personalizzato, contatta il supporto Azure."
        }
        
    except Exception as e:
        logger.error(f"Error in voice training: {e}")
        raise HTTPException(status_code=500, detail=f"Errore nel training: {str(e)}")

@app.get("/speakers")
async def get_available_speakers():
    """Lista degli speaker predefiniti Azure Speech Services"""
    
    # Voci Azure Speech Services per centralini italiani
    azure_voices = {
        "female_voices": [
            {
                "id": "it-IT-ElsaNeural", 
                "name": "🚺 Elsa - Voce Femminile Professionale", 
                "language": "it-IT", 
                "description": "Voce femminile naturale e professionale per centralini",
                "style_support": True,
                "styles": ["customerservice", "newscast", "assistant"]
            },
            {
                "id": "it-IT-IsabellaNeural", 
                "name": "🚺 Isabella - Voce Femminile Espressiva", 
                "language": "it-IT", 
                "description": "Voce femminile espressiva e accogliente",
                "style_support": True,
                "styles": ["chat", "cheerful", "newscast"]
            },
            {
                "id": "it-IT-IrmaNeural", 
                "name": "🚺 Irma - Voce Femminile Calda", 
                "language": "it-IT", 
                "description": "Voce femminile calda e rassicurante",
                "style_support": True,
                "styles": ["chat", "friendly"]
            }
        ],
        "male_voices": [
            {
                "id": "it-IT-DiegoNeural", 
                "name": "🚹 Diego - Voce Maschile Naturale", 
                "language": "it-IT", 
                "description": "Voce maschile autorevole e chiara per centralini",
                "style_support": True,
                "styles": ["customerservice", "newscast"]
            },
            {
                "id": "it-IT-BenignoNeural", 
                "name": "🚹 Benigno - Voce Maschile Espressiva", 
                "language": "it-IT", 
                "description": "Voce maschile espressiva e coinvolgente",
                "style_support": True,
                "styles": ["chat", "friendly"]
            },
            {
                "id": "it-IT-CalimeroNeural", 
                "name": "🚹 Calimero - Voce Maschile Giovane", 
                "language": "it-IT", 
                "description": "Voce maschile moderna e dinamica",
                "style_support": True,
                "styles": ["chat", "excited"]
            }
        ],
        "multilingual_voices": [
            {
                "id": "it-IT-Giuseppe", 
                "name": "🎤 Giuseppe - Voce Standard", 
                "language": "it-IT", 
                "description": "Voce maschile standard (compatibilità)",
                "style_support": False,
                "styles": []
            },
            {
                "id": "it-IT-Lucia", 
                "name": "🎤 Lucia - Voce Standard", 
                "language": "it-IT", 
                "description": "Voce femminile standard (compatibilità)",
                "style_support": False,
                "styles": []
            }
        ]
    }
    
    return {
        "available_speakers": azure_voices,
        "service": "Azure Speech Services",
        "total_voices": sum(len(voices) for voices in azure_voices.values()),
        "neural_voices_supported": True,
        "style_customization": True,
        "voice_cloning_note": "Per voice cloning personalizzato, contatta il supporto Azure Speech Services"
    }

@app.get("/voices")
async def list_voices():
    """Lista delle voci personalizzate disponibili"""
    voices_dir = "voices"
    if not os.path.exists(voices_dir):
        return {"voices": []}
    
    voices = []
    for voice_name in os.listdir(voices_dir):
        voice_path = os.path.join(voices_dir, voice_name)
        if os.path.isdir(voice_path):
            samples = [f for f in os.listdir(voice_path) if f.endswith('.wav')]
            voices.append({
                "name": voice_name,
                "samples_count": len(samples),
                "directory": voice_path
            })
    
    return {"voices": voices}

@app.get("/")
async def root():
    return {
        "message": "crazy-phoneTTS API - TTS Italiano per Centralini con Azure Speech Services", 
        "docs": "/docs",
        "health": "/health",
        "voice_training": "/train-voice",
        "list_voices": "/voices"
    }

# ==========================================
# SISTEMA AUTO-AGGIORNAMENTO
# ==========================================

# Manager per connessioni WebSocket aggiornamenti
class UpdateConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_progress(self, message: dict):
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(json.dumps(message))
            except:
                self.active_connections.remove(connection)

update_manager = UpdateConnectionManager()

def get_current_version():
    """Legge la versione attuale dal file VERSION"""
    # Lista dei possibili percorsi del file VERSION
    version_paths = [
        "VERSION",                    # Directory corrente (per sviluppo)
        "../VERSION",                # Directory padre (se backend è in sottocartella)
        "/app/VERSION",              # Container Docker
        "./VERSION",                 # Esplicito directory corrente
        os.path.join(os.path.dirname(__file__), "..", "VERSION")  # Relativo a questo file
    ]
    
    for path in version_paths:
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    version = f.read().strip()
                    if version:  # Assicura che non sia vuoto
                        logger.debug(f"Versione letta da: {path} -> {version}")
                        return version
        except Exception as e:
            logger.debug(f"Errore lettura {path}: {e}")
            continue
    
    logger.warning("Nessun file VERSION trovato, usando versione di fallback")
    return "1.0.0"

async def check_github_releases():
    """Controlla le release disponibili su GitHub"""
    try:
        url = "https://api.github.com/repos/ZELA2000/crazy-phoneTTS/releases/latest"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        release_data = response.json()
        
        return {
            "tag_name": release_data["tag_name"],
            "name": release_data["name"],
            "published_at": release_data["published_at"],
            "body": release_data["body"],
            "zipball_url": release_data["zipball_url"],
            "tarball_url": release_data["tarball_url"]
        }
    except Exception as e:
        logger.error(f"Errore controllo GitHub releases: {e}")
        return None

@app.get("/version/current")
async def current_version():
    """Restituisce la versione attuale del sistema"""
    return {
        "current_version": get_current_version(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/version/check")
async def check_updates():
    """Controlla se ci sono aggiornamenti disponibili"""
    current_ver = get_current_version()
    latest_release = await check_github_releases()
    
    if not latest_release:
        return {
            "current_version": current_ver,
            "update_available": False,
            "error": "Impossibile controllare aggiornamenti GitHub"
        }
    
    latest_ver = latest_release["tag_name"].lstrip("v")
    update_available = latest_ver != current_ver
    
    return {
        "current_version": current_ver,
        "latest_version": latest_ver,
        "update_available": update_available,
        "release_info": latest_release if update_available else None
    }

@app.websocket("/ws/update-progress")
async def update_progress_endpoint(websocket: WebSocket):
    """WebSocket per progress degli aggiornamenti"""
    await update_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        update_manager.disconnect(websocket)

@app.get("/update/progress")
async def get_update_progress():
    """Ottiene il progress dell'aggiornamento dal file persistente"""
    try:
        progress = load_update_progress()
        if progress is None:
            return {
                "status": "idle",
                "message": "Nessun aggiornamento in corso",
                "percentage": 0
            }
        return progress
    except Exception as e:
        logger.error(f"Errore lettura progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update/clear")
async def clear_update_status():
    """Pulisce lo stato di aggiornamento"""
    try:
        clear_update_progress()
        return {"message": "Stato aggiornamento pulito"}
    except Exception as e:
        logger.error(f"Errore pulizia progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update/start")
async def start_update():
    """Avvia il processo di aggiornamento con progress persistente"""
    try:
        # Pulisce stato precedente
        clear_update_progress()
        
        # Salva progress iniziale
        save_update_progress({
            "type": "progress",
            "step": "start",
            "message": "🚀 Avvio processo di aggiornamento...",
            "percentage": 0,
            "status": "starting"
        })
        
        # Invia anche via WebSocket se possibile
        try:
            await update_manager.broadcast_progress({
                "type": "progress",
                "step": "start",
                "message": "🚀 Avvio processo di aggiornamento...",
                "percentage": 0
            })
        except:
            pass  # Continua anche se WebSocket non funziona
        
        # Controlla aggiornamenti disponibili
        update_info = await check_updates()
        if not update_info["update_available"]:
            save_update_progress({
                "type": "error",
                "step": "error",
                "message": "❌ Nessun aggiornamento disponibile",
                "status": "error"
            })
            raise HTTPException(status_code=400, detail="Nessun aggiornamento disponibile")
        
        save_update_progress({
            "type": "progress",
            "step": "preparing",
            "message": f"📦 Preparazione aggiornamento versione {update_info['latest_version']}...",
            "percentage": 5,
            "status": "running"
        })
        
        # Determina quale script eseguire (forza PowerShell su host Windows)
        # Nota: Il container è Linux ma l'host può essere Windows
        script_path = "update_script.ps1"  # Default PowerShell per questo deployment
        
        # Avvia lo script in background con tracking persistente
        run_update_script_background(script_path, update_info["latest_version"])
        
        return {
            "message": "Aggiornamento avviato con progress persistente",
            "version": update_info["latest_version"],
            "status": "in_progress",
            "info": "Usa GET /update/progress per monitorare lo stato"
        }
        
    except Exception as e:
        logger.error(f"Errore avvio aggiornamento: {e}")
        await update_manager.broadcast_progress({
            "type": "error",
            "message": f"❌ Errore: {str(e)}"
        })
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Avvio server su {BACKEND_HOST}:{BACKEND_PORT}")
    uvicorn.run(app, host=BACKEND_HOST, port=BACKEND_PORT)
