"""
Elaborazione e conversione audio per formati telefonici.

Questo modulo gestisce la conversione dell'audio nei vari formati e qualità
richiesti per i centralini telefonici, applicando le specifiche corrette
per PCM, A-law e u-law.
"""

import os
import logging
from datetime import datetime
from typing import Tuple
from pydub import AudioSegment

logger = logging.getLogger(__name__)


class AudioQualitySpec:
    """Specifiche di qualità audio per formati telefonici."""

    PCM = {
        "sample_rate": 8000,
        "sample_width": 2,  # 16 bit
        "bitrate": "128k",
        "description": "PCM: 8kHz, 16bit, 128kbps"
    }

    ALAW = {
        "sample_rate": 8000,
        "sample_width": 1,  # 8 bit
        "bitrate": "64k",
        "codec": "pcm_alaw",
        "description": "A-law (G.711): 8kHz, 8bit, 64kbps"
    }

    ULAW = {
        "sample_rate": 8000,
        "sample_width": 1,  # 8 bit
        "bitrate": "64k",
        "codec": "pcm_mulaw",
        "description": "u-law (G.711): 8kHz, 8bit, 64kbps"
    }


class AudioConverter:
    """
    Converte audio nei formati richiesti per centralini telefonici.

    Applica le specifiche di qualità corrette e gestisce la generazione
    dei nomi file con timestamp.
    """

    SUPPORTED_FORMATS = ["wav", "mp3", "gsm"]
    SUPPORTED_QUALITIES = ["pcm", "alaw", "ulaw"]

    def __init__(self, output_directory: str = "output"):
        """
        Inizializza il convertitore audio.

        Args:
            output_directory: Directory dove salvare i file convertiti
        """
        self.output_directory = output_directory
        os.makedirs(output_directory, exist_ok=True)

    def convert(
        self,
        audio_segment: AudioSegment,
        output_format: str,
        audio_quality: str,
        custom_filename: str
    ) -> str:
        """
        Converte l'audio nel formato e qualità specificati.

        Args:
            audio_segment: Segmento audio da convertire
            output_format: Formato output (wav, mp3, gsm)
            audio_quality: Qualità audio (pcm, alaw, ulaw)
            custom_filename: Nome base del file di output

        Returns:
            Percorso del file audio convertito

        Raises:
            ValueError: Se formato o qualità non supportati
        """
        self._validate_parameters(output_format, audio_quality)

        # Applica specifiche qualità
        audio_segment = self._apply_quality_specs(audio_segment, audio_quality)

        # Genera percorso output
        output_path = self._generate_output_path(
            output_format, custom_filename
        )

        # Esporta con parametri corretti
        self._export_audio(audio_segment, output_path,
                           output_format, audio_quality)

        logger.info(f"Audio convertito: {output_path}")
        return output_path

    def _validate_parameters(self, output_format: str, audio_quality: str) -> None:
        """Valida i parametri di conversione."""
        if output_format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Formato non supportato: {output_format}. "
                f"Supportati: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        if audio_quality not in self.SUPPORTED_QUALITIES:
            raise ValueError(
                f"Qualità non supportata: {audio_quality}. "
                f"Supportate: {', '.join(self.SUPPORTED_QUALITIES)}"
            )

    def _apply_quality_specs(
        self,
        audio: AudioSegment,
        quality: str
    ) -> AudioSegment:
        """
        Applica le specifiche di qualità audio.

        Args:
            audio: Segmento audio da processare
            quality: Qualità da applicare (pcm, alaw, ulaw)

        Returns:
            Segmento audio con qualità applicata
        """
        if quality == "pcm":
            spec = AudioQualitySpec.PCM
        elif quality == "alaw":
            spec = AudioQualitySpec.ALAW
        else:  # ulaw
            spec = AudioQualitySpec.ULAW

        audio = audio.set_frame_rate(spec["sample_rate"])
        audio = audio.set_channels(1)  # Mono per telefonia
        audio = audio.set_sample_width(spec["sample_width"])

        return audio

    def _generate_output_path(
        self,
        output_format: str,
        custom_filename: str
    ) -> str:
        """
        Genera il percorso del file di output con timestamp.

        Args:
            output_format: Formato del file (wav, mp3, gsm)
            custom_filename: Nome personalizzato del file

        Returns:
            Percorso completo del file di output
        """
        # Sanitizza nome file
        clean_name = "".join(
            c for c in custom_filename if c.isalnum() or c in "._-"
        ).strip()

        if not clean_name:
            clean_name = "centralino_audio"

        # Genera data in formato YYMMDD
        date_str = datetime.now().strftime("%y%m%d")

        filename = f"{clean_name}_{date_str}.{output_format}"
        return os.path.join(self.output_directory, filename)

    def _export_audio(
        self,
        audio: AudioSegment,
        output_path: str,
        output_format: str,
        audio_quality: str
    ) -> None:
        """
        Esporta l'audio nel formato specificato.

        Args:
            audio: Segmento audio da esportare
            output_path: Percorso dove salvare il file
            output_format: Formato di output
            audio_quality: Qualità audio
        """
        if output_format == "wav":
            self._export_wav(audio, output_path, audio_quality)
        elif output_format == "mp3":
            self._export_mp3(audio, output_path, audio_quality)
        else:  # gsm
            audio.export(output_path, format="gsm")

    def _export_wav(
        self,
        audio: AudioSegment,
        output_path: str,
        quality: str
    ) -> None:
        """Esporta in formato WAV con codec appropriato."""
        if quality == "alaw":
            audio.export(
                output_path,
                format="wav",
                parameters=["-acodec", "pcm_alaw"]
            )
        elif quality == "ulaw":
            audio.export(
                output_path,
                format="wav",
                parameters=["-acodec", "pcm_mulaw"]
            )
        else:  # pcm
            audio.export(output_path, format="wav")

    def _export_mp3(
        self,
        audio: AudioSegment,
        output_path: str,
        quality: str
    ) -> None:
        """Esporta in formato MP3 con bitrate appropriato."""
        bitrate = "128k" if quality == "pcm" else "64k"
        audio.export(output_path, format="mp3", bitrate=bitrate)

    @staticmethod
    def get_media_type(output_format: str) -> str:
        """
        Restituisce il media type MIME per il formato.

        Args:
            output_format: Formato del file (wav, mp3, gsm)

        Returns:
            Media type MIME appropriato
        """
        media_types = {
            "wav": "audio/wav",
            "mp3": "audio/mpeg",
            "gsm": "audio/gsm"
        }
        return media_types.get(output_format, "audio/wav")
