"""
Gestione notifiche aggiornamenti disponibili.

Questo modulo è stato semplificato: il backend controlla solo se è disponibile
una nuova versione su GitHub e notifica l'utente. L'aggiornamento effettivo
deve essere eseguito manualmente sul server usando gli script update.ps1/update.sh.
"""

import logging

logger = logging.getLogger(__name__)


class UpdateNotificationManager:
    """
    Gestisce le notifiche di aggiornamento disponibile.

    Il backend non esegue più aggiornamenti automatici, ma solo:
    - Controlla versione GitHub
    - Notifica se disponibile aggiornamento
    - Fornisce istruzioni per aggiornare manualmente
    """

    def __init__(self):
        """Inizializza il gestore notifiche aggiornamenti."""
        logger.info("Sistema notifiche aggiornamenti inizializzato")

    def get_update_instructions(self, platform: str = "all") -> dict:
        """
        Restituisce le istruzioni per aggiornare manualmente il sistema.

        Args:
            platform: Piattaforma target ("windows", "linux", "mac", "all")

        Returns:
            Dizionario con le istruzioni per piattaforma
        """
        instructions = {
            "windows": {
                "command": ".\\update.ps1",
                "description": "Esegui PowerShell come amministratore e lancia:",
                "steps": [
                    "Apri PowerShell come amministratore",
                    "Naviga nella cartella del progetto",
                    "Esegui: .\\update.ps1",
                    "Attendi il completamento dell'aggiornamento"
                ]
            },
            "linux": {
                "command": "./update.sh",
                "description": "Apri il terminale e lancia:",
                "steps": [
                    "Apri il terminale",
                    "Naviga nella cartella del progetto",
                    "Esegui: chmod +x update.sh (se necessario)",
                    "Esegui: ./update.sh",
                    "Attendi il completamento dell'aggiornamento"
                ]
            },
            "mac": {
                "command": "./update.sh",
                "description": "Apri il terminale e lancia:",
                "steps": [
                    "Apri il terminale",
                    "Naviga nella cartella del progetto",
                    "Esegui: chmod +x update.sh (se necessario)",
                    "Esegui: ./update.sh",
                    "Attendi il completamento dell'aggiornamento"
                ]
            }
        }

        if platform == "all":
            return instructions

        return {platform: instructions.get(platform, instructions["linux"])}
