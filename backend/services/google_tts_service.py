"""
Servizio Google Cloud Text-to-Speech - Versione Essenziale

Integrazione minima con Google TTS per crazy-phoneTTS
"""

import asyncio
import os
from typing import Tuple, List, Dict, Optional

try:
    from google.cloud import texttospeech
    from google.auth import default
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    texttospeech = None

class GoogleTTSService:
    """Servizio essenziale Google Cloud Text-to-Speech"""
    
    def __init__(self):
        self.client = None
        self.available = False
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
                print("✅ Google TTS: Servizio attivo")
        except Exception as e:
            print(f"⚠️  Google TTS: {e}")
    
    def _check_default_credentials(self) -> bool:
        """Verifica credenziali di default"""
        try:
            default()
            return True
        except:
            return False
    
    def is_available(self) -> bool:
        """Controlla se il servizio è disponibile"""
        return self.available
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """Restituisce voci italiane Google nel formato standard"""
        if not self.available:
            return []
        
        # Voci Google più comuni per l'italiano
        return [
            {"id": "it-IT-Neural2-A", "name": "Google Neural2-A (Femminile)", "gender": "Femminile", "service": "google"},
            {"id": "it-IT-Neural2-C", "name": "Google Neural2-C (Maschile)", "gender": "Maschile", "service": "google"},
            {"id": "it-IT-Wavenet-A", "name": "Google WaveNet-A (Femminile)", "gender": "Femminile", "service": "google"},
            {"id": "it-IT-Wavenet-B", "name": "Google WaveNet-B (Femminile)", "gender": "Femminile", "service": "google"},
            {"id": "it-IT-Wavenet-C", "name": "Google WaveNet-C (Maschile)", "gender": "Maschile", "service": "google"},
            {"id": "it-IT-Wavenet-D", "name": "Google WaveNet-D (Maschile)", "gender": "Maschile", "service": "google"},
        ]
    
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