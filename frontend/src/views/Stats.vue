<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../api/axios';
import { useEntriesStore } from '../stores/entries';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const entriesStore = useEntriesStore();

// --- STATO NAVIGAZIONE TABS ---
const activeTab = ref('overview'); // Valori: 'overview', 'trends', 'ai'

// STATO AI SUMMARY
const aiSummary = ref(null);
const isLoadingAi = ref(false);
const aiError = ref('');

const moods = [
  { score: 1, emoji: '😢', label: 'Triste' },
  { score: 2, emoji: '😕', label: 'Così così' },
  { score: 3, emoji: '😐', label: 'Neutro' },
  { score: 4, emoji: '🙂', label: 'Bene' },
  { score: 5, emoji: '🤩', label: 'Ottimo' }
];

onMounted(() => {
  if (entriesStore.entries.length === 0) {
    entriesStore.fetchEntries();
  }
});

// --- FUNZIONE PER CHIAMARE L'ENDPOINT AI ---
const fetchAiSummary = async () => {
  try {
    isLoadingAi.value = true;
    aiError.value = '';
    const response = await api.get('/stats/ai-summary');
    aiSummary.value = typeof response.data === 'string' ? JSON.parse(response.data) : response.data;
  } catch (error) {
    aiError.value = error.response?.data?.detail || "Errore durante la generazione del resoconto AI.";
  } finally {
    isLoadingAi.value = false;
  }
};

// --- 1. LOGICA STREAKS (GIORNI CONSECUTIVI) ---
const currentStreak = computed(() => {
  if (!entriesStore.entries.length) return 0;
  
  const dates = [...new Set(entriesStore.entries.map(e => e.entry_date.split('T')[0]))]
    .sort((a, b) => new Date(b) - new Date(a));
  
  const formatDate = (d) => d.toISOString().split('T')[0];
  
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  const todayStr = formatDate(today);
  const yesterdayStr = formatDate(yesterday);

  if (dates[0] !== todayStr && dates[0] !== yesterdayStr) return 0;

  let streak = 0;
  let checkDate = new Date(dates[0]);

  for (let i = 0; i < dates.length; i++) {
    if (dates[i] === formatDate(checkDate)) {
      streak++;
      checkDate.setDate(checkDate.getDate() - 1);
    } else {
      break;
    }
  }
  return streak;
});

// --- 2. LOGICA HEATMAP STILE GITHUB ---
const heatmapWeeks = computed(() => {
  const map = {};
  entriesStore.entries.forEach(e => {
    if (e.mood_score) {
      const dStr = e.entry_date.split('T')[0];
      if (!map[dStr]) map[dStr] = { sum: 0, count: 0 };
      map[dStr].sum += e.mood_score;
      map[dStr].count += 1;
    }
  });

  const weeks = [];
  const today = new Date();
  
  const endDay = new Date(today);
  endDay.setDate(today.getDate() + (6 - today.getDay()));
  
  const WEEKS_TO_SHOW = 20;
  let currentDay = new Date(endDay);
  currentDay.setDate(currentDay.getDate() - (WEEKS_TO_SHOW * 7) + 1);

  for (let w = 0; w < WEEKS_TO_SHOW; w++) {
    const week = [];
    for (let d = 0; d < 7; d++) {
      const dStr = currentDay.toISOString().split('T')[0];
      let avgScore = 0;
      if (map[dStr]) avgScore = Math.round(map[dStr].sum / map[dStr].count);
      
      const isFuture = currentDay > today;
      week.push({ 
        date: dStr, 
        score: isFuture ? null : avgScore,
        isEmpty: !isFuture && avgScore === 0
      });
      currentDay.setDate(currentDay.getDate() + 1);
    }
    weeks.push(week);
  }
  return weeks.reverse();
});

const getHeatmapColor = (score, isEmpty) => {
  if (score === null) return 'bg-transparent';
  
  // MODIFICA QUI: Sostituito dark:bg-slate-800 con dark:bg-slate-700
  if (isEmpty) return 'bg-slate-100 dark:bg-slate-700';
  
  const colors = {
    1: 'bg-red-400 dark:bg-red-500',
    2: 'bg-orange-400 dark:bg-orange-500',
    3: 'bg-yellow-400 dark:bg-yellow-500',
    4: 'bg-emerald-400 dark:bg-emerald-500',
    5: 'bg-green-500 dark:bg-green-600'
  };
  return colors[score] || 'bg-brand';
};

// --- ELABORAZIONE DATI PER GRAFICO LINEARE ---
const recentEntriesWithMood = computed(() => {
  return [...entriesStore.entries]
    .filter(e => e.mood_score !== null && e.mood_score !== undefined)
    .sort((a, b) => new Date(a.entry_date) - new Date(b.entry_date))
    .slice(-30);
});

const chartData = computed(() => {
  const labels = recentEntriesWithMood.value.map(e => {
    const d = new Date(e.entry_date);
    return `${d.getDate()}/${d.getMonth() + 1}`;
  });
  const data = recentEntriesWithMood.value.map(e => e.mood_score);

  return {
    labels,
    datasets: [{
      label: 'Livello Umore',
      data,
      borderColor: '#4F46E5',
      backgroundColor: 'rgba(79, 70, 229, 0.1)',
      borderWidth: 3,
      tension: 0.35,
      fill: true,
      pointBackgroundColor: '#4F46E5',
      pointRadius: 5
    }]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      min: 1, max: 5,
      ticks: {
        stepSize: 1,
        callback: (value) => {
          const m = moods.find(x => x.score === value);
          return m ? `${m.emoji}` : value;
        }
      },
      grid: { color: 'rgba(150, 150, 150, 0.1)' }
    },
    x: { grid: { display: false } }
  },
  plugins: { legend: { display: false } }
};

// --- RESOCONTO MESE CORRENTE ---
const currentMonthEntries = computed(() => {
  const now = new Date();
  const currentMonth = now.getMonth();
  const currentYear = now.getFullYear();

  return entriesStore.entries.filter(e => {
    const d = new Date(e.entry_date);
    return d.getMonth() === currentMonth && d.getFullYear() === currentYear;
  });
});

const averageMood = computed(() => {
  const moodList = currentMonthEntries.value.filter(e => e.mood_score);
  if (moodList.length === 0) return null;
  const sum = moodList.reduce((acc, curr) => acc + curr.mood_score, 0);
  return (sum / moodList.length).toFixed(1);
});

const dominantMood = computed(() => {
  const moodList = currentMonthEntries.value.filter(e => e.mood_score);
  if (moodList.length === 0) return null;
  
  const counts = {};
  moodList.forEach(e => { counts[e.mood_score] = (counts[e.mood_score] || 0) + 1; });

  let maxScore = null;
  let maxCount = 0;
  for (const score in counts) {
    if (counts[score] > maxCount) {
      maxCount = counts[score];
      maxScore = Number(score);
    }
  }
  return moods.find(m => m.score === maxScore);
});
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 font-sans text-slate-800 dark:text-slate-100 pb-24 transition-colors duration-300">
    
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-800 transition-colors duration-300">
      <div class="max-w-md mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-indigo-100 dark:bg-indigo-900/40 text-brand rounded-xl flex items-center justify-center text-xl shadow-inner">
            📊
          </div>
          <h1 class="text-xl font-bold tracking-tight text-slate-900 dark:text-white">Statistiche</h1>
        </div>
      </div>
    </header>

    <main class="max-w-md mx-auto px-4 mt-6">
      
      <!-- MENU A SCHEDE (Segmented Control) -->
      <nav class="flex p-1 bg-slate-200/60 dark:bg-slate-800/60 rounded-xl mb-6 shadow-inner border border-slate-200/50 dark:border-slate-700/50">
        <button 
          @click="activeTab = 'overview'" 
          class="flex-1 py-2 text-xs font-bold rounded-lg transition-all duration-200"
          :class="activeTab === 'overview' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'"
        >
          Panoramica
        </button>
        <button 
          @click="activeTab = 'trends'" 
          class="flex-1 py-2 text-xs font-bold rounded-lg transition-all duration-200"
          :class="activeTab === 'trends' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'"
        >
          Andamento
        </button>
        <button 
          @click="activeTab = 'ai'" 
          class="flex-1 py-2 text-xs font-bold rounded-lg transition-all duration-200 flex items-center justify-center gap-1.5"
          :class="activeTab === 'ai' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'"
        >
          <span class="text-brand text-sm leading-none">✨</span>
          <span>AI Insight</span>
        </button>
      </nav>

      <!-- ============================================== -->
      <!-- TAB 1: PANORAMICA (Streaks, riassunto mensile, Heatmap) -->
      <!-- ============================================== -->
      <div v-show="activeTab === 'overview'" class="space-y-6 animate-fade-in">
        
        <!-- STREAKS CARD -->
        <section class="bg-gradient-to-r from-orange-500 to-rose-500 p-5 rounded-3xl shadow-md text-white flex items-center justify-between overflow-hidden relative">
          <div class="absolute -right-4 -top-8 text-8xl opacity-20 rotate-12 pointer-events-none">🔥</div>
          <div class="relative z-10">
            <span class="text-xs font-bold uppercase tracking-wider text-white/80">Continuità</span>
            <div class="text-4xl font-extrabold mt-1 flex items-baseline gap-2">
              {{ currentStreak }}
              <span class="text-lg font-medium text-white/80">Giorni</span>
            </div>
            <p class="text-[0.8rem] text-white/90 mt-1">
              {{ currentStreak > 0 ? "Non spezzare la catena!" : "Scrivi oggi per iniziare la tua striscia." }}
            </p>
          </div>
          <div class="relative z-10 w-14 h-14 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm border border-white/30 text-2xl shadow-inner">
            🔥
          </div>
        </section>

        <!-- RESOCONTO MENSILE CARDS -->
        <section class="grid grid-cols-2 gap-4">
          <!-- Totale Note -->
          <div class="bg-white dark:bg-slate-800 p-5 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700 flex flex-col justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Note Mese</span>
            <div>
              <div class="text-3xl font-extrabold text-slate-900 dark:text-white mt-2">
                {{ currentMonthEntries.length }}
              </div>
              <p class="text-[0.75rem] text-slate-500 dark:text-slate-400 mt-1">pensieri salvati</p>
            </div>
          </div>

          <!-- Umore Prevalente -->
          <div class="bg-white dark:bg-slate-800 p-5 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700 flex flex-col justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Umore Dominante</span>
            <div>
              <div class="text-3xl mt-2 flex items-center gap-2">
                <span>{{ dominantMood ? dominantMood.emoji : '➖' }}</span>
                <span class="text-base font-bold text-slate-800 dark:text-slate-100">{{ dominantMood ? dominantMood.label : 'N/D' }}</span>
              </div>
              <p class="text-[0.75rem] text-slate-500 dark:text-slate-400 mt-1">
                Media: <strong class="text-brand">{{ averageMood || 'N/D' }}</strong> / 5
              </p>
            </div>
          </div>
        </section>

        <!-- HEATMAP UMORE GITHUB STYLE -->
        <section class="bg-white dark:bg-slate-800 p-5 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-bold text-slate-900 dark:text-white">Mappa dell'Umore</h2>
            <span class="text-[0.65rem] text-slate-400 uppercase tracking-widest">Ultimi 5 Mesi</span>
          </div>
          
          <div class="overflow-x-auto scrollbar-none pb-2">
            <div class="flex gap-1.5 min-w-max">
              <div v-for="(week, wIdx) in heatmapWeeks" :key="wIdx" class="flex flex-col gap-1.5">
                <div 
                  v-for="(day, dIdx) in week" :key="dIdx"
                  class="w-3.5 h-3.5 rounded-sm transition-all"
                  :class="getHeatmapColor(day.score, day.isEmpty)"
                  :title="day.score !== null ? `${day.date}: Umore ${day.score || 'N/D'}` : ''"
                ></div>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-end gap-1.5 mt-3 text-[0.65rem] text-slate-400">
            <span>Triste</span>
            <div class="w-2.5 h-2.5 rounded-sm bg-red-400 dark:bg-red-500"></div>
            <div class="w-2.5 h-2.5 rounded-sm bg-orange-400 dark:bg-orange-500"></div>
            <div class="w-2.5 h-2.5 rounded-sm bg-yellow-400 dark:bg-yellow-500"></div>
            <div class="w-2.5 h-2.5 rounded-sm bg-emerald-400 dark:bg-emerald-500"></div>
            <div class="w-2.5 h-2.5 rounded-sm bg-green-500 dark:bg-green-600"></div>
            <span>Felice</span>
          </div>
        </section>
      </div>

      <!-- ============================================== -->
      <!-- TAB 2: ANDAMENTO (Grafico a Linea isolato) -->
      <!-- ============================================== -->
      <div v-show="activeTab === 'trends'" class="space-y-6 animate-fade-in">
        <section class="bg-white dark:bg-slate-800 p-5 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700">
          <h2 class="text-sm font-bold text-slate-900 dark:text-white mb-2">Andamento Umore</h2>
          <p class="text-xs text-slate-500 mb-6">Analisi delle fluttuazioni del tuo umore basata sugli ultimi 30 pensieri registrati.</p>
          
          <div v-if="recentEntriesWithMood.length < 2" class="text-center py-10 text-slate-400 text-sm bg-slate-50 dark:bg-slate-900/50 rounded-2xl border border-dashed border-slate-200 dark:border-slate-700">
            Scrivi almeno 2 pensieri con un indicatore di umore per generare il grafico.
          </div>
          
          <div v-else class="h-72 w-full">
            <Line :data="chartData" :options="chartOptions" />
          </div>
        </section>
      </div>

      <!-- ============================================== -->
      <!-- TAB 3: AI INSIGHT (Schermata esclusiva Groq) -->
      <!-- ============================================== -->
      <div v-show="activeTab === 'ai'" class="space-y-6 animate-fade-in">
        <section class="bg-gradient-to-br from-indigo-900 to-slate-900 text-white p-6 sm:p-8 rounded-3xl shadow-lg border border-indigo-500/20 relative overflow-hidden">
          
          <!-- Sfondo Decorativo -->
          <div class="absolute -right-10 -top-10 w-40 h-40 bg-brand/20 blur-3xl rounded-full pointer-events-none"></div>

          <div class="flex flex-col mb-6 relative z-10">
            <div class="flex items-center gap-3 mb-2">
              <span class="text-3xl">✨</span>
              <h2 class="text-xl font-bold tracking-tight">Insight Intelligente</h2>
            </div>
            <p class="text-indigo-200 text-xs leading-relaxed max-w-sm mt-1">
              Lascia che l'AI legga tra le righe del tuo mese, identificando pattern nascosti e offrendoti una prospettiva esterna.
            </p>
          </div>
          
          <button 
            @click="fetchAiSummary" 
            :disabled="isLoadingAi"
            class="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 disabled:opacity-70 text-sm font-bold rounded-2xl shadow-md transition-all flex items-center justify-center gap-2 relative z-10"
          >
            <span v-if="isLoadingAi" class="animate-spin text-lg">⏳</span>
            <span>{{ isLoadingAi ? 'Elaborazione in corso...' : (aiSummary ? 'Aggiorna Analisi' : 'Genera Analisi AI') }}</span>
          </button>

          <p v-if="aiError" class="text-red-300 text-xs mt-4 bg-red-950/50 p-3 rounded-xl border border-red-800/50 relative z-10">
            {{ aiError }}
          </p>

          <div v-if="aiSummary" class="space-y-5 text-sm mt-6 animate-fade-in pt-6 border-t border-indigo-500/30 relative z-10">
            <div>
              <h3 class="text-xs font-bold uppercase tracking-widest text-indigo-300 mb-3 flex items-center gap-2">
                🌟 Momenti Chiave
              </h3>
              <ul class="space-y-2">
                <li v-for="(item, idx) in aiSummary.highlights" :key="idx" class="flex gap-2 text-slate-200 text-[0.8rem] leading-relaxed bg-white/5 p-2.5 rounded-xl border border-white/5">
                  <span class="text-indigo-400 mt-0.5">•</span>
                  <span>{{ item }}</span>
                </li>
              </ul>
            </div>

            <div>
              <h3 class="text-xs font-bold uppercase tracking-widest text-indigo-300 mb-3 flex items-center gap-2">
                🔄 Temi Ricorrenti
              </h3>
              <div class="flex flex-wrap gap-2">
                <span 
                  v-for="(theme, idx) in aiSummary.recurring_themes" :key="idx"
                  class="bg-indigo-950/80 border border-indigo-500/40 text-indigo-200 text-xs px-3 py-1.5 rounded-full shadow-sm"
                >
                  # {{ theme }}
                </span>
              </div>
            </div>

            <div class="bg-white/10 p-5 rounded-2xl border border-white/10 mt-6 backdrop-blur-sm">
              <h3 class="text-[0.65rem] font-bold uppercase tracking-widest text-indigo-300 mb-2">💡 Riflessione per te</h3>
              <p class="text-white text-[0.85rem] leading-relaxed font-medium italic">
                "{{ aiSummary.advice }}"
              </p>
            </div>
          </div>
        </section>
      </div>

    </main>
  </div>
</template>

<style>
.scrollbar-none::-webkit-scrollbar {
  display: none;
}
.scrollbar-none {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.animate-fade-in {
  animation: fadeIn 0.35s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>