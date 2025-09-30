from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure Speech Services Configuration
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "westeurope")

if not AZURE_SPEECH_KEY:
    logger.warning("AZURE_SPEECH_KEY non configurata! Il servizio TTS potrebbe non funzionare.")

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
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure Speech Services Italian voices - Voci Microsoft di alta qualità commerciali
AZURE_VOICES = {
    "it-IT-ElsaNeural": "Elsa (Femmina - Naturale)",
    "it-IT-IsabellaNeural": "Isabella (Femmina - Espressiva)", 
    "it-IT-DiegoNeural": "Diego (Maschio - Naturale)",
    "it-IT-BenignoNeural": "Benigno (Maschio - Espressivo)"
}

@app.on_event("startup")
async def startup_event():
    logger.info("TTS server started - Azure Speech Services ready for commercial use!")
    logger.info(f"Azure Speech configured - Region: {AZURE_SPEECH_REGION}")
    if AZURE_SPEECH_KEY:
        logger.info("Azure Speech API Key: ✓ Configured")
    else:
        logger.warning("Azure Speech API Key: ✗ Missing - Add AZURE_SPEECH_KEY environment variable")
    # Azure Speech Services - Versione commerciale legale

async def generate_azure_speech(text: str, voice: str, output_path: str):
    """Genera audio usando Azure Speech Services - Versione commerciale legale"""
    try:
        if not AZURE_SPEECH_KEY:
            logger.error("AZURE_SPEECH_KEY non configurata")
            return False
            
        # Configurazione Azure Speech
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
        speech_config.speech_synthesis_voice_name = voice
        speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm)
        
        # Sintesi vocale
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        
        # Genera SSML per controllo qualità
        ssml = f"""
        <speak version="1.0" xml:lang="it-IT">
            <voice name="{voice}">
                <prosody rate="medium" pitch="medium">
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        
        # Sintesi asincrona
        result = synthesizer.speak_ssml_async(ssml).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # Salva l'audio direttamente
            with open(output_path, 'wb') as audio_file:
                audio_file.write(result.audio_data)
            return True
        else:
            logger.error(f"Azure Speech error: {result.reason}")
            return False
            
    except Exception as e:
        logger.error(f"Azure Speech error: {e}")
        return False

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "azure_speech_ready": bool(AZURE_SPEECH_KEY),
        "region": AZURE_SPEECH_REGION
    }

@app.get("/available-voices")
async def get_available_voices():
    """Ottieni lista delle voci disponibili Azure Speech Services"""
    voices = {
        "azure_voices": AZURE_VOICES,
        "supported_languages": ["it-IT"],
        "service": "Azure Speech Services",
        "commercial_license": True
    }
    
    return voices

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
        
        # Genera TTS basato sul servizio scelto
        logger.info(f"Generating TTS for text: {text[:50]}... using {tts_service}")
        
        if tts_service == "azure":
            # Usa Azure Speech Services - Versione commerciale legale
            success = await generate_azure_speech(text, edge_voice, tts_path)
            if not success:
                raise HTTPException(status_code=500, detail="Azure Speech generation failed")
        else:
            # Fallback per compatibilità - usa Azure come default
            success = await generate_azure_speech(text, edge_voice, tts_path)
            if not success:
                raise HTTPException(status_code=500, detail="Azure Speech generation failed")
            model_name = getattr(tts, 'model_name', '') or str(type(tts)).lower()
            
            if 'your_tts' in model_name.lower() or 'yourtts' in model_name.lower():
                # YourTTS è multi-speaker e RICHIEDE sempre uno speaker
                if voice_reference and voice_reference.filename:
                    logger.info("Using YourTTS voice cloning with reference audio")
                    tts.tts_to_file(
                        text=text,
                        file_path=tts_path,
                        speaker_wav=voice_ref_path,
                        language=language
                    )
                elif predefined_speaker:
                    logger.info(f"Using predefined speaker: {predefined_speaker}")
                    # Mappa gli speaker predefiniti a quelli reali del modello
                    speaker_mapping = {
                        "female_01": "female_01",
                        "female_02": "female_02", 
                        "female_03": "female_03",
                        "male_01": "male_01",
                        "male_02": "male_02",
                        "male_03": "male_03"
                    }
                    actual_speaker = speaker_mapping.get(predefined_speaker, predefined_speaker)
                    tts.tts_to_file(
                        text=text,
                        file_path=tts_path,
                        speaker=actual_speaker,
                        language=language
                    )
                else:
                    # YourTTS RICHIEDE uno speaker - usa il primo disponibile come default
                    try:
                        if hasattr(tts, 'speakers') and tts.speakers:
                            default_speaker = tts.speakers[0]  # Primo speaker disponibile
                            logger.info(f"Using default YourTTS speaker: {default_speaker}")
                            tts.tts_to_file(
                                text=text,
                                file_path=tts_path,
                                speaker=default_speaker,
                                language=language
                            )
                        else:
                            # Fallback con speaker generico
                            logger.info("Using fallback speaker for YourTTS")
                            tts.tts_to_file(
                                text=text,
                                file_path=tts_path,
                                speaker="speaker_00",  # Speaker generico
                                language=language
                            )
                    except Exception as speaker_error:
                        logger.error(f"Error with speaker selection: {speaker_error}")
                        # Ultimo tentativo senza specificare speaker
                        tts.tts_to_file(text=text, file_path=tts_path)
            elif 'xtts' in model_name.lower():
                # XTTS_v2 voice cloning
                if voice_reference and voice_reference.filename:
                    logger.info("Using XTTS_v2 voice cloning with reference audio")
                    tts.tts_to_file(
                        text=text, 
                        file_path=tts_path,
                        speaker_wav=voice_ref_path,
                        language=language
                    )
                else:
                    tts.tts_to_file(text=text, file_path=tts_path, language=language)
            else:
                # Altri modelli TTS (Glow-TTS, VITS, etc.)
                logger.info(f"Using standard TTS model: {model_name}")
                tts.tts_to_file(text=text, file_path=tts_path)
        
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
    Endpoint per allenare una nuova voce con XTTS_v2
    - voice_name: Nome per la nuova voce
    - audio_samples: Lista di file audio (WAV, MP3) di 3-30 secondi ciascuno
    - transcriptions: Trascrizioni corrispondenti separate da "|"
    """
    if not tts or not hasattr(tts, 'model_name') or 'xtts' not in tts.model_name.lower():
        raise HTTPException(status_code=400, detail="Voice training richiede XTTS_v2 model")
    
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
            "note": "Usa i file nella directory per voice cloning con il parametro voice_reference"
        }
        
    except Exception as e:
        logger.error(f"Error in voice training: {e}")
        raise HTTPException(status_code=500, detail=f"Errore nel training: {str(e)}")

@app.get("/speakers")
async def get_available_speakers():
    """Lista degli speaker predefiniti disponibili"""
    
    # Speaker predefiniti per diversi modelli
    predefined_speakers = {
        "female_voices": [
            {"id": "female_01", "name": "Sofia - Voce Femminile Italiana", "language": "it", "description": "Voce femminile naturale e professionale"},
            {"id": "female_02", "name": "Elena - Voce Femminile Calda", "language": "it", "description": "Voce femminile accogliente per centralini"},
            {"id": "female_03", "name": "Giulia - Voce Femminile Giovane", "language": "it", "description": "Voce femminile moderna e dinamica"}
        ],
        "male_voices": [
            {"id": "male_01", "name": "Marco - Voce Maschile Italiana", "language": "it", "description": "Voce maschile autorevole e chiara"},
            {"id": "male_02", "name": "Andrea - Voce Maschile Profonda", "language": "it", "description": "Voce maschile profonda e rassicurante"},
            {"id": "male_03", "name": "Luca - Voce Maschile Energica", "language": "it", "description": "Voce maschile vivace e coinvolgente"}
        ]
    }
    
    # Se abbiamo TTS caricato, prova a ottenere speaker reali
    if tts:
        try:
            # Per YourTTS e XTTS che supportano speaker multipli
            if hasattr(tts, 'speakers') and tts.speakers:
                real_speakers = []
                for i, speaker in enumerate(tts.speakers[:15]):  # Limita a 15 speaker
                    # Crea nomi più descrittivi per gli speaker
                    if 'female' in str(speaker).lower():
                        speaker_name = f"🚺 {speaker} - Voce Femminile"
                    elif 'male' in str(speaker).lower():
                        speaker_name = f"🚹 {speaker} - Voce Maschile"
                    else:
                        speaker_name = f"🎤 {speaker}"
                    
                    real_speakers.append({
                        "id": speaker,
                        "name": speaker_name,
                        "language": "multilingual",
                        "description": f"Speaker nativo del modello YourTTS"
                    })
                predefined_speakers["model_speakers"] = real_speakers
                logger.info(f"Found {len(real_speakers)} speakers in the model")
        except Exception as e:
            logger.warning(f"Could not get model speakers: {e}")
    
    return {
        "available_speakers": predefined_speakers,
        "model_loaded": tts is not None,
        "voice_cloning_supported": True
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
