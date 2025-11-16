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
      setTextHistory(prev => [message.data, ...prev.slice(0, 9)]);
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
      console.log('Cronologia caricata:', response.data.data);
    } catch (err) {
      console.error('Errore caricamento cronologia:', err);
    }
  };

  return {
    textHistory,
    isConnected,
    loadTextHistory
  };
};
