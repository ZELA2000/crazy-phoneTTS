"""
Servizio di sintesi vocale utilizzando Azure Speech Services.

Questo modulo fornisce un'interfaccia di alto livello per la generazione
di audio TTS tramite Azure Speech Services, supportando voci neurali italiane
e controlli avanzati tramite SSML.
"""

import os
import html
import logging
from typing import Dict, Optional, Any
import azure.cognitiveservices.speech as speechsdk

logger = logging.getLogger(__name__)


class VoiceStyle:
    """
    Definisce gli stili disponibili per le voci neurali.

    Gli stili permettono di modulare il tono emotivo e lo stile
    di presentazione della voce sintetizzata.
    """

    CUSTOMER_SERVICE = "customerservice"
    NEWSCAST = "newscast"
    ASSISTANT = "assistant"
    CHAT = "chat"
    CHEERFUL = "cheerful"
    SAD = "sad"
    EXCITED = "excited"
    FRIENDLY = "friendly"


class SSMLParameters:
    """
    Parametri per la generazione di SSML (Speech Synthesis Markup Language).

    SSML permette un controllo fine sulla sintesi vocale, includendo
    velocità, tono, volume e caratteristiche emotive.
    """

    def __init__(
        self,
        rate: str = "medium",
        pitch: str = "medium",
        volume: str = "medium",
        emphasis: Optional[str] = None,
        break_time: Optional[float] = None,
        style: Optional[str] = None,
        style_degree: str = "1.0"
    ):
        """
        Inizializza i parametri SSML.

        Args:
            rate: Velocità di pronuncia (x-slow, slow, medium, fast, x-fast)
            pitch: Altezza del tono (x-low, low, medium, high, x-high)
            volume: Volume di riproduzione (silent, x-soft, soft, medium, loud, x-loud)
            emphasis: Enfasi (strong, moderate, reduced)
            break_time: Pausa in secondi
            style: Stile emotivo (per voci neurali)
            style_degree: Intensità dello stile (0.01-2.0)
        """
        self.rate = rate
        self.pitch = pitch
        self.volume = volume
        self.emphasis = emphasis
        self.break_time = break_time
        self.style = style
        self.style_degree = style_degree


class SSMLGenerator:
    """Genera markup SSML per il controllo avanzato della sintesi vocale."""

    @staticmethod
    def generate(text: str, voice: str, parameters: SSMLParameters) -> str:
        """
        Genera markup SSML completo per la sintesi vocale.

        Args:
            text: Testo da sintetizzare
            voice: Identificativo della voce Azure
            parameters: Parametri SSML per il controllo della sintesi

        Returns:
            Stringa SSML formattata
        """
        escaped_text = html.escape(text)
        is_neural = "Neural" in voice

        ssml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="it-IT">'
        ]

        ssml_parts.extend(
            SSMLGenerator._generate_voice_tags(voice, parameters, is_neural)
        )
        ssml_parts.extend(
            SSMLGenerator._generate_prosody_tags(parameters)
        )

        if parameters.break_time:
            ssml_parts.append(f'<break time="{parameters.break_time}s"/>')

        if parameters.emphasis:
            ssml_parts.append(
                f'<emphasis level="{parameters.emphasis}">{escaped_text}</emphasis>'
            )
        else:
            ssml_parts.append(escaped_text)

        ssml_parts.extend(SSMLGenerator._close_tags(parameters, is_neural))

        ssml = ''.join(ssml_parts)
        logger.debug(f"SSML generato: {ssml[:200]}...")
        return ssml

    @staticmethod
    def _generate_voice_tags(
        voice: str,
        parameters: SSMLParameters,
        is_neural: bool
    ) -> list:
        """Genera i tag voice con eventuale stile."""
        tags = [f'<voice name="{voice}">']

        if parameters.style and is_neural:
            tags.append(
                f'<mstts:express-as style="{parameters.style}" '
                f'styledegree="{parameters.style_degree}" '
                f'xmlns:mstts="https://www.w3.org/2001/mstts">'
            )

        return tags

    @staticmethod
    def _generate_prosody_tags(parameters: SSMLParameters) -> list:
        """Genera i tag prosody per il controllo di rate, pitch e volume."""
        prosody_attrs = []

        if parameters.rate != 'medium':
            prosody_attrs.append(f'rate="{parameters.rate}"')
        if parameters.pitch != 'medium':
            prosody_attrs.append(f'pitch="{parameters.pitch}"')
        if parameters.volume != 'medium':
            prosody_attrs.append(f'volume="{parameters.volume}"')

        if prosody_attrs:
            return [f'<prosody {" ".join(prosody_attrs)}>']
        return []

    @staticmethod
    def _close_tags(parameters: SSMLParameters, is_neural: bool) -> list:
        """Genera i tag di chiusura nell'ordine corretto."""
        tags = []

        if parameters.rate != 'medium' or parameters.pitch != 'medium' or parameters.volume != 'medium':
            tags.append('</prosody>')

        if parameters.style and is_neural:
            tags.append('</mstts:express-as>')

        tags.append('</voice>')
        tags.append('</speak>')

        return tags


class AzureSpeechService:
    """
    Servizio per la sintesi vocale tramite Azure Speech Services.

    Fornisce metodi per generare audio da testo utilizzando le voci
    neurali italiane di Azure con supporto per SSML avanzato.
    """

    def __init__(self, speech_key: str, speech_region: str, speech_endpoint: Optional[str] = None):
        """
        Inizializza il servizio Azure Speech.

        Args:
            speech_key: Chiave API Azure Speech
            speech_region: Regione Azure (es. westeurope)
            speech_endpoint: Endpoint personalizzato opzionale
        """
        self.speech_key = speech_key
        self.speech_region = speech_region
        self.speech_endpoint = speech_endpoint
        self._voices_cache = None
        self._voices_cache_initialized = False

    def _create_speech_config(self) -> speechsdk.SpeechConfig:
        """
        Crea la configurazione Azure Speech.

        Returns:
            Oggetto SpeechConfig configurato
        """
        if self.speech_endpoint:
            return speechsdk.SpeechConfig(
                subscription=self.speech_key,
                endpoint=self.speech_endpoint
            )
        return speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.speech_region
        )

    async def test_connection(self) -> bool:
        """
        Testa la connessione ad Azure Speech Services.

        Returns:
            True se la connessione ha successo, False altrimenti
        """
        try:
            speech_config = self._create_speech_config()
            speech_config.speech_synthesis_voice_name = "it-IT-ElsaNeural"

            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=None
            )

            result = synthesizer.speak_text_async("Test").get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info("Connessione Azure Speech verificata con successo")
                return True

            self._log_synthesis_error(result)
            return False
        except Exception as error:
            logger.error(f"Errore test connessione Azure Speech: {error}")
            return False

    async def synthesize_to_file(
        self,
        text: str,
        voice: str,
        output_path: str,
        ssml_parameters: Optional[SSMLParameters] = None
    ) -> bool:
        """
        Sintetizza il testo in un file audio.

        Args:
            text: Testo da sintetizzare
            voice: Identificativo della voce Azure
            output_path: Percorso del file di output
            ssml_parameters: Parametri SSML opzionali per controllo avanzato

        Returns:
            True se la sintesi ha successo, False altrimenti
        """
        try:
            speech_config = self._create_speech_config()
            speech_config.speech_synthesis_voice_name = voice

            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config
            )

            if ssml_parameters and self._should_use_ssml(ssml_parameters):
                result = self._synthesize_with_ssml(
                    synthesizer, text, voice, ssml_parameters
                )
            else:
                result = synthesizer.speak_text_async(text).get()

            return self._save_audio_result(result, output_path)
        except Exception as error:
            logger.error(f"Errore sintesi Azure Speech: {error}")
            return False

    @staticmethod
    def _should_use_ssml(parameters: SSMLParameters) -> bool:
        """Determina se è necessario utilizzare SSML."""
        return any([
            parameters.rate != 'medium',
            parameters.pitch != 'medium',
            parameters.volume != 'medium',
            parameters.emphasis,
            parameters.break_time,
            parameters.style
        ])

    def _synthesize_with_ssml(
        self,
        synthesizer: speechsdk.SpeechSynthesizer,
        text: str,
        voice: str,
        parameters: SSMLParameters
    ) -> speechsdk.SpeechSynthesisResult:
        """Esegue la sintesi utilizzando SSML."""
        ssml = SSMLGenerator.generate(text, voice, parameters)
        logger.debug(f"Utilizzo SSML per sintesi avanzata")
        return synthesizer.speak_ssml_async(ssml).get()

    def _save_audio_result(
        self,
        result: speechsdk.SpeechSynthesisResult,
        output_path: str
    ) -> bool:
        """
        Salva il risultato della sintesi su file.

        Args:
            result: Risultato della sintesi Azure
            output_path: Percorso del file di output

        Returns:
            True se il salvataggio ha successo
        """
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            with open(output_path, 'wb') as audio_file:
                audio_file.write(result.audio_data)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(
                    f"Sintesi completata: {os.path.getsize(output_path)} bytes"
                )
                return True

            logger.error("File audio vuoto o non creato")
            return False

        self._log_synthesis_error(result)
        return False

    @staticmethod
    def _log_synthesis_error(result: speechsdk.SpeechSynthesisResult) -> None:
        """Registra informazioni dettagliate su errori di sintesi."""
        if result.reason == speechsdk.ResultReason.Canceled:
            details = speechsdk.CancellationDetails(result)
            logger.error(f"Sintesi annullata: {details.reason}")
            if details.error_details:
                logger.error(f"Dettagli errore: {details.error_details}")
        else:
            logger.error(f"Sintesi fallita: {result.reason}")

    async def get_available_voices(self) -> Dict[str, str]:
        """
        Ottiene le voci italiane disponibili dall'API Azure Speech.

        Returns:
            Dizionario {short_name: display_name}
        """
        if self._voices_cache_initialized:
            return self._voices_cache

        try:
            logger.info("📥 Caricamento voci italiane da Azure Speech API...")

            # Per get_voices usa solo key e region, non endpoint personalizzato
            speech_config = speechsdk.SpeechConfig(
                subscription=self.speech_key,
                region=self.speech_region
            )

            # Crea un synthesizer per ottenere la lista delle voci
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=None
            )

            # Ottieni tutte le voci
            result = synthesizer.get_voices_async().get()

            if result.reason == speechsdk.ResultReason.VoicesListRetrieved:
                # Filtra solo voci italiane neurali
                italian_voices = [
                    v for v in result.voices
                    if v.locale.startswith('it-IT') and 'Neural' in v.short_name
                ]

                # Debug: mostra prima voce
                if italian_voices:
                    logger.info(
                        f"🔍 Prima voce Azure: {italian_voices[0].short_name} - {italian_voices[0].local_name}")

                # Crea dizionario {short_name: display_name}
                self._voices_cache = {
                    voice.short_name: f"{voice.local_name} ({voice.gender.name})"
                    for voice in italian_voices
                }

                self._voices_cache_initialized = True
                logger.info(
                    f"✅ Caricate {len(self._voices_cache)} voci italiane da Azure Speech")

            else:
                logger.error(
                    f"❌ Errore caricamento voci Azure: {result.reason}")
                # Fallback a voci base
                self._voices_cache = {
                    "it-IT-ElsaNeural": "Elsa (Female)",
                    "it-IT-DiegoNeural": "Diego (Male)"
                }
                self._voices_cache_initialized = True

        except Exception as e:
            logger.error(f"❌ Errore caricamento voci Azure Speech: {e}")
            # Fallback a voci base
            self._voices_cache = {
                "it-IT-ElsaNeural": "Elsa (Female)",
                "it-IT-DiegoNeural": "Diego (Male)"
            }
            self._voices_cache_initialized = True

        return self._voices_cache
