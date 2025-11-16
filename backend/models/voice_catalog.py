"""
Catalogo delle voci neurali Azure disponibili.

Questo modulo contiene il database delle voci italiane supportate
da Azure Speech Services, con informazioni su stili, generi e
caratteristiche vocali.
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class VoiceInfo:
    """Informazioni su una voce neurale Azure."""

    short_name: str
    display_name: str
    gender: str
    styles: List[str]
    description: str = ""


class VoiceCatalog:
    """
    Catalogo completo delle voci neurali italiane Azure.

    Fornisce metodi per elencare le voci disponibili, filtrare
    per genere o stile, e ottenere informazioni dettagliate.
    """

    # Catalogo completo voci italiane
    ITALIAN_VOICES = {
        "it-IT-ElsaNeural": VoiceInfo(
            short_name="it-IT-ElsaNeural",
            display_name="Elsa",
            gender="Female",
            styles=["general"],
            description="Voce femminile neurale standard italiana"
        ),
        "it-IT-IsabellaNeural": VoiceInfo(
            short_name="it-IT-IsabellaNeural",
            display_name="Isabella",
            gender="Female",
            styles=["general"],
            description="Voce femminile neurale italiana con tono naturale"
        ),
        "it-IT-DiegoNeural": VoiceInfo(
            short_name="it-IT-DiegoNeural",
            display_name="Diego",
            gender="Male",
            styles=["general"],
            description="Voce maschile neurale standard italiana"
        ),
        "it-IT-BenignoNeural": VoiceInfo(
            short_name="it-IT-BenignoNeural",
            display_name="Benigno",
            gender="Male",
            styles=["general"],
            description="Voce maschile neurale italiana con tono cordiale"
        ),
        "it-IT-CalimeroNeural": VoiceInfo(
            short_name="it-IT-CalimeroNeural",
            display_name="Calimero",
            gender="Male",
            styles=["general"],
            description="Voce maschile neurale italiana giovane"
        ),
        "it-IT-CataldoNeural": VoiceInfo(
            short_name="it-IT-CataldoNeural",
            display_name="Cataldo",
            gender="Male",
            styles=["general"],
            description="Voce maschile neurale italiana matura"
        ),
        "it-IT-FabiolaNeural": VoiceInfo(
            short_name="it-IT-FabiolaNeural",
            display_name="Fabiola",
            gender="Female",
            styles=["general"],
            description="Voce femminile neurale italiana professionale"
        ),
        "it-IT-FiammaNeural": VoiceInfo(
            short_name="it-IT-FiammaNeural",
            display_name="Fiamma",
            gender="Female",
            styles=["general"],
            description="Voce femminile neurale italiana energica"
        ),
        "it-IT-GianniNeural": VoiceInfo(
            short_name="it-IT-GianniNeural",
            display_name="Gianni",
            gender="Male",
            styles=["general"],
            description="Voce maschile neurale italiana versatile"
        ),
        "it-IT-ImeldaNeural": VoiceInfo(
            short_name="it-IT-ImeldaNeural",
            display_name="Imelda",
            gender="Female",
            styles=["general"],
            description="Voce femminile neurale italiana calda"
        ),
        "it-IT-IrmaNeural": VoiceInfo(
            short_name="it-IT-IrmaNeural",
            display_name="Irma",
            gender="Female",
            styles=["general"],
            description="Voce femminile neurale italiana chiara"
        ),
        "it-IT-LisandroNeural": VoiceInfo(
            short_name="it-IT-LisandroNeural",
            display_name="Lisandro",
            gender="Male",
            styles=["general"],
            description="Voce maschile neurale italiana decisa"
        ),
        "it-IT-PalmiraNeural": VoiceInfo(
            short_name="it-IT-PalmiraNeural",
            display_name="Palmira",
            gender="Female",
            styles=["general"],
            description="Voce femminile neurale italiana elegante"
        ),
        "it-IT-PierinaNeural": VoiceInfo(
            short_name="it-IT-PierinaNeural",
            display_name="Pierina",
            gender="Female",
            styles=["general"],
            description="Voce femminile neurale italiana dolce"
        ),
        "it-IT-RinaldoNeural": VoiceInfo(
            short_name="it-IT-RinaldoNeural",
            display_name="Rinaldo",
            gender="Male",
            styles=["general"],
            description="Voce maschile neurale italiana autorevole"
        ),
        "it-IT-GiuseppeNeural": VoiceInfo(
            short_name="it-IT-GiuseppeNeural",
            display_name="Giuseppe",
            gender="Male",
            styles=[
                "cheerful", "chat", "customerservice", "newscast",
                "angry", "calm", "fearful", "sad", "serious", "general"
            ],
            description="Voce maschile multi-stile con supporto espressivo completo"
        )
    }

    def __init__(self):
        """Inizializza il catalogo voci."""
        logger.info(
            f"Catalogo voci inizializzato con {len(self.ITALIAN_VOICES)} voci")

    def get_all_voices(self) -> List[Dict]:
        """
        Restituisce tutte le voci disponibili.

        Returns:
            Lista di dizionari con informazioni sulle voci
        """
        return [
            {
                "short_name": voice.short_name,
                "display_name": voice.display_name,
                "gender": voice.gender,
                "styles": voice.styles,
                "description": voice.description
            }
            for voice in self.ITALIAN_VOICES.values()
        ]

    def get_voices_dict(self) -> Dict[str, str]:
        """
        Restituisce le voci in formato dizionario {voice_id: display_name}.
        Compatibile con il formato di Edge TTS.

        Returns:
            Dizionario {short_name: display_name}
        """
        return {
            voice.short_name: f"{voice.display_name} ({voice.gender}, Italiano)"
            for voice in self.ITALIAN_VOICES.values()
        }

    def get_voice(self, short_name: str) -> Optional[Dict]:
        """
        Ottiene le informazioni di una voce specifica.

        Args:
            short_name: Nome breve della voce (es. "it-IT-ElsaNeural")

        Returns:
            Dizionario con le informazioni della voce, None se non trovata
        """
        voice = self.ITALIAN_VOICES.get(short_name)

        if not voice:
            return None

        return {
            "short_name": voice.short_name,
            "display_name": voice.display_name,
            "gender": voice.gender,
            "styles": voice.styles,
            "description": voice.description
        }

    def filter_by_gender(self, gender: str) -> List[Dict]:
        """
        Filtra le voci per genere.

        Args:
            gender: Genere da filtrare ("Male" o "Female")

        Returns:
            Lista di voci che corrispondono al genere
        """
        return [
            {
                "short_name": voice.short_name,
                "display_name": voice.display_name,
                "gender": voice.gender,
                "styles": voice.styles,
                "description": voice.description
            }
            for voice in self.ITALIAN_VOICES.values()
            if voice.gender.lower() == gender.lower()
        ]

    def filter_by_style(self, style: str) -> List[Dict]:
        """
        Filtra le voci che supportano uno stile specifico.

        Args:
            style: Stile vocale richiesto (es. "cheerful", "calm")

        Returns:
            Lista di voci che supportano lo stile
        """
        return [
            {
                "short_name": voice.short_name,
                "display_name": voice.display_name,
                "gender": voice.gender,
                "styles": voice.styles,
                "description": voice.description
            }
            for voice in self.ITALIAN_VOICES.values()
            if style.lower() in [s.lower() for s in voice.styles]
        ]

    def get_available_styles(self) -> List[str]:
        """
        Restituisce tutti gli stili vocali disponibili.

        Returns:
            Lista di stili unici disponibili nel catalogo
        """
        all_styles = set()

        for voice in self.ITALIAN_VOICES.values():
            all_styles.update(voice.styles)

        return sorted(list(all_styles))

    def get_multistyle_voices(self) -> List[Dict]:
        """
        Restituisce solo le voci con supporto multi-stile.

        Returns:
            Lista di voci che supportano più di uno stile
        """
        return [
            {
                "short_name": voice.short_name,
                "display_name": voice.display_name,
                "gender": voice.gender,
                "styles": voice.styles,
                "description": voice.description
            }
            for voice in self.ITALIAN_VOICES.values()
            if len(voice.styles) > 1
        ]

    def validate_voice_style_combination(
        self,
        voice_name: str,
        style: str
    ) -> bool:
        """
        Verifica se una combinazione voce-stile è valida.

        Args:
            voice_name: Nome della voce
            style: Stile richiesto

        Returns:
            True se la combinazione è valida, False altrimenti
        """
        voice = self.ITALIAN_VOICES.get(voice_name)

        if not voice:
            return False

        return style.lower() in [s.lower() for s in voice.styles]
