import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from '../utils/apiConfig';

/**
 * Componente per selezione servizio TTS e voce
 */

const TTSServiceSelector = ({ selectedService, selectedVoice, onServiceChange, onVoiceChange }) => {
  const [services, setServices] = useState({});
  const [loading, setLoading] = useState(true);
  const [defaultService, setDefaultService] = useState('edge');

  useEffect(() => {
    loadTTSServices();
  }, []);

  const loadTTSServices = async () => {
    try {
      const response = await axios.get(`${API_URL}/tts/services`);
      setServices(response.data.services);
      setDefaultService(response.data.default_service);
      
      // Se non c'è un servizio selezionato, usa il default
      if (!selectedService) {
        onServiceChange(response.data.default_service);
        const defaultVoice = response.data.services[response.data.default_service].default_voice;
        onVoiceChange(defaultVoice);
      }
      
      console.log('Servizi TTS caricati:', response.data);
    } catch (err) {
      console.error('Errore caricamento servizi TTS:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleServiceChange = (service) => {
    const serviceData = services[service];
    
    // Se il servizio non è disponibile, mostra messaggio e non cambiare
    if (!serviceData?.available) {
      alert(`${serviceData?.name || 'Questo servizio'} non è disponibile.\n\n${serviceData?.description || 'Configura le credenziali necessarie.'}`);
      return;
    }
    
    onServiceChange(service);
    // Imposta voce di default per il servizio selezionato
    if (serviceData.default_voice) {
      onVoiceChange(serviceData.default_voice);
    }
  };

  if (loading) {
    return <div className="loading">Caricamento servizi TTS...</div>;
  }

  const currentService = services[selectedService];
  const voices = currentService?.voices || {};

  return (
    <div className="form-card">
      <h2>🎤 Servizio TTS e Voce</h2>
      
      {/* Selezione Servizio */}
      <div className="form-group">
        <label htmlFor="tts-service">Servizio TTS:</label>
        <select
          id="tts-service"
          value={selectedService || defaultService}
          onChange={(e) => handleServiceChange(e.target.value)}
          className="select-field"
        >
          {Object.entries(services).map(([key, service]) => (
            <option key={key} value={key} disabled={!service.available}>
              {service.name} {!service.available && '(Non disponibile)'}
            </option>
          ))}
        </select>
        {currentService && (
          <small style={{ display: 'block', marginTop: '8px', color: currentService.available ? '#666' : '#d32f2f' }}>
            {currentService.description}
            {selectedService === 'edge' && currentService.available && ' 🆓'}
            {selectedService === 'azure' && currentService.available && ' ⭐ Premium'}
          </small>
        )}
      </div>

      {/* Selezione Voce */}
      <div className="form-group">
        <label htmlFor="voice-select">Voce:</label>
        <select
          id="voice-select"
          value={selectedVoice}
          onChange={(e) => onVoiceChange(e.target.value)}
          className="select-field"
        >
          {Object.entries(voices).map(([voiceId, voiceName]) => (
            <option key={voiceId} value={voiceId}>
              {voiceName}
            </option>
          ))}
        </select>
        <small>
          {Object.keys(voices).length} voci italiane disponibili
        </small>
      </div>

      {/* Info servizio */}
      {selectedService === 'edge' && (
        <div className="info-box" style={{ 
          marginTop: '16px', 
          padding: '12px', 
          backgroundColor: '#e8f5e9', 
          borderRadius: '8px',
          border: '1px solid #4caf50'
        }}>
          <strong>✅ Servizio Gratuito</strong>
          <p style={{ margin: '8px 0 0 0', fontSize: '14px' }}>
            Edge TTS non richiede API key ed è sempre disponibile
          </p>
        </div>
      )}
      
      {selectedService === 'azure' && currentService?.available && (
        <div className="info-box" style={{ 
          marginTop: '16px', 
          padding: '12px', 
          backgroundColor: '#e3f2fd', 
          borderRadius: '8px',
          border: '1px solid #2196f3'
        }}>
          <strong>⭐ Servizio Premium</strong>
          <p style={{ margin: '8px 0 0 0', fontSize: '14px' }}>
            Azure Speech Services offre voci neurali di qualità superiore con stili vocali personalizzabili
          </p>
        </div>
      )}
      
      {selectedService === 'azure' && !currentService?.available && (
        <div className="info-box" style={{ 
          marginTop: '16px', 
          padding: '12px', 
          backgroundColor: '#fff3e0', 
          borderRadius: '8px',
          border: '1px solid #ff9800'
        }}>
          <strong>⚠️ API Key Non Configurata</strong>
          <p style={{ margin: '8px 0 0 0', fontSize: '14px' }}>
            Per usare Azure Speech Services, configura AZURE_SPEECH_KEY nel file .env
          </p>
        </div>
      )}
    </div>
  );
};

export default TTSServiceSelector;
