import { defineStore } from 'pinia';
import api from '../api/axios';

export const useHabitsStore = defineStore('habits', {
  state: () => ({ habits: [], isLoading: false }),
  actions: {
    async fetchHabits() {
      this.isLoading = true;
      try {
        const response = await api.get('/habits/');
        this.habits = response.data;
      } catch (error) { console.error('Errore:', error); } 
      finally { this.isLoading = false; }
    },
    async createHabit(habitData) {
      const response = await api.post('/habits/', habitData);
      this.habits.push(response.data);
    },
    async deleteHabit(id) {
      await api.delete(`/habits/${id}`);
      this.habits = this.habits.filter(h => h.id !== id);
    },
    // AGGIUNGI QUESTA NUOVA FUNZIONE:
    async updateHabit(id, habitData) {
      const response = await api.put(`/habits/${id}`, habitData);
      const index = this.habits.findIndex(h => h.id === id);
      if (index !== -1) {
        this.habits[index] = response.data; // Aggiorna l'elemento nella lista
      }
    }
  }
});