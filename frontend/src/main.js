import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import './style.css'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router) 

if (localStorage.getItem('theme') === 'dark') {
  document.documentElement.classList.add('dark');
}

app.mount('#app')