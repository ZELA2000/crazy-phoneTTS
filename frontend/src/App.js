import React, { useState } from 'react';
import './UpdateDialog.css';

// Hooks personalizzati
import { usePreferences } from './hooks/usePreferences';
import { useTextHistory } from './hooks/useTextHistory';
import { useMusicLibrary } from './hooks/useMusicLibrary';
import { useUpdateSystem } from './hooks/useUpdateSystem';

// Componenti
import UpdateDialog from './components/UpdateDialog';
import UpdateProgress from './components/UpdateProgress';
import HistoryPanel from './components/HistoryPanel';
import MusicLibrary from './components/MusicLibrary';
import AudioControls from './components/AudioControls';
import OutputSettings from './components/OutputSettings';
import TTSGenerator from './components/TTSGenerator';

/**
 * crazy-phoneTTS - Sistema Text-to-Speech Professionale
 * Applicazione React refactorizzata con clean code principles
 */

function App() {
  // Stati locali
  const [audioUrl, setAudioUrl] = useState('');
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  // Hook personalizzati
  const preferences = usePreferences();
  const { textHistory, isConnected } = useTextHistory();
  const musicLibrary = useMusicLibrary(preferences.selectedMusic, preferences.setSelectedMusic);
  const updateSystem = useUpdateSystem();

  // Handler per upload musica
  const handleMusicUpload = async (file) => {
    const result = await musicLibrary.uploadMusic(file);
    if (result.success) {
      setSuccess(result.message);
      setTimeout(() => setSuccess(''), 3000);
    } else {
      setError(result.error);
      setTimeout(() => setError(''), 3000);
    }
  };

  // Handler per eliminazione musica
  const handleMusicDelete = async (songId) => {
    const result = await musicLibrary.deleteMusic(songId);
    if (result.success) {
      setSuccess(result.message);
      setTimeout(() => setSuccess(''), 3000);
    } else if (result.error) {
      setError(result.error);
      setTimeout(() => setError(''), 3000);
    }
  };

  // Handler per reset preferenze
  const handleResetPreferences = () => {
    if (preferences.resetPreferences()) {
      setSuccess('🔄 Impostazioni ripristinate ai valori di default');
      setTimeout(() => setSuccess(''), 3000);
    }
  };

  // Handler per copia comando aggiornamento
  const handleCopyCommand = (command) => {
    navigator.clipboard.writeText(command);
    setSuccess('✅ Comando copiato negli appunti!');
    setTimeout(() => setSuccess(''), 2000);
  };

  return (
    <div className="container">
      {/* HEADER */}
      <div className="header">
        <h1>🎙️ crazy-phoneTTS</h1>
        <p>Sistema Text-to-Speech professionale per centralini telefonici</p>
        <div className="repo-link">
          <a
            href="https://github.com/ZELA2000/crazy-phoneTTS"
            target="_blank"
            rel="noopener noreferrer"
            className="github-link"
          >
            🔗 Progetto su GitHub
          </a>
        </div>
        <div className="connection-status">
          {isConnected ? (
            <span className="connected">🟢 Live connesso</span>
          ) : (
            <span className="disconnected">🔴 Disconnesso</span>
          )}
          {preferences.preferencesSaved && (
            <span className="preferences-saved">💾 Preferenze salvate</span>
          )}
        </div>
      </div>

      {/* MESSAGGI */}
      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      {/* DIALOG AGGIORNAMENTO */}
      {updateSystem.showUpdateDialog && (
        <UpdateDialog
          updateInfo={updateSystem.updateInfo}
          onConfirm={updateSystem.cancelUpdate}
          onCancel={updateSystem.cancelUpdate}
          onCopyCommand={handleCopyCommand}
        />
      )}

      {/* PROGRESS BAR AGGIORNAMENTO */}
      {updateSystem.isUpdating && (
        <UpdateProgress progress={updateSystem.updateProgress} />
      )}

      {/* NOTIFICA AGGIORNAMENTO */}
      {updateSystem.updateAvailable && !updateSystem.showUpdateDialog && !updateSystem.isUpdating && (
        <div className="update-notification">
          <span className="update-icon">🔄</span>
          <span className="update-text">
            Aggiornamento disponibile ({updateSystem.updateInfo?.latest_version})
          </span>
          <button 
            className="update-show-btn"
            onClick={() => updateSystem.setShowUpdateDialog(true)}
          >
            Dettagli
          </button>
        </div>
      )}

      {/* CRONOLOGIA TESTI */}
      <HistoryPanel
        textHistory={textHistory}
        isConnected={isConnected}
        onSelectText={(text) => {}} // Gestito direttamente in TTSGenerator
      />

      {/* LIBRERIA MUSICALE */}
      <MusicLibrary
        musicLibrary={musicLibrary.musicLibrary}
        selectedMusic={preferences.selectedMusic}
        uploadingMusic={musicLibrary.uploadingMusic}
        onSelectMusic={preferences.setSelectedMusic}
        onUploadMusic={handleMusicUpload}
        onDeleteMusic={handleMusicDelete}
      />

      {/* CONTROLLI AUDIO */}
      {preferences.selectedMusic && (
        <AudioControls
          musicVolume={preferences.musicVolume}
          musicBefore={preferences.musicBefore}
          musicAfter={preferences.musicAfter}
          fadeIn={preferences.fadeIn}
          fadeOut={preferences.fadeOut}
          fadeInDuration={preferences.fadeInDuration}
          fadeOutDuration={preferences.fadeOutDuration}
          onMusicVolumeChange={preferences.setMusicVolume}
          onMusicBeforeChange={preferences.setMusicBefore}
          onMusicAfterChange={preferences.setMusicAfter}
          onFadeInChange={preferences.setFadeIn}
          onFadeOutChange={preferences.setFadeOut}
          onFadeInDurationChange={preferences.setFadeInDuration}
          onFadeOutDurationChange={preferences.setFadeOutDuration}
        />
      )}

      {/* IMPOSTAZIONI OUTPUT */}
      <OutputSettings
        fileName={preferences.fileName}
        outputFormat={preferences.outputFormat}
        audioQuality={preferences.audioQuality}
        onFileNameChange={preferences.setFileName}
        onOutputFormatChange={preferences.setOutputFormat}
        onAudioQualityChange={preferences.setAudioQuality}
        onResetPreferences={handleResetPreferences}
      />

      {/* GENERATORE TTS */}
      <TTSGenerator
        preferences={preferences}
        audioUrl={audioUrl}
        setAudioUrl={setAudioUrl}
      />

      {/* FOOTER */}
      <div className="footer">
        <p>💡 Sistema TTS italiano per centralini</p>
        <p>🏢 Alimentato da Azure Speech Services (Licenza Commerciale)</p>
        <p>🎵 Con libreria musicale integrata</p>
        <p>
          🔗 Repository:{" "}
          <a
            href="https://github.com/ZELA2000/crazy-phoneTTS"
            target="_blank"
            rel="noopener noreferrer"
          >
            https://github.com/ZELA2000/crazy-phoneTTS
          </a>
        </p>
      </div>
    </div>
  );
}

export default App;
