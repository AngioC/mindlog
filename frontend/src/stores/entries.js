import { defineStore } from 'pinia';
import api from '../api/axios';

export const useEntriesStore = defineStore('entries', {
  state: () => ({
    entries: [],
    isLoading: false,
  }),
  actions: {
    // Recupera la lista dei pensieri
    async fetchEntries() {
      this.isLoading = true;
      try {
        const response = await api.get('/entries/');
        this.entries = response.data;
      } catch (error) {
        console.error("Errore nel caricamento dei pensieri:", error);
      } finally {
        this.isLoading = false;
      }
    },
    // Crea un nuovo pensiero
    async createEntry(entryData) {
      try {
        const response = await api.post('/entries/', entryData);
        // Aggiungiamo il nuovo pensiero in cima alla lista localmente,
        // senza dover ricaricare tutto dal server!
        this.entries.unshift(response.data); 
      } catch (error) {
        console.error("Errore nella creazione del pensiero:", error);
        throw error;
      }
    }
  }
});