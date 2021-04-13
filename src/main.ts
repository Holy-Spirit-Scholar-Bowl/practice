import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createStore } from 'vuex'

export const practiceStore = createStore({})
export const modulesStore = createStore({})

createApp(App)
  .use(router)
  .use(practiceStore)
  .mount('#app')
