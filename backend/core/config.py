"""
Configurazione centralizzata per il servizio TTS.

Questo modulo gestisce tutte le configurazioni necessarie per il funzionamento
del sistema, incluse le credenziali Azure, le impostazioni di rete e i percorsi
dei file.
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class AzureConfiguration:
    """
    Gestisce la configurazione di Azure Speech Services.

    Attributes:
        speech_key: Chiave API per Azure Speech Services
        speech_region: Regione Azure (default: westeurope)
        speech_endpoint: Endpoint personalizzato opzionale
    """

    def __init__(self):
        self.speech_key = os.getenv("AZURE_SPEECH_KEY")
        self.speech_region = os.getenv("AZURE_SPEECH_REGION", "westeurope")
        self.speech_endpoint = os.getenv("AZURE_SPEECH_ENDPOINT")

    def is_configured(self) -> bool:
        """Verifica se la configurazione Azure è completa."""
        return bool(self.speech_key)

    def log_status(self) -> None:
        """Registra lo stato della configurazione Azure."""
        if not self.is_configured():
            logger.error("AZURE_SPEECH_KEY non configurata")
            logger.info(
                "Per ottenere una chiave Azure Speech: "
                "https://docs.microsoft.com/azure/cognitive-services/speech-service/get-started"
            )
        else:
            logger.info("Azure Speech Services configurato correttamente")


class NetworkConfiguration:
    """
    Gestisce la configurazione di rete del servizio.

    Attributes:
        host: Indirizzo IP su cui il server accetta connessioni
        port: Porta su cui il server è in ascolto
    """

    def __init__(self):
        self.host = os.getenv("BACKEND_HOST", "0.0.0.0")
        self.port = int(os.getenv("BACKEND_PORT", "8000"))

    def log_status(self) -> None:
        """Registra la configurazione di rete corrente."""
        logger.info(
            f"Server configurato per ascoltare su: {self.host}:{self.port}")


class AudioQualityConfiguration:
    """
    Definisce le specifiche di qualità audio per formati telefonici.

    Le configurazioni seguono gli standard industriali per centralini telefonici:
    - PCM: 8kHz, 16bit, 128kbps (alta qualità)
    - A-law: 8kHz, 8bit, 64kbps (standard G.711)
    - u-law: 8kHz, 8bit, 64kbps (standard G.711)
    """

    CONFIGURATIONS: Dict[str, Dict[str, Any]] = {
        "pcm": {
            "sample_rate": 8000,
            "sample_width": 2,
            "bitrate": "128k",
            "description": "PCM: 8kHz, 16bit, 128kbps"
        },
        "alaw": {
            "sample_rate": 8000,
            "sample_width": 1,
            "bitrate": "64k",
            "codec": "pcm_alaw",
            "description": "A-law (G.711): 8kHz, 8bit, 64kbps"
        },
        "ulaw": {
            "sample_rate": 8000,
            "sample_width": 1,
            "bitrate": "64k",
            "codec": "pcm_mulaw",
            "description": "u-law (G.711): 8kHz, 8bit, 64kbps"
        }
    }

    @classmethod
    def get_configuration(cls, quality: str) -> Dict[str, Any]:
        """
        Recupera la configurazione per una specifica qualità audio.

        Args:
            quality: Tipo di qualità richiesta (pcm, alaw, ulaw)

        Returns:
            Dizionario con i parametri di configurazione

        Raises:
            ValueError: Se la qualità specificata non è supportata
        """
        if quality not in cls.CONFIGURATIONS:
            raise ValueError(
                f"Qualità audio non supportata: {quality}. "
                f"Supportate: {', '.join(cls.CONFIGURATIONS.keys())}"
            )
        return cls.CONFIGURATIONS[quality]


class FilePathConfiguration:
    """Gestisce i percorsi dei file e delle directory dell'applicazione."""

    OUTPUT_DIR = "output"
    UPLOADS_DIR = "uploads"
    MUSIC_LIBRARY_DIR = "uploads/library"
    VOICES_DIR = "voices"
    DATABASE_FILE = "text_history.db"
    UPDATE_PROGRESS_FILE = "update_progress.json"

    @classmethod
    def ensure_directories_exist(cls) -> None:
        """Crea le directory necessarie se non esistono."""
        directories = [
            cls.OUTPUT_DIR,
            cls.UPLOADS_DIR,
            cls.MUSIC_LIBRARY_DIR,
            cls.VOICES_DIR
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


class ApplicationConfiguration:
    """
    Configurazione principale dell'applicazione.

    Centralizza tutte le configurazioni necessarie per il funzionamento
    del sistema TTS.
    """

    def __init__(self):
        self.azure = AzureConfiguration()
        self.network = NetworkConfiguration()
        self.audio_quality = AudioQualityConfiguration()
        self.paths = FilePathConfiguration()

    def initialize(self) -> None:
        """
        Inizializza l'applicazione verificando e preparando
        tutte le configurazioni necessarie.
        """
        self.azure.log_status()
        self.network.log_status()
        self.paths.ensure_directories_exist()

    def is_ready(self) -> bool:
        """
        Verifica se l'applicazione è pronta per l'esecuzione.

        Returns:
            True se tutte le configurazioni critiche sono presenti
        """
        return self.azure.is_configured()
