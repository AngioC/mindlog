# 📖 MindLog - Diario Personale & Mood Tracker

MindLog è un'applicazione web moderna e reattiva stilizzata in formato Progressive Web App (PWA). Permette agli utenti di registrare i propri pensieri quotidiani, tracciare il proprio stato d'animo (Mood Tracker), organizzare le note tramite Tag personalizzati e consultare la cronologia in una vista a Calendario.

---

## 🚀 Tecnologie Utilizzate

### **Backend**
* **Framework:** FastAPI (Python 3.10+)
* **Database ORM:** SQLAlchemy
* **Database Engine:** SQLite (predefinito)
* **Autenticazione:** OAuth2 con Password Flow e JWT (JSON Web Tokens)
* **CORS Middleware:** Abilitato per comunicazione sicura tra origini

### **Frontend**
* **Framework:** Vue.js 3 (Composition API con `<script setup>`)
* **Build Tool:** Vite
* **State Management:** Pinia
* **Routing:** Vue Router (con Navigation Guard per rotte protette)
* **HTTP Client:** Axios (con interceptors per la gestione automatica dei token JWT)
* **CSS Framework:** Tailwind CSS v4 (con supporto Dark Mode nativo)
* **PWA Plugin:** `vite-plugin-pwa`

---

## 📦 Dipendenze del Progetto

### Backend (`requirements.txt`)
* `fastapi` - Web framework ad alte prestazioni.
* `uvicorn` - Server ASGI per l'esecuzione di FastAPI.
* `sqlalchemy` - ORM per la gestione delle tabelle del database.
* `pydantic` - Validazione e serializzazione dei dati.
* `python-jose` - Gestione e firma dei token JWT.
* `passlib[bcrypt]` - Hashing sicuro delle password degli utenti.
* `python-multipart` - Parsing delle richieste form-data per OAuth2.

### Frontend (`package.json`)
```json
{
  "dependencies": {
    "axios": "^1.6.0",
    "pinia": "^2.1.0",
    "vue": "^3.4.0",
    "vue-router": "^4.3.0"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.0.0",
    "@vitejs/plugin-vue": "^5.0.0",
    "tailwindcss": "^4.0.0",
    "vite": "^5.0.0",
    "vite-plugin-pwa": "^0.19.0"
  }
}
```

---

## 🛠️ Guida all'Installazione e Avvio

### 1. Configurazione Backend (FastAPI)

1. Naviga nella cartella del backend:
   ```bash
   cd backend
   ```
2. Crea e attiva un ambiente virtuale (consigliato):
   ```bash
   python -m venv venv
   # Su Windows:
   venv\Scripts\activate
   # Su macOS/Linux:
   source venv/bin/activate
   ```
3. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
4. Avvia il server in modalità sviluppo:
   ```bash
   uvicorn main:app --reload
   ```
   *L'API sarà raggiungibile all'indirizzo `http://127.0.0.1:8000` e la documentazione Swagger sarà disponibile su `http://127.0.0.1:8000/docs`.*

---

### 2. Configurazione Frontend (Vue 3 + Vite)

1. Apri un nuovo terminale e naviga nella cartella del frontend:
   ```bash
   cd frontend
   ```
2. Installa i pacchetti `npm`:
   ```bash
   npm install
   ```
3. Avvia il server di sviluppo:
   ```bash
   npm run dev
   ```
   *L'applicazione sarà accessibile dal browser all'indirizzo `http://localhost:5173`.*

---

## 🌟 Funzionalità Principali

- 🔐 **Autenticazione Sicura:** Login e registrazione con memorizzazione automatica del token JWT in Local Storage e gestione token scaduti.
- 📝 **Editor in Inizio Pagina:** Box di scrittura espandibile con selezione della data nativa tramite pulsante personalizzato e opzione di titolo facoltativo.
- 🏷️ **Gestione Tag:** Creazione di tag colorati dalla sezione Impostazioni e associazione dinamica ai pensieri.
- 🎭 **Mood Tracker:** Selezione rapida dell'umore (da 1 a 5 con emoji visive).
- 📅 **Vista Calendario:** Calendario mensile interattivo con indicatori visivi per i giorni in cui sono presenti delle annotazioni.
- 🌙 **Dark Mode:** Supporto per il tema scuro attivabile e persistente nelle impostazioni.
- 📱 **PWA Installabile:** Predisposta per l'installazione su dispositivi mobile (iOS/Android) o desktop.