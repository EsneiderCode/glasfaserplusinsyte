import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'

import 'primevue/resources/themes/aura-light-blue/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import './assets/style.css'

import App from './App.vue'
import WorkOrdersList from './views/WorkOrdersList.vue'
import WorkOrderDetail from './views/WorkOrderDetail.vue'
import BoardView from './views/BoardView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/workorders' },
    { path: '/workorders', component: WorkOrdersList },
    { path: '/workorders/:id', component: WorkOrderDetail },
    { path: '/board', component: BoardView },
  ],
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(PrimeVue)
app.use(ToastService)
app.use(ConfirmationService)
app.mount('#app')
