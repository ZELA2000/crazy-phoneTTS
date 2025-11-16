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
      console.log('Connessione WebSocket a:', url);
      
      wsRef.current = new WebSocket(url);
      
      wsRef.current.onopen = () => {
        console.log('✅ WebSocket connesso');
        setIsConnected(true);
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('📨 Messaggio WebSocket ricevuto:', message);
          onMessage(message);
        } catch (err) {
          console.error('Errore parsing messaggio WebSocket:', err);
        }
      };
      
      wsRef.current.onclose = () => {
        console.log('❌ WebSocket disconnesso');
        setIsConnected(false);
        
        // Riconnetti dopo 3 secondi
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };
      
      wsRef.current.onerror = (error) => {
        console.error('❌ Errore WebSocket:', error);
        setIsConnected(false);
      };
    } catch (err) {
      console.error('Errore setup WebSocket:', err);
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
      console.warn('WebSocket non connesso, impossibile inviare messaggio');
    }
  };

  return {
    isConnected,
    send,
    reconnect: connect
  };
};
