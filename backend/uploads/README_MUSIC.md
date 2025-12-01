# Libreria Musicale - Guida Tecnica

Questa guida descrive la gestione della libreria musicale integrata nel sistema crazy-phoneTTS per centralini professionali.

## Formati Supportati
- MP3 (consigliato per compatibilità e spazio)
- WAV (massima qualità audio)
- OGG (buon compromesso qualità/dimensione)

## Integrazione e Mixaggio
1. Carica file musicale tramite interfaccia web
2. Il sistema analizza durata e metadati
3. Mixaggio automatico voce + musica
4. Output ottimizzato per centralini (WAV, MP3, GSM)

## Linee Guida Audio Centralino
- Sample Rate: 8kHz, 16kHz, 22kHz supportati
- Normalizzazione automatica volume
- Compressione ottimizzata per telefonia

## Best Practice per Musica Centralino

### Musica per Attesa
- Brani strumentali rilassanti
- Durata: 2-5 minuti (loop automatico)
- Volume: 15-25% durante il parlato

### Intro Aziendali
- Brani corporate di 15-30 secondi
- Crescendo verso la voce
- Volume: 40-60% in intro, 20-30% durante parlato

### Menu Navigazione
- Musica neutra, non distraente
- Durata: 1-2 minuti
- Volume: 10-20% per chiarezza voce

## Controlli Avanzati
- Musica Prima (Intro): 1-3 secondi
- Musica Dopo (Outro): 2-5 secondi
- Fade In: 0.5-1.5 secondi
- Fade Out: 1-3 secondi
- Volume durante voce: 20-30%

## Gestione File e Performance
- MP3 320kbps: ~1MB/minuto
- WAV 16bit/44kHz: ~10MB/minuto
- OGG Vorbis: ~2MB/minuto
- Metadati automatici: filename, durata, sample rate, canali, data upload, volume ottimale

## API e Automazione

### Upload Programmatico
```bash
curl -X POST "http://localhost:8000/music-library/upload" \
  -F "file=@corporate_music.mp3" \
  -F "name=Corporate Background" \
  -F "description=Musica aziendale professionale" \
  -F "optimal_volume=0.25"
```

### Gestione Batch
```bash
curl http://localhost:8000/music-library/list
curl http://localhost:8000/music-library/stats
curl -X POST http://localhost:8000/music-library/cleanup
```

## Esempi di Template Centralino

### Accoglienza Corporate
- Musica: Piano aziendale soft
- Timing: 2s intro + 3s outro
- Volume: 35% intro, 20% durante voce
- Fade: 1s in, 2s out
- Formato: WAV/PCM

### Attesa Servizio Clienti
- Musica: Ambient electronic calmo
- Timing: 1s intro + loop continuo
- Volume: 15% costante
- Fade: 0.5s in, 1s out
- Formato: MP3

### Menu Navigazione Rapida
- Musica: Minimale strumentale
- Timing: 0.5s intro + 1s outro
- Volume: 10% per chiarezza massima
- Fade: No fade
- Formato: GSM

## Note Finali
Questa guida fornisce solo linee guida tecniche e best practice per la gestione della musica nei centralini. Per dettagli sulle licenze, consultare le policy aziendali e le fonti musicali utilizzate.
