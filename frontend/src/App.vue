<script setup>
import { useAuthStore } from './stores/auth';
import { useRoute } from 'vue-router';

const authStore = useAuthStore();
const route = useRoute();
</script>

<template>
  <router-view></router-view>

  <!-- Bottom Navigation Bar -->
  <nav 
    v-if="authStore.isAuthenticated && route.name !== 'Login' && route.name !== 'Register'" 
    class="fixed bottom-0 inset-x-0 bg-white/80 dark:bg-slate-900/80 backdrop-blur-lg border-t border-slate-200 dark:border-slate-800 pb-safe shadow-[0_-4px_20px_rgba(0,0,0,0.02)] z-50 transition-colors duration-300"
  >
    <div class="max-w-md mx-auto flex justify-around items-center h-16">

      <!-- Bottone Impostazioni -->
      <router-link 
        to="/settings" 
        class="flex flex-col items-center justify-center w-20 h-full text-slate-400 hover:text-brand transition-colors"
        active-class="text-brand font-semibold"
      >
        <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
        <span class="text-[0.65rem] uppercase tracking-wider">Impost.</span>
      </router-link>
      
      <!-- Bottone Dashboard -->
      <router-link 
        to="/" 
        class="flex flex-col items-center justify-center w-20 h-full text-slate-400 hover:text-brand transition-colors"
        active-class="text-brand font-semibold"
      >
        <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
        <span class="text-[0.65rem] uppercase tracking-wider">Diario</span>
      </router-link>

      <!-- NUOVO: Bottone Calendario -->
      <router-link 
        to="/calendar" 
        class="flex flex-col items-center justify-center w-20 h-full text-slate-400 hover:text-brand transition-colors"
        active-class="text-brand font-semibold"
      >
        <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
        <span class="text-[0.65rem] uppercase tracking-wider">Calendario</span>
      </router-link>

    </div>
  </nav>
</template>