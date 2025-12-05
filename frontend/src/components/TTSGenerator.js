import React, { useState } from 'react';
import axios from 'axios';
import { API_URL } from '../utils/apiConfig';

/**
 * Componente generatore TTS
 */

const TTSGenerator = ({ preferences, audioUrl, setAudioUrl }) => {
  const [text, setText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!text.trim()) {
      setError('Inserisci il testo da convertire');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');
    setAudioUrl('');

    try {
      const formData = new FormData();
      formData.append('text', text);
      formData.append('tts_service', preferences.ttsService);
      formData.append('voice_name', preferences.ttsVoice);
      formData.append('language', 'it');

      // Parametri musicali
      if (preferences.selectedMusic) {
        formData.append('library_song_id', preferences.selectedMusic);
        formData.append('music_volume', preferences.musicVolume.toString());
        formData.append('music_before', preferences.musicBefore.toString());
        formData.append('music_after', preferences.musicAfter.toString());
        formData.append('fade_in', preferences.fadeIn.toString());
        formData.append('fade_out', preferences.fadeOut.toString());
        formData.append('fade_in_duration', preferences.fadeInDuration.toString());
        formData.append('fade_out_duration', preferences.fadeOutDuration.toString());
      }

      // Parametri formato e qualità
      formData.append('output_format', preferences.outputFormat);
      formData.append('audio_quality', preferences.audioQuality);
      formData.append('custom_filename', preferences.fileName.trim() || 'centralino_audio');

      const response = await axios.post(`${API_URL}/generate-audio`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob'
      });

      const mimeType = preferences.outputFormat === 'mp3' ? 'audio/mpeg' : 
                       preferences.outputFormat === 'gsm' ? 'audio/gsm' : 'audio/wav';
      
      const audioBlob = new Blob([response.data], { type: mimeType });
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);
      setSuccess(`Audio generato con successo${preferences.selectedMusic ? ' con musica!' : '!'} (${preferences.outputFormat.toUpperCase()}, ${preferences.audioQuality.toUpperCase()})`);
      
    } catch (err) {
      console.error('❌ [Audio Generation] Errore generazione audio:', {
        servizio: preferences.ttsService,
        voce: preferences.ttsVoice,
        errore: err.response?.data || err.message || err
      });
      setError('Errore durante la generazione dell\'audio');
    } finally {
      setIsLoading(false);
    }
  };

  const downloadAudio = () => {
    if (audioUrl) {
      const a = document.createElement('a');
      a.href = audioUrl;
      const today = new Date();
      const dateStr = today.getFullYear().toString().substr(-2) + 
                     (today.getMonth() + 1).toString().padStart(2, '0') + 
                     today.getDate().toString().padStart(2, '0');
      const cleanFileName = preferences.fileName.trim() || 'centralino_audio';
      a.download = `${cleanFileName}_${dateStr}.${preferences.outputFormat}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  return (
    <>
      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      {/* SEZIONE GENERAZIONE TTS */}
      <div className="form-card">
        <h2>🎙️ Genera Audio</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="text">Testo da convertire in voce:</label>
            <textarea
              id="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Inserisci qui il messaggio per il centralino..."
              maxLength={1000}
              disabled={isLoading}
            />
            <small>{text.length}/1000 caratteri</small>
          </div>

          <button 
            type="submit" 
            className="generate-btn" 
            disabled={isLoading || !text.trim()}
          >
            {isLoading ? (
              <div className="loading">
                <div className="spinner"></div>
                Generazione in corso...
              </div>
            ) : (
              `🚀 Genera Audio${preferences.selectedMusic ? ' con Musica' : ''}`
            )}
          </button>
        </form>
      </div>

      {/* SEZIONE RISULTATO */}
      {audioUrl && (
        <div className="form-card">
          <h3>🎉 Audio Generato</h3>
          <audio controls className="audio-player" src={audioUrl}>
            Il tuo browser non supporta l'elemento audio.
          </audio>
          <br />
          <button onClick={downloadAudio} className="download-btn">
            📥 Scarica Audio
          </button>
        </div>
      )}
    </>
  );
};

export default TTSGenerator;
