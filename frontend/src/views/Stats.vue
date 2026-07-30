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
    
    // Se il backend risponde con una stringa JSON, facciamo il parse
    aiSummary.value = typeof response.data === 'string' ? JSON.parse(response.data) : response.data;
  } catch (error) {
    aiError.value = error.response?.data?.detail || "Errore durante la generazione del resoconto AI.";
  } finally {
    isLoadingAi.value = false;
  }
};

// --- ELABORAZIONE DATI PER STATISTICHE ---

// Consideriamo le entry degli ultimi 30 giorni che hanno un mood_score
const recentEntriesWithMood = computed(() => {
  return [...entriesStore.entries]
    .filter(e => e.mood_score !== null && e.mood_score !== undefined)
    .sort((a, b) => new Date(a.entry_date) - new Date(b.entry_date))
    .slice(-30);
});

// Dati per il grafico
const chartData = computed(() => {
  const labels = recentEntriesWithMood.value.map(e => {
    const d = new Date(e.entry_date);
    return `${d.getDate()}/${d.getMonth() + 1}`;
  });
  
  const data = recentEntriesWithMood.value.map(e => e.mood_score);

  return {
    labels,
    datasets: [
      {
        label: 'Livello Umore',
        data,
        borderColor: '#4F46E5',
        backgroundColor: 'rgba(79, 70, 229, 0.1)',
        borderWidth: 3,
        tension: 0.35,
        fill: true,
        pointBackgroundColor: '#4F46E5',
        pointRadius: 5
      }
    ]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      min: 1,
      max: 5,
      ticks: {
        stepSize: 1,
        callback: (value) => {
          const m = moods.find(x => x.score === value);
          return m ? `${m.emoji} ${m.label}` : value;
        }
      },
      grid: { color: 'rgba(150, 150, 150, 0.1)' }
    },
    x: {
      grid: { display: false }
    }
  },
  plugins: {
    legend: { display: false }
  }
};

// Resoconto Mese Corrente
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
  moodList.forEach(e => {
    counts[e.mood_score] = (counts[e.mood_score] || 0) + 1;
  });

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
          <h1 class="text-xl font-bold tracking-tight text-slate-900 dark:text-white">Statistiche & Insights</h1>
        </div>
      </div>
    </header>

    <main class="max-w-md mx-auto px-4 mt-6 space-y-6">
      
      <!-- RESOCONTO MENSILE CARDS -->
      <section class="grid grid-cols-2 gap-4">
        
        <!-- Totale Note -->
        <div class="bg-white dark:bg-slate-800 p-5 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700">
          <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Note Mese</span>
          <div class="text-3xl font-extrabold text-slate-900 dark:text-white mt-2">
            {{ currentMonthEntries.length }}
          </div>
          <p class="text-[0.75rem] text-slate-500 dark:text-slate-400 mt-1">pensieri salvati</p>
        </div>

        <!-- Umore Prevalente -->
        <div class="bg-white dark:bg-slate-800 p-5 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700">
          <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Umore Dominante</span>
          <div class="text-3xl mt-2 flex items-center gap-2">
            <span>{{ dominantMood ? dominantMood.emoji : '➖' }}</span>
            <span class="text-base font-bold text-slate-800 dark:text-slate-100">{{ dominantMood ? dominantMood.label : 'N/D' }}</span>
          </div>
          <p class="text-[0.75rem] text-slate-500 dark:text-slate-400 mt-1">
            Media: <strong class="text-brand">{{ averageMood || 'N/D' }}</strong> / 5
          </p>
        </div>

      </section>

      <!-- CARD AI MONTHLY SUMMARY -->
      <section class="bg-gradient-to-br from-indigo-900 to-slate-900 text-white p-6 rounded-3xl shadow-lg border border-indigo-500/20 relative overflow-hidden">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <span class="text-2xl">✨</span>
            <h2 class="text-base font-bold tracking-tight">Insight Intelligente</h2>
          </div>
          
          <button 
            @click="fetchAiSummary" 
            :disabled="isLoadingAi"
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-xs font-semibold rounded-full shadow-md transition-all flex items-center gap-2"
          >
            <span v-if="isLoadingAi" class="animate-spin">⏳</span>
            <span>{{ isLoadingAi ? 'Elaborazione...' : (aiSummary ? 'Aggiorna' : 'Genera AI') }}</span>
          </button>
        </div>

        <!-- Messaggio di errore se presente -->
        <p v-if="aiError" class="text-red-300 text-xs mb-3 bg-red-950/50 p-3 rounded-xl border border-red-800/50">
          {{ aiError }}
        </p>

        <!-- Stato iniziale vuoto -->
        <p v-if="!aiSummary && !isLoadingAi && !aiError" class="text-slate-300 text-xs leading-relaxed">
          L'AI analizzerà i tuoi pensieri del mese tramite Groq per rilevare momenti chiave, temi ricorrenti e offrirti una riflessione personalizzata.
        </p>

        <!-- Risultati dell'AI -->
        <div v-if="aiSummary" class="space-y-4 text-sm mt-4 animate-fade-in pt-3 border-t border-indigo-500/30">
          
          <!-- Momenti Chiave -->
          <div>
            <h3 class="text-xs font-bold uppercase tracking-wider text-indigo-300 mb-2">🌟 Momenti Chiave</h3>
            <ul class="list-disc list-inside space-y-1 text-slate-200 text-xs">
              <li v-for="(item, idx) in aiSummary.highlights" :key="idx">{{ item }}</li>
            </ul>
          </div>

          <!-- Temi Ricorrenti -->
          <div>
            <h3 class="text-xs font-bold uppercase tracking-wider text-indigo-300 mb-2">🔄 Temi Ricorrenti</h3>
            <div class="flex flex-wrap gap-1.5">
              <span 
                v-for="(theme, idx) in aiSummary.recurring_themes" 
                :key="idx"
                class="bg-indigo-950/80 border border-indigo-500/40 text-indigo-200 text-[0.7rem] px-2.5 py-1 rounded-lg"
              >
                # {{ theme }}
              </span>
            </div>
          </div>

          <!-- Riflessione -->
          <div class="bg-indigo-950/60 p-3.5 rounded-2xl border border-indigo-500/30">
            <h3 class="text-xs font-bold uppercase tracking-wider text-indigo-300 mb-1">💡 Riflessione per te</h3>
            <p class="text-slate-200 text-xs leading-relaxed italic">
              "{{ aiSummary.advice }}"
            </p>
          </div>

        </div>
      </section>

      <!-- GRAFICO ANDAMENTO UMORE -->
      <section class="bg-white dark:bg-slate-800 p-5 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700">
        <h2 class="text-sm font-bold text-slate-900 dark:text-white mb-4">Andamento Umore (Ultimi 30 giorni)</h2>
        
        <div v-if="recentEntriesWithMood.length < 2" class="text-center py-10 text-slate-400 text-sm">
          Scrivi almeno 2 pensieri con l'emoji dell'umore selezionata per generare il grafico.
        </div>
        
        <div v-else class="h-64">
          <Line :data="chartData" :options="chartOptions" />
        </div>
      </section>

    </main>
  </div>
</template>