<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTagsStore } from '../stores/tags';
import { useHabitsStore } from '../stores/habits';
import { useMedicationsStore } from '../stores/medications';
import { useAuthStore } from '../stores/auth';
import api from '../api/axios';

import EmojiPicker from 'vue3-emoji-picker';
import 'vue3-emoji-picker/css';

const tagsStore = useTagsStore();
const habitsStore = useHabitsStore();
const medicationsStore = useMedicationsStore();
const authStore = useAuthStore();
const router = useRouter();

const currentView = ref('main'); // 'main', 'tags', 'habits', 'medications', 'app', 'profile'
const isDarkMode = ref(false);

const newTag = ref({ name: '', color: '#4F46E5' });
const tagErrorMsg = ref('');

// --- LOGICA ABITUDINI ---
const newHabit = ref({ name: '', icon: '💧' });
const habitErrorMsg = ref('');
const showEmojiPicker = ref(false);

const onSelectEmoji = (emoji) => {
  newHabit.value.icon = emoji.i; 
  showEmojiPicker.value = false;
};

const editingHabitId = ref(null);
const editHabitData = ref({ name: '', icon: '' });
const showEditEmojiPicker = ref(false);

const onSelectEditEmoji = (emoji) => {
  editHabitData.value.icon = emoji.i;
  showEditEmojiPicker.value = false;
};

// --- LOGICA FARMACI ---
const newMedication = ref({ name: '', icon: '💊', daily_doses: 1 });
const medErrorMsg = ref('');
const showMedEmojiPicker = ref(false);

const onSelectMedEmoji = (emoji) => {
  newMedication.value.icon = emoji.i;
  showMedEmojiPicker.value = false;
};

const handleCreateMedication = async () => {
  try {
    medErrorMsg.value = '';
    if (!newMedication.value.name || newMedication.value.daily_doses < 1) return;
    await medicationsStore.createMedication(newMedication.value);
    newMedication.value = { name: '', icon: '💊', daily_doses: 1 };
  } catch (error) {
    medErrorMsg.value = error.response?.data?.detail || 'Errore';
  }
};

const handleDeleteMedication = async (id) => {
  if (confirm("Vuoi eliminare questo promemoria?")) {
    await medicationsStore.deleteMedication(id);
  }
};

// --- PROFILO ---
const passData = ref({ oldPassword: '', newPassword: '', confirmPassword: '' });
const profileMsg = ref('');
const profileError = ref('');
const isChangingPassword = ref(false);

onMounted(() => {
  tagsStore.fetchTags();
  habitsStore.fetchHabits();
  medicationsStore.fetchMedications();
  loadUserProfile();
  isDarkMode.value = document.documentElement.classList.contains('dark');
});

const loadUserProfile = async () => {
  if (!authStore.user?.email) {
    try {
      const response = await api.get('/me');
      authStore.user = response.data; 
    } catch (error) { console.error(error); }
  }
};

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
  if (isDarkMode.value) { document.documentElement.classList.add('dark'); localStorage.setItem('theme', 'dark'); } 
  else { document.documentElement.classList.remove('dark'); localStorage.setItem('theme', 'light'); }
};

const handleLogout = () => { if (confirm("Vuoi davvero uscire?")) { authStore.logout(); router.push('/login'); } };

const handleCreateTag = async () => {
  try { tagErrorMsg.value = ''; if (!newTag.value.name) return; await tagsStore.createTag(newTag.value); newTag.value.name = ''; } 
  catch (error) { tagErrorMsg.value = error.response?.data?.detail || 'Errore'; }
};
const handleDeleteTag = async (id) => { if (confirm("Vuoi eliminare questo tag?")) await tagsStore.deleteTag(id); };

const handleCreateHabit = async () => {
  try { 
    habitErrorMsg.value = ''; 
    if (!newHabit.value.name) return; 
    await habitsStore.createHabit(newHabit.value); 
    newHabit.value.name = ''; 
    newHabit.value.icon = '💧'; 
  } catch (error) { habitErrorMsg.value = error.response?.data?.detail || 'Errore'; }
};
const handleDeleteHabit = async (id) => { if (confirm("Vuoi eliminare questa abitudine?")) await habitsStore.deleteHabit(id); };

const startEditingHabit = (habit) => {
  editingHabitId.value = habit.id;
  editHabitData.value = { name: habit.name, icon: habit.icon };
  showEditEmojiPicker.value = false;
};
const cancelEditingHabit = () => { editingHabitId.value = null; showEditEmojiPicker.value = false; };
const handleUpdateHabit = async () => {
  try {
    if (!editHabitData.value.name) return;
    await habitsStore.updateHabit(editingHabitId.value, editHabitData.value);
    editingHabitId.value = null;
  } catch (error) { console.error("Errore", error); }
};

const handleChangePassword = async () => {
  profileError.value = ''; profileMsg.value = '';
  if (passData.value.newPassword !== passData.value.confirmPassword) { profileError.value = "Le password non coincidono."; return; }
  if (passData.value.newPassword.length < 6) { profileError.value = "Minimo 6 caratteri."; return; }
  try {
    isChangingPassword.value = true;
    await api.put('/change-password', { old_password: passData.value.oldPassword, new_password: passData.value.newPassword });
    profileMsg.value = "Password aggiornata!"; passData.value = { oldPassword: '', newPassword: '', confirmPassword: '' };
  } catch (error) { profileError.value = error.response?.data?.detail || "Errore."; } 
  finally { isChangingPassword.value = false; }
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 font-sans text-slate-800 dark:text-slate-100 pb-24 transition-colors duration-300">
    <header class="sticky top-0 z-50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-800 transition-colors duration-300">
      <div class="max-w-md mx-auto px-4 py-4 flex items-center justify-between">
        <button v-if="currentView !== 'main'" @click="currentView = 'main'" class="text-brand flex items-center gap-1 font-medium"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"></path></svg>Indietro</button>
        <div v-else class="w-16"></div> 
        <h1 class="text-[1.15rem] font-semibold tracking-tight text-slate-900 dark:text-white">
          {{ currentView === 'main' ? 'Impostazioni' : (currentView === 'tags' ? 'Tag' : (currentView === 'habits' ? 'Abitudini' : (currentView === 'medications' ? 'Farmaci' : (currentView === 'profile' ? 'Profilo' : 'App')))) }}
        </h1>
        <div class="w-16"></div>
      </div>
    </header>

    <main class="max-w-md mx-auto px-4 mt-6">
      
      <!-- MENU PRINCIPALE -->
      <div v-if="currentView === 'main'" class="space-y-6 animate-fade-in">
        <div>
          <h2 class="text-xs font-semibold text-slate-500 uppercase tracking-wider ml-4 mb-2">Account & Organizzazione</h2>
          <div class="bg-white dark:bg-slate-800 rounded-2xl overflow-hidden shadow-sm border border-slate-100 dark:border-slate-700">
            <button @click="currentView = 'profile'" class="w-full flex items-center justify-between p-4 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/50 border-b border-slate-100 dark:border-slate-700">
              <div class="flex items-center gap-3"><div class="w-8 h-8 rounded-lg bg-orange-100 dark:bg-orange-900/30 text-orange-600 flex items-center justify-center text-lg">👤</div><span class="font-medium">Profilo Utente</span></div><svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
            </button>
            <button @click="currentView = 'tags'" class="w-full flex items-center justify-between p-4 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/50 border-b border-slate-100 dark:border-slate-700">
              <div class="flex items-center gap-3"><div class="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-600 flex items-center justify-center text-lg">🏷️</div><span class="font-medium">Gestione Tag</span></div><svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
            </button>
            <button @click="currentView = 'habits'" class="w-full flex items-center justify-between p-4 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/50 border-b border-slate-100 dark:border-slate-700">
              <div class="flex items-center gap-3"><div class="w-8 h-8 rounded-lg bg-green-100 dark:bg-green-900/30 text-green-600 flex items-center justify-center text-lg">📋</div><span class="font-medium">Tracker Abitudini</span></div><svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
            </button>
            <button @click="currentView = 'medications'" class="w-full flex items-center justify-between p-4 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <div class="flex items-center gap-3"><div class="w-8 h-8 rounded-lg bg-rose-100 dark:bg-rose-900/30 text-rose-600 flex items-center justify-center text-lg">💊</div><span class="font-medium">Gestione Farmaci</span></div><svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
            </button>
          </div>
        </div>

        <div>
          <h2 class="text-xs font-semibold text-slate-500 uppercase tracking-wider ml-4 mb-2">Sistema</h2>
          <div class="bg-white dark:bg-slate-800 rounded-2xl overflow-hidden shadow-sm border border-slate-100 dark:border-slate-700">
            <button @click="currentView = 'app'" class="w-full flex items-center justify-between p-4 border-b border-slate-100 dark:border-slate-700">
              <div class="flex items-center gap-3"><div class="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-600 flex items-center justify-center text-lg">⚙️</div><span class="font-medium">Aspetto e Tema</span></div><svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
            </button>
            <button @click="handleLogout" class="w-full flex items-center justify-between p-4 hover:bg-red-50 dark:hover:bg-red-900/20">
              <div class="flex items-center gap-3"><div class="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-600 flex items-center justify-center text-lg">🚪</div><span class="font-medium text-red-600">Esci dall'Account</span></div>
            </button>
          </div>
        </div>
      </div>

      <!-- ========================================== -->
      <!-- VISTA: FARMACI (MEDICATIONS)               -->
      <!-- ========================================== -->
      <div v-else-if="currentView === 'medications'" class="animate-fade-in space-y-6">
        <div class="bg-white dark:bg-slate-800 p-5 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700">
          <form @submit.prevent="handleCreateMedication" class="flex flex-col gap-4">
            <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Nuovo Promemoria</label>
            
            <div class="flex gap-3 relative">
              <button 
                type="button" @click="showMedEmojiPicker = !showMedEmojiPicker"
                class="w-14 shrink-0 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl px-2 flex items-center justify-center text-2xl shadow-inner hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors"
              >
                {{ newMedication.icon }}
              </button>
              
              <div v-if="showMedEmojiPicker" class="absolute top-14 left-0 z-50 shadow-2xl rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700">
                <EmojiPicker :native="true" :theme="isDarkMode ? 'dark' : 'light'" @select="onSelectMedEmoji" />
              </div>

              <input v-model="newMedication.name" type="text" placeholder="Nome (es. Vitamina C)" required class="flex-1 bg-slate-50 dark:bg-slate-700 border-0 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-rose-500 text-slate-700 dark:text-white">
            </div>

            <div class="flex items-center justify-between bg-slate-50 dark:bg-slate-700 p-3 rounded-xl border border-slate-100 dark:border-slate-600">
              <span class="text-sm font-medium text-slate-600 dark:text-slate-300">Dosi giornaliere</span>
              <div class="flex items-center gap-3">
                <button type="button" @click="newMedication.daily_doses > 1 ? newMedication.daily_doses-- : null" class="w-8 h-8 rounded-full bg-white dark:bg-slate-600 shadow text-slate-500 flex items-center justify-center font-bold hover:text-rose-500">-</button>
                <span class="font-bold text-lg w-4 text-center">{{ newMedication.daily_doses }}</span>
                <button type="button" @click="newMedication.daily_doses++" class="w-8 h-8 rounded-full bg-white dark:bg-slate-600 shadow text-slate-500 flex items-center justify-center font-bold hover:text-rose-500">+</button>
              </div>
            </div>
            
            <button type="submit" class="w-full mt-1 bg-rose-500 text-white py-2.5 rounded-xl font-medium shadow-sm hover:bg-rose-600 transition-all">Aggiungi Promemoria</button>
          </form>
          <p v-if="medErrorMsg" class="text-red-500 text-sm mt-3">{{ medErrorMsg }}</p>
        </div>

        <div>
          <h2 class="text-xs font-semibold text-slate-500 uppercase tracking-wider ml-4 mb-2">I tuoi farmaci</h2>
          <div class="bg-white dark:bg-slate-800 rounded-2xl overflow-hidden shadow-sm border border-slate-100 dark:border-slate-700">
            <div v-if="medicationsStore.isLoading" class="p-4 text-slate-400 text-sm text-center">Caricamento...</div>
            <div v-else-if="medicationsStore.medications.length === 0" class="p-4 text-slate-500 text-sm text-center">Nessun farmaco configurato.</div>
            
            <div v-else class="divide-y divide-slate-100 dark:divide-slate-700">
              <div v-for="med in medicationsStore.medications" :key="med.id" class="flex items-center justify-between p-4">
                <div class="flex items-center gap-3">
                  <span class="text-xl w-10 h-10 bg-slate-50 dark:bg-slate-700 border border-slate-100 dark:border-slate-600 rounded-xl flex items-center justify-center">{{ med.icon }}</span>
                  <div class="flex flex-col">
                    <span class="font-bold text-slate-700 dark:text-slate-200">{{ med.name }}</span>
                    <span class="text-[0.65rem] uppercase tracking-wider text-slate-400 font-semibold">{{ med.daily_doses }} {{ med.daily_doses > 1 ? 'volte' : 'volta' }}/giorno</span>
                  </div>
                </div>
                <button @click="handleDeleteMedication(med.id)" class="text-slate-300 hover:text-red-500 bg-slate-50 dark:bg-slate-700 hover:bg-red-50 p-2 rounded-full transition-colors">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ALTRE VISTE ESISTENTI Omesse per brevità in questa spiegazione, ma INCLUSE NEL TUO CODICE -->
      <div v-else-if="currentView === 'habits'" class="animate-fade-in space-y-6">
        <div class="bg-white dark:bg-slate-800 p-5 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700">
          <form @submit.prevent="handleCreateHabit" class="flex flex-col gap-3">
            <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Nuova Abitudine</label>
            <div class="flex gap-3 relative">
              <button type="button" @click="showEmojiPicker = !showEmojiPicker" class="w-14 shrink-0 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl px-2 flex items-center justify-center text-2xl hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors shadow-inner">{{ newHabit.icon }}</button>
              <div v-if="showEmojiPicker" class="absolute top-14 left-0 z-50 shadow-2xl rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700"><EmojiPicker :native="true" :theme="isDarkMode ? 'dark' : 'light'" @select="onSelectEmoji" /></div>
              <input v-model="newHabit.name" type="text" placeholder="Nome (es. Palestra...)" required class="flex-1 bg-slate-50 dark:bg-slate-700 border-0 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-brand text-slate-700 dark:text-white">
            </div>
            <button type="submit" class="w-full mt-2 bg-green-500 text-white py-2.5 rounded-xl font-medium shadow-sm hover:opacity-90 transition-all">Aggiungi Abitudine</button>
          </form>
          <p v-if="habitErrorMsg" class="text-red-500 text-sm mt-3">{{ habitErrorMsg }}</p>
        </div>
        <div>
          <h2 class="text-xs font-semibold text-slate-500 uppercase tracking-wider ml-4 mb-2">Le tue abitudini</h2>
          <div class="bg-white dark:bg-slate-800 rounded-2xl overflow-hidden shadow-sm border border-slate-100 dark:border-slate-700">
            <div v-if="habitsStore.isLoading" class="p-4 text-slate-400 text-sm text-center">Caricamento...</div>
            <div v-else-if="habitsStore.habits.length === 0" class="p-4 text-slate-500 text-sm text-center">Nessuna abitudine creata.</div>
            <div v-else class="divide-y divide-slate-100 dark:divide-slate-700">
              <div v-for="habit in habitsStore.habits" :key="habit.id" class="p-4">
                <div v-if="editingHabitId !== habit.id" class="flex items-center justify-between">
                  <div class="flex items-center gap-3"><span class="text-xl w-10 h-10 bg-slate-50 dark:bg-slate-700 border border-slate-100 dark:border-slate-600 rounded-xl flex items-center justify-center">{{ habit.icon }}</span><span class="font-medium text-slate-700 dark:text-slate-200">{{ habit.name }}</span></div>
                  <div class="flex items-center gap-1">
                    <button @click="startEditingHabit(habit)" class="text-slate-400 hover:text-brand bg-slate-50 dark:bg-slate-700 hover:bg-indigo-50 p-2 rounded-full transition-colors"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg></button>
                    <button @click="handleDeleteHabit(habit.id)" class="text-slate-400 hover:text-red-500 bg-slate-50 dark:bg-slate-700 hover:bg-red-50 p-2 rounded-full transition-colors"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg></button>
                  </div>
                </div>
                <div v-else class="animate-fade-in">
                  <form @submit.prevent="handleUpdateHabit" class="flex gap-2 relative">
                    <button type="button" @click="showEditEmojiPicker = !showEditEmojiPicker" class="w-12 shrink-0 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl flex items-center justify-center text-xl hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors shadow-inner">{{ editHabitData.icon }}</button>
                    <div v-if="showEditEmojiPicker" class="absolute top-12 left-0 z-50 shadow-2xl rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700"><EmojiPicker :native="true" :theme="isDarkMode ? 'dark' : 'light'" @select="onSelectEditEmoji" /></div>
                    <input v-model="editHabitData.name" type="text" required class="flex-1 min-w-0 bg-slate-50 dark:bg-slate-700 border-0 rounded-xl px-3 py-2 focus:ring-2 focus:ring-brand text-slate-700 dark:text-white">
                    <button type="submit" class="px-3 py-2 bg-brand text-white rounded-xl font-medium shadow-sm hover:opacity-90 transition-all">✓</button>
                    <button type="button" @click="cancelEditingHabit" class="px-3 py-2 bg-slate-200 dark:bg-slate-600 text-slate-700 dark:text-slate-200 rounded-xl font-medium shadow-sm hover:opacity-90 transition-all">✕</button>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- PROFILO -->
      <div v-else-if="currentView === 'profile'" class="animate-fade-in space-y-6">
        <div class="bg-white dark:bg-slate-800 p-5 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 flex items-center gap-4">
          <div class="w-12 h-12 bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 rounded-full flex items-center justify-center text-2xl font-bold">
            {{ authStore.user?.email ? authStore.user.email.charAt(0).toUpperCase() : 'U' }}
          </div>
          <div>
            <p class="text-sm text-slate-500 dark:text-slate-400 font-medium">Accesso effettuato come</p>
            <p class="font-bold text-slate-900 dark:text-white">{{ authStore.user?.email || 'Utente' }}</p>
          </div>
        </div>
        <div class="bg-white dark:bg-slate-800 p-5 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700">
          <h2 class="text-sm font-bold text-slate-900 dark:text-white mb-4">Cambia Password</h2>
          <form @submit.prevent="handleChangePassword" class="space-y-4">
            <div><label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Password Attuale</label><input v-model="passData.oldPassword" type="password" required class="w-full bg-slate-50 dark:bg-slate-700 border-0 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-brand text-slate-700 dark:text-white"></div>
            <div><label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Nuova Password</label><input v-model="passData.newPassword" type="password" required class="w-full bg-slate-50 dark:bg-slate-700 border-0 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-brand text-slate-700 dark:text-white"></div>
            <div><label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Conferma Nuova Password</label><input v-model="passData.confirmPassword" type="password" required class="w-full bg-slate-50 dark:bg-slate-700 border-0 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-brand text-slate-700 dark:text-white"></div>
            <button type="submit" :disabled="isChangingPassword" class="w-full mt-2 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 py-3 rounded-xl font-bold shadow-sm hover:opacity-90 transition-all disabled:opacity-50">{{ isChangingPassword ? 'Salvataggio...' : 'Aggiorna Password' }}</button>
          </form>
          <p v-if="profileError" class="text-red-500 text-sm mt-4 text-center font-medium">{{ profileError }}</p>
          <p v-if="profileMsg" class="text-emerald-500 text-sm mt-4 text-center font-medium">{{ profileMsg }}</p>
        </div>
      </div>
      
      <!-- TAGS -->
      <div v-else-if="currentView === 'tags'" class="animate-fade-in space-y-6">
        <div class="bg-white dark:bg-slate-800 p-5 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700">
          <form @submit.prevent="handleCreateTag" class="flex flex-col gap-3">
            <label class="text-sm font-semibold text-slate-600 dark:text-slate-300">Crea un nuovo tag</label>
            <div class="flex gap-3"><input v-model="newTag.color" type="color" class="w-12 h-12 rounded-xl cursor-pointer border-0 p-1 bg-slate-50 dark:bg-slate-700" title="Scegli il colore"><input v-model="newTag.name" type="text" placeholder="Es. Viaggi, Lavoro..." required class="flex-1 bg-slate-50 dark:bg-slate-700 border-0 rounded-xl px-4 focus:ring-2 focus:ring-brand text-slate-700 dark:text-white"></div>
            <button type="submit" class="w-full mt-2 bg-brand text-white py-2.5 rounded-xl font-medium shadow-sm hover:opacity-90 transition-all">Aggiungi Tag</button>
          </form>
          <p v-if="tagErrorMsg" class="text-red-500 text-sm mt-3">{{ tagErrorMsg }}</p>
        </div>
        <div>
          <h2 class="text-xs font-semibold text-slate-500 uppercase tracking-wider ml-4 mb-2">I tuoi Tag</h2>
          <div class="bg-white dark:bg-slate-800 rounded-2xl overflow-hidden shadow-sm border border-slate-100 dark:border-slate-700">
            <div v-if="tagsStore.isLoading" class="p-4 text-slate-400 text-sm text-center">Caricamento...</div>
            <div v-else-if="tagsStore.tags.length === 0" class="p-4 text-slate-500 text-sm text-center">Nessun tag creato.</div>
            <div v-else class="divide-y divide-slate-100 dark:divide-slate-700">
              <div v-for="tag in tagsStore.tags" :key="tag.id" class="flex items-center justify-between p-4"><div class="flex items-center gap-3"><div class="w-4 h-4 rounded-full" :style="{ backgroundColor: tag.color }"></div><span class="font-medium text-slate-700 dark:text-slate-200">{{ tag.name }}</span></div><button @click="handleDeleteTag(tag.id)" class="text-slate-300 hover:text-red-500 bg-slate-50 dark:bg-slate-700 hover:bg-red-50 p-2 rounded-full transition-colors"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg></button></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- APP -->
      <div v-else-if="currentView === 'app'" class="animate-fade-in">
        <h2 class="text-xs font-semibold text-slate-500 uppercase tracking-wider ml-4 mb-2">Aspetto Visivo</h2>
        <div class="bg-white dark:bg-slate-800 rounded-2xl overflow-hidden shadow-sm border border-slate-100 dark:border-slate-700">
          <div class="flex items-center justify-between p-4">
            <div class="flex items-center gap-3"><div class="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-lg">{{ isDarkMode ? '🌙' : '☀️' }}</div><span class="font-medium text-slate-800 dark:text-slate-200">Tema Scuro</span></div>
            <button @click="toggleTheme" class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-300 focus:outline-none" :class="isDarkMode ? 'bg-brand' : 'bg-slate-200 dark:bg-slate-600'"><span class="inline-block h-5 w-5 transform rounded-full bg-white shadow-md transition-transform duration-300" :class="isDarkMode ? 'translate-x-6' : 'translate-x-1'"></span></button>
          </div>
        </div>
        <p class="mt-3 px-4 text-xs text-slate-500 text-center">La Dark Mode riposa gli occhi durante la scrittura serale.</p>
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
:deep(.v3-emoji-picker) { --ep-color-bg: #ffffff; }
:deep(.dark .v3-emoji-picker) { --ep-color-bg: #1e293b; --ep-color-border: #334155; }
.scrollbar-none::-webkit-scrollbar { display: none; }
.scrollbar-none { -ms-overflow-style: none; scrollbar-width: none; }
</style>