# 🌐 Guida Deployment in Rete

## Configurazione per Accesso in Rete Aziendale

### 📋 Prerequisiti

1. **Docker e Docker Compose** installati sul server
2. **Chiavi Azure Speech Services** configurate
3. **Accesso alla rete** aziendale con porte 3000 e 8000 disponibili

### 🚀 Deployment Rapido

#### 1. Preparazione Sistema

```powershell
# Clona o copia il progetto sul server
git clone <repository-url> tts-system
cd tts-system

# Configura le variabili Azure
copy .env.example .env
# Modifica .env con le tue credenziali Azure
```

#### 2. Configurazione Network

Il sistema è già configurato per il **rilevamento automatico dell'IP**:

- ✅ **Localhost**: Automaticamente usa `http://localhost:8000`
- ✅ **Rete aziendale**: Automaticamente usa `http://[IP-SERVER]:8000`
- ✅ **Nessuna configurazione richiesta**

#### 3. Avvio Sistema

```powershell
# Avvio completo del sistema
docker-compose up --build -d

# Verifica stato servizi
docker-compose ps

# Visualizza logs
docker-compose logs -f
```

### 🖥️ Accesso al Sistema

#### Per l'Amministratore (sul server):
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

#### Per gli Utenti in Rete:
- **Web Interface**: http://[IP-SERVER]:3000
- **API**: http://[IP-SERVER]:8000

### 🔧 Configurazioni Avanzate

#### Personalizzazione IP e Porte

Nel file `.env`, puoi configurare:

```env
# Forza un IP specifico (opzionale)
BACKEND_HOST=192.168.1.100

# Cambia porta backend (opzionale)
BACKEND_PORT=8080

# Override URL API frontend (solo per configurazioni complesse)
FRONTEND_API_URL=http://server-aziendale:8080
```

#### Docker Compose Personalizzato

Per configurazioni enterprise, modifica `docker-compose.yml`:

```yaml
version: '3.8'
services:
  backend:
    ports:
      - "8080:8000"  # Cambia porta esposta
    environment:
      - BACKEND_HOST=0.0.0.0
      - BACKEND_PORT=8000
  
  frontend:
    ports:
      - "80:3000"    # Usa porta 80 standard
```

### 🔒 Sicurezza in Rete

#### Raccomandazioni

1. **Firewall**: Apri solo le porte necessarie (3000, 8000)
2. **HTTPS**: Per produzione, configura reverse proxy con SSL
3. **Backup**: Backup automatico del database cronologia
4. **Monitoring**: Monitoraggio uptime e performance

#### Configurazione Firewall Windows

```powershell
# Apri porte per TTS System
New-NetFirewallRule -DisplayName "TTS Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
New-NetFirewallRule -DisplayName "TTS Frontend" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow
```

### 📊 Monitoraggio e Manutenzione

#### Controllo Stato Sistema

```powershell
# Status completo
docker-compose ps

# Logs in tempo reale
docker-compose logs -f backend
docker-compose logs -f frontend

# Statistiche risorse
docker stats
```

#### Backup Database Cronologia

```powershell
# Backup database
docker-compose exec backend cp /app/text_history.db /app/output/backup_$(date +%Y%m%d).db

# Copia backup su host
docker cp $(docker-compose ps -q backend):/app/output/backup_*.db ./backups/
```

### 🛠️ Risoluzione Problemi

#### Problemi Comuni

**❌ Frontend non riesce a connettersi al backend**
```
Soluzione: Verifica che il backend sia raggiungibile dall'IP del server
Test: curl http://[IP-SERVER]:8000/health
```

**❌ Errori Azure Speech Services**
```
Soluzione: Verifica credenziali in .env e connettività internet
Test: docker-compose logs backend | grep Azure
```

**❌ WebSocket disconnessi frequentemente**
```
Soluzione: Configura timeout più alti nel reverse proxy
Aggiungi: proxy_read_timeout 3600; nel nginx
```

#### Test Connettività

```powershell
# Test backend API
curl http://[IP-SERVER]:8000/health

# Test frontend
curl http://[IP-SERVER]:3000

# Test WebSocket (dal frontend)
# Apri Developer Tools > Console nel browser
# Verifica connessione WebSocket attiva
```

### 📱 Accesso Multi-Dispositivo

Il sistema supporta **accesso simultaneo** da:

- 💻 **Desktop** (Windows, Mac, Linux)
- 📱 **Mobile** (iOS, Android) via browser
- 🖥️ **Tablet** con interfaccia responsive

**Funzionalità Collaborative:**
- ✅ Cronologia condivisa in tempo reale
- ✅ Preferenze individuali per dispositivo
- ✅ Audio generato accessibile a tutti
- ✅ Aggiornamenti live tra utenti

### 🎯 Performance in Rete

#### Ottimizzazioni Consigliate

1. **Rete Locale**: Latenza < 5ms per performance ottimali
2. **Banda**: Minimo 10 Mbps per audio HD
3. **CPU Server**: 4+ cores per uso intensivo
4. **RAM Server**: 8GB+ per Azure Speech caching

#### Scaling per Aziende Grandi

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3  # 3 istanze backend
    ports:
      - "8000-8002:8000"
  
  nginx:  # Load balancer
    image: nginx:alpine
    ports:
      - "80:80"
    # Configurazione load balancing
```

---

## 📞 Supporto

Per assistenza tecnica o configurazioni avanzate, consulta:
- 📖 **README.md** per setup base
- 🔧 **FEATURES.md** per funzionalità complete
- 🚀 **QUICKSTART.md** per avvio rapido

**Sistema pronto per deployment enterprise** ✅