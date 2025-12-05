import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from '../utils/apiConfig';

/**
 * Hook per gestione libreria musicale
 */

export const useMusicLibrary = (selectedMusic, setSelectedMusic) => {
  const [musicLibrary, setMusicLibrary] = useState([]);
  const [uploadingMusic, setUploadingMusic] = useState(false);

  useEffect(() => {
    loadMusicLibrary();
  }, []);

  const loadMusicLibrary = async () => {
    try {
      const response = await axios.get(`${API_URL}/music-library/list`);
      setMusicLibrary(response.data.songs || []);
      console.log('🎵 [Music Library] Libreria caricata:', response.data.songs.length, 'brani disponibili');
    } catch (err) {
      console.error('❌ [Music Library] Errore caricamento libreria:', err.message || err);
    }
  };

  const uploadMusic = async (file) => {
    if (!file) return { success: false, error: 'Nessun file selezionato' };

    // Verifica che sia un file audio (qualsiasi formato)
    if (!file.type.startsWith('audio/')) {
      return { success: false, error: 'Il file selezionato non è un file audio.' };
    }

    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      return { success: false, error: 'File troppo grande. Massimo 50MB.' };
    }

    setUploadingMusic(true);

    try {
      const formData = new FormData();
      formData.append('music_file', file);
      const name = file.name.replace(/\.[^/.]+$/, '');
      formData.append('name', name);

      await axios.post(`${API_URL}/music-library/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      await loadMusicLibrary();
      return { success: true, message: 'Musica caricata con successo!' };
    } catch (err) {
      console.error('❌ [Music Library] Errore upload brano:', {
        file: file?.name,
        size: file?.size,
        tipo: file?.type,
        errore: err.response?.data?.detail || err.message || err
      });
      return { 
        success: false, 
        error: err.response?.data?.detail || 'Errore durante il caricamento della musica' 
      };
    } finally {
      setUploadingMusic(false);
    }
  };

  const deleteMusic = async (songId) => {
    if (!window.confirm('Sei sicuro di voler eliminare questo file?')) {
      return { success: false };
    }

    try {
      await axios.delete(`${API_URL}/music-library/${songId}`);
      await loadMusicLibrary();
      
      if (selectedMusic === songId) {
        setSelectedMusic('');
      }
      
      return { success: true, message: 'Musica eliminata con successo!' };
    } catch (err) {
      console.error('❌ [Music Library] Errore eliminazione brano:', songId, '|', err.message || err);
      return { success: false, error: 'Errore durante l\'eliminazione della musica' };
    }
  };

  return {
    musicLibrary,
    uploadingMusic,
    uploadMusic,
    deleteMusic,
    loadMusicLibrary
  };
};
