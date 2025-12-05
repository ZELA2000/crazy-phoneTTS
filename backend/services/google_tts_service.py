"""
Servizio Google Cloud Text-to-Speech - Versione Essenziale

Integrazione minima con Google TTS per crazy-phoneTTS
"""

import asyncio
import os
import logging
from typing import Tuple, Dict

try:
    from google.cloud import texttospeech
    from google.auth import default
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    texttospeech = None

logger = logging.getLogger(__name__)


class GoogleTTSService:
    """Servizio essenziale Google Cloud Text-to-Speech"""

    def __init__(self):
        self.client = None
        self.available = False
        self._voices_cache = {}
        self._initialize()

    def _initialize(self):
        """Inizializza il client se possibile"""
        if not GOOGLE_AVAILABLE:
            return

        try:
            # Verifica credenziali
            if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or self._check_default_credentials():
                self.client = texttospeech.TextToSpeechClient()
                self.available = True
                logger.info("✅ [Google TTS] Servizio inizializzato con successo")
        except Exception as e:
            logger.warning(f"⚠️ [Google TTS] Servizio non disponibile: {e}")

    def _check_default_credentials(self) -> bool:
        """Verifica credenziali di default"""
        try:
            default()
            return True
        except Exception:
            return False

    def is_available(self) -> bool:
        """Controlla se il servizio è disponibile"""
        return self.available

    def get_available_voices(self) -> Dict[str, str]:
        """Restituisce voci italiane Google caricandole dinamicamente dall'API"""
        if not self.available:
            return {}

        # Se già in cache, restituisci
        if self._voices_cache:
            return self._voices_cache

        try:
            # Carica tutte le voci disponibili dall'API Google
            voices_response = self.client.list_voices(language_code="it-IT")

            voices_dict = {}
            for voice in voices_response.voices:
                # Filtra solo voci italiane
                if voice.language_codes and "it-IT" in voice.language_codes:
                    # Crea nome descrittivo
                    gender_label = "Femminile" if voice.ssml_gender == texttospeech.SsmlVoiceGender.FEMALE else "Maschile"

                    # Estrai tipo voce dal nome (Neural2, Wavenet, Standard)
                    voice_type = "Standard"
                    if "Neural2" in voice.name:
                        voice_type = "Neural2"
                    elif "Wavenet" in voice.name:
                        voice_type = "WaveNet"

                    display_name = f"Google {voice_type} - {voice.name.split('-')[-1]} ({gender_label})"
                    voices_dict[voice.name] = display_name

            # Salva in cache
            self._voices_cache = voices_dict
            logger.info(
                f"✅ [Google TTS] Caricate {len(voices_dict)} voci italiane dall'API")

            return voices_dict

        except Exception as e:
            logger.error(f"❌ [Google TTS] Errore caricamento voci: {e}")
            # Fallback: voci base se l'API fallisce
            return {
                "it-IT-Neural2-A": "Google Neural2-A (Femminile)",
                "it-IT-Neural2-C": "Google Neural2-C (Maschile)",
            }

    async def synthesize_text(self, text: str, voice_name: str = "it-IT-Neural2-A", speed: float = 1.0) -> Tuple[bytes, str]:
        """
        Sintetizza testo in audio

        Returns:
            Tuple[bytes, str]: (audio_bytes, formato)
        """
        if not self.available:
            raise Exception("Google TTS non disponibile")

        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)

            voice = texttospeech.VoiceSelectionParams(
                name=voice_name,
                language_code="it-IT"
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=max(0.25, min(4.0, speed))
            )

            # Esegui sintesi in thread
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
            )

            return response.audio_content, "mp3"

        except Exception as e:
            raise Exception(f"Errore Google TTS: {str(e)}")
