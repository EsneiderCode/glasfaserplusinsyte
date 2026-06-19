<template>
  <div style="min-height: 100vh; background: #f1f5f9;">

    <!-- Topbar -->
    <div class="app-topbar">
      <div class="brand">
        <div class="brand-icon">
          <i class="pi pi-list-check"></i>
        </div>
        <div>
          <div class="brand-title">WorkOrders Agent</div>
          <div class="brand-subtitle">UMTELKOMD &mdash; Portal IMASM</div>
        </div>
        <!-- Badge en vista Tablero -->
        <div v-if="$route.path === '/board' && ordersStore.boardTotal > 0" style="margin-left: 0.5rem;">
          <span style="background: #8b5cf6; color: #fff; font-size: 0.72rem; font-weight: 700; padding: 2px 10px; border-radius: 20px;">
            {{ ordersStore.boardTotal }} clasificadas
          </span>
        </div>
        <!-- Badge en vista Ordenes -->
        <div v-else-if="$route.path !== '/board' && ordersStore.total > 0" style="margin-left: 0.5rem; display: flex; align-items: center; gap: 0.35rem;">
          <span style="background: #3b82f6; color: #fff; font-size: 0.72rem; font-weight: 700; padding: 2px 10px; border-radius: 20px;">
            {{ ordersStore.total }} ordenes
          </span>
          <span
            v-if="ordersStore.totalUnclassified > 0 && ordersStore.totalUnclassified < ordersStore.total"
            style="background: #f1f5f9; color: #64748b; font-size: 0.68rem; font-weight: 600; padding: 2px 8px; border-radius: 20px; border: 1px solid #e2e8f0;"
            :title="`${ordersStore.totalUnclassified} sin clasificar de ${ordersStore.total} totales`"
          >
            {{ ordersStore.totalUnclassified }} sin clasificar
          </span>
        </div>
      </div>

      <!-- Nav links -->
      <div style="display: flex; align-items: center; gap: 0.25rem;">
        <button class="nav-link" :class="{ active: $route.path === '/workorders' }" @click="router.push('/workorders')">
          <i class="pi pi-list"></i> Ordenes
        </button>
        <button class="nav-link" :class="{ active: $route.path === '/board' }" @click="router.push('/board')">
          <i class="pi pi-table"></i> Tablero
        </button>
      </div>

      <div style="display: flex; align-items: center; gap: 1rem;">
        <!-- Sync info -->
        <div v-if="ordersStore.sync.running" class="sync-info">
          <ProgressSpinner style="width: 18px; height: 18px;" strokeWidth="6" />
          <span>{{ ordersStore.sync.message || 'Sincronizando...' }}</span>
          <span style="color: #38bdf8; font-weight: 600;">
            {{ ordersStore.sync.orders_synced }} ord. / {{ ordersStore.sync.files_downloaded }} arch.
          </span>
        </div>
        <div v-else-if="ordersStore.lastSyncedAt" class="sync-info">
          <i class="pi pi-check-circle" style="color: #22c55e; font-size: 0.9rem;"></i>
          <span>{{ formatRelative(ordersStore.lastSyncedAt) }}</span>
        </div>

        <Button
          v-if="ordersStore.total > 0 && !ordersStore.sync.running"
          label="Resolver Labels"
          icon="pi pi-tag"
          severity="secondary"
          outlined
          size="small"
          :loading="fixingLabels"
          @click="handleFixLabels"
        />
        <Button
          :label="ordersStore.sync.running ? 'Sincronizando...' : 'Sincronizar'"
          icon="pi pi-refresh"
          :loading="ordersStore.sync.running"
          :disabled="ordersStore.sync.running"
          @click="handleSync"
          size="small"
          style="background: #3b82f6; border-color: #3b82f6; font-weight: 600;"
        />
      </div>
    </div>

    <!-- Sync progress bar -->
    <div v-if="ordersStore.sync.running" class="sync-progress-bar">
      <div class="bar" :style="{ width: syncProgress + '%' }"></div>
    </div>

    <div class="app-content">
      <RouterView />
    </div>

    <Toast />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useRouter } from 'vue-router'
import { useOrdersStore } from './stores/orders'
import api from './services/api'
import Button from 'primevue/button'
import Toast from 'primevue/toast'
import ProgressSpinner from 'primevue/progressspinner'

const ordersStore = useOrdersStore()
const toast = useToast()
const router = useRouter()
const fixingLabels = ref(false)

const syncProgress = computed(() => {
  const s = ordersStore.sync
  if (!s.running) return 0
  return Math.min(95, (s.orders_synced / Math.max(s.orders_synced + 10, 1)) * 100)
})

function formatRelative(date) {
  const diff = Math.floor((Date.now() - date.getTime()) / 1000)
  if (diff < 60) return 'hace menos de 1 min'
  if (diff < 3600) return `hace ${Math.floor(diff / 60)} min`
  return `hace ${Math.floor(diff / 3600)}h`
}

async function handleSync() {
  await ordersStore.triggerSync()
  toast.add({ severity: 'info', summary: 'Sincronizacion iniciada', detail: 'Descargando datos del portal...', life: 3000 })
}

async function handleFixLabels() {
  fixingLabels.value = true
  try {
    const res = await api.fixLabels()
    toast.add({ severity: 'success', summary: 'Labels resueltos', detail: res.data.message, life: 4000 })
    await ordersStore.fetchOrders()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron resolver los labels', life: 3000 })
  } finally {
    fixingLabels.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    ordersStore.fetchMasters(),
    ordersStore.fetchOrders(),
  ])
  ordersStore.checkSyncStatus()
})
</script>
