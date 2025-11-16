"""
Gestione della libreria musicale per mixaggio audio.

Questo modulo fornisce funzionalità per caricare, elencare e gestire
i file musicali utilizzati come sottofondo per gli audio TTS.
"""

import os
import json
import uuid
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pydub import AudioSegment

logger = logging.getLogger(__name__)


class MusicLibrary:
    """
    Gestisce la libreria di file musicali.

    Permette di caricare file audio, salvare metadata, elencare
    le canzoni disponibili e rimuoverle quando necessario.
    """

    SUPPORTED_FORMATS = [
        # Formati compressi comuni
        'audio/mp3', 'audio/mpeg',          # MP3
        'audio/mp4', 'audio/m4a',           # M4A/AAC
        'audio/ogg', 'audio/vorbis',        # OGG Vorbis
        'audio/opus',                        # Opus
        'audio/webm',                        # WebM
        'audio/flac',                        # FLAC (lossless)
        'audio/aac', 'audio/aacp',          # AAC
        'audio/vnd.dlna.adts',              # AAC ADTS
        'audio/x-m4a',                       # M4A alternativo
        'audio/wma',                         # Windows Media Audio

        # Formati non compressi
        'audio/wav', 'audio/wave', 'audio/x-wav',  # WAV
        'audio/aiff', 'audio/x-aiff',       # AIFF
        'audio/pcm',                         # PCM raw

        # Altri formati
        'audio/3gpp', 'audio/3gpp2',        # 3GP
        'audio/amr',                         # AMR
        'audio/basic',                       # AU/SND
        'audio/x-ms-wma',                    # WMA alternativo

        # MIME types generici
        'application/ogg',                   # OGG container
        'application/octet-stream',          # Generico
        'audio/*'                            # Accetta qualsiasi audio
    ]

    def __init__(self, library_directory: str = "uploads/library"):
        """
        Inizializza la libreria musicale.

        Args:
            library_directory: Directory dove salvare i file musicali
        """
        self.library_directory = library_directory
        os.makedirs(library_directory, exist_ok=True)

    def add_song(
        self,
        name: str,
        file_content: bytes,
        filename: str,
        content_type: str
    ) -> Dict:
        """
        Aggiunge una canzone alla libreria.

        Args:
            name: Nome descrittivo della canzone
            file_content: Contenuto binario del file
            filename: Nome originale del file
            content_type: Tipo MIME del file

        Returns:
            Dizionario con i metadata della canzone

        Raises:
            ValueError: Se il formato del file non è supportato
        """
        # Accetta qualsiasi tipo MIME che inizia con 'audio/' o è nella lista
        is_audio = content_type.startswith(
            'audio/') or content_type.startswith('application/ogg')
        is_in_list = content_type in self.SUPPORTED_FORMATS

        if not (is_audio or is_in_list):
            raise ValueError(
                f"Formato non supportato: {content_type}. "
                f"Deve essere un file audio."
            )

        # Genera ID univoco
        song_id = str(uuid.uuid4())
        extension = os.path.splitext(filename)[1]
        file_path = os.path.join(
            self.library_directory, f"{song_id}{extension}")

        # Salva file
        with open(file_path, 'wb') as file:
            file.write(file_content)

        # Ottieni durata audio
        duration_seconds = self._get_audio_duration(file_path)

        # Crea metadata
        metadata = {
            "id": song_id,
            "name": name,
            "filename": filename,
            "file_path": file_path,
            "duration_seconds": duration_seconds,
            "uploaded_at": datetime.now().isoformat(),
            "size_bytes": os.path.getsize(file_path)
        }

        # Salva metadata
        self._save_metadata(song_id, metadata)

        logger.info(f"Canzone aggiunta alla libreria: {name} ({song_id})")
        return metadata

    def list_songs(self) -> List[Dict]:
        """
        Elenca tutte le canzoni nella libreria.

        Returns:
            Lista di dizionari con i metadata delle canzoni
        """
        songs = []

        if not os.path.exists(self.library_directory):
            return songs

        for filename in os.listdir(self.library_directory):
            if not filename.endswith('.json'):
                continue

            metadata_path = os.path.join(self.library_directory, filename)

            try:
                with open(metadata_path, 'r', encoding='utf-8') as file:
                    metadata = json.load(file)

                # Verifica che il file audio esista ancora
                if os.path.exists(metadata["file_path"]):
                    songs.append(metadata)
            except Exception as error:
                logger.warning(f"Errore lettura metadata {filename}: {error}")

        # Ordina per data di upload (più recenti prima)
        songs.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)

        return songs

    def get_song(self, song_id: str) -> Optional[Dict]:
        """
        Recupera i metadata di una canzone specifica.

        Args:
            song_id: ID univoco della canzone

        Returns:
            Dizionario con i metadata, None se non trovata
        """
        metadata_path = os.path.join(self.library_directory, f"{song_id}.json")

        if not os.path.exists(metadata_path):
            return None

        try:
            with open(metadata_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as error:
            logger.error(f"Errore lettura metadata canzone {song_id}: {error}")
            return None

    def delete_song(self, song_id: str) -> bool:
        """
        Elimina una canzone dalla libreria.

        Args:
            song_id: ID univoco della canzone da eliminare

        Returns:
            True se eliminata con successo, False altrimenti
        """
        metadata = self.get_song(song_id)

        if not metadata:
            logger.warning(f"Canzone non trovata: {song_id}")
            return False

        try:
            # Elimina file audio
            if os.path.exists(metadata["file_path"]):
                os.remove(metadata["file_path"])

            # Elimina metadata
            metadata_path = os.path.join(
                self.library_directory,
                f"{song_id}.json"
            )
            if os.path.exists(metadata_path):
                os.remove(metadata_path)

            logger.info(f"Canzone eliminata: {metadata['name']} ({song_id})")
            return True
        except Exception as error:
            logger.error(f"Errore eliminazione canzone {song_id}: {error}")
            return False

    def _get_audio_duration(self, file_path: str) -> float:
        """
        Calcola la durata del file audio.

        Args:
            file_path: Percorso del file audio

        Returns:
            Durata in secondi, 0 se non determinabile
        """
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0  # Converti da ms a secondi
        except Exception as error:
            logger.warning(f"Impossibile determinare durata audio: {error}")
            return 0.0

    def _save_metadata(self, song_id: str, metadata: Dict) -> None:
        """
        Salva i metadata di una canzone.

        Args:
            song_id: ID univoco della canzone
            metadata: Dizionario con i metadata da salvare
        """
        metadata_path = os.path.join(
            self.library_directory,
            f"{song_id}.json"
        )

        with open(metadata_path, 'w', encoding='utf-8') as file:
            json.dump(metadata, file, ensure_ascii=False, indent=2)
