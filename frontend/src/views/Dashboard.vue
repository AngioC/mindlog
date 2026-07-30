<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useEntriesStore } from '../stores/entries';

const authStore = useAuthStore();
const entriesStore = useEntriesStore();
const router = useRouter();

// Stato per mostrare/nascondere il form di nuovo pensiero
const showNewEntryForm = ref(false);

// Modello per il form (impostiamo la data a oggi come default)
const newEntry = ref({
  title: '',
  content: '',
  entry_date: new Date().toISOString().split('T')[0] // Formato YYYY-MM-DD
});

// Quando la pagina si carica, chiediamo i pensieri al backend
onMounted(() => {
  entriesStore.fetchEntries();
});

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};

const submitEntry = async () => {
  if (!newEntry.value.content) return; // Controllo base
  
  await entriesStore.createEntry(newEntry.value);
  
  // Resetta e chiudi il form
  newEntry.value = { title: '', content: '', entry_date: new Date().toISOString().split('T')[0] };
  showNewEntryForm.value = false;
};

// Funzione per formattare la data in modo leggibile
const formatDate = (dateString) => {
  const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('it-IT', options);
};
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-800">
    <!-- Header (Navbar) -->
    <header class="bg-white shadow-sm border-b">
      <div class="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-2xl font-bold text-brand flex items-center gap-2">
          <span class="text-3xl">📖</span> MindLog
        </h1>
        <button 
          @click="handleLogout" 
          class="text-sm font-medium text-red-600 hover:bg-red-50 px-4 py-2 rounded-lg transition"
        >
          Esci
        </button>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-8">
      
      <!-- Sezione Introduttiva e Bottone Nuovo Pensiero -->
      <div class="flex justify-between items-end mb-8">
        <div>
          <h2 class="text-3xl font-extrabold text-gray-900">Il tuo Diario</h2>
          <p class="text-gray-500 mt-1">Cosa ti passa per la testa oggi?</p>
        </div>
        <button 
          @click="showNewEntryForm = !showNewEntryForm"
          class="bg-brand text-white px-5 py-2.5 rounded-xl font-medium shadow-sm hover:bg-brand-600 transition flex items-center gap-2"
        >
          <span v-if="!showNewEntryForm">+ Scrivi</span>
          <span v-else>Annulla</span>
        </button>
      </div>

      <!-- Form Nuovo Pensiero (A comparsa) -->
      <div v-if="showNewEntryForm" class="bg-white p-6 rounded-2xl shadow-md border mb-8 transition-all">
        <form @submit.prevent="submitEntry" class="space-y-4">
          <div class="flex gap-4">
            <div class="flex-1">
              <input 
                v-model="newEntry.title" 
                type="text" 
                placeholder="Titolo (opzionale)" 
                class="w-full text-lg font-medium px-0 py-2 border-b-2 border-transparent hover:border-gray-200 focus:border-brand focus:outline-none bg-transparent transition"
              >
            </div>
            <div class="w-40">
              <input 
                v-model="newEntry.entry_date" 
                type="date" 
                required
                class="w-full px-3 py-2 border rounded-lg text-sm text-gray-600 focus:outline-none focus:border-brand focus:ring-1 focus:ring-brand"
              >
            </div>
          </div>
          
          <textarea 
            v-model="newEntry.content" 
            required
            placeholder="Caro diario..." 
            rows="5"
            class="w-full p-4 border rounded-xl bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand resize-none transition"
          ></textarea>
          
          <div class="flex justify-end">
            <button type="submit" class="bg-gray-900 text-white px-6 py-2 rounded-lg font-medium hover:bg-gray-800 transition">
              Salva nel diario
            </button>
          </div>
        </form>
      </div>

      <!-- Loading State -->
      <div v-if="entriesStore.isLoading" class="text-center py-12 text-gray-400">
        <p>Caricamento dei pensieri in corso...</p>
      </div>

      <!-- Empty State (Se non ci sono pensieri) -->
      <div v-else-if="entriesStore.entries.length === 0 && !showNewEntryForm" class="text-center py-20 bg-white rounded-3xl border border-dashed border-gray-300">
        <div class="text-5xl mb-4">✍️</div>
        <h3 class="text-xl font-semibold text-gray-700">Il diario è vuoto</h3>
        <p class="text-gray-500 mt-2">Inizia a scrivere il tuo primo pensiero cliccando in alto a destra.</p>
      </div>

      <!-- Lista dei Pensieri -->
      <div v-else class="space-y-6">
        <article 
          v-for="entry in entriesStore.entries" 
          :key="entry.id"
          class="bg-white p-6 rounded-2xl shadow-sm border hover:shadow-md transition-shadow"
        >
          <div class="flex justify-between items-start mb-3">
            <h3 class="text-xl font-bold text-gray-900">
              {{ entry.title || 'Senza titolo' }}
            </h3>
            <span class="text-xs font-semibold uppercase tracking-wider text-gray-400 bg-gray-100 px-3 py-1 rounded-full">
              {{ formatDate(entry.entry_date) }}
            </span>
          </div>
          
          <!-- white-space: pre-wrap mantiene gli a capo (Invio) del testo -->
          <p class="text-gray-600 leading-relaxed whitespace-pre-wrap">{{ entry.content }}</p>
        </article>
      </div>
      
    </main>
  </div>
</template>