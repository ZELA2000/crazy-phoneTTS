import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from '../utils/apiConfig';
import { useWebSocket } from './useWebSocket';

/**
 * Hook per gestione cronologia testi con WebSocket
 */

export const useTextHistory = () => {
  const [textHistory, setTextHistory] = useState([]);

  const handleWebSocketMessage = (message) => {
    if (message.type === 'history_update') {
      setTextHistory(message.data);
    } else if (message.type === 'new_text') {
      // Evita duplicati verificando se l'ID esiste già
      setTextHistory(prev => {
        const exists = prev.some(item => item.id === message.data.id);
        if (exists) {
          return prev; // Non aggiungere se esiste già
        }
        return [message.data, ...prev.slice(0, 9)];
      });
    }
  };

  const wsUrl = API_URL.replace('http', 'ws') + '/ws';
  const { isConnected } = useWebSocket(wsUrl, handleWebSocketMessage);

  useEffect(() => {
    loadTextHistory();
  }, []);

  const loadTextHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/history`);
      setTextHistory(response.data.data || []);
      console.log('📜 [History] Cronologia caricata:', response.data.data.length, 'elementi');
    } catch (err) {
      console.error('❌ [History] Errore caricamento cronologia:', err.message || err);
    }
  };

  return {
    textHistory,
    isConnected,
    loadTextHistory
  };
};
