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
    },
    // Elimina pensiero
    async deleteEntry(entryId) {
      try {
        await api.delete(`/entries/${entryId}`);
        // Rimuoviamo il pensiero dalla lista locale senza ricaricare la pagina
        this.entries = this.entries.filter(entry => entry.id !== entryId);
      } catch (error) {
        console.error("Errore durante l'eliminazione:", error);
        throw error;
      }
    },
    // Aggiorna pensiero
    async updateEntry(entryId, entryData) {
      try {
        const response = await api.put(`/entries/${entryId}`, entryData);
        // Troviamo il post nella lista e lo aggiorniamo con i nuovi dati
        const index = this.entries.findIndex(e => e.id === entryId);
        if (index !== -1) {
          this.entries[index] = response.data;
        }
      } catch (error) {
        console.error("Errore durante l'aggiornamento:", error);
        throw error;
      }
    }

  }
});