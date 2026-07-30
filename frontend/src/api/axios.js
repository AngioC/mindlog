import axios from 'axios';
import router from '../router'; // Importiamo il router per poter reindirizzare

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
});

// 1. Interceptor per le RICHIESTE (Aggiunge il token)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 2. Interceptor per le RISPOSTE (Gestisce gli errori)
api.interceptors.response.use(
  (response) => response, // Se va tutto bene, procedi normalmente
  (error) => {
    // Se riceviamo un 401 Unauthorized (token scaduto o non valido)
    if (error.response && error.response.status === 401) {
      console.warn("Token scaduto o non valido. Disconnessione in corso...");
      localStorage.removeItem('token'); // Puliamo il token vecchio
      router.push('/login'); // Rimandiamo alla pagina di accesso
    }
    return Promise.reject(error);
  }
);

export default api;