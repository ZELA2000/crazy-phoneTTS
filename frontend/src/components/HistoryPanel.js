import React, { useState } from 'react';

/**
 * Componente pannello cronologia testi
 */

const HistoryPanel = ({ textHistory, isConnected, onSelectText }) => {
  const [showHistory, setShowHistory] = useState(true);

  return (
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
                    <div 
                      className="history-text" 
                      onClick={() => onSelectText(item.text.replace('...', ''))}
                    >
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
                    onClick={() => onSelectText(item.text.replace('...', ''))}
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
  );
};

export default HistoryPanel;
