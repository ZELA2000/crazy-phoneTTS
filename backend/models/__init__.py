"""
Models - Modelli di dati e cataloghi.
"""

from .history import TextHistoryDatabase
from .voice_catalog import VoiceCatalog, VoiceInfo

__all__ = [
    "TextHistoryDatabase",
    "VoiceCatalog",
    "VoiceInfo"
]
