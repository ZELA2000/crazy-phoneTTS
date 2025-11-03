FROM node:18-alpine

WORKDIR /app

# Installa dipendenze di sistema se necessarie
RUN apk add --no-cache --virtual .build-deps \
    python3 make g++

# Copia package files e installa dipendenze
COPY package*.json ./
RUN npm install

# Copia il codice sorgente
COPY . .

# Fix permessi per node_modules
RUN chmod -R 755 node_modules/.bin

# Variabili d'ambiente per React
ENV BROWSER=none
ENV CI=true

EXPOSE 3000

# Avvia in modalità development per hot reload
CMD ["npm", "start"]
