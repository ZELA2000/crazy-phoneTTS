import { useState, useEffect, useRef } from 'react';

/**
 * Hook per gestione connessione WebSocket con riconnessione automatica
 */

export const useWebSocket = (url, onMessage) => {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    connect();
    
    return () => {
      cleanup();
    };
  }, [url]);

  const connect = () => {
    try {
      console.log('🔌 [WebSocket] Inizializzazione connessione a:', url);
      
      wsRef.current = new WebSocket(url);
      
      wsRef.current.onopen = () => {
        console.log('✅ [WebSocket] Connessione stabilita con successo');
        setIsConnected(true);
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('📨 [WebSocket] Messaggio ricevuto:', {
            tipo: message.type || 'unknown',
            dati: message
          });
          onMessage(message);
        } catch (err) {
          console.error('❌ [WebSocket] Errore parsing messaggio:', err.message, '| Raw:', event.data);
        }
      };
      
      wsRef.current.onclose = () => {
        console.log('🔌 [WebSocket] Connessione chiusa');
        setIsConnected(false);
        
        // Riconnetti dopo 3 secondi
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };
      
      wsRef.current.onerror = (error) => {
        console.error('❌ [WebSocket] Errore di connessione:', error.message || error);
        setIsConnected(false);
      };
    } catch (err) {
      console.error('❌ [WebSocket] Errore inizializzazione:', err.message || err);
    }
  };

  const cleanup = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
    }
  };

  const send = (data) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn('⚠️ [WebSocket] Impossibile inviare messaggio: connessione non stabilita');
    }
  };

  return {
    isConnected,
    send,
    reconnect: connect
  };
};
