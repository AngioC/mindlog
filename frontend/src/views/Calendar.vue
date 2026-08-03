<script setup>
import { ref, computed, onMounted } from 'vue';
import { useEntriesStore } from '../stores/entries';

const entriesStore = useEntriesStore();

const today = new Date();
const currentDate = ref(new Date(today.getFullYear(), today.getMonth(), 1));
const selectedDate = ref(today.toISOString().split('T')[0]);

const weekdays = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom'];

onMounted(() => {
  if (entriesStore.entries.length === 0) {
    entriesStore.fetchEntries();
  }
});

const formatToISODate = (year, month, day) => {
  const y = year;
  const m = String(month + 1).padStart(2, '0');
  const d = String(day).padStart(2, '0');
  return `${y}-${m}-${d}`;
};

const currentMonthYearLabel = computed(() => {
  return new Intl.DateTimeFormat('it-IT', { month: 'long', year: 'numeric' }).format(currentDate.value);
});

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear();
  const month = currentDate.value.getMonth();
  
  let firstDayIndex = new Date(year, month, 1).getDay() - 1;
  if (firstDayIndex === -1) firstDayIndex = 6; 

  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const days = [];

  for (let i = 0; i < firstDayIndex; i++) {
    days.push(null);
  }

  for (let i = 1; i <= daysInMonth; i++) {
    days.push({
      dateStr: formatToISODate(year, month, i),
      dayNumber: i
    });
  }

  return days;
});

const prevMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1);
};
const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1);
};

const hasEntries = (dateStr) => {
  return entriesStore.entries.some(entry => entry.entry_date === dateStr);
};

const selectedDayEntries = computed(() => {
  return entriesStore.entries.filter(entry => entry.entry_date === selectedDate.value);
});

const formattedSelectedDate = computed(() => {
  if (!selectedDate.value) return '';
  const date = new Date(selectedDate.value);
  return new Intl.DateTimeFormat('it-IT', { weekday: 'long', day: 'numeric', month: 'long' }).format(date);
});
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 font-sans text-slate-800 dark:text-slate-100 pb-24 transition-colors duration-300">
    
    <header class="sticky top-0 z-50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-800 transition-colors duration-300">
      <div class="max-w-md mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-indigo-100 dark:bg-indigo-900/40 text-brand rounded-xl flex items-center justify-center text-xl shadow-inner">📅</div>
          <h1 class="text-xl font-bold tracking-tight text-slate-900 dark:text-white">Calendario</h1>
        </div>

        <router-link 
          to="/" 
          class="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs font-semibold transition-all border border-slate-200/60 dark:border-slate-700"
        >
          <svg class="w-3.5 h-3.5 text-brand" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
          <span>Diario</span>
        </router-link>
      </div>
    </header>

    <main class="max-w-md mx-auto px-4 mt-6 space-y-6">
      
      <section class="bg-white dark:bg-slate-800 p-5 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700 transition-colors duration-300">
        <div class="flex justify-between items-center mb-6 px-2">
          <button @click="prevMonth" class="p-2 text-slate-400 hover:text-brand hover:bg-slate-50 dark:hover:bg-slate-700 rounded-full transition-colors"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg></button>
          <h2 class="text-lg font-bold text-slate-900 dark:text-white capitalize">{{ currentMonthYearLabel }}</h2>
          <button @click="nextMonth" class="p-2 text-slate-400 hover:text-brand hover:bg-slate-50 dark:hover:bg-slate-700 rounded-full transition-colors"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg></button>
        </div>

        <div class="grid grid-cols-7 gap-1 mb-2 text-center">
          <div v-for="day in weekdays" :key="day" class="text-xs font-semibold text-slate-400 uppercase tracking-wider py-1">{{ day }}</div>
        </div>

        <div class="grid grid-cols-7 gap-1">
          <div v-for="(day, index) in calendarDays" :key="index" class="aspect-square flex items-center justify-center p-1">
            <div v-if="!day"></div>
            <button 
              v-else
              @click="selectedDate = day.dateStr"
              class="relative w-full h-full rounded-2xl flex flex-col items-center justify-center text-sm font-medium transition-all duration-200 focus:outline-none"
              :class="[selectedDate === day.dateStr ? 'bg-brand text-white shadow-md shadow-brand/30 scale-105' : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50']"
            >
              <span>{{ day.dayNumber }}</span>
              <span v-if="hasEntries(day.dateStr)" class="absolute bottom-1.5 w-1 h-1 rounded-full" :class="selectedDate === day.dateStr ? 'bg-white' : 'bg-brand'"></span>
            </button>
          </div>
        </div>
      </section>

      <section>
        <h2 class="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider ml-4 mb-4 capitalize">{{ formattedSelectedDate }}</h2>

        <div v-if="selectedDayEntries.length === 0" class="text-center py-10 bg-white/50 dark:bg-slate-800/50 rounded-3xl border border-dashed border-slate-300 dark:border-slate-700">
          <div class="text-3xl mb-2 opacity-50">🍃</div>
          <p class="text-slate-500 dark:text-slate-400 text-sm">Nessun pensiero in questa data.</p>
        </div>

        <div v-else class="space-y-4">
          <article 
            v-for="entry in selectedDayEntries" 
            :key="entry.id"
            class="bg-white dark:bg-slate-800 p-5 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700"
          >
            <div class="flex items-center gap-2 mb-2">
              <span v-if="entry.mood_score" class="text-lg">{{ getMoodEmoji(entry.mood_score) }}</span>
              <h3 v-if="entry.title" class="font-bold text-slate-900 dark:text-white">{{ entry.title }}</h3>
            </div>
            
            <p class="text-slate-600 dark:text-slate-300 text-sm leading-relaxed whitespace-pre-wrap line-clamp-4">{{ entry.content }}</p>

            <!-- Metadati: Tag e Abitudini -->
            <div class="mt-4 flex flex-col gap-2">
              <!-- Tag (Categorie) -->
              <div v-if="entry.tags && entry.tags.length > 0" class="flex flex-wrap gap-1.5 items-center">
                <span class="text-[0.6rem] font-bold uppercase text-slate-400 mr-1">Categorie:</span>
                <span 
                  v-for="tag in entry.tags" :key="tag.id" 
                  class="text-[0.65rem] uppercase tracking-wider px-2 py-0.5 rounded text-white"
                  :style="{ backgroundColor: tag.color }"
                >
                  {{ tag.name }}
                </span>
              </div>
              
              <!-- Abitudini -->
              <div v-if="entry.habits && entry.habits.length > 0" class="flex flex-wrap gap-1.5 items-center">
                <span class="text-[0.6rem] font-bold uppercase text-slate-400 mr-1">Abitudini:</span>
                <span 
                  v-for="habit in entry.habits" :key="habit.id" 
                  class="text-[0.65rem] px-2 py-0.5 rounded font-medium bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 flex items-center gap-1"
                >
                  <span>{{ habit.icon }}</span> {{ habit.name }}
                </span>
              </div>
            </div>
          </article>
        </div>
      </section>

    </main>
  </div>
</template>

<script>
const moods = [
  { score: 1, emoji: '😢', label: 'Triste' },
  { score: 2, emoji: '😕', label: 'Così così' },
  { score: 3, emoji: '😐', label: 'Neutro' },
  { score: 4, emoji: '🙂', label: 'Bene' },
  { score: 5, emoji: '🤩', label: 'Ottimo' }
];

const getMoodEmoji = (score) => {
  const mood = moods.find(m => m.score === score);
  return mood ? mood.emoji : '';
};
</script>