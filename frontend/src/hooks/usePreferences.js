import { useState, useEffect } from 'react';

/**
 * Hook per gestione preferenze utente con localStorage
 */

const DEFAULT_PREFERENCES = {
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
  selectedMusic: '',
  ttsService: 'edge',  // Servizio TTS di default (edge o azure)
  ttsVoice: 'it-IT-ElsaNeural'  // Voce di default
};

const STORAGE_KEY = 'crazy-phonetts-preferences';

export const usePreferences = () => {
  const [musicVolume, setMusicVolume] = useState(DEFAULT_PREFERENCES.musicVolume);
  const [musicBefore, setMusicBefore] = useState(DEFAULT_PREFERENCES.musicBefore);
  const [musicAfter, setMusicAfter] = useState(DEFAULT_PREFERENCES.musicAfter);
  const [fadeIn, setFadeIn] = useState(DEFAULT_PREFERENCES.fadeIn);
  const [fadeOut, setFadeOut] = useState(DEFAULT_PREFERENCES.fadeOut);
  const [fadeInDuration, setFadeInDuration] = useState(DEFAULT_PREFERENCES.fadeInDuration);
  const [fadeOutDuration, setFadeOutDuration] = useState(DEFAULT_PREFERENCES.fadeOutDuration);
  const [outputFormat, setOutputFormat] = useState(DEFAULT_PREFERENCES.outputFormat);
  const [audioQuality, setAudioQuality] = useState(DEFAULT_PREFERENCES.audioQuality);
  const [fileName, setFileName] = useState(DEFAULT_PREFERENCES.fileName);
  const [selectedMusic, setSelectedMusic] = useState(DEFAULT_PREFERENCES.selectedMusic);
  const [ttsService, setTtsService] = useState(DEFAULT_PREFERENCES.ttsService);
  const [ttsVoice, setTtsVoice] = useState(DEFAULT_PREFERENCES.ttsVoice);
  const [preferencesSaved, setPreferencesSaved] = useState(false);

  // Carica preferenze all'avvio
  useEffect(() => {
    loadPreferences();
  }, []);

  // Salva automaticamente quando cambiano
  useEffect(() => {
    const timer = setTimeout(() => {
      savePreferences();
    }, 500); // Debounce di 500ms
    
    return () => clearTimeout(timer);
  }, [musicVolume, musicBefore, musicAfter, fadeIn, fadeOut, fadeInDuration, fadeOutDuration, outputFormat, audioQuality, fileName, selectedMusic, ttsService, ttsVoice]);

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
      selectedMusic,
      ttsService,
      ttsVoice
    };
    
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
      console.log('✅ Preferenze salvate:', preferences);
      
      setPreferencesSaved(true);
      setTimeout(() => setPreferencesSaved(false), 2000);
    } catch (err) {
      console.error('❌ Errore salvataggio preferenze:', err);
    }
  };

  const loadPreferences = () => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const preferences = JSON.parse(saved);
        console.log('📖 Caricamento preferenze salvate:', preferences);
        
        setMusicVolume(preferences.musicVolume ?? DEFAULT_PREFERENCES.musicVolume);
        setMusicBefore(preferences.musicBefore ?? DEFAULT_PREFERENCES.musicBefore);
        setMusicAfter(preferences.musicAfter ?? DEFAULT_PREFERENCES.musicAfter);
        setFadeIn(preferences.fadeIn ?? DEFAULT_PREFERENCES.fadeIn);
        setFadeOut(preferences.fadeOut ?? DEFAULT_PREFERENCES.fadeOut);
        setFadeInDuration(preferences.fadeInDuration ?? DEFAULT_PREFERENCES.fadeInDuration);
        setFadeOutDuration(preferences.fadeOutDuration ?? DEFAULT_PREFERENCES.fadeOutDuration);
        setOutputFormat(preferences.outputFormat ?? DEFAULT_PREFERENCES.outputFormat);
        setAudioQuality(preferences.audioQuality ?? DEFAULT_PREFERENCES.audioQuality);
        setFileName(preferences.fileName ?? DEFAULT_PREFERENCES.fileName);
        setSelectedMusic(preferences.selectedMusic ?? DEFAULT_PREFERENCES.selectedMusic);
        setTtsService(preferences.ttsService ?? DEFAULT_PREFERENCES.ttsService);
        setTtsVoice(preferences.ttsVoice ?? DEFAULT_PREFERENCES.ttsVoice);
        
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
      localStorage.removeItem(STORAGE_KEY);
      
      setMusicVolume(DEFAULT_PREFERENCES.musicVolume);
      setMusicBefore(DEFAULT_PREFERENCES.musicBefore);
      setMusicAfter(DEFAULT_PREFERENCES.musicAfter);
      setFadeIn(DEFAULT_PREFERENCES.fadeIn);
      setFadeOut(DEFAULT_PREFERENCES.fadeOut);
      setFadeInDuration(DEFAULT_PREFERENCES.fadeInDuration);
      setFadeOutDuration(DEFAULT_PREFERENCES.fadeOutDuration);
      setOutputFormat(DEFAULT_PREFERENCES.outputFormat);
      setAudioQuality(DEFAULT_PREFERENCES.audioQuality);
      setFileName(DEFAULT_PREFERENCES.fileName);
      setSelectedMusic(DEFAULT_PREFERENCES.selectedMusic);
      setTtsService(DEFAULT_PREFERENCES.ttsService);
      setTtsVoice(DEFAULT_PREFERENCES.ttsVoice);
      
      console.log('🔄 Preferenze ripristinate ai default');
      return true;
    } catch (err) {
      console.error('❌ Errore reset preferenze:', err);
      return false;
    }
  };

  return {
    // Stati
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
    selectedMusic,
    ttsService,
    ttsVoice,
    preferencesSaved,
    
    // Setters
    setMusicVolume,
    setMusicBefore,
    setMusicAfter,
    setFadeIn,
    setFadeOut,
    setFadeInDuration,
    setFadeOutDuration,
    setOutputFormat,
    setAudioQuality,
    setFileName,
    setSelectedMusic,
    setTtsService,
    setTtsVoice,
    
    // Metodi
    resetPreferences
  };
};
