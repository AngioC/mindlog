<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useEntriesStore } from '../stores/entries';
import { useTagsStore } from '../stores/tags';

const authStore = useAuthStore();
const entriesStore = useEntriesStore();
const tagsStore = useTagsStore();
const router = useRouter();

// STATO CREAZIONE
const isComposing = ref(false);
const newEntry = ref({
  title: '',
  content: '',
  entry_date: new Date().toISOString().split('T')[0],
  tag_ids: [],
  mood_score: null 
});

// STATO MODIFICA
const editingId = ref(null);
const editEntryData = ref({});

// STATO FILTRI & RICERCA
const showSearchFilters = ref(false); // <- Nascosto di default!
const searchQuery = ref('');
const selectedTagFilter = ref(null);
const selectedMoodFilter = ref(null);

const moods = [
  { score: 1, emoji: '😢', label: 'Triste' },
  { score: 2, emoji: '😕', label: 'Così così' },
  { score: 3, emoji: '😐', label: 'Neutro' },
  { score: 4, emoji: '🙂', label: 'Bene' },
  { score: 5, emoji: '🤩', label: 'Ottimo' }
];

onMounted(() => {
  entriesStore.fetchEntries();
  tagsStore.fetchTags();
});

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};

// --- LOGICA CREAZIONE E MODIFICA ---
const toggleTag = (tagId, isEdit = false) => {
  const target = isEdit ? editEntryData : newEntry;
  const index = target.value.tag_ids.indexOf(tagId);
  if (index === -1) {
    target.value.tag_ids.push(tagId);
  } else {
    target.value.tag_ids.splice(index, 1);
  }
};

const submitEntry = async () => {
  if (!newEntry.value.content) return;
  await entriesStore.createEntry(newEntry.value);
  newEntry.value = { title: '', content: '', entry_date: new Date().toISOString().split('T')[0], tag_ids: [], mood_score: null };
  isComposing.value = false;
};

const startEditing = (entry) => {
  editingId.value = entry.id;
  editEntryData.value = {
    title: entry.title || '',
    content: entry.content,
    entry_date: entry.entry_date,
    mood_score: entry.mood_score,
    tag_ids: entry.tags ? entry.tags.map(t => t.id) : []
  };
};

const cancelEditing = () => {
  editingId.value = null;
  editEntryData.value = {};
};

const saveEdit = async () => {
  if (!editEntryData.value.content) return;
  await entriesStore.updateEntry(editingId.value, editEntryData.value);
  editingId.value = null;
};

const handleDelete = async (id) => {
  if (confirm("Vuoi davvero eliminare questo pensiero?")) {
    await entriesStore.deleteEntry(id);
  }
};

// --- LOGICA FILTRI E RICERCA COMPUTATA ---
const filteredEntries = computed(() => {
  return entriesStore.entries.filter(entry => {
    const query = searchQuery.value.toLowerCase().trim();
    const matchesQuery = !query || 
      (entry.title && entry.title.toLowerCase().includes(query)) ||
      entry.content.toLowerCase().includes(query);

    const matchesTag = !selectedTagFilter.value || 
      (entry.tags && entry.tags.some(t => t.id === selectedTagFilter.value));

    const matchesMood = !selectedMoodFilter.value || 
      entry.mood_score === selectedMoodFilter.value;

    return matchesQuery && matchesTag && matchesMood;
  });
});

const isFilterActive = computed(() => {
  return searchQuery.value.trim() !== '' || selectedTagFilter.value !== null || selectedMoodFilter.value !== null;
});

// Calcola quanti filtri sono attivi contemporaneamente
const activeFiltersCount = computed(() => {
  let count = 0;
  if (searchQuery.value.trim() !== '') count++;
  if (selectedTagFilter.value !== null) count++;
  if (selectedMoodFilter.value !== null) count++;
  return count;
});

const clearFilters = () => {
  searchQuery.value = '';
  selectedTagFilter.value = null;
  selectedMoodFilter.value = null;
};

// --- FORMATTAZIONE DATE ---
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('it-IT', { day: 'numeric', month: 'long', year: 'numeric' }).format(date);
};

const formatShortDate = (dateString) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('it-IT', { day: 'numeric', month: 'short' }).format(date);
};

const getMoodEmoji = (score) => {
  const mood = moods.find(m => m.score === score);
  return mood ? mood.emoji : '';
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 font-sans text-slate-800 dark:text-slate-100 selection:bg-brand selection:text-white pb-20 transition-colors duration-300">
    
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-800 transition-colors duration-300">
      <div class="max-w-3xl mx-auto px-4 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-brand rounded-xl flex items-center justify-center text-white text-xl shadow-lg shadow-brand/30">✨</div>
          <h1 class="text-xl font-bold tracking-tight text-slate-900 dark:text-white">MindLog</h1>
        </div>

        <!-- Bottone Calendario in alto a destra -->
        <router-link 
          to="/calendar" 
          class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs font-semibold transition-all border border-slate-200/60 dark:border-slate-700"
        >
          <svg class="w-4 h-4 text-brand" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
          <span>Calendario</span>
        </router-link>
      </div>
    </header>

    <main class="max-w-3xl mx-auto px-4 mt-8">
      
      <!-- COMPOSER (BOX DI SCRITTURA) -->
      <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700 p-2 mb-6 transition-all duration-300 focus-within:shadow-md focus-within:border-brand/40">
        <form @submit.prevent="submitEntry" class="p-4 sm:p-5">
          
          <div v-show="isComposing" class="animate-fade-in mb-4">
            <div class="inline-block relative">
              <div class="flex items-center gap-2 bg-slate-100 dark:bg-slate-700/50 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 px-3 py-1.5 rounded-full text-sm font-semibold transition-colors cursor-pointer">
                📅 <span>{{ formatShortDate(newEntry.entry_date) }}</span>
              </div>
              <input 
                v-model="newEntry.entry_date" 
                type="date" 
                required 
                class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                title="Cambia data"
              >
            </div>

            <input 
              v-model="newEntry.title" 
              type="text" 
              placeholder="Titolo (opzionale)" 
              class="w-full mt-4 text-2xl sm:text-3xl font-bold bg-transparent border-0 focus:ring-0 p-0 text-slate-900 dark:text-white placeholder-slate-300 dark:placeholder-slate-600 transition-colors"
            >
          </div>

          <textarea 
            v-model="newEntry.content" 
            @focus="isComposing = true"
            placeholder="Scrivi qui i tuoi pensieri..." 
            :rows="isComposing ? 5 : 1"
            class="w-full bg-transparent border-0 focus:ring-0 p-0 resize-none text-[1.1rem] leading-relaxed text-slate-700 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 transition-all duration-300 mt-2"
          ></textarea>

          <div v-show="isComposing" class="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700 animate-fade-in space-y-4">
            
            <div v-if="tagsStore.tags.length > 0" class="flex flex-wrap gap-2">
              <button
                v-for="tag in tagsStore.tags" :key="tag.id" type="button" @click="toggleTag(tag.id, false)"
                class="text-xs px-3 py-1.5 rounded-lg font-medium transition-all duration-200 border"
                :class="newEntry.tag_ids.includes(tag.id) ? 'shadow-sm' : 'bg-transparent opacity-60 hover:opacity-100'"
                :style="newEntry.tag_ids.includes(tag.id) ? { backgroundColor: tag.color, borderColor: tag.color, color: '#fff' } : { color: tag.color, borderColor: tag.color }"
              >
                {{ tag.name }}
              </button>
            </div>

            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div class="flex items-center gap-3">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Umore</span>
                <div class="flex gap-1.5 bg-slate-50 dark:bg-slate-700 p-1.5 rounded-2xl border border-slate-100 dark:border-slate-600">
                  <button
                    v-for="mood in moods" :key="mood.score" type="button"
                    @click="newEntry.mood_score = newEntry.mood_score === mood.score ? null : mood.score"
                    class="w-8 h-8 flex items-center justify-center text-xl rounded-xl transition-all duration-200"
                    :class="newEntry.mood_score === mood.score ? 'scale-110 bg-white dark:bg-slate-600 shadow-sm saturate-100' : 'saturate-0 opacity-40 hover:opacity-100 hover:saturate-100 hover:scale-110'"
                    :title="mood.label"
                  >
                    {{ mood.emoji }}
                  </button>
                </div>
              </div>
              
              <div class="flex gap-2 w-full sm:w-auto justify-end">
                <button type="button" @click="isComposing = false" class="px-5 py-2 text-sm font-medium text-slate-500 hover:text-slate-800 dark:hover:text-slate-300 transition-colors">Annulla</button>
                <button type="submit" :disabled="!newEntry.content" class="px-6 py-2 bg-brand disabled:bg-slate-300 dark:disabled:bg-slate-700 text-white text-sm font-medium rounded-full shadow-sm hover:shadow-md transition-all">Salva Pensiero</button>
              </div>
            </div>
          </div>
        </form>
      </div>

      <!-- ========================================== -->
      <!-- BARRA AZIONI E PULSANTE MOSTRA FILTRI      -->
      <!-- ========================================== -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xs font-bold uppercase tracking-widest text-slate-400">
          I tuoi ricordi
        </h2>

        <!-- Pulsante per mostrare/nascondere la ricerca -->
        <button 
          @click="showSearchFilters = !showSearchFilters"
          class="relative flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all duration-200 border shadow-sm"
          :class="showSearchFilters || isFilterActive
            ? 'bg-brand text-white border-brand shadow-brand/20' 
            : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700'"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          <span>{{ showSearchFilters ? 'Nascondi Cerca' : 'Cerca e Filtra' }}</span>
          
          <!-- Badge se ci sono filtri attivi -->
          <span 
            v-if="isFilterActive && !showSearchFilters" 
            class="ml-1 px-1.5 py-0.2 bg-white text-brand text-[0.65rem] font-bold rounded-full"
          >
            {{ activeFiltersCount }}
          </span>
        </button>
      </div>

      <!-- ========================================== -->
      <!-- BOX RICERCA E FILTRI (A COMPARSA)          -->
      <!-- ========================================== -->
      <div 
        v-show="showSearchFilters" 
        class="bg-white dark:bg-slate-800 rounded-3xl p-4 sm:p-5 shadow-sm border border-slate-100 dark:border-slate-700 mb-8 space-y-4 animate-fade-in"
      >
        <!-- 1. Barra di Ricerca Testuale -->
        <div class="relative">
          <svg class="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="Cerca per titolo o parola chiave..." 
            class="w-full bg-slate-50 dark:bg-slate-900/60 border-0 rounded-2xl pl-11 pr-4 py-2.5 text-sm text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:ring-2 focus:ring-brand transition-all"
          >
          <button 
            v-if="searchQuery" 
            @click="searchQuery = ''" 
            class="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-sm font-bold"
          >✕</button>
        </div>

        <!-- 2. Filtro per Tag & Filtro per Umore -->
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pt-1">
          
          <!-- Chip Tag -->
          <div v-if="tagsStore.tags.length > 0" class="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0 scrollbar-none">
            <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider mr-1 shrink-0">Tag:</span>
            <button
              v-for="tag in tagsStore.tags"
              :key="tag.id"
              @click="selectedTagFilter = selectedTagFilter === tag.id ? null : tag.id"
              class="text-xs px-2.5 py-1 rounded-lg font-medium transition-all duration-200 border shrink-0"
              :class="selectedTagFilter === tag.id ? 'shadow-sm' : 'opacity-60 hover:opacity-100'"
              :style="{ 
                backgroundColor: selectedTagFilter === tag.id ? tag.color : 'transparent',
                borderColor: tag.color,
                color: selectedTagFilter === tag.id ? '#fff' : tag.color
              }"
            >
              {{ tag.name }}
            </button>
          </div>

          <!-- Chip Umore -->
          <div class="flex items-center gap-2">
            <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider mr-1">Umore:</span>
            <div class="flex gap-1 bg-slate-50 dark:bg-slate-900/60 p-1 rounded-xl">
              <button
                v-for="mood in moods"
                :key="mood.score"
                @click="selectedMoodFilter = selectedMoodFilter === mood.score ? null : mood.score"
                class="w-7 h-7 flex items-center justify-center text-base rounded-lg transition-all"
                :class="selectedMoodFilter === mood.score 
                  ? 'bg-white dark:bg-slate-700 shadow-sm saturate-100 scale-110' 
                  : 'saturate-0 opacity-40 hover:opacity-100 hover:saturate-100'"
                :title="mood.label"
              >
                {{ mood.emoji }}
              </button>
            </div>
          </div>
        </div>

        <!-- Indicatore Filtri Attivi e Bottone Reset -->
        <div v-if="isFilterActive" class="flex justify-between items-center pt-2 border-t border-slate-100 dark:border-slate-700/60 text-xs">
          <span class="text-slate-400">Risultati trovati: <strong class="text-slate-700 dark:text-slate-200">{{ filteredEntries.length }}</strong></span>
          <button @click="clearFilters" class="text-brand font-semibold hover:underline">Azzera filtri</button>
        </div>
      </div>

      <!-- FEED DEI PENSIERI -->
      <div v-if="filteredEntries.length === 0" class="text-center py-16 bg-white/50 dark:bg-slate-800/50 rounded-3xl border border-dashed border-slate-300 dark:border-slate-700">
        <div class="text-4xl mb-3">🔍</div>
        <h3 class="font-bold text-slate-700 dark:text-slate-200">Nessun pensiero trovato</h3>
        <p class="text-slate-400 text-sm mt-1">Prova a modificare i filtri di ricerca per trovare quello che cerchi.</p>
        <button v-if="isFilterActive" @click="clearFilters" class="mt-4 px-4 py-2 bg-slate-200 dark:bg-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 rounded-full hover:opacity-80 transition-all">Azzera tutti i filtri</button>
      </div>

      <TransitionGroup v-else name="list" tag="div" class="space-y-6">
        <article 
          v-for="entry in filteredEntries" 
          :key="entry.id"
          class="group bg-white dark:bg-slate-800 p-6 sm:p-8 rounded-[2rem] shadow-sm hover:shadow-xl hover:-translate-y-1 border border-slate-100/80 dark:border-slate-700/80 transition-all duration-300 relative overflow-hidden"
        >
          <!-- MODALITÀ LETTURA -->
          <div v-if="editingId !== entry.id">
            <div class="flex justify-between items-start mb-4">
              <div>
                <div class="flex items-center gap-3 mb-2">
                  <time class="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                    {{ formatDate(entry.entry_date) }}
                  </time>
                  <span v-if="entry.mood_score" class="text-xl bg-slate-50 dark:bg-slate-700 px-2 rounded-lg" :title="'Umore: ' + entry.mood_score">
                    {{ getMoodEmoji(entry.mood_score) }}
                  </span>
                </div>
                <h3 v-if="entry.title" class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
                  {{ entry.title }}
                </h3>
              </div>
              
              <div class="flex gap-1 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity duration-200">
                <button @click="startEditing(entry)" class="p-2 text-slate-400 hover:text-brand hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-full transition-all" title="Modifica">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                </button>
                <button @click="handleDelete(entry.id)" class="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full transition-all" title="Elimina">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                </button>
              </div>
            </div>
            
            <p class="text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-wrap text-[1.05rem]">{{ entry.content }}</p>

            <div v-if="entry.tags && entry.tags.length > 0" class="mt-5 flex flex-wrap gap-2">
              <span v-for="tag in entry.tags" :key="tag.id" class="text-xs px-2.5 py-1 rounded-md font-medium text-white shadow-sm" :style="{ backgroundColor: tag.color }">
                {{ tag.name }}
              </span>
            </div>
          </div>

          <!-- MODALITÀ MODIFICA -->
          <div v-else class="animate-fade-in">
            <form @submit.prevent="saveEdit">
              <div class="inline-block relative mb-4">
                <div class="flex items-center gap-2 bg-slate-100 dark:bg-slate-700/50 text-slate-600 dark:text-slate-300 px-3 py-1.5 rounded-full text-sm font-semibold">
                  📅 <span>{{ formatShortDate(editEntryData.entry_date) }}</span>
                </div>
                <input v-model="editEntryData.entry_date" type="date" required class="absolute inset-0 w-full h-full opacity-0 cursor-pointer">
              </div>

              <input v-model="editEntryData.title" type="text" placeholder="Titolo (opzionale)" class="w-full mb-3 text-2xl font-bold bg-transparent border-0 focus:ring-0 p-0 text-slate-900 dark:text-white placeholder-slate-300 dark:placeholder-slate-600">
              <textarea v-model="editEntryData.content" required rows="5" class="w-full bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-slate-200 dark:border-slate-700 focus:ring-2 focus:ring-brand p-4 resize-none text-[1.1rem] leading-relaxed text-slate-700 dark:text-slate-200"></textarea>

              <div v-if="tagsStore.tags.length > 0" class="mt-4 flex flex-wrap gap-2">
                <button v-for="tag in tagsStore.tags" :key="tag.id" type="button" @click="toggleTag(tag.id, true)"
                  class="text-xs px-3 py-1.5 rounded-lg font-medium transition-all duration-200 border"
                  :class="editEntryData.tag_ids.includes(tag.id) ? 'shadow-sm' : 'bg-transparent opacity-60'"
                  :style="editEntryData.tag_ids.includes(tag.id) ? { backgroundColor: tag.color, borderColor: tag.color, color: '#fff' } : { color: tag.color, borderColor: tag.color }">
                  {{ tag.name }}
                </button>
              </div>

              <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mt-6">
                <div class="flex gap-1.5 bg-slate-50 dark:bg-slate-700 p-1.5 rounded-2xl border border-slate-100 dark:border-slate-600">
                  <button v-for="mood in moods" :key="mood.score" type="button"
                    @click="editEntryData.mood_score = editEntryData.mood_score === mood.score ? null : mood.score"
                    class="w-8 h-8 flex items-center justify-center text-xl rounded-xl transition-all"
                    :class="editEntryData.mood_score === mood.score ? 'scale-110 bg-white dark:bg-slate-600 shadow-sm saturate-100' : 'saturate-0 opacity-40'">
                    {{ mood.emoji }}
                  </button>
                </div>
                <div class="flex gap-2">
                  <button type="button" @click="cancelEditing" class="px-5 py-2 text-sm font-medium text-slate-500 bg-slate-100 dark:bg-slate-700 rounded-full hover:bg-slate-200 dark:hover:bg-slate-600">Annulla</button>
                  <button type="submit" class="px-6 py-2 bg-brand text-white text-sm font-medium rounded-full shadow-sm hover:opacity-90">Salva Modifiche</button>
                </div>
              </div>
            </form>
          </div>

        </article>
      </TransitionGroup>
      
    </main>
  </div>
</template>

<style>
.list-enter-active,
.list-leave-active { transition: all 0.4s ease; }
.list-enter-from { opacity: 0; transform: translateY(-20px) scale(0.95); }
.list-leave-to { opacity: 0; transform: translateY(20px) scale(0.95); }

.animate-fade-in { animation: fadeIn 0.3s ease-out forwards; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

.scrollbar-none::-webkit-scrollbar {
  display: none;
}
.scrollbar-none {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

input[type="date"]::-webkit-calendar-picker-indicator {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}
</style>