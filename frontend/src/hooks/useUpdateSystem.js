import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { API_URL } from '../utils/apiConfig';

/**
 * Hook per gestione sistema di aggiornamento
 */

export const useUpdateSystem = () => {
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [updateInfo, setUpdateInfo] = useState(null);
  const [showUpdateDialog, setShowUpdateDialog] = useState(false);
  const [updateProgress, setUpdateProgress] = useState(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const updateWsRef = useRef(null);

  useEffect(() => {
    initializeUpdateSystem();
    
    // Controlla ogni ora per nuovi aggiornamenti
    const interval = setInterval(checkForUpdates, 60 * 60 * 1000);
    
    return () => {
      clearInterval(interval);
      if (updateWsRef.current) {
        updateWsRef.current.close();
      }
    };
  }, []);

  const initializeUpdateSystem = async () => {
    // Controlla se c'è un aggiornamento in corso dal precedente avvio
    try {
      const progressResponse = await axios.get(`${API_URL}/update/progress`, { timeout: 3000 });
      const progress = progressResponse.data;
      
      if (progress.status === 'running') {
        console.log('🔄 Rilevato aggiornamento in corso, riprendo monitoring...');
        setIsUpdating(true);
        setUpdateProgress(progress);
        startProgressPolling();
      } else if (progress.status === 'completed') {
        console.log('🎉 Rilevato aggiornamento completato, pulisco stato...');
        await axios.post(`${API_URL}/update/clear`).catch(() => {});
      }
    } catch (err) {
      console.log('ℹ️ Nessun aggiornamento in corso o backend non raggiungibile');
    }
    
    // Controlla nuovi aggiornamenti disponibili
    checkForUpdates();
  };

  const checkForUpdates = async () => {
    try {
      const response = await axios.get(`${API_URL}/version/check`);
      const data = response.data;
      
      if (data.update_available) {
        setUpdateAvailable(true);
        setUpdateInfo(data);
        setShowUpdateDialog(true);
        console.log('🔄 Aggiornamento disponibile:', data.latest_version);
      } else {
        console.log('✅ Sistema aggiornato alla versione:', data.current_version);
      }
    } catch (error) {
      console.error('❌ Errore controllo aggiornamenti:', error);
    }
  };

  const setupUpdateWebSocket = () => {
    try {
      const wsUrl = API_URL.replace('http', 'ws') + '/ws/update-progress';
      updateWsRef.current = new WebSocket(wsUrl);
      
      updateWsRef.current.onopen = () => {
        console.log('✅ WebSocket aggiornamenti connesso');
      };
      
      updateWsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('📊 Progress WebSocket:', message);
          
          setUpdateProgress(message);
          
          if (message.type === 'error') {
            setIsUpdating(false);
          } else if (message.step === 'completed' || message.status === 'completed') {
            setIsUpdating(false);
            setTimeout(() => {
              window.location.reload();
            }, 2000);
          }
        } catch (err) {
          console.error('❌ Errore parsing messaggio WebSocket:', err);
        }
      };

      updateWsRef.current.onclose = () => {
        console.log('🔌 WebSocket aggiornamenti disconnesso');
      };

      updateWsRef.current.onerror = (error) => {
        console.log('⚠️ Errore WebSocket:', error);
      };
    } catch (error) {
      console.error('❌ Errore setup WebSocket aggiornamenti:', error);
    }
  };

  const startUpdate = async () => {
    try {
      setIsUpdating(true);
      setUpdateProgress({ type: 'progress', message: '🚀 Avvio aggiornamento...', percentage: 0 });
      setShowUpdateDialog(false);
      
      try {
        setupUpdateWebSocket();
      } catch (wsErr) {
        console.log('⚠️ WebSocket non disponibile, uso solo polling');
      }
      
      const response = await axios.post(`${API_URL}/deploy/trigger`);
      console.log('✅ Deploy triggered:', response.data);
      
      if (response.data.status === 'manual_required') {
        setUpdateProgress({
          type: 'info',
          message: `ℹ️ ${response.data.message}`,
          percentage: 10,
          command: response.data.command
        });
      } else if (response.data.status === 'no_update') {
        setUpdateProgress({
          type: 'info',
          message: '✓ Nessun aggiornamento disponibile',
          percentage: 100
        });
        setTimeout(() => setIsUpdating(false), 3000);
        return;
      }
      
      startProgressPolling();
      
    } catch (error) {
      setIsUpdating(false);
      console.error('❌ Errore avvio aggiornamento:', error);
    }
  };

  const cancelUpdate = () => {
    setShowUpdateDialog(false);
    setUpdateAvailable(false);
  };

  const pollUpdateProgress = async () => {
    try {
      const response = await axios.get(`${API_URL}/update/progress`, { timeout: 3000 });
      const progress = response.data;
      
      console.log('📊 Progress persistente:', progress);
      setUpdateProgress(progress);
      
      if (progress.status === 'completed') {
        setIsUpdating(false);
        await axios.post(`${API_URL}/update/clear`).catch(() => {}); 
        setTimeout(() => {
          window.location.reload();
        }, 2000);
        return false;
      } else if (progress.status === 'error') {
        setIsUpdating(false);
        return false;
      } else if (progress.status === 'idle') {
        return false;
      }
      
      return true;
    } catch (error) {
      console.log('🔍 Backend non raggiungibile, continuo polling...');
      return true;
    }
  };

  const startProgressPolling = () => {
    let pollInterval;
    let wsRetryTimeout;
    let backendOnline = false;
    
    const poll = async () => {
      const shouldContinue = await pollUpdateProgress();
      
      if (!shouldContinue) {
        clearInterval(pollInterval);
        return;
      }
      
      if (!backendOnline) {
        try {
          await axios.get(`${API_URL}/health`, { timeout: 2000 });
          backendOnline = true;
          console.log('🔄 Backend rilevato online, tentativo riconnessione WebSocket...');
          
          wsRetryTimeout = setTimeout(() => {
            try {
              setupUpdateWebSocket();
            } catch (err) {
              console.log('⚠️ Riconnessione WebSocket fallita');
            }
          }, 2000);
          
        } catch (err) {
          // Backend ancora offline
        }
      }
    };
    
    poll();
    pollInterval = setInterval(poll, 2000);
    
    return () => {
      clearInterval(pollInterval);
      clearTimeout(wsRetryTimeout);
    };
  };

  return {
    updateAvailable,
    updateInfo,
    showUpdateDialog,
    updateProgress,
    isUpdating,
    setShowUpdateDialog,
    startUpdate,
    cancelUpdate,
    checkForUpdates
  };
};
