<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTagsStore } from '../stores/tags';
import { useAuthStore } from '../stores/auth';
import api from '../api/axios'; // Ci servirà per la chiamata di cambio password

const tagsStore = useTagsStore();
const authStore = useAuthStore();
const router = useRouter();

// Navigazione interna stile iOS ('main', 'tags', 'app', 'profile')
const currentView = ref('main');

// Stato Tag
const newTag = ref({ name: '', color: '#4F46E5' });
const errorMsg = ref('');

// Stato Tema (Dark Mode)
const isDarkMode = ref(false);

// Stato Cambio Password
const passData = ref({ oldPassword: '', newPassword: '', confirmPassword: '' });
const profileMsg = ref('');
const profileError = ref('');
const isChangingPassword = ref(false);

onMounted(() => {
  tagsStore.fetchTags();
  loadUserProfile();
  // Controlla se la dark mode è attiva sul tag HTML
  isDarkMode.value = document.documentElement.classList.contains('dark');
});

// --- FUNZIONE PER RECUPERARE IL PROFILO ---
const loadUserProfile = async () => {
  // Se non abbiamo l'email nello store, la chiediamo al backend
  if (!authStore.user?.email) {
    try {
      const response = await api.get('/me');
      // Salviamo l'intero utente (id, email, created_at) nello store
      authStore.user = response.data; 
    } catch (error) {
      console.error("Impossibile recuperare i dati dell'utente:", error);
    }
  }
};

// -- LOGICA TEMA --
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark');
    localStorage.setItem('theme', 'dark');
  } else {
    document.documentElement.classList.remove('dark');
    localStorage.setItem('theme', 'light');
  }
};

// -- LOGICA LOGOUT --
const handleLogout = () => {
  if (confirm("Vuoi davvero uscire da MindLog?")) {
    authStore.logout();
    router.push('/login');
  }
};

// -- LOGICA TAG --
const handleCreateTag = async () => {
  try {
    errorMsg.value = '';
    if (!newTag.value.name) return;
    await tagsStore.createTag(newTag.value);
    newTag.value.name = '';
  } catch (error) {
    errorMsg.value = error.response?.data?.detail || 'Errore nella creazione del tag';
  }
};

const handleDeleteTag = async (id) => {
  if (confirm("Vuoi eliminare questo tag?")) {
    await tagsStore.deleteTag(id);
  }
};

// -- LOGICA CAMBIO PASSWORD --
const handleChangePassword = async () => {
  profileError.value = '';
  profileMsg.value = '';

  if (passData.value.newPassword !== passData.value.confirmPassword) {
    profileError.value = "Le nuove password non coincidono.";
    return;
  }

  if (passData.value.newPassword.length < 6) {
    profileError.value = "La nuova password deve avere almeno 6 caratteri.";
    return;
  }

  try {
    isChangingPassword.value = true;
    await api.put('/change-password', {
      old_password: passData.value.oldPassword,
      new_password: passData.value.newPassword
    });
    
    profileMsg.value = "Password aggiornata con successo!";
    passData.value = { oldPassword: '', newPassword: '', confirmPassword: '' };
  } catch (error) {
    profileError.value = error.response?.data?.detail || "Errore durante il cambio password.";
  } finally {
    isChangingPassword.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 font-sans text-slate-800 dark:text-slate-100 pb-24 transition-colors duration-300">
    
    <!-- HEADER -->
    <header class="sticky top-0 z-50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-800 transition-colors duration-300">
      <div class="max-w-md mx-auto px-4 py-4 flex items-center justify-between">
        
        <!-- Bottone Indietro -->
        <button 
          v-if="currentView !== 'main'" 
          @click="currentView = 'main'"
          class="text-brand flex items-center gap-1 font-medium"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"></path></svg>
          Indietro
        </button>
        <div v-else class="w-16"></div> 
        
        <h1 class="text-[1.15rem] font-semibold tracking-tight text-slate-900 dark:text-white">
          {{ currentView === 'main' ? 'Impostazioni' : (currentView === 'tags' ? 'Gestione Tag' : (currentView === 'profile' ? 'Profilo' : 'App')) }}
        </h1>
        
        <div class="w-16"></div>
      </div>
    </header>

    <main class="max-w-md mx-auto px-4 mt-6">
      
      <!-- ========================================== -->
      <!-- VISTA PRINCIPALE (MENU)                    -->
      <!-- ========================================== -->
      <div v-if="currentView === 'main'" class="space-y-6 animate-fade-in">
        
        <!-- Blocco 1: Account -->
        <div>
          <h2 class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider ml-4 mb-2">Account</h2>
          <div class="bg-white dark:bg-slate-800 rounded-2xl overflow-hidden shadow-sm border border-slate-100 dark:border-slate-700">
            <!-- Riga: Profilo -->
            <button @click="currentView = 'profile'" class="w-full flex items-center justify-between p-4 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/50 active:bg-slate-100 dark:active:bg-slate-700 transition-colors border-b border-slate-100 dark:border-slate-700">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 flex items-center justify-center text-lg">👤</div>
                <div class="flex flex-col items-start">
                  <span class="font-medium">Profilo Utente</span>
                </div>
              </div>
              <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
            </button>
            
            <!-- Riga: Gestione Tag -->
            <button @click="currentView = 'tags'" class="w-full flex items-center justify-between p-4 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/50 active:bg-slate-100 dark:active:bg-slate-700 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-lg">🏷️</div>
                <span class="font-medium">Gestione Tag</span>
              </div>
              <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
            </button>
          </div>
        </div>

        <!-- Blocco 2: Sistema -->
        <div>
          <h2 class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider ml-4 mb-2">Sistema</h2>
          <div class="bg-white dark:bg-slate-800 rounded-2xl overflow-hidden shadow-sm border border-slate-100 dark:border-slate-700">
            <!-- Riga: Impostazioni App -->
            <button @click="currentView = 'app'" class="w-full flex items-center justify-between p-4 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/50 active:bg-slate-100 dark:active:bg-slate-700 transition-colors border-b border-slate-100 dark:border-slate-700">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 flex items-center justify-center text-lg">⚙️</div>
                <span class="font-medium">Aspetto e Tema</span>
              </div>
              <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
            </button>
            
            <!-- Riga: Logout -->
            <button @click="handleLogout" class="w-full flex items-center justify-between p-4 bg-white dark:bg-slate-800 hover:bg-red-50 dark:hover:bg-red-900/20 active:bg-red-100 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-600 flex items-center justify-center text-lg">🚪</div>
                <span class="font-medium text-red-600">Esci dall'Account</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- ========================================== -->
      <!-- VISTA: PROFILO E PASSWORD                  -->
      <!-- ========================================== -->
      <div v-else-if="currentView === 'profile'" class="animate-fade-in space-y-6">
        
        <!-- Info Utente Corrente (Se presenti nello store auth) -->
        <div class="bg-white dark:bg-slate-800 p-5 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 flex items-center gap-4">
          <div class="w-12 h-12 bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 rounded-full flex items-center justify-center text-2xl font-bold">
            {{ authStore.user?.email ? authStore.user.email.charAt(0).toUpperCase() : 'U' }}
          </div>
          <div>
            <p class="text-sm text-slate-500 dark:text-slate-400 font-medium">Accesso effettuato come</p>
            <p class="font-bold text-slate-900 dark:text-white">{{ authStore.user?.email || 'Utente' }}</p>
          </div>
        </div>

        <!-- Modulo Cambio Password -->
        <div class="bg-white dark:bg-slate-800 p-5 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700">
          <h2 class="text-sm font-bold text-slate-900 dark:text-white mb-4">Cambia Password</h2>
          
          <form @submit.prevent="handleChangePassword" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Password Attuale</label>
              <input 
                v-model="passData.oldPassword" 
                type="password" 
                required
                class="w-full bg-slate-50 dark:bg-slate-700 border-0 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-brand text-slate-700 dark:text-white"
              >
            </div>
            
            <div>
              <label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Nuova Password</label>
              <input 
                v-model="passData.newPassword" 
                type="password" 
                required
                class="w-full bg-slate-50 dark:bg-slate-700 border-0 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-brand text-slate-700 dark:text-white"
              >
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Conferma Nuova Password</label>
              <input 
                v-model="passData.confirmPassword" 
                type="password" 
                required
                class="w-full bg-slate-50 dark:bg-slate-700 border-0 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-brand text-slate-700 dark:text-white"
              >
            </div>

            <button 
              type="submit" 
              :disabled="isChangingPassword"
              class="w-full mt-2 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 py-3 rounded-xl font-bold shadow-sm hover:opacity-90 transition-all disabled:opacity-50"
            >
              {{ isChangingPassword ? 'Salvataggio...' : 'Aggiorna Password' }}
            </button>
          </form>

          <!-- Messaggi di Feedback -->
          <p v-if="profileError" class="text-red-500 text-sm mt-4 text-center font-medium">{{ profileError }}</p>
          <p v-if="profileMsg" class="text-emerald-500 text-sm mt-4 text-center font-medium">{{ profileMsg }}</p>
        </div>
      </div>

      <!-- ========================================== -->
      <!-- VISTA: GESTIONE TAG                        -->
      <!-- ========================================== -->
      <div v-else-if="currentView === 'tags'" class="animate-fade-in space-y-6">
        
        <!-- Form Creazione Tag -->
        <div class="bg-white dark:bg-slate-800 p-5 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700">
          <form @submit.prevent="handleCreateTag" class="flex flex-col gap-3">
            <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Crea un nuovo tag</label>
            <div class="flex gap-3">
              <input 
                v-model="newTag.color" 
                type="color" 
                class="w-12 h-12 rounded-xl cursor-pointer border-0 p-1 bg-slate-50 dark:bg-slate-700"
                title="Scegli il colore"
              >
              <input 
                v-model="newTag.name" 
                type="text" 
                placeholder="Es. Viaggi, Lavoro..."
                required
                class="flex-1 bg-slate-50 dark:bg-slate-700 border-0 rounded-xl px-4 focus:ring-2 focus:ring-brand text-slate-700 dark:text-white"
              >
            </div>
            <button type="submit" class="w-full mt-2 bg-brand text-white py-2.5 rounded-xl font-medium shadow-sm hover:opacity-90 transition-all">
              Aggiungi Tag
            </button>
          </form>
          <p v-if="errorMsg" class="text-red-500 text-sm mt-3">{{ errorMsg }}</p>
        </div>

        <!-- Lista Tag -->
        <div>
          <h2 class="text-xs font-semibold text-slate-500 uppercase tracking-wider ml-4 mb-2">I tuoi Tag</h2>
          <div class="bg-white dark:bg-slate-800 rounded-2xl overflow-hidden shadow-sm border border-slate-100 dark:border-slate-700">
            <div v-if="tagsStore.isLoading" class="p-4 text-slate-400 text-sm text-center">Caricamento...</div>
            <div v-else-if="tagsStore.tags.length === 0" class="p-4 text-slate-500 text-sm text-center">Nessun tag creato.</div>
            
            <div v-else class="divide-y divide-slate-100 dark:divide-slate-700">
              <div 
                v-for="tag in tagsStore.tags" 
                :key="tag.id"
                class="flex items-center justify-between p-4"
              >
                <div class="flex items-center gap-3">
                  <div class="w-4 h-4 rounded-full" :style="{ backgroundColor: tag.color }"></div>
                  <span class="font-medium text-slate-700 dark:text-slate-200">{{ tag.name }}</span>
                </div>
                <button 
                  @click="handleDeleteTag(tag.id)" 
                  class="text-slate-300 hover:text-red-500 bg-slate-50 dark:bg-slate-700 hover:bg-red-50 p-2 rounded-full transition-colors"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ========================================== -->
      <!-- VISTA: IMPOSTAZIONI APP (DARK MODE)        -->
      <!-- ========================================== -->
      <div v-else-if="currentView === 'app'" class="animate-fade-in">
        <h2 class="text-xs font-semibold text-slate-500 uppercase tracking-wider ml-4 mb-2">Aspetto Visivo</h2>
        <div class="bg-white dark:bg-slate-800 rounded-2xl overflow-hidden shadow-sm border border-slate-100 dark:border-slate-700">
          
          <!-- Toggle Dark Mode -->
          <div class="flex items-center justify-between p-4">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-lg">
                {{ isDarkMode ? '🌙' : '☀️' }}
              </div>
              <span class="font-medium text-slate-800 dark:text-slate-200">Tema Scuro</span>
            </div>
            
            <!-- Interruttore (Toggle Switch) Stile iOS -->
            <button 
              @click="toggleTheme" 
              class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-300 focus:outline-none"
              :class="isDarkMode ? 'bg-brand' : 'bg-slate-200 dark:bg-slate-600'"
            >
              <span 
                class="inline-block h-5 w-5 transform rounded-full bg-white shadow-md transition-transform duration-300"
                :class="isDarkMode ? 'translate-x-6' : 'translate-x-1'"
              ></span>
            </button>
          </div>
          
        </div>
        <p class="mt-3 px-4 text-xs text-slate-500 text-center">
          La Dark Mode riposa gli occhi durante la scrittura serale.
        </p>
      </div>

    </main>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeInRight 0.25s ease-out forwards;
}
@keyframes fadeInRight {
  from { opacity: 0; transform: translateX(10px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>