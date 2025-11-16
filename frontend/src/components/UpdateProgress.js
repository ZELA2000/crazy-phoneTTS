import React from 'react';

/**
 * Componente Progress Bar per aggiornamento
 */

const UpdateProgress = ({ progress }) => {
  if (!progress) return null;

  return (
    <div className="update-progress-overlay">
      <div className="update-progress">
        <div className="progress-header">
          <h3>🔄 Aggiornamento in corso...</h3>
        </div>
        <div className="progress-content">
          <div className="progress-message">
            {progress.message}
          </div>
          {progress.percentage !== undefined && (
            <div className="progress-bar-container">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${progress.percentage}%` }}
                ></div>
              </div>
              <span className="progress-text">{progress.percentage}%</span>
            </div>
          )}
          <div className="progress-warning">
            ⚠️ Non chiudere la finestra durante l'aggiornamento
          </div>
        </div>
      </div>
    </div>
  );
};

export default UpdateProgress;
