"""
Gestione delle connessioni WebSocket per comunicazione real-time.

Questo modulo fornisce gestori per le connessioni WebSocket utilizzate
per aggiornamenti in tempo reale della cronologia e del progresso degli
aggiornamenti di sistema.
"""

import json
import logging
from typing import List
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketConnectionManager:
    """
    Gestisce un pool di connessioni WebSocket attive.

    Permette di inviare messaggi broadcast a tutti i client connessi
    e gestisce automaticamente la pulizia delle connessioni interrotte.
    """

    def __init__(self):
        """Inizializza il gestore con una lista vuota di connessioni."""
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accetta e registra una nuova connessione WebSocket.

        Args:
            websocket: Oggetto WebSocket da connettere
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            f"Nuova connessione WebSocket. Totale: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Rimuove una connessione WebSocket dalla lista attiva.

        Args:
            websocket: Oggetto WebSocket da disconnettere
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(
            f"Connessione WebSocket chiusa. Totale: {len(self.active_connections)}"
        )

    async def broadcast(self, message: dict) -> None:
        """
        Invia un messaggio a tutti i client connessi.

        Gestisce automaticamente la rimozione delle connessioni interrotte
        durante l'invio del messaggio.

        Args:
            message: Dizionario da inviare come JSON a tutti i client
        """
        if not self.active_connections:
            return

        dead_connections = []
        message_json = json.dumps(message)

        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as error:
                logger.warning(f"Errore invio messaggio WebSocket: {error}")
                dead_connections.append(connection)

        for dead_connection in dead_connections:
            self.disconnect(dead_connection)

    def get_connection_count(self) -> int:
        """
        Restituisce il numero di connessioni attive.

        Returns:
            Numero di connessioni WebSocket attive
        """
        return len(self.active_connections)


class HistoryUpdateManager(WebSocketConnectionManager):
    """
    Gestore specializzato per aggiornamenti della cronologia testi.

    Estende il gestore base aggiungendo metodi specifici per
    notificare i client di nuove voci nella cronologia.
    """

    async def notify_new_text(
        self,
        entry_id: int,
        text: str,
        voice: str,
        user_ip: str
    ) -> None:
        """
        Notifica tutti i client di un nuovo testo nella cronologia.

        Args:
            entry_id: ID della voce nella cronologia
            text: Testo sintetizzato
            voice: Voce utilizzata
            user_ip: IP dell'utente (già anonimizzato)
        """
        from datetime import datetime

        message = {
            "type": "new_text",
            "data": {
                "id": entry_id,
                "text": text,
                "voice": voice,
                "timestamp": datetime.now().isoformat(),
                "user_ip": user_ip
            }
        }
        await self.broadcast(message)
        logger.info(
            f"Notificato nuovo testo nella cronologia (ID: {entry_id})")

    async def send_history_snapshot(
        self,
        websocket: WebSocket,
        history_data: list
    ) -> None:
        """
        Invia uno snapshot completo della cronologia a un client specifico.

        Utilizzato quando un nuovo client si connette per fornirgli
        lo stato corrente della cronologia.

        Args:
            websocket: WebSocket del client destinatario
            history_data: Lista delle voci della cronologia
        """
        message = {
            "type": "history_update",
            "data": history_data
        }
        try:
            await websocket.send_text(json.dumps(message))
            logger.debug("Snapshot cronologia inviato al nuovo client")
        except Exception as error:
            logger.error(f"Errore invio snapshot cronologia: {error}")


class UpdateProgressManager(WebSocketConnectionManager):
    """
    Gestore specializzato per aggiornamenti del progresso di sistema.

    Utilizzato per comunicare in tempo reale lo stato degli aggiornamenti
    software ai client connessi.
    """

    async def broadcast_progress(self, progress_data: dict) -> None:
        """
        Invia un aggiornamento di progresso a tutti i client.

        Args:
            progress_data: Dizionario contenente i dati del progresso
        """
        await self.broadcast(progress_data)

        step = progress_data.get("step", "unknown")
        percentage = progress_data.get("percentage", 0)
        logger.info(
            f"Progresso aggiornamento broadcast: {step} ({percentage}%)")
