<script setup>
import { onMounted } from 'vue';
import { useMedicationsStore } from '../stores/medications';

const medicationsStore = useMedicationsStore();

onMounted(() => {
  medicationsStore.fetchTodayMedications();
});

const handleDoseToggle = async (medId, currentTaken, indexClicked) => {
  let newTaken = indexClicked + 1;
  // Se l'utente clicca sull'ultima presa effettuata, la deseleziona
  if (newTaken === currentTaken) {
    newTaken = currentTaken - 1;
  }
  await medicationsStore.updateLog(medId, newTaken);
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 font-sans text-slate-800 dark:text-slate-100 pb-24 transition-colors duration-300">
    
    <!-- HEADER -->
    <header class="sticky top-0 z-50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-800 transition-colors duration-300">
      <div class="max-w-md mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-rose-100 dark:bg-rose-900/40 text-rose-500 rounded-xl flex items-center justify-center text-xl shadow-inner">
            💊
          </div>
          <h1 class="text-xl font-bold tracking-tight text-slate-900 dark:text-white">La Mia Routine</h1>
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
      
      <!-- INTRO -->
      <div class="text-center px-4 py-2">
        <p class="text-sm text-slate-500 dark:text-slate-400">
          Tieni traccia delle tue attività quotidiane. Inizia configurando i tuoi farmaci o integratori dalle Impostazioni.
        </p>
      </div>

      <!-- SEZIONE FARMACI -->
      <section class="bg-white dark:bg-slate-800 p-5 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700">
        <h2 class="text-xs font-bold uppercase tracking-widest text-slate-400 mb-6 flex items-center gap-2">
          Promemoria Farmaci di Oggi
        </h2>
        
        <div v-if="medicationsStore.todayMedications.length === 0" class="text-center py-8">
          <span class="text-3xl opacity-50 block mb-2">🍃</span>
          <p class="text-sm text-slate-400">Nessun farmaco configurato.</p>
        </div>

        <div v-else class="space-y-6">
          <div v-for="item in medicationsStore.todayMedications" :key="item.medication.id" class="flex flex-col gap-3 pb-4 border-b border-slate-50 dark:border-slate-700/50 last:border-0 last:pb-0">
            
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="text-2xl">{{ item.medication.icon }}</span>
                <span class="text-sm font-bold text-slate-700 dark:text-slate-200">{{ item.medication.name }}</span>
              </div>
              <span class="text-xs font-bold text-slate-400 bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded-md">
                {{ item.taken_count }} / {{ item.medication.daily_doses }}
              </span>
            </div>
            
            <!-- Checkbox (Dosi) -->
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

    </main>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.2s ease-out forwards; }
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}
</style>