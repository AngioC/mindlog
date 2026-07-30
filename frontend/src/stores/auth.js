import { defineStore } from 'pinia';
import api from '../api/axios';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // Inizializza il token leggendolo dal localStorage, se esiste
    token: localStorage.getItem('token') || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(email, password) {
      // FastAPI richiede i dati di login come Form Data (x-www-form-urlencoded)
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await api.post('/login', formData);
      
      this.token = response.data.access_token;
      localStorage.setItem('token', this.token);
    },
    async register(email, password) {
      // La registrazione usa un normale JSON
      await api.post('/signup', { email, password });
      // Dopo esserci registrati, facciamo il login in automatico
      await this.login(email, password);
    },
    logout() {
      this.token = null;
      localStorage.removeItem('token');
    }
  }
});