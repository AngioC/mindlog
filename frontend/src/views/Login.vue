<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const email = ref('');
const password = ref('');
const errorMsg = ref('');

const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  try {
    errorMsg.value = '';
    await authStore.login(email.value, password.value);
    router.push('/');
  } catch (error) {
    errorMsg.value = 'Email o password non validi. Riprova.';
  }
};
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-slate-900 transition-colors duration-300 p-4">
    <div class="w-full max-w-md p-8 bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-transparent dark:border-slate-700">
      <h2 class="text-3xl font-bold text-center text-brand mb-6">Accedi a MindLog</h2>
      
      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">Email</label>
          <input 
            v-model="email" 
            type="email" 
            required 
            placeholder="es. mario@email.com"
            class="w-full px-4 py-2 border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand transition"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">Password</label>
          <input 
            v-model="password" 
            type="password" 
            required 
            placeholder="••••••••"
            class="w-full px-4 py-2 border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand transition"
          >
        </div>
        
        <p v-if="errorMsg" class="text-red-500 text-sm font-medium">{{ errorMsg }}</p>
        
        <button 
          type="submit" 
          class="w-full py-3 px-4 bg-brand text-white font-semibold rounded-lg shadow-md hover:opacity-90 transition-opacity"
        >
          Entra nel Diario
        </button>
      </form>
      
      <p class="mt-6 text-center text-sm text-gray-600 dark:text-slate-400">
        Non hai un account? 
        <router-link to="/register" class="text-brand font-semibold hover:underline">
          Registrati qui
        </router-link>
      </p>
    </div>
  </div>
</template>