/**
 * Configurazione API URL con rilevamento automatico
 */

export const getApiUrl = () => {
  // Se specificato come variabile d'ambiente, usa quello
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // Rileva automaticamente l'IP giusto da usare
  const currentHost = window.location.hostname;
  
  // Se stiamo accedendo tramite localhost, usa localhost
  if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  
  // Se stiamo accedendo tramite un IP di rete, usa lo stesso IP
  return `http://${currentHost}:8000`;
};

export const API_URL = getApiUrl();

// Log per debugging
if (process.env.NODE_ENV === 'development') {
  console.log('🌐 [API Config] URL backend rilevato:', API_URL);
  console.log('🖥️ [API Config] Host corrente:', window.location.hostname);
}
