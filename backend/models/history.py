"""
Gestione della cronologia dei testi sintetizzati.

Questo modulo fornisce funzionalità per tracciare e recuperare
la cronologia dei testi convertiti in audio tramite il sistema TTS.
"""

import sqlite3
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TextHistoryDatabase:
    """
    Gestisce il database SQLite per la cronologia dei testi.

    Il database traccia tutti i testi convertiti in audio, includendo
    informazioni sulla voce utilizzata e sull'utente che ha effettuato
    la richiesta.
    """

    def __init__(self, database_path: str = "text_history.db"):
        """
        Inizializza il gestore del database.

        Args:
            database_path: Percorso del file database SQLite
        """
        self.database_path = database_path
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Crea le tabelle del database se non esistono."""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS text_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    voice TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_ip TEXT,
                    audio_generated BOOLEAN DEFAULT FALSE
                )
            ''')

            connection.commit()
            connection.close()
            logger.info("Database cronologia inizializzato")
        except Exception as error:
            logger.error(f"Errore inizializzazione database: {error}")
            raise

    def _get_connection(self) -> sqlite3.Connection:
        """
        Crea una connessione al database.

        Returns:
            Oggetto connessione SQLite
        """
        return sqlite3.connect(self.database_path)

    def add_text_entry(
        self,
        text: str,
        voice: str,
        user_ip: Optional[str] = None
    ) -> int:
        """
        Aggiunge un nuovo testo alla cronologia.

        Args:
            text: Il testo sintetizzato
            voice: Identificativo della voce utilizzata
            user_ip: Indirizzo IP dell'utente (opzionale)

        Returns:
            ID del record inserito

        Raises:
            Exception: Se l'inserimento fallisce
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()

            cursor.execute('''
                INSERT INTO text_history (text, voice, user_ip, audio_generated)
                VALUES (?, ?, ?, TRUE)
            ''', (text, voice, user_ip))

            connection.commit()
            entry_id = cursor.lastrowid
            connection.close()

            logger.info(f"Testo aggiunto alla cronologia (ID: {entry_id})")
            return entry_id
        except Exception as error:
            logger.error(f"Errore aggiunta testo alla cronologia: {error}")
            raise

    def get_recent_entries(self, limit: int = 10) -> List[Dict]:
        """
        Recupera le voci più recenti della cronologia.

        Args:
            limit: Numero massimo di voci da recuperare

        Returns:
            Lista di dizionari contenenti i dati delle voci
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()

            cursor.execute('''
                SELECT id, text, voice, timestamp, user_ip
                FROM text_history 
                WHERE audio_generated = TRUE
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))

            rows = cursor.fetchall()
            connection.close()

            return self._format_history_entries(rows)
        except Exception as error:
            logger.error(f"Errore recupero cronologia: {error}")
            return []

    def _format_history_entries(self, rows: List[tuple]) -> List[Dict]:
        """
        Formatta le righe del database in dizionari leggibili.

        Args:
            rows: Righe del database da formattare

        Returns:
            Lista di dizionari con i dati formattati
        """
        entries = []
        for row in rows:
            entry = {
                "id": row[0],
                "text": self._truncate_text(row[1], max_length=100),
                "voice": row[2],
                "timestamp": row[3],
                "user_ip": self._anonymize_ip(row[4])
            }
            entries.append(entry)
        return entries

    @staticmethod
    def _truncate_text(text: str, max_length: int = 100) -> str:
        """
        Tronca il testo se supera la lunghezza massima.

        Args:
            text: Testo da troncare
            max_length: Lunghezza massima

        Returns:
            Testo troncato con ellissi se necessario
        """
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text

    @staticmethod
    def _anonymize_ip(ip_address: Optional[str]) -> str:
        """
        Anonimizza l'indirizzo IP per privacy.

        Mantiene solo gli ultimi 8 caratteri dell'IP per scopi
        di analisi mantenendo la privacy dell'utente.

        Args:
            ip_address: Indirizzo IP da anonimizzare

        Returns:
            IP anonimizzato o "unknown" se non fornito
        """
        if not ip_address:
            return "unknown"
        return ip_address[-8:]
