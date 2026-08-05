import { defineStore } from 'pinia';
import api from '../api/axios';

export const useMedicationsStore = defineStore('medications', {
  state: () => ({
    medications: [],
    dailyMedications: [], 
    historyStats: [], // NUOVO: Dati per il grafico a barre
    isLoading: false
  }),
  actions: {
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
    async fetchMedicationsByDate(dateStr) {
      try {
        const response = await api.get(`/medications/by-date?target_date=${dateStr}`);
        this.dailyMedications = response.data;
      } catch (error) {
        console.error('Errore nel recupero promemoria farmaci:', error);
      }
    },
    async updateLog(medId, takenCount, dateStr) {
      try {
        const response = await api.post(`/medications/${medId}/log`, { 
          taken_count: takenCount,
          target_date: dateStr 
        });
        const index = this.dailyMedications.findIndex(item => item.medication.id === medId);
        if (index !== -1) {
          this.dailyMedications[index].taken_count = response.data.taken_count;
        }
      } catch (error) {
        console.error("Errore durante l'aggiornamento:", error);
      }
    },
    // NUOVO: Recupera lo storico calcolando in automatico le date
    async fetchHistory(days = 7) {
      try {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - (days - 1)); // -6 per avere 7 giorni totali
        
        const startStr = startDate.toISOString().split('T')[0];
        const endStr = endDate.toISOString().split('T')[0];
        
        const response = await api.get(`/medications/history?start_date=${startStr}&end_date=${endStr}`);
        this.historyStats = response.data;
      } catch (error) {
        console.error('Errore nel recupero storico farmaci:', error);
      }
    }
  }
});