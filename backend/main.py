"""
crazy-phoneTTS - Sistema Text-to-Speech Professionale per Centralini

Questo modulo fornisce un'API REST completa per la generazione di audio TTS
utilizzando Azure Speech Services, con supporto per mixaggio musicale,
cronologia real-time e sistema di aggiornamento automatico.

Caratteristiche principali:
- Voci neurali italiane di alta qualità
- Mixaggio audio con musica di sottofondo personalizzabile
- Libreria musicale persistente
- Cronologia testi con aggiornamenti WebSocket real-time
- Sistema di aggiornamento automatico con backup
- Supporto formati telefonici (PCM, A-law, u-law)
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil
import sqlite3
import json
from typing import List, Dict, Any, Optional
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

# Import moduli refactorizzati organizzati per cartella
from core.config import ApplicationConfiguration
from models.history import TextHistoryDatabase
from models.voice_catalog import VoiceCatalog
from services.azure_speech import AzureSpeechService, SSMLParameters, VoiceStyle
from services.edge_tts_service import EdgeTTSService
from services.google_tts_service import GoogleTTSService
from managers.websocket_manager import HistoryUpdateManager, UpdateProgressManager as WebSocketUpdateProgressManager
from managers.update_manager import UpdateNotificationManager
from managers.audio_processor import AudioConverter, AudioQualitySpec
from managers.music_library import MusicLibrary
from managers.version_manager import VersionManager

# Configurazione logging con formato dettagliato
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==========================================
# INIZIALIZZAZIONE CONFIGURAZIONE
# ==========================================

# Inizializza configurazione centralizzata
app_config = ApplicationConfiguration()
app_config.initialize()

# Variabili per compatibilità con codice esistente
AZURE_SPEECH_KEY = app_config.azure.speech_key
AZURE_SPEECH_REGION = app_config.azure.speech_region
AZURE_SPEECH_ENDPOINT = app_config.azure.speech_endpoint
BACKEND_HOST = app_config.network.host
BACKEND_PORT = app_config.network.port
UPDATE_PROGRESS_FILE = app_config.paths.UPDATE_PROGRESS_FILE

# Verifica configurazione
IS_CONFIGURATION_VALID = app_config.is_ready()

# ==========================================
# INIZIALIZZAZIONE SERVIZI APPLICAZIONE
# ==========================================

# Servizio Azure Speech per sintesi vocale
azure_speech_service = AzureSpeechService(
    speech_key=AZURE_SPEECH_KEY,
    speech_region=AZURE_SPEECH_REGION,
    speech_endpoint=AZURE_SPEECH_ENDPOINT
) if AZURE_SPEECH_KEY else None

# Servizio Edge TTS (gratuito, sempre disponibile)
edge_tts_service = EdgeTTSService()

# Servizio Google TTS (opzionale, richiede credenziali)
google_tts_service = GoogleTTSService()

# Gestore per cronologia testi real-time
manager = HistoryUpdateManager()

# Gestore database per cronologia testi
history_db = TextHistoryDatabase()

# Gestore notifiche aggiornamenti
update_notification_manager = UpdateNotificationManager()

# Convertitore audio
audio_converter = AudioConverter(output_directory="output")

# Libreria musicale
music_library = MusicLibrary(library_directory="uploads/library")

# Gestore versioni
version_manager = VersionManager(
    version_file="VERSION",
    github_repo="ZELA2000/crazy-phoneTTS"
)

# Catalogo voci
voice_catalog = VoiceCatalog()

# Flag per tracciare disponibilità reale di Azure Speech
azure_speech_available = False


# Funzioni wrapper per compatibilità con codice esistente


def add_text_to_history(text: str, voice: str, user_ip: str = None) -> int:
    """Aggiunge testo alla cronologia usando il gestore database."""
    return history_db.add_text_entry(text, voice, user_ip)


def get_recent_history(limit: int = 10) -> List[Dict]:
    """Recupera cronologia recente usando il gestore database."""
    return history_db.get_recent_entries(limit)


def convert_audio_to_format(audio_segment, output_format, audio_quality, custom_filename):
    """
    Wrapper per compatibilità - usa il convertitore audio refactorizzato.
    """
    return audio_converter.convert(
        audio_segment,
        output_format,
        audio_quality,
        custom_filename
    )


def get_media_type(output_format):
    """Wrapper per compatibilità - usa il convertitore audio refactorizzato."""
    return AudioConverter.get_media_type(output_format)


app = FastAPI(title="crazy-phoneTTS API",
              description="TTS con mixaggio musicale per centralini")

# CORS middleware per il frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consenti tutte le origini
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Catalogo voci Azure - gestito dal modulo refactorizzato
# Mantieni variabile per compatibilità con codice esistente
AZURE_VOICES = {
    voice["short_name"]: {
        "name": voice["display_name"],
        "gender": voice["gender"],
        "description": voice["description"],
        "styles": voice["styles"]
    }
    for voice in voice_catalog.get_all_voices()
}


@app.on_event("startup")
async def startup_event():
    """Inizializzazione e validazione della configurazione Azure Speech Services"""
    global azure_speech_available

    logger.info("🚀 ===========================================")
    logger.info("🚀 crazy-phoneTTS Server - Avvio in corso...")
    logger.info("🚀 ===========================================")
    logger.info(f"📍 [Config] Azure Speech Region: {AZURE_SPEECH_REGION}")

    if AZURE_SPEECH_KEY:
        logger.info("🔑 [Azure] API Key configurata correttamente")

        # Test della connessione Azure Speech
        try:
            await test_azure_speech_connection()
            azure_speech_available = True
            logger.info("✅ [Azure] Connessione verificata con successo")
        except Exception as e:
            azure_speech_available = False
            logger.error(f"❌ [Azure] Connessione fallita: {e}")
            logger.warning(
                "⚠️ [Azure] Azure Speech non disponibile. Utilizzare Edge TTS (gratuito)")
    else:
        azure_speech_available = False
        logger.warning(
            "⚠️ [Azure] API Key non configurata. Utilizzare Edge TTS o Google TTS")

    logger.info("✅ ===========================================")
    logger.info("✅ TTS Server pronto per l'uso!")
    logger.info("✅ ===========================================")


async def test_azure_speech_connection():
    """
    Testa la connessione ad Azure Speech Services usando il servizio refactorizzato.

    Raises:
        ValueError: Se la chiave Azure non è configurata
        Exception: Se il test di connessione fallisce
    """
    if not azure_speech_service:
        raise ValueError("Azure Speech Service non configurato")

    logger.info("🔍 [Azure] Verifica connessione in corso...")

    success = await azure_speech_service.test_connection()
    if not success:
        raise Exception("Test connessione Azure Speech fallito")


async def generate_azure_speech(text: str, voice: str, output_path: str, ssml_options: dict = None):
    """
    Wrapper per compatibilità che usa il servizio Azure Speech refactorizzato.

    Args:
        text: Testo da sintetizzare
        voice: Nome della voce Azure (es. it-IT-ElsaNeural)
        output_path: Percorso file output
        ssml_options: Opzioni SSML personalizzate (rate, pitch, volume, etc.)

    Returns:
        bool: True se successo, False altrimenti
    """
    if not azure_speech_service:
        logger.error("❌ [Azure] Servizio non configurato correttamente")
        return False

    # Converti dict opzioni in SSMLParameters se fornite
    ssml_params = None
    if ssml_options:
        ssml_params = SSMLParameters(
            rate=ssml_options.get('rate', 'medium'),
            pitch=ssml_options.get('pitch', 'medium'),
            volume=ssml_options.get('volume', 'medium'),
            emphasis=ssml_options.get('emphasis'),
            break_time=ssml_options.get('break_time'),
            style=ssml_options.get('style'),
            style_degree=ssml_options.get('style_degree', '1.0')
        )

    return await azure_speech_service.synthesize_to_file(
        text=text,
        voice=voice,
        output_path=output_path,
        ssml_parameters=ssml_params
    )


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
        logger.error(f"❌ [History] Errore recupero cronologia: {e}")
        raise HTTPException(
            status_code=500, detail="Errore recupero cronologia")


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
            speech_config = speechsdk.SpeechConfig(
                subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
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
    test_text: str = Form(
        "Benvenuti nel nostro centralino telefonico. Come possiamo aiutarvi oggi?")
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
            raise HTTPException(
                status_code=500, detail="Errore nella generazione audio di test")

    except Exception as e:
        logger.error(f"❌ [Voice Test] Errore test voce {voice_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Errore nel test della voce: {str(e)}")


@app.get("/available-voices")
async def get_available_voices():
    """Ottieni lista dettagliata delle voci Azure usando il catalogo refactorizzato."""

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

    # Usa il catalogo refactorizzato
    all_voices = voice_catalog.get_all_voices()

    for voice in all_voices:
        voice_id = voice["short_name"]
        voice_type = "neural_voices" if "Neural" in voice_id else "standard_voices"
        gender_key = "female" if voice["gender"] == "Female" else "male"

        organized_voices[voice_type][gender_key][voice_id] = {
            "id": voice_id,
            "name": voice["display_name"],
            "description": voice["description"],
            "styles": voice["styles"],
            "is_neural": "Neural" in voice_id
        }

    return {
        "voices": organized_voices,
        "total_count": len(all_voices),
        "neural_count": len([v for v in all_voices if "Neural" in v["short_name"]]),
        "supported_languages": ["it-IT"],
        "service": "Azure Speech Services",
        "commercial_license": True,
        "style_support": True,
        "available_styles": voice_catalog.get_available_styles(),
        "pricing_info": "Pay-per-character pricing - see Azure pricing page",
        "documentation": "https://docs.microsoft.com/azure/cognitive-services/speech-service/language-support"
    }


@app.post("/generate-audio")
async def generate_audio(
    text: str = Form(...),
    music_file: UploadFile = File(None),  # Opzionale
    # Volume musica (0.0 = silenziata, 1.0 = volume originale)
    music_volume: float = Form(0.3),
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
    voice_name: str = Form("it-IT-ElsaNeural"),  # Voce TTS (per tutti i servizi)
    library_song_id: str = Form(None),  # ID della canzone dalla libreria
    output_format: str = Form("wav"),  # Formato output: "wav", "mp3", "gsm"
    audio_quality: str = Form("pcm"),  # Qualità: "pcm", "alaw", "ulaw"
    # Nome personalizzato del file
    custom_filename: str = Form("centralino_audio")
):
    """
    Genera audio con TTS italiano e opzionalmente musica di sottofondo con controlli avanzati
    """
    if not text.strip():
        raise HTTPException(
            status_code=400, detail="Testo non può essere vuoto")

    if music_volume < 0 or music_volume > 1:
        raise HTTPException(
            status_code=400, detail="Volume musica deve essere tra 0.0 e 1.0")

    if music_before < 0 or music_after < 0:
        raise HTTPException(
            status_code=400, detail="Durata musica deve essere positiva")

    if fade_in_duration < 0 or fade_out_duration < 0:
        raise HTTPException(
            status_code=400, detail="Durata fade deve essere positiva")

    # Validazione formato output
    if output_format not in ["wav", "mp3", "gsm"]:
        raise HTTPException(
            status_code=400, detail="Formato output deve essere wav, mp3 o gsm")

    # Validazione qualità audio
    if audio_quality not in ["pcm", "alaw", "ulaw"]:
        raise HTTPException(
            status_code=400, detail="Qualità audio deve essere pcm, alaw o ulaw")

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
                raise HTTPException(
                    status_code=404, detail="Canzone della libreria non trovata")

            import json
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            music_path = metadata["file_path"]

            if not os.path.exists(music_path):
                raise HTTPException(
                    status_code=404, detail="File audio della libreria non trovato")
        elif music_file and music_file.filename:
            # Salva file temporaneo con estensione originale
            original_ext = os.path.splitext(music_file.filename)[1]
            temp_music_path = f"uploads/music_{session_id}{original_ext}"
            music_path = f"uploads/music_{session_id}.wav"

            # Salva file caricato
            with open(temp_music_path, "wb") as buffer:
                shutil.copyfileobj(music_file.file, buffer)

            # Converti in WAV se necessario (pydub supporta tutti i formati)
            try:
                if original_ext.lower() != '.wav':
                    logger.info(f"🔄 [Audio] Conversione formato: {original_ext} → WAV")
                    audio = AudioSegment.from_file(temp_music_path)
                    audio.export(music_path, format="wav")
                    os.remove(temp_music_path)  # Rimuovi file temporaneo
                else:
                    # È già WAV, rinomina
                    os.rename(temp_music_path, music_path)
            except Exception as e:
                logger.error(f"❌ [Audio] Errore conversione formato: {e}")
                if os.path.exists(temp_music_path):
                    os.remove(temp_music_path)
                raise HTTPException(
                    status_code=400,
                    detail=f"Formato audio non supportato o file corrotto: {str(e)}"
                )

        # Salva file voce di riferimento se presente
        if voice_reference and voice_reference.filename:
            with open(voice_ref_path, "wb") as buffer:
                shutil.copyfileobj(voice_reference.file, buffer)

        # Genera TTS usando il servizio selezionato
        logger.info(
            f"🎤 [TTS] Generazione audio | Servizio: {tts_service.upper()} | Voce: {voice_name} | Testo: '{text[:50]}...'")

        if tts_service == "edge":
            # Usa Edge TTS (gratuito)
            # Converti i parametri SSML in parametri Edge TTS
            rate_map = {'x-slow': '-50%', 'slow': '-25%',
                        'medium': '+0%', 'fast': '+25%', 'x-fast': '+50%'}
            volume_map = {'silent': '-100%', 'soft': '-50%',
                          'medium': '+0%', 'loud': '+50%', 'x-loud': '+100%'}

            rate = rate_map.get('medium', '+0%')
            volume = volume_map.get('loud', '+50%')

            success = await edge_tts_service.generate_speech(
                text=text,
                voice=voice_name,
                output_path=tts_path,
                rate=rate,
                volume=volume,
                pitch="+0Hz"
            )
        elif tts_service == "google":
            # Usa Google Cloud TTS
            if not google_tts_service.is_available():
                raise HTTPException(
                    status_code=503,
                    detail="Google TTS non configurato. Configura credenziali Google Cloud o usa tts_service='edge'."
                )
            
            try:
                audio_data, audio_format = await google_tts_service.synthesize_text(
                    text=text,
                    voice_name=voice_name,
                    speed=1.0
                )
                
                # Salva l'audio
                os.makedirs("output", exist_ok=True)
                with open(tts_path, 'wb') as f:
                    f.write(audio_data)
                
                # Converti MP3 in WAV se necessario
                if audio_format == "mp3":
                    audio = AudioSegment.from_mp3(tts_path)
                    audio.export(tts_path, format="wav")
                
                success = True
                
            except Exception as e:
                logger.error(f"❌ [Google TTS] Errore sintesi: {e}")
                success = False
        else:
            # Usa Azure Speech Services (richiede API key)
            if not azure_speech_service:
                raise HTTPException(
                    status_code=503,
                    detail="Azure Speech Service non configurato. Usa tts_service='edge' per il servizio gratuito."
                )

            # Opzioni SSML personalizzate per centralini
            ssml_options = {
                'rate': 'medium',
                'pitch': 'medium',
                'volume': 'loud',
                'style': 'customerservice' if 'Neural' in voice_name else None,
                'emphasis': 'moderate'
            }

            success = await generate_azure_speech(text, voice_name, tts_path, ssml_options)

        if not success:
            raise HTTPException(
                status_code=500, detail=f"{tts_service.upper()} TTS generation failed")

        # Salva nella cronologia e notifica utenti connessi
        try:
            # Ottieni IP utente per tracking (solo ultimi caratteri per privacy)
            user_ip = "unknown"  # In produzione: request.client.host

            history_id = add_text_to_history(text, voice_name, user_ip)

            # Notifica tutti gli utenti connessi del nuovo testo
            history_update = {
                "type": "new_text",
                "data": {
                    "id": history_id,
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "voice": voice_name,
                    "timestamp": datetime.now().isoformat(),
                    "user_ip": user_ip[-8:] if user_ip != "unknown" else "unknown"
                }
            }
            await manager.broadcast(history_update)

            logger.info(f"✅ [History] Testo salvato (ID: {history_id})")
        except Exception as e:
            logger.warning(f"⚠️ [History] Errore salvataggio: {e}")
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
            music_during_voice = music[music_before_ms:
                                       music_before_ms + voice_duration]
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
        final_path = convert_audio_to_format(
            final_audio, output_format, audio_quality, custom_filename)

        # Cleanup file temporanei
        if os.path.exists(tts_path):
            os.remove(tts_path)
        if music_path and not library_song_id and os.path.exists(music_path):
            # Non eliminare le canzoni della libreria, solo i file temporanei
            os.remove(music_path)

        logger.info(f"✅ [Audio] Generazione completata: {os.path.basename(final_path)}")

        # Pulisci il nome personalizzato per la sicurezza e genera data
        clean_name = "".join(
            c for c in custom_filename if c.isalnum() or c in "._-").strip()
        if not clean_name:
            clean_name = "centralino_audio"

        date_str = datetime.now().strftime("%y%m%d")

        return FileResponse(
            final_path,
            media_type=get_media_type(output_format),
            filename=f"{clean_name}_{date_str}.{output_format}"
        )

    except Exception as e:
        logger.error(f"❌ [Audio] Errore durante la generazione: {e}")
        # Cleanup in case of error
        for path in [tts_path, final_path]:
            if 'path' in locals() and os.path.exists(path):
                os.remove(path)
        if music_path and not library_song_id and os.path.exists(music_path):
            os.remove(music_path)
        if voice_ref_path and os.path.exists(voice_ref_path):
            os.remove(voice_ref_path)
        raise HTTPException(
            status_code=500, detail=f"Errore nella generazione audio: {str(e)}")


@app.post("/music-library/upload")
async def upload_music_to_library(
    name: str = Form(...),
    music_file: UploadFile = File(...)
):
    """
    Carica una canzone nella libreria musicale usando il gestore refactorizzato.
    """
    if not music_file.filename:
        raise HTTPException(status_code=400, detail="File musicale richiesto")

    # Verifica che sia un file audio (accetta qualsiasi tipo audio/*)
    content_type = music_file.content_type or ''
    is_audio = content_type.startswith(
        'audio/') or content_type.startswith('application/ogg')

    if not is_audio:
        raise HTTPException(
            status_code=400,
            detail=f"File non audio. Tipo ricevuto: {content_type}"
        )

    try:
        # Leggi contenuto file
        file_content = await music_file.read()

        # Usa il gestore della libreria musicale
        metadata = music_library.add_song(
            name=name,
            file_content=file_content,
            filename=music_file.filename,
            content_type=music_file.content_type
        )

        logger.info(f"🎵 [Music Library] Brano caricato: '{name}' (ID: {metadata['id']})")

        return {
            "message": f"Canzone '{name}' aggiunta alla libreria con successo",
            "song_id": metadata["id"],
            "duration_seconds": metadata["duration_seconds"]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Errore caricamento musica: {e}")
        raise HTTPException(
            status_code=500, detail=f"Errore nel caricamento: {str(e)}"
        )


@app.get("/music-library/list")
async def list_music_library():
    """
    Lista tutte le canzoni nella libreria usando il gestore refactorizzato.
    """
    try:
        songs = music_library.list_songs()
        return {"songs": songs}
    except Exception as e:
        logger.error(f"Errore lista canzoni: {e}")
        raise HTTPException(
            status_code=500, detail=f"Errore recupero lista: {str(e)}"
        )


@app.delete("/music-library/{song_id}")
async def delete_music_from_library(song_id: str):
    """
    Elimina una canzone dalla libreria usando il gestore refactorizzato.
    """
    try:
        # Recupera metadata prima di eliminare
        metadata = music_library.get_song(song_id)

        if not metadata:
            raise HTTPException(
                status_code=404,
                detail="Canzone non trovata nella libreria"
            )

        # Elimina la canzone
        success = music_library.delete_song(song_id)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Errore durante l'eliminazione"
            )

        logger.info(f"Canzone eliminata: {metadata['name']} ({song_id})")

        return {
            "message": f"Canzone '{metadata['name']}' eliminata dalla libreria",
            "song_id": song_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore eliminazione musica: {e}")
        raise HTTPException(
            status_code=500, detail=f"Errore nell'eliminazione: {str(e)}"
        )


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

        logger.info(
            f"Voice training data saved for '{voice_name}' - {len(audio_samples)} samples")

        return {
            "message": f"Training data per la voce '{voice_name}' salvati con successo",
            "samples_count": len(audio_samples),
            "voice_dir": voice_dir,
            "note": "Azure Speech Services usa voci Neural predefinite. Per voice cloning personalizzato, contatta il supporto Azure."
        }

    except Exception as e:
        logger.error(f"Error in voice training: {e}")
        raise HTTPException(
            status_code=500, detail=f"Errore nel training: {str(e)}")


@app.get("/speakers")
async def get_available_speakers():
    """Lista degli speaker usando il catalogo voci refactorizzato."""

    # Ottieni voci femminili
    female_voices = voice_catalog.filter_by_gender("Female")

    # Ottieni voci maschili
    male_voices = voice_catalog.filter_by_gender("Male")

    # Formatta per l'API
    azure_voices = {
        "female_voices": [
            {
                "id": voice["short_name"],
                "name": f"🚺 {voice['display_name']} - {voice['description']}",
                "language": "it-IT",
                "description": voice["description"],
                "style_support": len(voice["styles"]) > 1,
                "styles": voice["styles"]
            }
            for voice in female_voices
        ],
        "male_voices": [
            {
                "id": voice["short_name"],
                "name": f"🚹 {voice['display_name']} - {voice['description']}",
                "language": "it-IT",
                "description": voice["description"],
                "style_support": len(voice["styles"]) > 1,
                "styles": voice["styles"]
            }
            for voice in male_voices
        ]
    }

    return {
        "available_speakers": azure_voices,
        "service": "Azure Speech Services",
        "total_voices": len(female_voices) + len(male_voices),
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


@app.get("/tts/services")
async def get_tts_services():
    """Restituisce i servizi TTS disponibili con le loro voci"""
    services = {}

    # Edge TTS (sempre disponibile, gratuito)
    edge_voices = await edge_tts_service.get_available_voices()
    services["edge"] = {
        "name": "Microsoft Edge TTS",
        "description": "Servizio gratuito senza API key",
        "available": True,
        "voices": edge_voices,
        "default_voice": "it-IT-ElsaNeural"
    }

    # Azure Speech Services (richiede API key e connessione valida)
    azure_voices = {}
    azure_available = azure_speech_service is not None and azure_speech_available

    if azure_available:
        try:
            azure_voices = await azure_speech_service.get_available_voices()
        except Exception as e:
            logger.error(f"Errore caricamento voci Azure: {e}")
            azure_available = False

    services["azure"] = {
        "name": "Azure Speech Services",
        "description": "Servizio premium con voci neurali avanzate" if azure_available else "Non disponibile - configura AZURE_SPEECH_KEY",
        "available": azure_available,
        "voices": azure_voices,
        "default_voice": "it-IT-ElsaNeural"
    }

    # Google Cloud TTS (richiede credenziali Google Cloud)
    google_available = google_tts_service.is_available()
    services["google"] = {
        "name": "Google Cloud Text-to-Speech",
        "description": "Servizio Google con voci Neural2" if google_available else "Non disponibile - configura credenziali Google Cloud",
        "available": google_available,
        "voices": google_tts_service.get_available_voices(),
        "default_voice": "it-IT-Neural2-A"
    }

    return {
        "services": services,
        "default_service": "edge"  # Sempre Edge come default
    }


@app.get("/")
async def root():
    return {
        "message": "crazy-phoneTTS API - TTS Italiano per Centralini con Azure Speech Services",
        "docs": "/docs",
        "health": "/health",
        "voice_training": "/train-voice",
        "list_voices": "/voices",
        "tts_services": "/tts/services"
    }

# ==========================================
# SISTEMA AUTO-AGGIORNAMENTO
# ==========================================

# Gestore notifiche aggiornamenti
update_notification_manager = UpdateNotificationManager()


def get_current_version():
    """Legge la versione usando il gestore refactorizzato."""
    return version_manager.get_current_version()


async def check_github_releases():
    """Controlla le release su GitHub usando il gestore refactorizzato."""
    return version_manager.check_github_releases()


@app.get("/version/current")
async def current_version():
    """Restituisce la versione attuale del sistema."""
    return {
        "current_version": get_current_version(),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/version/check")
async def check_updates():
    """Controlla se ci sono aggiornamenti disponibili usando il gestore refactorizzato."""
    update_info = version_manager.is_update_available()

    if not update_info["available"]:
        return {
            "current_version": update_info["current_version"],
            "latest_version": update_info.get("latest_version"),
            "update_available": update_info["available"],
            "message": update_info["message"]
        }

    # Istruzioni per l'aggiornamento
    update_instructions = {
        "windows": {
            "command": ".\\update.ps1",
            "description": "Apri PowerShell nella cartella del progetto ed esegui"
        },
        "linux": {
            "command": "./update.sh",
            "description": "Apri il terminale nella cartella del progetto ed esegui"
        },
        "mac": {
            "command": "./update.sh",
            "description": "Apri il terminale nella cartella del progetto ed esegui"
        }
    }

    return {
        "current_version": update_info["current_version"],
        "latest_version": update_info["latest_version"],
        "update_available": update_info["available"],
        "release_info": update_info["release_info"],
        "update_instructions": update_instructions
    }


@app.get("/update/instructions")
async def get_update_instructions():
    """Fornisce le istruzioni per aggiornare manualmente il sistema."""
    return {
        "message": "L'aggiornamento deve essere eseguito manualmente sul server",
        "instructions": update_notification_manager.get_update_instructions("all"),
        "note": "Il backend non esegue aggiornamenti automatici per motivi di sicurezza"
    }


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Avvio server su {BACKEND_HOST}:{BACKEND_PORT}")
    uvicorn.run(app, host=BACKEND_HOST, port=BACKEND_PORT)
