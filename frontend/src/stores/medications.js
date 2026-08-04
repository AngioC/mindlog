import { defineStore } from 'pinia';
import api from '../api/axios';

export const useMedicationsStore = defineStore('medications', {
  state: () => ({
    medications: [],
    todayMedications: [],
    isLoading: false
  }),
  actions: {
    // Per le Impostazioni
    async fetchMedications() {
      this.isLoading = true;
      try {
        const response = await api.get('/medications/');
        this.medications = response.data;
      } catch (error) {
        console.error('Errore nel recupero farmaci:', error);
      } finally {
        this.isLoading = false;
      }
    },
    async createMedication(data) {
      const response = await api.post('/medications/', data);
      this.medications.push(response.data);
    },
    async deleteMedication(id) {
      await api.delete(`/medications/${id}`);
      this.medications = this.medications.filter(m => m.id !== id);
    },
    
    // Per la Dashboard (Widget giornaliero)
    async fetchTodayMedications() {
      try {
        const response = await api.get('/medications/today');
        this.todayMedications = response.data;
      } catch (error) {
        console.error('Errore nel recupero promemoria farmaci:', error);
      }
    },
    async updateLog(medId, takenCount) {
      try {
        const response = await api.post(`/medications/${medId}/log`, { taken_count: takenCount });
        const index = this.todayMedications.findIndex(item => item.medication.id === medId);
        if (index !== -1) {
          this.todayMedications[index].taken_count = response.data.taken_count;
        }
      } catch (error) {
        console.error("Errore durante l'aggiornamento della dose:", error);
      }
    }
  }
});