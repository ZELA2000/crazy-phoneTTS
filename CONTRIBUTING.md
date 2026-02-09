# 🤝 Contribuire a crazy-phoneTTS

Grazie per il tuo interesse nel contribuire al progetto crazy-phoneTTS! Questo documento fornisce le linee guida per contribuire efficacemente.

## 📋 Indice

- [Codice di Condotta](#codice-di-condotta)
- [Come Posso Contribuire?](#come-posso-contribuire)
- [Segnalare Bug](#segnalare-bug)
- [Proporre Funzionalità](#proporre-funzionalità)
- [Contribuire con Codice](#contribuire-con-codice)
- [Convenzioni di Sviluppo](#convenzioni-di-sviluppo)
- [Testing](#testing)

## 📜 Codice di Condotta

Questo progetto adotta un codice di condotta basato sul rispetto reciproco. Partecipando, ti impegni a mantenere un ambiente accogliente e professionale.

## 🎯 Come Posso Contribuire?

Ci sono molti modi per contribuire a crazy-phoneTTS:

### 🐛 Segnalare Bug

Se trovi un bug:

1. Controlla che non sia già stato segnalato nelle [Issues](../../issues)
2. Usa il template [Bug Report](.github/ISSUE_TEMPLATE/bug_report.yml)
3. Fornisci quanti più dettagli possibile:
   - Versione dell'applicazione
   - Sistema operativo
   - Passi per riprodurre il problema
   - Log e messaggi di errore
   - Screenshot se applicabile

### ✨ Proporre Funzionalità

Per proporre nuove funzionalità:

1. Controlla che non sia già stata proposta nelle [Issues](../../issues)
2. Usa il template [Feature Request](.github/ISSUE_TEMPLATE/feature_request.yml)
3. Descrivi chiaramente:
   - Il problema che risolve
   - La soluzione proposta
   - Casi d'uso concreti
   - Eventuali alternative considerate

### 💬 Fare Domande

Per domande generali:

1. Consulta prima il [README.md](README.md)
2. Cerca nelle [Issues](../../issues) esistenti
3. Usa il template [Domanda/Supporto](.github/ISSUE_TEMPLATE/question.yml)
4. Oppure avvia una [Discussion](../../discussions)

### 📝 Migliorare la Documentazione

La documentazione può sempre migliorare:

- Correggere errori di battitura
- Aggiungere esempi
- Chiarire sezioni confuse
- Tradurre in altre lingue
- Aggiungere guide d'uso

## 💻 Contribuire con Codice

### Setup Ambiente di Sviluppo

1. **Fork del repository**
   ```bash
   # Clona il tuo fork
   git clone https://github.com/TUO-USERNAME/crazy-phoneTTS.git
   cd crazy-phoneTTS
   ```

2. **Setup con Docker (consigliato)**
   ```bash
   docker-compose up --build
   ```

3. **Setup locale (opzionale)**
   
   **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
   
   **Frontend:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Workflow di Sviluppo

1. **Crea un branch per la tua modifica**
   ```bash
   git checkout -b feature/nome-feature
   # oppure
   git checkout -b fix/nome-bug
   ```

2. **Sviluppa e testa le modifiche**
   - Scrivi codice chiaro e ben commentato
   - Segui le convenzioni di stile
   - Aggiungi test se applicabile
   - Testa localmente e con Docker

3. **Commit delle modifiche**
   ```bash
   git add .
   git commit -m "feat: breve descrizione delle modifiche"
   ```

4. **Push al tuo fork**
   ```bash
   git push origin feature/nome-feature
   ```

5. **Apri una Pull Request**
   - Usa il template per le PR
   - Descrivi chiaramente le modifiche
   - Riferisci eventuali issue correlate
   - Attendi la review

### Convenzioni per i Commit

Usa [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - Nuova funzionalità
- `fix:` - Correzione bug
- `docs:` - Solo documentazione
- `style:` - Formattazione, senza cambi logici
- `refactor:` - Refactoring senza nuove feature o fix
- `perf:` - Miglioramenti performance
- `test:` - Aggiunta o correzione test
- `chore:` - Modifiche build, dipendenze, ecc.

Esempi:
```
feat: aggiungi supporto per voci neural in Google TTS
fix: correggi normalizzazione volume nell'audio mixer
docs: aggiorna guida installazione Docker
refactor: riorganizza gestione websocket
```

## 🎨 Convenzioni di Sviluppo

### Python (Backend)

- **Stile**: Segui [PEP 8](https://pep8.org/)
- **Formattazione**: Usa `black` per la formattazione
- **Type hints**: Usa type hints dove possibile
- **Docstrings**: Documenta classi e funzioni
- **Imports**: Ordina con `isort`

Esempio:
```python
from typing import Optional, Dict, Any

async def generate_audio(
    text: str,
    voice: str,
    options: Optional[Dict[str, Any]] = None
) -> bytes:
    """
    Genera audio TTS dal testo fornito.
    
    Args:
        text: Testo da convertire in audio
        voice: Nome della voce da utilizzare
        options: Opzioni aggiuntive per la generazione
        
    Returns:
        Audio in formato bytes (WAV)
    """
    # Implementazione...
    pass
```

### JavaScript/React (Frontend)

- **Stile**: Usa ESLint per il linting
- **Formattazione**: Usa Prettier
- **Componenti**: Preferisci functional components con hooks
- **Naming**: PascalCase per componenti, camelCase per funzioni
- **Props**: Usa PropTypes o TypeScript

Esempio:
```javascript
import React, { useState, useEffect } from 'react';

/**
 * Componente per il controllo del volume audio
 * @param {Object} props - Props del componente
 * @param {number} props.initialVolume - Volume iniziale (0-100)
 * @param {Function} props.onChange - Callback quando il volume cambia
 */
const VolumeControl = ({ initialVolume = 50, onChange }) => {
  const [volume, setVolume] = useState(initialVolume);

  useEffect(() => {
    onChange(volume);
  }, [volume, onChange]);

  return (
    <input
      type="range"
      min="0"
      max="100"
      value={volume}
      onChange={(e) => setVolume(Number(e.target.value))}
    />
  );
};

export default VolumeControl;
```

### Struttura dei File

**Backend:**
```
backend/
├── main.py                 # Entry point FastAPI
├── core/                   # Configurazioni core
│   └── config.py
├── managers/               # Business logic
│   ├── audio_processor.py
│   └── music_library.py
├── models/                 # Modelli dati
│   └── voice_catalog.py
└── services/              # Servizi esterni
    ├── azure_speech.py
    └── edge_tts_service.py
```

**Frontend:**
```
frontend/src/
├── App.js                 # Componente principale
├── components/            # Componenti React
│   ├── TTSGenerator.js
│   └── MusicLibrary.js
├── hooks/                 # Custom hooks
│   └── useMusicLibrary.js
└── utils/                 # Utility functions
    └── apiConfig.js
```

## 🧪 Testing

### Backend Testing

```bash
cd backend
pytest tests/ -v
```

### Frontend Testing

```bash
cd frontend
npm test
```

### Testing con Docker

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Checklist Testing

Prima di inviare una PR, verifica:

- [ ] Il codice funziona localmente
- [ ] Il codice funziona in Docker
- [ ] Tutti i test passano
- [ ] Non ci sono errori di linting
- [ ] L'audio viene generato correttamente
- [ ] Il mixaggio con musica funziona
- [ ] Tutti i servizi TTS funzionano (se modificati)
- [ ] Il frontend si avvia senza errori
- [ ] Non ci sono warning nella console

## 🔍 Review Process

1. **Automated Checks**: GitHub Actions esegue controlli automatici
2. **Code Review**: Un maintainer esaminerà il codice
3. **Testing**: Verifica che tutto funzioni come atteso
4. **Discussion**: Potrebbero essere richieste modifiche
5. **Merge**: Una volta approvata, la PR verrà mergiata

## 📚 Risorse Utili

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [Azure Speech Documentation](https://learn.microsoft.com/azure/ai-services/speech-service/)
- [Edge TTS GitHub](https://github.com/rany2/edge-tts)
- [Google Cloud TTS](https://cloud.google.com/text-to-speech)

## 🎖️ Riconoscimenti

Tutti i contributori vengono elencati nel file [README.md](README.md).

## ❓ Domande?

Se hai domande:

- Apri una [Discussion](../../discussions)
- Crea un'issue con il template "Domanda/Supporto"
- Contatta i maintainer

## 📄 Licenza

Contribuendo a questo progetto, accetti che le tue modifiche siano rilasciate sotto la stessa licenza del progetto (vedi [LICENSE](LICENSE)).

---

**Grazie per contribuire a crazy-phoneTTS! 🎉**

Ogni contributo, grande o piccolo, è prezioso e aiuta a rendere questo progetto migliore per tutti.
