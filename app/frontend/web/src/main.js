import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

console.log('Starting Vue app...')

try {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)
  app.use(router)

  console.log('Vue app created, mounting...')
  app.mount('#app')
  console.log('Vue app mounted successfully!')
} catch (error) {
  console.error('Error starting Vue app:', error)
  document.getElementById('app').innerHTML = `<h1>Error: ${error.message}</h1>`
}