"""
Services - Servizi di integrazione con sistemi esterni.
"""

from .azure_speech import (
    AzureSpeechService,
    SSMLGenerator,
    SSMLParameters,
    VoiceStyle
)

__all__ = [
    "AzureSpeechService",
    "SSMLGenerator",
    "SSMLParameters",
    "VoiceStyle"
]
