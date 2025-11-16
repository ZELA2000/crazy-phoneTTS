"""
Gestione delle versioni e controllo aggiornamenti da GitHub.

Questo modulo gestisce il versioning dell'applicazione, il confronto
delle versioni e il controllo dei nuovi rilasci su GitHub.
"""

import os
import logging
import requests
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class VersionManager:
    """
    Gestisce le versioni dell'applicazione e gli aggiornamenti.

    Permette di leggere la versione corrente, confrontarla con le
    release disponibili su GitHub e determinare se sono disponibili
    aggiornamenti.
    """

    def __init__(
        self,
        version_file: str = "VERSION",
        github_repo: str = "ZELA2000/crazy-phoneTTS"
    ):
        """
        Inizializza il gestore delle versioni.

        Args:
            version_file: Percorso del file contenente la versione
            github_repo: Repository GitHub nel formato 'owner/repo'
        """
        self.version_file = version_file
        self.github_repo = github_repo
        self.github_api_url = f"https://api.github.com/repos/{github_repo}/releases/latest"

    def get_current_version(self) -> str:
        """
        Legge la versione corrente dal file VERSION.

        Returns:
            Stringa con la versione corrente (es. "1.2.3")
        """
        # Tentativi di percorsi per trovare il file VERSION
        possible_paths = [
            self.version_file,
            f"/app/{self.version_file}",
            f"../{self.version_file}",
            f"/app/backend/{self.version_file}"
        ]

        for path in possible_paths:
            try:
                with open(path, 'r') as file:
                    version = file.read().strip()

                logger.info(f"Versione corrente: {version} (letta da {path})")
                return version
            except FileNotFoundError:
                continue
            except Exception as error:
                logger.error(f"Errore lettura versione da {path}: {error}")
                continue

        logger.warning(
            f"File versione non trovato in nessuno dei percorsi: {possible_paths}")
        return "0.0.0"

    def check_github_releases(self) -> Optional[Dict]:
        """
        Controlla l'ultima release disponibile su GitHub.

        Returns:
            Dizionario con le informazioni della release, None se non disponibile
        """
        try:
            response = requests.get(self.github_api_url, timeout=10)

            if response.status_code == 200:
                release_data = response.json()

                latest_version = release_data.get("tag_name", "").lstrip("v")

                logger.info(f"Ultima versione GitHub: {latest_version}")

                return {
                    "version": latest_version,
                    "name": release_data.get("name", ""),
                    "body": release_data.get("body", ""),
                    "published_at": release_data.get("published_at", ""),
                    "html_url": release_data.get("html_url", "")
                }
            else:
                logger.warning(
                    f"GitHub API risposta non valida: {response.status_code}"
                )
                return None
        except requests.exceptions.Timeout:
            logger.error("Timeout controllo aggiornamenti GitHub")
            return None
        except requests.exceptions.RequestException as error:
            logger.error(f"Errore connessione GitHub API: {error}")
            return None
        except Exception as error:
            logger.error(f"Errore generico controllo GitHub: {error}")
            return None

    def compare_versions(self, version1: str, version2: str) -> int:
        """
        Confronta due versioni in formato semver.

        Args:
            version1: Prima versione (es. "1.2.3")
            version2: Seconda versione (es. "1.3.0")

        Returns:
            -1 se version1 < version2
             0 se version1 == version2
             1 se version1 > version2
        """
        try:
            # Rimuove prefissi comuni come 'v', 'V', 'version'
            v1 = version1.lower().strip()
            v2 = version2.lower().strip()

            for prefix in ['version', 'v']:
                if v1.startswith(prefix):
                    v1 = v1[len(prefix):].strip()
                if v2.startswith(prefix):
                    v2 = v2[len(prefix):].strip()

            # Estrae solo la parte numerica (major.minor.patch)
            import re
            match1 = re.match(r'^(\d+)\.(\d+)\.(\d+)', v1)
            match2 = re.match(r'^(\d+)\.(\d+)\.(\d+)', v2)

            # Se una delle versioni non ha formato semver, usa confronto stringa
            if not match1 or not match2:
                logger.warning(
                    f"Versione non in formato semver: {version1} vs {version2}, confronto lessicografico")
                if v1 < v2:
                    return -1
                elif v1 > v2:
                    return 1
                else:
                    return 0

            parts1 = [int(match1.group(i)) for i in range(1, 4)]
            parts2 = [int(match2.group(i)) for i in range(1, 4)]

            # Confronta parte per parte
            for p1, p2 in zip(parts1, parts2):
                if p1 < p2:
                    return -1
                elif p1 > p2:
                    return 1

            return 0
        except Exception as error:
            logger.error(f"Errore confronto versioni: {error}")
            return 0

    def is_update_available(self) -> Dict:
        """
        Verifica se è disponibile un aggiornamento.

        Returns:
            Dizionario con informazioni sull'aggiornamento disponibile
        """
        current_version = self.get_current_version()
        github_release = self.check_github_releases()

        if not github_release:
            return {
                "available": False,
                "current_version": current_version,
                "message": "Impossibile verificare aggiornamenti"
            }

        latest_version = github_release["version"]

        # Se le versioni sono diverse, è disponibile un aggiornamento
        if current_version != latest_version:
            return {
                "available": True,
                "current_version": current_version,
                "latest_version": latest_version,
                "release_info": github_release,
                "message": f"Aggiornamento disponibile: {latest_version}"
            }
        else:
            return {
                "available": False,
                "current_version": current_version,
                "latest_version": latest_version,
                "message": "Software aggiornato"
            }
