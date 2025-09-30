FROM node:18-alpine

WORKDIR /app

# Copia package files e installa dipendenze
COPY package*.json ./
RUN npm install --omit=dev

# Copia il codice sorgente
COPY . .

EXPOSE 3000

# Avvia in modalità development per hot reload
CMD ["npm", "start"]
