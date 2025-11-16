"""
Managers - Gestori per funzionalità complesse e coordinamento.
"""

from .websocket_manager import (
    WebSocketConnectionManager,
    HistoryUpdateManager,
    UpdateProgressManager as WebSocketUpdateProgressManager
)
from .update_manager import UpdateNotificationManager
from .audio_processor import AudioConverter, AudioQualitySpec
from .music_library import MusicLibrary
from .version_manager import VersionManager

__all__ = [
    "WebSocketConnectionManager",
    "HistoryUpdateManager",
    "WebSocketUpdateProgressManager",
    "UpdateNotificationManager",
    "AudioConverter",
    "AudioQualitySpec",
    "MusicLibrary",
    "VersionManager"
]
