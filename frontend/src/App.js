import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

// ==========================================
// RILEVAMENTO AUTOMATICO IP PER RETE
// ==========================================

const getApiUrl = () => {
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

const API_URL = getApiUrl();

console.log('🌐 API URL rilevato automaticamente:', API_URL);
console.log('🖥️ Host corrente:', window.location.hostname);

function App() {
  // Stati base
  const [text, setText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [audioUrl, setAudioUrl] = useState('');

  // Stati per cronologia real-time
  const [textHistory, setTextHistory] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [showHistory, setShowHistory] = useState(true);
  const [preferencesSaved, setPreferencesSaved] = useState(false);
  const wsRef = useRef(null);

  // Stati per la libreria musicale
  const [musicLibrary, setMusicLibrary] = useState([]);
  const [selectedMusic, setSelectedMusic] = useState('');
  const [uploadingMusic, setUploadingMusic] = useState(false);

  // Stati per i controlli audio
  const [musicVolume, setMusicVolume] = useState(0.3);
  const [musicBefore, setMusicBefore] = useState(2.0);
  const [musicAfter, setMusicAfter] = useState(2.0);
  const [fadeIn, setFadeIn] = useState(true);
  const [fadeOut, setFadeOut] = useState(true);
  const [fadeInDuration, setFadeInDuration] = useState(1.0);
  const [fadeOutDuration, setFadeOutDuration] = useState(1.0);

  // Stati per formato e qualità output
  const [outputFormat, setOutputFormat] = useState('wav');
  const [audioQuality, setAudioQuality] = useState('pcm');
  const [fileName, setFileName] = useState('centralino_audio');

  // ==========================================
  // SISTEMA SALVATAGGIO PREFERENZE UTENTE
  // ==========================================

  const defaultPreferences = {
    musicVolume: 0.7,
    musicBefore: 2.0,
    musicAfter: 2.0,
    fadeIn: true,
    fadeOut: true,
    fadeInDuration: 1.0,
    fadeOutDuration: 1.0,
    outputFormat: 'wav',
    audioQuality: 'pcm',
    fileName: 'centralino_audio',
    selectedMusic: ''
  };

  const savePreferences = () => {
    const preferences = {
      musicVolume,
      musicBefore,
      musicAfter,
      fadeIn,
      fadeOut,
      fadeInDuration,
      fadeOutDuration,
      outputFormat,
      audioQuality,
      fileName,
      selectedMusic
    };
    
    try {
      localStorage.setItem('crazy-phonetts-preferences', JSON.stringify(preferences));
      console.log('✅ Preferenze salvate:', preferences);
      
      // Mostra indicatore visivo brevemente
      setPreferencesSaved(true);
      setTimeout(() => setPreferencesSaved(false), 2000);
    } catch (err) {
      console.error('❌ Errore salvataggio preferenze:', err);
    }
  };

  const loadPreferences = () => {
    try {
      const saved = localStorage.getItem('crazy-phonetts-preferences');
      if (saved) {
        const preferences = JSON.parse(saved);
        console.log('📖 Caricamento preferenze salvate:', preferences);
        
        // Applica le preferenze salvate
        setMusicVolume(preferences.musicVolume ?? defaultPreferences.musicVolume);
        setMusicBefore(preferences.musicBefore ?? defaultPreferences.musicBefore);
        setMusicAfter(preferences.musicAfter ?? defaultPreferences.musicAfter);
        setFadeIn(preferences.fadeIn ?? defaultPreferences.fadeIn);
        setFadeOut(preferences.fadeOut ?? defaultPreferences.fadeOut);
        setFadeInDuration(preferences.fadeInDuration ?? defaultPreferences.fadeInDuration);
        setFadeOutDuration(preferences.fadeOutDuration ?? defaultPreferences.fadeOutDuration);
        setOutputFormat(preferences.outputFormat ?? defaultPreferences.outputFormat);
        setAudioQuality(preferences.audioQuality ?? defaultPreferences.audioQuality);
        setFileName(preferences.fileName ?? defaultPreferences.fileName);
        setSelectedMusic(preferences.selectedMusic ?? defaultPreferences.selectedMusic);
        
        return true;
      }
      return false;
    } catch (err) {
      console.error('❌ Errore caricamento preferenze:', err);
      return false;
    }
  };

  const resetPreferences = () => {
    try {
      localStorage.removeItem('crazy-phonetts-preferences');
      
      // Ripristina valori default
      setMusicVolume(defaultPreferences.musicVolume);
      setMusicBefore(defaultPreferences.musicBefore);
      setMusicAfter(defaultPreferences.musicAfter);
      setFadeIn(defaultPreferences.fadeIn);
      setFadeOut(defaultPreferences.fadeOut);
      setFadeInDuration(defaultPreferences.fadeInDuration);
      setFadeOutDuration(defaultPreferences.fadeOutDuration);
      setOutputFormat(defaultPreferences.outputFormat);
      setAudioQuality(defaultPreferences.audioQuality);
      setFileName(defaultPreferences.fileName);
      setSelectedMusic(defaultPreferences.selectedMusic);
      
      setSuccess('🔄 Impostazioni ripristinate ai valori di default');
      setTimeout(() => setSuccess(''), 3000);
      
      console.log('🔄 Preferenze ripristinate ai default');
    } catch (err) {
      console.error('❌ Errore reset preferenze:', err);
    }
  };

  // Carica la libreria musicale e preferenze all'avvio
  useEffect(() => {
    // Carica preferenze salvate PRIMA di tutto
    const preferencesLoaded = loadPreferences();
    if (preferencesLoaded) {
      console.log('✅ Preferenze utente caricate dal localStorage');
    } else {
      console.log('ℹ️ Nessuna preferenza salvata, uso valori default');
    }
    
    loadMusicLibrary();
    setupWebSocketConnection();
    loadTextHistory();
    
    // Cleanup WebSocket quando componente viene smontato
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Salva automaticamente le preferenze quando cambiano
  useEffect(() => {
    // Evita di salvare durante il caricamento iniziale
    const timer = setTimeout(() => {
      savePreferences();
    }, 500); // Debounce di 500ms
    
    return () => clearTimeout(timer);
  }, [musicVolume, musicBefore, musicAfter, fadeIn, fadeOut, fadeInDuration, fadeOutDuration, outputFormat, audioQuality, fileName, selectedMusic]);

  const setupWebSocketConnection = () => {
    try {
      const wsUrl = API_URL.replace('http', 'ws') + '/ws';
      console.log('Connessione WebSocket a:', wsUrl);
      
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('✅ WebSocket connesso');
        setIsConnected(true);
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('📨 Messaggio WebSocket ricevuto:', message);
          
          if (message.type === 'history_update') {
            setTextHistory(message.data);
          } else if (message.type === 'new_text') {
            setTextHistory(prev => [message.data, ...prev.slice(0, 9)]); // Mantieni ultimi 10
          }
        } catch (err) {
          console.error('Errore parsing messaggio WebSocket:', err);
        }
      };
      
      wsRef.current.onclose = () => {
        console.log('❌ WebSocket disconnesso');
        setIsConnected(false);
        
        // Riconnetti dopo 3 secondi
        setTimeout(() => {
          setupWebSocketConnection();
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

  const loadTextHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/history`);
      setTextHistory(response.data.data || []);
      console.log('Cronologia caricata:', response.data.data);
    } catch (err) {
      console.error('Errore caricamento cronologia:', err);
    }
  };

  const loadMusicLibrary = async () => {
    try {
      const response = await axios.get(`${API_URL}/music-library/list`);
      setMusicLibrary(response.data.songs || []);
      console.log('Libreria musicale caricata:', response.data.songs);
    } catch (err) {
      console.error('Errore nel caricamento della libreria:', err);
    }
  };

  const uploadMusic = async (file) => {
    if (!file) return;

    // Validazione file
    const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/ogg'];
    if (!allowedTypes.includes(file.type)) {
      setError('Formato file non supportato. Usa MP3, WAV o OGG.');
      return;
    }

    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      setError('File troppo grande. Massimo 50MB.');
      return;
    }

    setUploadingMusic(true);
    setError('');

    try {
      const formData = new FormData();
      // CORREZIONE: Usa 'music_file' come aspetta il backend
      formData.append('music_file', file);
      // Usa il nome del file senza estensione come nome
      const name = file.name.replace(/\.[^/.]+$/, '');
      formData.append('name', name);

      console.log('Uploading file:', file.name, 'with name:', name);

      const response = await axios.post(`${API_URL}/music-library/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      console.log('Upload response:', response.data);
      setSuccess('Musica caricata con successo!');
      await loadMusicLibrary(); // Ricarica la libreria
      
    } catch (err) {
      console.error('Errore upload:', err);
      if (err.response?.data?.detail) {
        setError(`Errore: ${err.response.data.detail}`);
      } else {
        setError('Errore durante il caricamento della musica');
      }
    } finally {
      setUploadingMusic(false);
    }
  };

  const deleteMusic = async (songId) => {
    if (!window.confirm('Sei sicuro di voler eliminare questo file?')) return;

    try {
      await axios.delete(`${API_URL}/music-library/${songId}`);
      setSuccess('Musica eliminata con successo!');
      await loadMusicLibrary();
      
      // Se era selezionata, deseleziona
      if (selectedMusic === songId) {
        setSelectedMusic('');
      }
    } catch (err) {
      console.error('Errore eliminazione:', err);
      setError('Errore durante l\'eliminazione della musica');
    }
  };

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
      formData.append('tts_service', 'azure');
      formData.append('edge_voice', 'it-IT-ElsaNeural');
      formData.append('language', 'it');

      // Aggiungi parametri musicali se selezionata
      if (selectedMusic) {
        formData.append('library_song_id', selectedMusic);
        formData.append('music_volume', musicVolume.toString());
        formData.append('music_before', musicBefore.toString());
        formData.append('music_after', musicAfter.toString());
        formData.append('fade_in', fadeIn.toString());
        formData.append('fade_out', fadeOut.toString());
        formData.append('fade_in_duration', fadeInDuration.toString());
        formData.append('fade_out_duration', fadeOutDuration.toString());
        
        console.log('Parametri musica inviati:', {
          library_song_id: selectedMusic,
          music_volume: musicVolume,
          music_before: musicBefore,
          music_after: musicAfter,
          fade_in: fadeIn,
          fade_out: fadeOut,
          fade_in_duration: fadeInDuration,
          fade_out_duration: fadeOutDuration
        });
      }

      // Aggiungi parametri formato e qualità
      formData.append('output_format', outputFormat);
      formData.append('audio_quality', audioQuality);
      formData.append('custom_filename', fileName.trim() || 'centralino_audio');

      const response = await axios.post(`${API_URL}/generate-audio`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob'
      });

      // Determina il tipo MIME corretto
      const mimeType = outputFormat === 'mp3' ? 'audio/mpeg' : 
                       outputFormat === 'gsm' ? 'audio/gsm' : 'audio/wav';
      
      const audioBlob = new Blob([response.data], { type: mimeType });
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);
      setSuccess(`Audio generato con successo${selectedMusic ? ' con musica!' : '!'} (${outputFormat.toUpperCase()}, ${audioQuality.toUpperCase()})`);
      
    } catch (err) {
      console.error('Errore generazione:', err);
      setError('Errore durante la generazione dell\'audio');
    } finally {
      setIsLoading(false);
    }
  };

  const downloadAudio = () => {
    if (audioUrl) {
      const a = document.createElement('a');
      a.href = audioUrl;
      // Crea nome file: nomepersonalizzato_data.estensione (formato YYMMDD)
      const today = new Date();
      const dateStr = today.getFullYear().toString().substr(-2) + 
                     (today.getMonth() + 1).toString().padStart(2, '0') + 
                     today.getDate().toString().padStart(2, '0');
      const cleanFileName = fileName.trim() || 'centralino_audio';
      a.download = `${cleanFileName}_${dateStr}.${outputFormat}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🎙️ crazy-phoneTTS</h1>
        <p>Sistema Text-to-Speech professionale per centralini telefonici</p>
        <div className="connection-status">
          {isConnected ? (
            <span className="connected">🟢 Live connesso</span>
          ) : (
            <span className="disconnected">🔴 Disconnesso</span>
          )}
          {preferencesSaved && (
            <span className="preferences-saved">💾 Preferenze salvate</span>
          )}
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      {/* SEZIONE CRONOLOGIA LIVE */}
      <div className="form-card">
        <div className="history-header">
          <h2>📜 Cronologia Testi Live</h2>
          <button 
            className="toggle-button"
            onClick={() => setShowHistory(!showHistory)}
          >
            {showHistory ? 'Nascondi' : 'Mostra'}
          </button>
        </div>
        
        {showHistory && (
          <div className="history-container">
            {textHistory.length === 0 ? (
              <p className="no-history">Nessun testo nella cronologia</p>
            ) : (
              <div className="history-list">
                {textHistory.map((item, index) => (
                  <div key={item.id || index} className="history-item">
                    <div className="history-content">
                      <div className="history-text" onClick={() => setText(item.text.replace('...', ''))}>
                        📝 {item.text}
                      </div>
                      <div className="history-meta">
                        🎤 {item.voice} • ⏰ {new Date(item.timestamp).toLocaleString('it-IT', { 
                          hour: '2-digit', 
                          minute: '2-digit',
                          day: '2-digit',
                          month: '2-digit'
                        })} • 👤 {item.user_ip}
                      </div>
                    </div>
                    <button 
                      className="use-text-button"
                      onClick={() => setText(item.text.replace('...', ''))}
                      title="Usa questo testo"
                    >
                      ↩️
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* SEZIONE LIBRERIA MUSICALE */}
      <div className="form-card">
        <h2>🎵 Libreria Musicale</h2>
        
        {/* Upload Musica */}
        <div className="form-group">
          <label htmlFor="music-upload">Carica nuova musica:</label>
          <input
            id="music-upload"
            type="file"
            accept="audio/mp3,audio/wav,audio/ogg"
            onChange={(e) => uploadMusic(e.target.files[0])}
            disabled={uploadingMusic}
          />
          {uploadingMusic && <div className="loading">📤 Caricamento...</div>}
        </div>

        {/* Lista Musica */}
        <div className="form-group">
          <label>Seleziona musica di sottofondo:</label>
          <div className="music-list">
            <div 
              className={`music-item ${!selectedMusic ? 'selected' : ''}`}
              onClick={() => setSelectedMusic('')}
            >
              <span>🚫 Nessuna musica</span>
            </div>
            {musicLibrary.map((music) => (
              <div 
                key={music.id}
                className={`music-item ${selectedMusic === music.id ? 'selected' : ''}`}
              >
                <div onClick={() => setSelectedMusic(music.id)}>
                  <span>🎵 {music.name || music.filename}</span>
                  <small>{music.duration_seconds ? `${music.duration_seconds.toFixed(1)}s` : ''}</small>
                </div>
                <button 
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteMusic(music.id);
                  }}
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* SEZIONE CONTROLLI AUDIO */}
      {selectedMusic && (
        <div className="form-card">
          <h2>🎛️ Controlli Audio</h2>
          
          {/* Volume Musica */}
          <div className="form-group">
            <label>Volume musica: {(musicVolume * 100).toFixed(0)}%</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={musicVolume}
              onChange={(e) => setMusicVolume(parseFloat(e.target.value))}
              className="slider"
            />
          </div>

          {/* Timing Musica */}
          <div className="form-row">
            <div className="form-group">
              <label>Musica prima del testo: {musicBefore.toFixed(1)}s</label>
              <input
                type="range"
                min="0"
                max="10"
                step="0.5"
                value={musicBefore}
                onChange={(e) => setMusicBefore(parseFloat(e.target.value))}
                className="slider"
              />
            </div>
            <div className="form-group">
              <label>Musica dopo il testo: {musicAfter.toFixed(1)}s</label>
              <input
                type="range"
                min="0"
                max="10"
                step="0.5"
                value={musicAfter}
                onChange={(e) => setMusicAfter(parseFloat(e.target.value))}
                className="slider"
              />
            </div>
          </div>

          {/* Controlli Fade */}
          <div className="form-row">
            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={fadeIn}
                  onChange={(e) => setFadeIn(e.target.checked)}
                />
                Fade In ({fadeInDuration.toFixed(1)}s)
              </label>
              {fadeIn && (
                <input
                  type="range"
                  min="0.1"
                  max="3"
                  step="0.1"
                  value={fadeInDuration}
                  onChange={(e) => setFadeInDuration(parseFloat(e.target.value))}
                  className="slider small"
                />
              )}
            </div>
            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={fadeOut}
                  onChange={(e) => setFadeOut(e.target.checked)}
                />
                Fade Out ({fadeOutDuration.toFixed(1)}s)
              </label>
              {fadeOut && (
                <input
                  type="range"
                  min="0.1"
                  max="3"
                  step="0.1"
                  value={fadeOutDuration}
                  onChange={(e) => setFadeOutDuration(parseFloat(e.target.value))}
                  className="slider small"
                />
              )}
            </div>
          </div>

        </div>
      )}

      {/* SEZIONE FORMATO E QUALITÀ OUTPUT */}
      <div className="form-card">
        <h2>⚙️ Impostazioni Output</h2>
        
        {/* Nome File Personalizzato */}
        <div className="form-group">
          <label htmlFor="fileName">Nome File (prefisso):</label>
          <input
            type="text"
            id="fileName"
            value={fileName}
            onChange={(e) => setFileName(e.target.value)}
            placeholder="centralino_audio"
            maxLength={50}
            className="input-field"
          />
          <small>
            Il file sarà salvato come: <strong>{(fileName.trim() || 'centralino_audio')}_qualità_timestamp.formato</strong>
          </small>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="outputFormat">Formato File:</label>
            <select
              id="outputFormat"
              value={outputFormat}
              onChange={(e) => setOutputFormat(e.target.value)}
              className="select-field"
            >
              <option value="wav">WAV (raccomandato)</option>
              <option value="mp3">MP3</option>
              <option value="gsm">GSM (compresso)</option>
            </select>
            <small>File massimo 8MB supportato</small>
          </div>
          <div className="form-group">
            <label htmlFor="audioQuality">Qualità Audio:</label>
            <select
              id="audioQuality"
              value={audioQuality}
              onChange={(e) => setAudioQuality(e.target.value)}
              className="select-field"
            >
              <option value="pcm">PCM - 8K, 16bit, 128kbps</option>
              <option value="alaw">A-law (G.711) - 8k, 8bit, 64kbps</option>
              <option value="ulaw">μ-law (G.711) - 8k, 8bit, 64kbps</option>
            </select>
            <small>Formati ottimizzati per centralini telefonici</small>
          </div>
        </div>
        
        {/* Pulsante Reset Preferenze */}
        <div className="form-group" style={{marginTop: '24px', textAlign: 'center'}}>
          <button
            type="button"
            onClick={resetPreferences}
            className="reset-btn"
            title="Ripristina tutte le impostazioni audio ai valori di default"
          >
            🔄 Ripristina Impostazioni Default
          </button>
          <small style={{display: 'block', marginTop: '8px', color: '#64748b'}}>
            Ripristina volumi, tempi, fade, formato e qualità ai valori di default
          </small>
        </div>
      </div>

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
              `🚀 Genera Audio${selectedMusic ? ' con Musica' : ''}`
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

      <div className="footer">
        <p>💡 Sistema TTS italiano per centralini</p>
        <p>🏢 Alimentato da Azure Speech Services (Licenza Commerciale)</p>
        <p>🎵 Con libreria musicale integrata</p>
      </div>
    </div>
  );
}

export default App;
