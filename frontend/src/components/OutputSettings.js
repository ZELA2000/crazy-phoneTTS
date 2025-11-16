import React from 'react';

/**
 * Componente impostazioni output
 */

const OutputSettings = ({
  fileName,
  outputFormat,
  audioQuality,
  onFileNameChange,
  onOutputFormatChange,
  onAudioQualityChange,
  onResetPreferences
}) => {
  return (
    <div className="form-card">
      <h2>⚙️ Impostazioni Output</h2>
      
      {/* Nome File Personalizzato */}
      <div className="form-group">
        <label htmlFor="fileName">Nome File (prefisso):</label>
        <input
          type="text"
          id="fileName"
          value={fileName}
          onChange={(e) => onFileNameChange(e.target.value)}
          placeholder="centralino_audio"
          maxLength={50}
          className="input-field"
        />
        <small>
          Il file sarà salvato come: <strong>{(fileName.trim() || 'centralino_audio')}_YYMMDD.{outputFormat}</strong>
        </small>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="outputFormat">Formato File:</label>
          <select
            id="outputFormat"
            value={outputFormat}
            onChange={(e) => onOutputFormatChange(e.target.value)}
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
            onChange={(e) => onAudioQualityChange(e.target.value)}
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
          onClick={onResetPreferences}
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
  );
};

export default OutputSettings;
