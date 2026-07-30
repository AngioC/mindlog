# 📖 MindLog - Diario Personale & Mood Tracker

MindLog è un'applicazione web moderna e reattiva stilizzata in formato Progressive Web App (PWA). Permette agli utenti di registrare i propri pensieri quotidiani, tracciare il proprio stato d'animo (Mood Tracker), organizzare le note tramite Tag personalizzati, filtrare e cercare tra i ricordi, analizzare le proprie statistiche sull'umore e consultare la cronologia in una vista a Calendario.

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
* **Grafici:** Chart.js + `vue-chartjs`
* **PWA Plugin:** `vite-plugin-pwa`

---

## 📦 Dipendenze del Progetto

### Backend (`requirements.txt`)
* `fastapi` - Web framework ad alte prestazioni.
* `uvicorn[standard]` - Server ASGI per l'esecuzione di FastAPI.
* `sqlalchemy` - ORM per la gestione delle tabelle del database.
* `pydantic` - Validazione e serializzazione dei dati.
* `python-jose[cryptography]` - Gestione e firma dei token JWT.
* `passlib[bcrypt]` - Hashing sicuro delle password degli utenti.
* `python-multipart` - Parsing delle richieste form-data per OAuth2.

### Frontend (`package.json`)
```json
{
  "dependencies": {
    "axios": "^1.6.0",
    "chart.js": "^4.4.0",
    "pinia": "^2.1.0",
    "vue": "^3.4.0",
    "vue-chartjs": "^5.3.0",
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

- 🔐 **Autenticazione Sicura:** Login e registrazione con memorizzazione automatica del token JWT in Local Storage e gestione dei token scaduti.
- 📝 **Editor Interattivo & Modifica Inline:** Box di scrittura con selettore data a pillola personalizzato, titolo facoltativo, tag e mood tracker. Possibilità di modificare e aggiornare i pensieri creati precedentemente.
- 🔍 **Ricerca & Filtri Avanzati:** Pannello a comparsa nella Dashboard per la ricerca testuale in tempo reale (in titoli e contenuto) e filtraggio combinato per Tag e punteggio di Umore.
- 📊 **Statistiche & Mood Analytics:** Vista dedicata con grafici dell'andamento emotivo degli ultimi 30 giorni (Chart.js), riepilogo mensile delle note scritte, umore dominante e media dell'umore.
- 📅 **Vista Calendario:** Calendario mensile interattivo per la navigazione rapida tra i giorni e consultazione rapida dei pensieri passati.
- 🏷️ **Gestione Tag:** Sezione iOS-style per la creazione e cancellazione di tag con codice colore personalizzato.
- 🌙 **Dark Mode:** Supporto nativo per il tema scuro attivabile dalle impostazioni e memorizzato nel localStorage.
- 📱 **PWA Installabile:** Configurazione Progressive Web App completa di Web Manifest per l'installazione su mobile (iOS/Android) e desktop.