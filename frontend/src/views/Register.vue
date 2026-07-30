<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const email = ref('');
const password = ref('');
const errorMsg = ref('');

const authStore = useAuthStore();
const router = useRouter();

const handleRegister = async () => {
  try {
    errorMsg.value = '';
    // Chiama la registrazione (che poi fa login in automatico)
    await authStore.register(email.value, password.value);
    router.push('/'); // Ti porta dritto alla Dashboard
  } catch (error) {
    // Se l'API restituisce un errore (es. email già usata), lo mostriamo
    errorMsg.value = error.response?.data?.detail || 'Errore durante la registrazione.';
  }
};
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 p-4">
    <div class="w-full max-w-md p-8 bg-white rounded-2xl shadow-xl">
      <h2 class="text-3xl font-bold text-center text-brand mb-6">Crea il tuo MindLog</h2>
      
      <form @submit.prevent="handleRegister" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input 
            v-model="email" 
            type="email" 
            required 
            placeholder="La tua migliore email"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand transition"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input 
            v-model="password" 
            type="password" 
            required 
            placeholder="Scegli una password sicura"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand transition"
          >
        </div>
        
        <p v-if="errorMsg" class="text-red-500 text-sm font-medium">{{ errorMsg }}</p>
        
        <button 
          type="submit" 
          class="w-full py-3 px-4 bg-brand text-white font-semibold rounded-lg shadow-md hover:opacity-90 transition-opacity"
        >
          Registrati
        </button>
      </form>
      
      <p class="mt-6 text-center text-sm text-gray-600">
        Hai già un account? 
        <router-link to="/login" class="text-brand font-semibold hover:underline">
          Accedi
        </router-link>
      </p>
    </div>
  </div>
</template>