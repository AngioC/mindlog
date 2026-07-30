import { defineStore } from 'pinia';
import api from '../api/axios';

export const useTagsStore = defineStore('tags', {
  state: () => ({
    tags: [],
    isLoading: false,
  }),
  actions: {
    async fetchTags() {
      this.isLoading = true;
      try {
        const response = await api.get('/tags/');
        this.tags = response.data;
      } catch (error) {
        console.error("Errore nel caricamento dei tag:", error);
      } finally {
        this.isLoading = false;
      }
    },
    async createTag(tagData) {
      try {
        const response = await api.post('/tags/', tagData);
        this.tags.push(response.data);
      } catch (error) {
        console.error("Errore nella creazione del tag:", error);
        throw error;
      }
    },
    async deleteTag(tagId) {
      try {
        await api.delete(`/tags/${tagId}`);
        this.tags = this.tags.filter(t => t.id !== tagId);
      } catch (error) {
        console.error("Errore nell'eliminazione del tag:", error);
        throw error;
      }
    }
  }
});