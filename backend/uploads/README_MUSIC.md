# 🎵 Libreria Musicale - Azure Speech Services TTS

Documentazione per la gestione della libreria musicale integrata nel sistema TTS per centralini professionali.

## 📂 Formati Supportati
- **MP3** (consigliato per spazio e compatibilità)
- **WAV** (massima qualità audio)
- **OGG** (buon compromesso qualità/dimensione)

## 🎙️ Integrazione con Azure Speech Services

### **Processo Automatico**
1. **Upload** file musicale tramite web interface
2. **Analisi** automatica durata e metadati
3. **Integrazione** con Azure Speech TTS
4. **Mixaggio** professionale voce + musica
5. **Output** ottimizzato per centralini

### **Qualità Audio Centralino**
- **Sample Rate**: 8kHz, 16kHz, 22kHz supportati
- **Normalizzazione**: Automatica per volume uniforme
- **Compressione**: Ottimizzata per telefonia
- **Formato Output**: WAV/PCM, MP3, GSM

## 🏢 Suggerimenti per Centralini Professionali

### **Musica per Attesa**
```
Caratteristiche ideali:
- Brani strumentali rilassanti
- Jazz soft, ambient, classica leggera
- Durata: 2-5 minuti (loop automatico)
- BPM: 70-120 (ritmo calmo)
- Volume: 15-25% durante il parlato
```

### **Intro Aziendali**
```
Caratteristiche ideali:  
- Brani corporate di 15-30 secondi
- Intro orchestrali o piano
- Crescendo verso la voce
- Volume: 40-60% in intro, 20-30% durante parlato
```

### **Menu Navigazione**
```
Caratteristiche ideali:
- Musica neutra, non distraente
- Durata: 1-2 minuti per menù lunghi
- Evitare melodie riconoscibili
- Volume: 10-20% per massima chiarezza voce
```

## ⚙️ Controlli Avanzati Sistema

### **Timing Professionale**
```
Musica Prima (Intro): 1-3 secondi
- Attesa centralino: 2 secondi
- Annunci importanti: 3 secondi
- Menu navigazione: 1 secondo

Musica Dopo (Outro): 2-5 secondi  
- Conclusioni naturali: 3 secondi
- Redirect ad operatore: 2 secondi
- Fine chiamata: 4-5 secondi
```

### **Fade Effects per Centralini**
```
Fade In: 0.5-1.5 secondi
- Ingresso morbido, non disturba
- Evita shock audio iniziale

Fade Out: 1-3 secondi
- Conclusione naturale
- Transizione smooth a operatore
```

### **Volume Mixing Ottimale**
```
Centralini Standard:
- Intro/Outro: 50-70% volume musica
- Durante voce: 20-30% volume musica
- Menu critico: 10-15% volume musica

Ambienti Rumorosi:
- Ridurre musica del 50%
- Aumentare chiarezza voce
- Privilegiare frequenze medie
```

## 📊 Gestione File e Performance

### **Storage Ottimizzato**
```
MP3 320kbps: ~1MB per minuto
WAV 16bit/44kHz: ~10MB per minuto  
OGG Vorbis: ~2MB per minuto

Centralini consigliato: MP3 192-320kbps
```

### **Metadati Automatici**
```json
{
  "filename": "corporate_intro.mp3",
  "duration": "00:00:45",
  "sample_rate": "44100",
  "channels": "stereo",
  "upload_date": "2025-09-30",
  "usage_count": 156,
  "optimal_volume": 0.25
}
```

### **Cache e Performance**
- **Pre-processing**: File analizzati all'upload
- **Cache**: Mixing templates per riuso rapido  
- **Cleanup**: Rimozione automatica file inutilizzati
- **Backup**: Sync automatico Azure Storage (opzionale)

## 🔒 Compliance e Licensing

### **Uso Commerciale Centralini**
⚠️ **IMPORTANTE**: Per centralini aziendali verificare sempre:

- ✅ **Licenze SIAE/SCF** per musica italiana
- ✅ **Royalty-free** per uso commerciale
- ✅ **Creative Commons** con attribuzione corretta
- ✅ **Musica originale** o commissionata

### **Risorse Legali Consigliate**
```
GRATUITO:
- Freesound.org (CC licenses)
- Incompetech.com (Kevin MacLeod)
- YouTube Audio Library
- Pixabay Music

COMMERCIALE:
- Epidemic Sound
- Artlist
- AudioJungle (Envato)
- PremiumBeat
```

## 🎯 Template Centralino Predefiniti

### **Template 1: Accoglienza Corporate**
```
Musica: Piano aziendale soft
Timing: 2s intro + 3s outro
Volume: 35% intro, 20% durante voce
Fade: 1s in, 2s out
Formato: WAV/PCM per qualità
```

### **Template 2: Attesa Servizio Clienti**
```
Musica: Ambient electronic calmo
Timing: 1s intro + loop continuo
Volume: 15% costante
Fade: 0.5s in, 1s out
Formato: MP3 per efficienza
```

### **Template 3: Menu Navigazione Rapida**
```
Musica: Minimale strumentale
Timing: 0.5s intro + 1s outro  
Volume: 10% per chiarezza massima
Fade: No fade per immediatezza
Formato: GSM per telefonia
```

## 🛠️ API e Automazione

### **Upload Programmatico**
```bash
# Upload via API
curl -X POST "http://localhost:8000/music-library/upload" \
     -F "file=@corporate_music.mp3" \
     -F "name=Corporate Background" \
     -F "description=Musica aziendale professionale" \
     -F "optimal_volume=0.25"
```

### **Gestione Batch**
```bash
# Lista completa
curl http://localhost:8000/music-library/list

# Statistiche utilizzo
curl http://localhost:8000/music-library/stats

# Cleanup automatico
curl -X POST http://localhost:8000/music-library/cleanup
```

## 📞 Esempi Caso d'Uso Reali

### **Centralino Medico**
```
Scenario: Studio medico, attesa pazienti
Musica: Classical piano, 3 min loop
Volume: 20% durante voce
Messaggio: "Grazie per aver chiamato Studio Dr. Rossi..."
Output: WAV per qualità professionale
```

### **Assistenza Tecnica IT** 
```
Scenario: Help desk aziendale
Musica: Ambient tech, 2 min loop
Volume: 15% per chiarezza istruzioni
Messaggio: "Per assistenza urgente prema 1..."
Output: MP3 per efficienza server
```

### **E-commerce Customer Care**
```
Scenario: Servizio clienti online
Musica: Upbeat corporate, 90 sec
Volume: 25% per energia positiva
Messaggio: "Grazie per aver scelto [Brand]..."
Output: GSM per centralino VoIP
```

---

**Libreria musicale pronta per centralini professionali con Azure Speech Services** 🎵📞
