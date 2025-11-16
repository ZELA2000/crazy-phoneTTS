import React from 'react';

/**
 * Componente libreria musicale
 */

const MusicLibrary = ({ 
  musicLibrary, 
  selectedMusic, 
  uploadingMusic,
  onSelectMusic,
  onUploadMusic,
  onDeleteMusic 
}) => {
  return (
    <div className="form-card">
      <h2>🎵 Libreria Musicale</h2>
      
      {/* Upload Musica */}
      <div className="form-group">
        <label htmlFor="music-upload">Carica nuova musica:</label>
        <input
          id="music-upload"
          type="file"
          accept="audio/*"
          onChange={(e) => onUploadMusic(e.target.files[0])}
          disabled={uploadingMusic}
        />
        {uploadingMusic && <div className="loading">📤 Caricamento...</div>}
        <small style={{ display: 'block', marginTop: '4px', color: '#666' }}>
          Supportati tutti i formati audio: MP3, WAV, OGG, FLAC, M4A, AAC, WMA, ecc.
        </small>
      </div>

      {/* Lista Musica */}
      <div className="form-group">
        <label>Seleziona musica di sottofondo:</label>
        <div className="music-list">
          <div 
            className={`music-item ${!selectedMusic ? 'selected' : ''}`}
            onClick={() => onSelectMusic('')}
          >
            <span>🚫 Nessuna musica</span>
          </div>
          {musicLibrary.map((music) => (
            <div 
              key={music.id}
              className={`music-item ${selectedMusic === music.id ? 'selected' : ''}`}
            >
              <div onClick={() => onSelectMusic(music.id)}>
                <span>🎵 {music.name || music.filename}</span>
                <small>{music.duration_seconds ? `${music.duration_seconds.toFixed(1)}s` : ''}</small>
              </div>
              <button 
                className="delete-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteMusic(music.id);
                }}
              >
                🗑️
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MusicLibrary;
