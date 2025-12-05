"""
Servizio Edge TTS (Microsoft Edge TTS gratuito senza API key)

Utilizza l'API gratuita di Microsoft Edge per generare speech di alta qualità
senza necessità di chiavi API o abbonamenti.
"""

import edge_tts
import asyncio
import logging
import os
import tempfile
from typing import Optional
from pydub import AudioSegment

logger = logging.getLogger(__name__)


class EdgeTTSService:
    """Servizio per generazione TTS usando Edge TTS (gratuito)"""

    def __init__(self):
        """Inizializza il servizio Edge TTS"""
        self.available_voices = None
        self._voices_cache_initialized = False
        logger.info("✅ [Edge TTS] Servizio inizializzato con successo")

    async def _initialize_voices(self):
        """Carica le voci italiane disponibili dall'API Edge TTS"""
        if self._voices_cache_initialized:
            return

        try:
            logger.info("📥 [Edge TTS] Caricamento voci italiane da API Edge TTS...")
            all_voices = await edge_tts.list_voices()

            # Filtra solo voci italiane
            italian_voices = [
                v for v in all_voices if v['Locale'].startswith('it-')]

            # Debug: mostra struttura della prima voce
            if italian_voices:
                logger.info(
                    f"🔍 Struttura voce Edge TTS: {list(italian_voices[0].keys())}")

            # Crea dizionario {short_name: display_name}
            # I campi corretti sono: ShortName, Name, Gender, Locale
            self.available_voices = {
                voice['ShortName']: f"{voice['Name']} ({voice['Gender']})"
                for voice in italian_voices
            }

            self._voices_cache_initialized = True
            logger.info(
                f"✅ Caricate {len(self.available_voices)} voci italiane da Edge TTS")

        except Exception as e:
            logger.error(f"❌ [Edge TTS] Errore caricamento voci: {e}")
            # Fallback a voci base
            self.available_voices = {
                "it-IT-ElsaNeural": "Elsa (Female)",
                "it-IT-DiegoNeural": "Diego (Male)"
            }
            self._voices_cache_initialized = True

    async def generate_speech(
        self,
        text: str,
        voice: str,
        output_path: str,
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz"
    ) -> bool:
        """
        Genera audio TTS usando Edge TTS e converte in WAV.

        Args:
            text: Testo da convertire in speech
            voice: Nome della voce da utilizzare
            output_path: Percorso dove salvare il file audio (WAV)
            rate: Velocità (es. "+20%", "-10%")
            volume: Volume (es. "+50%", "-20%")
            pitch: Tono (es. "+5Hz", "-3Hz")

        Returns:
            True se successo, False altrimenti
        """
        try:
            # Inizializza le voci se necessario
            await self._initialize_voices()

            # Valida la voce
            if voice not in self.available_voices:
                logger.warning(
                    f"Voce {voice} non disponibile, uso default it-IT-ElsaNeural")
                voice = "it-IT-ElsaNeural"

            logger.info(
                f"🎤 Generazione TTS con Edge: voce={voice}, rate={rate}, volume={volume}, pitch={pitch}")

            # Edge TTS genera MP3, quindi salviamo prima in un file temporaneo
            temp_mp3 = output_path.replace('.wav', '_temp.mp3')

            # Crea comunicazione Edge TTS
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                volume=volume,
                pitch=pitch
            )

            # Salva l'audio MP3 temporaneo
            await communicate.save(temp_mp3)

            # Verifica che il file MP3 sia stato creato
            if not os.path.exists(temp_mp3):
                raise Exception(f"File MP3 temporaneo non creato: {temp_mp3}")

            logger.info(
                f"✅ MP3 temporaneo creato: {temp_mp3} ({os.path.getsize(temp_mp3)} bytes)")

            # Converti MP3 in WAV usando pydub
            logger.info(f"🔄 [Edge TTS] Conversione formato: MP3 → WAV")
            audio = AudioSegment.from_mp3(temp_mp3)
            audio.export(output_path, format="wav")

            # Verifica che il WAV sia stato creato
            if not os.path.exists(output_path):
                raise Exception(f"File WAV non creato: {output_path}")

            logger.info(
                f"✅ WAV creato: {output_path} ({os.path.getsize(output_path)} bytes)")

            # Rimuovi file temporaneo
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
                logger.info(f"🗑️ [Edge TTS] File temporaneo rimosso: {os.path.basename(temp_mp3)}")

            logger.info(
                f"✅ Audio generato e convertito con successo: {output_path}")
            return True

        except Exception as error:
            logger.error(f"❌ [Edge TTS] Errore durante la generazione: {error}")
            # Cleanup in caso di errore
            temp_mp3 = output_path.replace('.wav', '_temp.mp3')
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
            return False

    async def get_available_voices(self) -> dict:
        """Restituisce le voci disponibili"""
        await self._initialize_voices()
        return self.available_voices

    @staticmethod
    async def list_all_voices():
        """Lista tutte le voci disponibili (metodo utility)"""
        voices = await edge_tts.list_voices()
        italian_voices = [v for v in voices if v['Locale'].startswith('it-')]
        return italian_voices
