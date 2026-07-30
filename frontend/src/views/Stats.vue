<script setup>
import { computed, onMounted } from 'vue';
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