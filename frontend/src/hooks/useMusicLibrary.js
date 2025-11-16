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
      console.log('Libreria musicale caricata:', response.data.songs);
    } catch (err) {
      console.error('Errore nel caricamento della libreria:', err);
    }
  };

  const uploadMusic = async (file) => {
    if (!file) return { success: false, error: 'Nessun file selezionato' };

    const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/ogg'];
    if (!allowedTypes.includes(file.type)) {
      return { success: false, error: 'Formato file non supportato. Usa MP3, WAV o OGG.' };
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

      const response = await axios.post(`${API_URL}/music-library/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      await loadMusicLibrary();
      return { success: true, message: 'Musica caricata con successo!' };
    } catch (err) {
      console.error('Errore upload:', err);
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
      console.error('Errore eliminazione:', err);
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
