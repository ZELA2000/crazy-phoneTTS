import React from 'react';
import { formatTime, parseTimeInput } from '../utils/timeUtils';

/**
 * Componente controlli audio
 */

const AudioControls = ({
  musicVolume,
  musicBefore,
  musicAfter,
  fadeIn,
  fadeOut,
  fadeInDuration,
  fadeOutDuration,
  onMusicVolumeChange,
  onMusicBeforeChange,
  onMusicAfterChange,
  onFadeInChange,
  onFadeOutChange,
  onFadeInDurationChange,
  onFadeOutDurationChange
}) => {
  return (
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
          onChange={(e) => onMusicVolumeChange(parseFloat(e.target.value))}
          className="slider"
        />
      </div>

      {/* Timing Musica */}
      <div className="form-row">
        <div className="form-group">
          <label>Musica prima del testo: {formatTime(musicBefore)}</label>
          <div className="time-input-group">
            <input
              type="number"
              min="0"
              max="999"
              step="0.1"
              value={musicBefore < 60 ? musicBefore.toFixed(1) : (musicBefore / 60).toFixed(1)}
              onChange={(e) => {
                const value = parseFloat(e.target.value) || 0;
                const unit = musicBefore < 60 ? 'seconds' : 'minutes';
                onMusicBeforeChange(parseTimeInput(value, unit));
              }}
              className="time-input"
            />
            <select
              value={musicBefore < 60 ? 'seconds' : 'minutes'}
              onChange={(e) => {
                const currentValue = musicBefore < 60 ? musicBefore : musicBefore / 60;
                onMusicBeforeChange(parseTimeInput(currentValue, e.target.value));
              }}
              className="time-unit-select"
            >
              <option value="seconds">secondi</option>
              <option value="minutes">minuti</option>
            </select>
          </div>
          <div className="time-presets">
            <button type="button" onClick={() => onMusicBeforeChange(0)} className="preset-btn">0s</button>
            <button type="button" onClick={() => onMusicBeforeChange(2)} className="preset-btn">2s</button>
            <button type="button" onClick={() => onMusicBeforeChange(5)} className="preset-btn">5s</button>
            <button type="button" onClick={() => onMusicBeforeChange(10)} className="preset-btn">10s</button>
            <button type="button" onClick={() => onMusicBeforeChange(30)} className="preset-btn">30s</button>
            <button type="button" onClick={() => onMusicBeforeChange(60)} className="preset-btn">1min</button>
            <button type="button" onClick={() => onMusicBeforeChange(120)} className="preset-btn">2min</button>
          </div>
        </div>
        <div className="form-group">
          <label>Musica dopo il testo: {formatTime(musicAfter)}</label>
          <div className="time-input-group">
            <input
              type="number"
              min="0"
              max="999"
              step="0.1"
              value={musicAfter < 60 ? musicAfter.toFixed(1) : (musicAfter / 60).toFixed(1)}
              onChange={(e) => {
                const value = parseFloat(e.target.value) || 0;
                const unit = musicAfter < 60 ? 'seconds' : 'minutes';
                onMusicAfterChange(parseTimeInput(value, unit));
              }}
              className="time-input"
            />
            <select
              value={musicAfter < 60 ? 'seconds' : 'minutes'}
              onChange={(e) => {
                const currentValue = musicAfter < 60 ? musicAfter : musicAfter / 60;
                onMusicAfterChange(parseTimeInput(currentValue, e.target.value));
              }}
              className="time-unit-select"
            >
              <option value="seconds">secondi</option>
              <option value="minutes">minuti</option>
            </select>
          </div>
          <div className="time-presets">
            <button type="button" onClick={() => onMusicAfterChange(0)} className="preset-btn">0s</button>
            <button type="button" onClick={() => onMusicAfterChange(2)} className="preset-btn">2s</button>
            <button type="button" onClick={() => onMusicAfterChange(5)} className="preset-btn">5s</button>
            <button type="button" onClick={() => onMusicAfterChange(10)} className="preset-btn">10s</button>
            <button type="button" onClick={() => onMusicAfterChange(30)} className="preset-btn">30s</button>
            <button type="button" onClick={() => onMusicAfterChange(60)} className="preset-btn">1min</button>
            <button type="button" onClick={() => onMusicAfterChange(120)} className="preset-btn">2min</button>
          </div>
        </div>
      </div>

      {/* Controlli Fade */}
      <div className="form-row">
        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={fadeIn}
              onChange={(e) => onFadeInChange(e.target.checked)}
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
              onChange={(e) => onFadeInDurationChange(parseFloat(e.target.value))}
              className="slider small"
            />
          )}
        </div>
        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={fadeOut}
              onChange={(e) => onFadeOutChange(e.target.checked)}
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
              onChange={(e) => onFadeOutDurationChange(parseFloat(e.target.value))}
              className="slider small"
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default AudioControls;
