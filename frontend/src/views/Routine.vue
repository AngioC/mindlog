<script setup>
import { ref, computed, onMounted } from 'vue';
import { useMedicationsStore } from '../stores/medications';

// Importiamo Chart.js
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

// Registriamo i componenti necessari per il grafico ad anello
ChartJS.register(ArcElement, Tooltip, Legend);

const medicationsStore = useMedicationsStore();

// --- LOGICA DATE ---
const getISODate = (dateObj) => {
  const y = dateObj.getFullYear();
  const m = String(dateObj.getMonth() + 1).padStart(2, '0');
  const d = String(dateObj.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
};

const todayStr = getISODate(new Date());
const selectedDate = ref(todayStr);

onMounted(() => {
  medicationsStore.fetchMedicationsByDate(selectedDate.value);
});

const changeDate = (days) => {
  const currentObj = new Date(selectedDate.value);
  currentObj.setDate(currentObj.getDate() + days);
  selectedDate.value = getISODate(currentObj);
  medicationsStore.fetchMedicationsByDate(selectedDate.value);
};

const goToToday = () => {
  selectedDate.value = todayStr;
  medicationsStore.fetchMedicationsByDate(selectedDate.value);
};

const formattedDateLabel = computed(() => {
  if (selectedDate.value === todayStr) return 'Oggi';
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  if (selectedDate.value === getISODate(yesterday)) return 'Ieri';
  const dateObj = new Date(selectedDate.value);
  return new Intl.DateTimeFormat('it-IT', { day: 'numeric', month: 'long', year: 'numeric' }).format(dateObj);
});

const isToday = computed(() => selectedDate.value === todayStr);

// --- LOGICA SPUNTE ---
const handleDoseToggle = async (medId, currentTaken, indexClicked) => {
  let newTaken = indexClicked + 1;
  if (newTaken === currentTaken) {
    newTaken = currentTaken - 1;
  }
  await medicationsStore.updateLog(medId, newTaken, selectedDate.value);
};

// --- LOGICA GRAFICO (COMPUTATA) ---
const dailyStats = computed(() => {
  let taken = 0;
  let total = 0;
  
  medicationsStore.dailyMedications.forEach(item => {
    total += item.medication.daily_doses;
    taken += item.taken_count;
  });
  
  const missed = Math.max(0, total - taken);
  const percentage = total === 0 ? 0 : Math.round((taken / total) * 100);
  
  return { taken, total, missed, percentage };
});

const chartData = computed(() => {
  return {
    labels: ['Prese', 'Da prendere'],
    datasets: [{
      data: dailyStats.value.total === 0 ? [0, 1] : [dailyStats.value.taken, dailyStats.value.missed],
      backgroundColor: ['#f43f5e', '#e2e8f0'], // Colore rosa per il completato, grigio per il mancante
      borderWidth: 0,
      hoverOffset: 2
    }]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '78%', // Rende l'anello molto sottile ed elegante
  plugins: {
    legend: { display: false }, // Nascondiamo la legenda di default per un look più pulito
    tooltip: {
      callbacks: {
        label: function(context) {
          return ` ${context.label}: ${context.raw}`;
        }
      }
    }
  }
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 font-sans text-slate-800 dark:text-slate-100 pb-24 transition-colors duration-300">
    
    <!-- HEADER -->
    <header class="sticky top-0 z-50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-800 transition-colors duration-300">
      <div class="max-w-md mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-rose-100 dark:bg-rose-900/40 text-rose-500 rounded-xl flex items-center justify-center text-xl shadow-inner">💊</div>
          <h1 class="text-xl font-bold tracking-tight text-slate-900 dark:text-white">La Mia Routine</h1>
        </div>
        <router-link to="/" class="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs font-semibold transition-all border border-slate-200/60 dark:border-slate-700">
          <svg class="w-3.5 h-3.5 text-brand" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
          <span>Diario</span>
        </router-link>
      </div>
    </header>

    <main class="max-w-md mx-auto px-4 mt-6 space-y-6">
      
      <!-- NAVIGATORE DATA -->
      <div class="flex items-center justify-between bg-white dark:bg-slate-800 p-2 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700">
        <button @click="changeDate(-1)" class="w-10 h-10 flex items-center justify-center text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20 rounded-xl transition-all">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"></path></svg>
        </button>
        <div class="flex flex-col items-center">
          <span class="text-sm font-bold text-slate-700 dark:text-slate-200 capitalize">{{ formattedDateLabel }}</span>
          <button v-if="!isToday" @click="goToToday" class="text-[0.65rem] uppercase tracking-widest font-bold text-rose-500 hover:underline mt-0.5">Torna a Oggi</button>
        </div>
        <button @click="changeDate(1)" class="w-10 h-10 flex items-center justify-center text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20 rounded-xl transition-all" :class="{ 'opacity-30 pointer-events-none': isToday }">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"></path></svg>
        </button>
      </div>

      <!-- SEZIONE FARMACI -->
      <section class="bg-white dark:bg-slate-800 p-5 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700">
        <h2 class="text-xs font-bold uppercase tracking-widest text-slate-400 mb-6 flex items-center gap-2">
          Promemoria Farmaci
        </h2>
        
        <div v-if="medicationsStore.dailyMedications.length === 0" class="text-center py-8">
          <span class="text-3xl opacity-50 block mb-2">🍃</span>
          <p class="text-sm text-slate-400">Nessun farmaco configurato.</p>
        </div>

        <div v-else class="space-y-6">
          <div v-for="item in medicationsStore.dailyMedications" :key="item.medication.id" class="flex flex-col gap-3 pb-4 border-b border-slate-50 dark:border-slate-700/50 last:border-0 last:pb-0">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="text-2xl">{{ item.medication.icon }}</span>
                <span class="text-sm font-bold text-slate-700 dark:text-slate-200">{{ item.medication.name }}</span>
              </div>
              <span class="text-xs font-bold text-slate-400 bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded-md">
                {{ item.taken_count }} / {{ item.medication.daily_doses }}
              </span>
            </div>
            
            <div class="flex gap-3">
              <button 
                v-for="(_, index) in item.medication.daily_doses" :key="index"
                @click="handleDoseToggle(item.medication.id, item.taken_count, index)"
                class="h-10 flex-1 rounded-xl border-2 transition-all flex items-center justify-center text-white font-bold"
                :class="index < item.taken_count ? 'bg-rose-500 border-rose-500 shadow-sm shadow-rose-500/30' : 'bg-slate-50 dark:bg-slate-700 border-slate-200 dark:border-slate-600 hover:border-rose-300 hover:bg-rose-50 dark:hover:bg-rose-900/20'"
              >
                <svg v-if="index < item.taken_count" class="w-5 h-5 animate-fade-in" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- GRAFICO DI COMPLETAMENTO GIORNALIERO -->
      <section v-if="medicationsStore.dailyMedications.length > 0" class="bg-white dark:bg-slate-800 p-6 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700 flex items-center justify-between">
        <div>
          <h2 class="text-[0.65rem] font-bold uppercase tracking-widest text-slate-400 mb-1">Completamento Odierno</h2>
          <div class="flex items-baseline gap-1">
            <span class="text-4xl font-black text-slate-800 dark:text-white tracking-tight">{{ dailyStats.percentage }}</span>
            <span class="text-xl font-bold text-slate-400">%</span>
          </div>
          <p class="text-xs font-medium text-slate-500 dark:text-slate-400 mt-2">
            Hai preso <strong class="text-rose-500">{{ dailyStats.taken }}</strong> dosi su <strong class="text-slate-700 dark:text-slate-300">{{ dailyStats.total }}</strong>
          </p>
        </div>
        
        <div class="w-24 h-24 relative flex items-center justify-center">
          <!-- Testo al centro dell'anello -->
          <span v-if="dailyStats.percentage === 100" class="absolute text-2xl animate-fade-in">🎉</span>
          <span v-else class="absolute text-sm font-bold text-slate-300 dark:text-slate-600">{{ dailyStats.taken }}/{{ dailyStats.total }}</span>
          
          <Doughnut :data="chartData" :options="chartOptions" />
        </div>
      </section>

    </main>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.2s ease-out forwards; }
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}
/* Modifichiamo leggermente il colore grigio del grafico se siamo in Dark Mode */
:deep(.dark) .bg-white {
  /* Vue chart js non è super reattivo al cambio tema Tailwind live sui canvas, ma per il reload funziona bene */
}
</style>