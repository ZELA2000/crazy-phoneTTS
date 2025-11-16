import React from 'react';
import '../UpdateDialog.css';

/**
 * Componente Dialog per notifica aggiornamento
 */

const UpdateDialog = ({ updateInfo, onConfirm, onCancel, onCopyCommand }) => {
  if (!updateInfo) return null;

  return (
    <div className="update-dialog-overlay">
      <div className="update-dialog">
        <div className="update-header">
          <h3>🔄 Aggiornamento Disponibile</h3>
        </div>
        <div className="update-content">
          <p>
            È disponibile una nuova versione: <strong>{updateInfo.latest_version}</strong>
          </p>
          <p>Versione attuale: {updateInfo.current_version}</p>
          {updateInfo.release_info?.body && (
            <div className="release-notes">
              <h4>📝 Note di rilascio:</h4>
              <div className="release-body">
                {updateInfo.release_info.body.split('\n').slice(0, 5).map((line, i) => (
                  <p key={i}>{line}</p>
                ))}
              </div>
            </div>
          )}
          
          {updateInfo.update_instructions && (
            <div className="update-instructions">
              <h4>📋 Come Aggiornare:</h4>
              
              <div className="instruction-section">
                <div className="instruction-item">
                  <strong>🪟 Windows:</strong>
                  <p>{updateInfo.update_instructions.windows.description}</p>
                  <div className="command-box">
                    <code>{updateInfo.update_instructions.windows.command}</code>
                    <button 
                      className="copy-btn" 
                      onClick={() => onCopyCommand(updateInfo.update_instructions.windows.command)}
                      title="Copia comando"
                    >
                      📋
                    </button>
                  </div>
                </div>
                
                <div className="instruction-item">
                  <strong>🐧 Linux / 🍎 Mac:</strong>
                  <p>{updateInfo.update_instructions.linux.description}</p>
                  <div className="command-box">
                    <code>{updateInfo.update_instructions.linux.command}</code>
                    <button 
                      className="copy-btn" 
                      onClick={() => onCopyCommand(updateInfo.update_instructions.linux.command)}
                      title="Copia comando"
                    >
                      📋
                    </button>
                  </div>
                </div>
              </div>
              
              <div className="update-note">
                <p>ℹ️ Lo script creerà automaticamente un backup completo prima dell'aggiornamento</p>
                <p>⚠️ Il servizio sarà offline per circa 1-2 minuti durante l'aggiornamento</p>
              </div>
            </div>
          )}
        </div>
        <div className="update-actions">
          <button className="btn btn-secondary" onClick={onConfirm}>
            ✅ Ho Capito
          </button>
        </div>
      </div>
    </div>
  );
};

export default UpdateDialog;
