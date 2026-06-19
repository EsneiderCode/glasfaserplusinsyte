<template>
  <div>
    <!-- Back + Title -->
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem;">
      <Button icon="pi pi-arrow-left" text rounded @click="router.back()" />
      <div>
        <h2 style="margin: 0; font-size: 1.15rem; color: #1e293b; font-weight: 700;">Orden #{{ orderId }}</h2>
        <span v-if="order" style="font-size: 0.8rem; color: #64748b;">
          {{ order.address_id }} &mdash; {{ order.name }}
        </span>
      </div>
      <div v-if="order" style="margin-left: auto; display: flex; gap: 0.5rem; flex-wrap: wrap;">
        <span v-if="order.appoin_status_label" :class="['status-badge', appointClass(order.appoin_status)]">
          {{ order.appoin_status_label }}
        </span>
        <span v-if="order.workgroup_label" class="status-badge" style="background: #f0fdf4; color: #166534;">
          {{ order.workgroup_label }}
        </span>
        <span v-if="order.priority_label" :class="['status-badge', priorityClass(order.priority)]">
          {{ order.priority_label }}
        </span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" style="display: flex; justify-content: center; padding: 4rem;">
      <ProgressSpinner />
    </div>

    <!-- Not found -->
    <div v-else-if="!order" style="text-align: center; padding: 4rem; color: #94a3b8;">
      <i class="pi pi-exclamation-triangle" style="font-size: 2.5rem; display: block; margin-bottom: 1rem; color: #fbbf24;"></i>
      <p style="font-size: 0.9rem;">Orden no encontrada. Puede que necesites sincronizar primero.</p>
    </div>

    <div v-else>
      <!-- Summary Cards -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.75rem; margin-bottom: 1.25rem;">

        <div class="summary-card">
          <div class="card-icon icon-blue"><i class="pi pi-user"></i></div>
          <div>
            <div class="card-label">Nombre</div>
            <div class="card-value">{{ order.name || '-' }}</div>
            <div v-if="order.mail" class="card-sub">{{ order.mail }}</div>
          </div>
        </div>

        <div class="summary-card">
          <div class="card-icon icon-green"><i class="pi pi-phone"></i></div>
          <div>
            <div class="card-label">Telefono</div>
            <div class="card-value">{{ order.phone || '-' }}</div>
            <div v-if="order.address_id" class="card-sub">ID: {{ order.address_id }}</div>
          </div>
        </div>

        <div class="summary-card">
          <div class="card-icon icon-amber"><i class="pi pi-calendar"></i></div>
          <div>
            <div class="card-label">Cita</div>
            <div class="card-value">{{ order.appoin_date || '-' }}</div>
            <div v-if="order.appoin_slot" class="card-sub">{{ order.appoin_slot }}</div>
          </div>
        </div>

        <div class="summary-card">
          <div class="card-icon icon-purple"><i class="pi pi-users"></i></div>
          <div>
            <div class="card-label">Equipo</div>
            <div class="card-value" style="color: #7c3aed;">{{ order.appoin_team || order.workgroup_label || '-' }}</div>
            <div v-if="order.appoin_subco_label" class="card-sub">{{ order.appoin_subco_label }}</div>
            <div v-if="!order.appoin_team && order.workgroup_label" class="card-sub" style="color: #a78bfa;">Work Group</div>
          </div>
        </div>

        <div class="summary-card">
          <div class="card-icon icon-rose"><i class="pi pi-wrench"></i></div>
          <div>
            <div class="card-label">Install Status</div>
            <div class="card-value" style="font-size: 0.875rem;">{{ order.install_status_label || '-' }}</div>
            <div v-if="order.hc_status_label" class="card-sub">HC: {{ order.hc_status_label }}</div>
          </div>
        </div>

        <div class="summary-card">
          <div class="card-icon icon-slate"><i class="pi pi-building"></i></div>
          <div>
            <div class="card-label">Building (Type / HP / WO)</div>
            <div class="card-value" style="font-size: 0.875rem;">
              {{ [order.building_type_label, order.building_hp, order.building_wo].filter(v => v != null && v !== '').join(' / ') || '-' }}
            </div>
            <div v-if="order.origen_label" class="card-sub">Origen: {{ order.origen_label }}</div>
          </div>
        </div>

      </div>

      <!-- Tabs -->
      <div class="card">
        <TabView>

          <!-- Info General -->
          <TabPanel header="Informacion General">
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 0; padding: 0.5rem 1rem;">
              <div v-for="field in infoFields" :key="field.key" class="detail-field" style="padding: 0.7rem 0.5rem;">
                <div class="field-label">{{ field.label }}</div>
                <div class="field-value">
                  <template v-if="field.badgeStyle">
                    <span v-if="field.badgeStyle === 'priority' && order[field.key]"
                          class="status-badge" :class="priorityClass(order.priority)">
                      {{ order[field.key] }}
                    </span>
                    <span v-else-if="field.badgeStyle !== 'priority' && (field.format ? field.format(order) !== '—' : order[field.key])"
                          class="status-badge" :style="field.badgeStyle">
                      {{ field.format ? field.format(order) : order[field.key] }}
                    </span>
                    <span v-else style="color: #94a3b8;">—</span>
                  </template>
                  <span v-else>{{ field.format ? field.format(order) : (order[field.key] || '—') }}</span>
                </div>
              </div>
            </div>
          </TabPanel>

          <!-- Detalles -->
          <TabPanel header="Detalles">
            <div style="padding: 1rem;">
              <div v-if="order.details && Object.keys(order.details).length > 0"
                style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 0.25rem;">
                <div v-for="(val, key) in order.details" :key="key" class="detail-field" style="padding: 0.6rem 0.5rem;">
                  <div class="field-label">{{ key }}</div>
                  <div class="field-value" style="font-size: 0.82rem;">{{ formatValue(val) }}</div>
                </div>
              </div>
              <div v-else style="text-align: center; padding: 2rem; color: #94a3b8;">Sin detalles adicionales</div>
            </div>
          </TabPanel>

          <!-- Fotos -->
          <TabPanel :header="`Fotos (${order.photos?.length || 0})`">
            <div style="padding: 1rem;">
              <div v-if="order.photos && order.photos.length > 0">
                <!-- Grouped by insyte_fase -->
                <div v-for="grupo in fotosPorFase" :key="grupo.fase" style="margin-bottom: 1.75rem;">
                  <!-- Section header -->
                  <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.75rem;">
                    <div :style="{ background: faseBg(grupo.fase), color: faseColor(grupo.fase) }"
                      style="padding: 3px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.4px; white-space: nowrap;">
                      {{ grupo.fase }}
                    </div>
                    <span style="font-size: 0.72rem; color: #94a3b8;">{{ grupo.fotos.length }} foto{{ grupo.fotos.length !== 1 ? 's' : '' }}</span>
                    <div style="flex: 1; height: 1px; background: #e2e8f0;"></div>
                  </div>

                  <!-- Photos grid -->
                  <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(175px, 1fr)); gap: 0.75rem;">
                    <div
                      v-for="photo in grupo.fotos"
                      :key="photo.filename"
                      @click="openImage(photo)"
                      style="cursor: pointer; border-radius: 10px; overflow: hidden; border: 2px solid #e2e8f0; background: #fff; transition: all 0.15s; box-shadow: 0 1px 3px rgba(0,0,0,0.06);"
                      @mouseenter="e => e.currentTarget.style.borderColor='#3b82f6'"
                      @mouseleave="e => e.currentTarget.style.borderColor='#e2e8f0'"
                    >
                      <!-- Image -->
                      <div style="aspect-ratio: 4/3; background: #f1f5f9; position: relative; overflow: hidden;">
                        <img
                          :src="photo.url"
                          :alt="photo.filename"
                          style="width: 100%; height: 100%; object-fit: cover; display: block;"
                          @error="onImgError"
                        />
                        <!-- fotoId badge -->
                        <div v-if="photo.fotoId"
                          style="position: absolute; top: 6px; left: 6px; background: rgba(0,0,0,0.55); color: #fff; font-size: 0.65rem; font-weight: 700; padding: 1px 7px; border-radius: 10px; backdrop-filter: blur(2px);">
                          {{ photo.fotoId }}
                        </div>
                      </div>
                      <!-- Label + meta -->
                      <div style="padding: 6px 8px; background: #f8fafc; border-top: 1px solid #f1f5f9;">
                        <div v-if="fotoLabel(photo.fotoId)"
                          style="font-size: 0.7rem; font-weight: 600; color: #374151; line-height: 1.3; margin-bottom: 1px;">
                          {{ fotoLabel(photo.fotoId) }}
                        </div>
                        <div v-if="photo.comment"
                          style="font-size: 0.67rem; color: #6366f1; font-style: italic; margin-top: 2px;">
                          {{ photo.comment }}
                        </div>
                        <div v-if="photo.created_at"
                          style="font-size: 0.65rem; color: #94a3b8; margin-top: 1px;">
                          {{ formatPhotoDate(photo.created_at) }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state">
                <i class="pi pi-images"></i>
                <p>Sin fotos. Sincroniza para descargarlas.</p>
              </div>
            </div>
          </TabPanel>

          <!-- Historia -->
          <TabPanel :header="`Historia (${order.history?.length || 0})`">
            <div style="padding: 1rem;">
              <div v-if="order.history && order.history.length > 0"
                class="scroll-y"
                style="max-height: 500px;">
                <div
                  v-for="(h, i) in order.history"
                  :key="i"
                  style="display: flex; gap: 0.75rem; margin-bottom: 0.75rem;"
                >
                  <!-- Timeline dot -->
                  <div style="display: flex; flex-direction: column; align-items: center; padding-top: 4px;">
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #3b82f6; flex-shrink: 0;"></div>
                    <div v-if="i < order.history.length - 1" style="width: 2px; flex: 1; background: #e2e8f0; margin-top: 4px;"></div>
                  </div>
                  <!-- Card -->
                  <div style="flex: 1; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.65rem 0.85rem; margin-bottom: 0.25rem;">
                    <!-- Header: fecha + usuario if available -->
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem; flex-wrap: wrap; gap: 0.25rem;">
                      <span style="font-size: 0.72rem; font-weight: 700; color: #3b82f6;">
                        {{ h.fecha || h.date || h.created_at || h.createdAt || '' }}
                      </span>
                      <span v-if="h.usuario || h.user || h.nombre_usuario"
                        style="font-size: 0.7rem; background: #ede9fe; color: #5b21b6; padding: 1px 8px; border-radius: 10px; font-weight: 600;">
                        {{ h.usuario || h.user || h.nombre_usuario }}
                      </span>
                    </div>
                    <!-- Action/description highlight -->
                    <div v-if="h.accion || h.action || h.descripcion || h.description || h.comentario || h.comment"
                      style="font-size: 0.82rem; color: #1e293b; font-weight: 500; margin-bottom: 0.35rem;">
                      {{ h.accion || h.action || h.descripcion || h.description || h.comentario || h.comment }}
                    </div>
                    <!-- Remaining fields -->
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem 1.25rem;">
                      <div v-for="(val, key) in historyExtraFields(h)" :key="key"
                        style="font-size: 0.72rem;">
                        <span style="color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px;">{{ key }}: </span>
                        <span style="color: #334155;">{{ formatValue(val) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else style="text-align: center; padding: 2rem; color: #94a3b8;">Sin historia</div>
            </div>
          </TabPanel>

          <!-- Boletin -->
          <TabPanel header="Boletin">
            <div style="padding: 1rem;">
              <div v-if="boletinTask && Object.keys(boletinTask).length > 0"
                style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 0;">
                <div v-for="(val, key) in boletinTask" :key="key" class="detail-field" style="padding: 0.6rem 0.5rem;">
                  <div class="field-label">{{ key }}</div>
                  <div class="field-value" style="font-size: 0.82rem;">{{ formatValue(val) }}</div>
                </div>
              </div>
              <div v-else style="text-align: center; padding: 2rem; color: #94a3b8;">Sin datos de boletin</div>
            </div>
          </TabPanel>

          <!-- JSON Raw -->
          <TabPanel header="JSON">
            <div style="padding: 1rem;">
              <pre
                class="scroll-y"
                style="font-size: 0.75rem; background: #0f172a; color: #e2e8f0; border-radius: 10px; padding: 1rem; max-height: 500px; overflow: auto; -webkit-overflow-scrolling: touch; margin: 0; line-height: 1.5;"
              >{{ JSON.stringify(order, null, 2) }}</pre>
            </div>
          </TabPanel>

        </TabView>
      </div>
    </div>

    <!-- Image lightbox -->
    <Dialog v-model:visible="lightboxVisible" :header="lightboxFile?.filename" :modal="true" :maximizable="true" style="max-width: 95vw; max-height: 95vh;">
      <img
        v-if="lightboxFile"
        :src="lightboxFile.url"
        :alt="lightboxFile.filename"
        style="max-width: 100%; max-height: 80vh; object-fit: contain; display: block; margin: auto;"
      />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import Button from 'primevue/button'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'
import RawDataViewer from '../components/RawDataViewer.vue'

const route = useRoute()
const router = useRouter()

const orderId = computed(() => route.params.id)
const order = ref(null)
const loading = ref(true)
const lightboxVisible = ref(false)
const lightboxFile = ref(null)

const boletinTask = computed(() => {
  if (!order.value?.boletin?.tabTask?.task) return order.value?.boletin || {}
  return order.value.boletin.tabTask.task
})

const infoFields = [
  { key: 'address_id', label: 'Address ID' },
  { key: 'origen_label',            label: 'Origen',              badgeStyle: 'background: #fef3c7; color: #92400e;' },
  { key: 'priority_label',          label: 'Prioridad',           badgeStyle: 'priority' },
  { key: 'hc_status_label',         label: 'HC Status',           badgeStyle: 'background: #dbeafe; color: #1d4ed8;' },
  { key: 'install_status_label',    label: 'Install Status',      badgeStyle: 'background: #fee2e2; color: #b91c1c;' },
  { key: 'insyte_status_label',     label: 'Insyte Status',       badgeStyle: 'background: #f0f9ff; color: #0369a1;' },
  { key: 'deploy_status_label',     label: 'Deploy Status',       badgeStyle: 'background: #f0fdfa; color: #0f766e;' },
  { key: 'operational_status_label',label: 'Operational Status',  badgeStyle: 'background: #dcfce7; color: #15803d;' },
  { key: 'pop_status_label',        label: 'POP Status',          badgeStyle: 'background: #ffedd5; color: #c2410c;' },
  { key: 'approve_status_label',    label: 'Approve Status',      badgeStyle: 'background: #dcfce7; color: #166534;' },
  { key: 'ticket_status_label',     label: 'Ticket Status',       badgeStyle: 'background: #ede9fe; color: #5b21b6;' },
  { key: 'building_type_label',     label: 'Building (Type/HP/WO)', badgeStyle: 'background: #f5f3ff; color: #5b21b6;', format: (o) => [o.building_type_label, o.building_hp, o.building_wo].filter(v => v != null && v !== '').join(' / ') || '—' },
  { key: 'appoin_subco_label',      label: 'Appoin Subco',        badgeStyle: 'background: #f0fdf4; color: #166534;' },
  { key: 'mail', label: 'Email' },
  { key: 'synced_at', label: 'Ultima sync' },
]

const appointClassMap = {
  1: 'status-appoin-1',
  2: 'status-appoin-2',
  3: 'status-appoin-3',
  4: 'status-appoin-4',
  5: 'status-appoin-5',
  6: 'status-appoin-6',
  7: 'status-appoin-7',
}
function appointClass(status) {
  return appointClassMap[status] || 'status-appoin-default'
}

function priorityClass(priority) {
  if (priority === 1) return 'priority-high'
  if (priority === 2) return 'priority-mid'
  if (priority === 3) return 'priority-low'
  return 'priority-other'
}

// ===== Photo steps definition (extracted from Insyte portal) =====
const PHOTO_STEPS = [
  { id: '1.1', label: 'Previo trabajos - Pasamuros Exterior',     insyte_fase: 'Obra Civil' },
  { id: '1.2', label: 'Previo trabajos - Pasamuros Interior',     insyte_fase: 'Obra Civil' },
  { id: '2.1', label: 'Post trabajos - Pasamuros Exterior',       insyte_fase: 'Obra Civil' },
  { id: '2.2', label: 'Post trabajos - Pasamuros Interior',       insyte_fase: 'Obra Civil' },
  { id: '3.1', label: 'OTB/AP Abierta - Entrada cable + splitter', insyte_fase: 'OTB/AP' },
  { id: '3.2', label: 'OTB/AP Abierta - Bandeja Fusion',          insyte_fase: 'OTB/AP' },
  { id: '3.3', label: 'OTB/AP Cerrada + Etiqueta Address ID / KLS ID', insyte_fase: 'OTB/AP' },
  { id: '5.1', label: 'Canalizado Interno: OTB/AP a Entrada Vivienda', insyte_fase: 'OTB/AP' },
  { id: '5.4', label: 'Cableado Interno: OTB/AP a Entrada Vivienda',   insyte_fase: 'OTB/AP' },
  { id: '4.1', label: 'ONT/TA Abierta - Entrada cable',           insyte_fase: 'ONT/TA' },
  { id: '4.2', label: 'ONT/TA Abierta - Bandeja Fusion',          insyte_fase: 'ONT/TA' },
  { id: '4.3', label: 'ONT/TA Cerrada + Etiqueta Home ID (QR)',   insyte_fase: 'ONT/TA' },
  { id: '20.1', label: 'Fotos SDU UGG',                           insyte_fase: 'ONT/TA' },
  { id: '21.2', label: 'Fotos MDU UGG',                           insyte_fase: 'ONT/TA' },
  { id: '5.2', label: 'Canalizado Interno: OTB/AP a SammelPunkt', insyte_fase: 'Interior' },
  { id: '5.3', label: 'Canalizado Interno: SammelPunkt a Entrada Vivienda', insyte_fase: 'Interior' },
  { id: '5.5', label: 'Cableado Interno: OTB/AP a SammelPunkt',   insyte_fase: 'Interior' },
  { id: '5.6', label: 'Cableado Interno: SammelPunkt a Entrada Vivienda', insyte_fase: 'Interior' },
  { id: '5.7', label: 'Cableado Interno: Entrada Vivienda - ONT/TA', insyte_fase: 'Interior' },
  { id: '6.1', label: 'Captura Activacion en App Cliente',        insyte_fase: 'Miscellaneous' },
  { id: '7.1', label: 'Patch en POP/NVT',                         insyte_fase: 'Miscellaneous' },
  { id: '8.1', label: 'Luz Roja - Fibras NVT a OTB/AP',           insyte_fase: 'Miscellaneous' },
  { id: '9.1', label: 'Fusion DP/NVT - Bandeja + Etiqueta',       insyte_fase: 'Miscellaneous' },
  { id: '0.0', label: 'Otros Documentos',                         insyte_fase: 'Miscellaneous' },
  { id: '0.1', label: 'Reporte No Ejecucion',                     insyte_fase: 'Miscellaneous' },
  { id: '10.1', label: 'Reporte de Averia',                       insyte_fase: 'Averia HA' },
]

const FASE_ORDER = ['Obra Civil', 'OTB/AP', 'ONT/TA', 'Interior', 'Miscellaneous', 'Averia HA']

const FOTO_LABEL_MAP = Object.fromEntries(PHOTO_STEPS.map(s => [s.id, s.label]))

function fotoLabel(fotoId) {
  return FOTO_LABEL_MAP[fotoId] || null
}

// Group photos by insyte_fase preserving FASE_ORDER
const fotosPorFase = computed(() => {
  if (!order.value?.photos?.length) return []
  const groups = {}
  for (const photo of order.value.photos) {
    const fase = photo.insyte_fase || 'Sin clasificar'
    if (!groups[fase]) groups[fase] = []
    groups[fase].push(photo)
  }
  // Sort photos within each group by fotoId numerically
  for (const fase in groups) {
    groups[fase].sort((a, b) => {
      const ai = parseFloat(a.fotoId || '99')
      const bi = parseFloat(b.fotoId || '99')
      return ai - bi
    })
  }
  // Return groups in defined order, unknown fases at end
  const ordered = []
  for (const fase of FASE_ORDER) {
    if (groups[fase]) ordered.push({ fase, fotos: groups[fase] })
  }
  for (const fase in groups) {
    if (!FASE_ORDER.includes(fase)) ordered.push({ fase, fotos: groups[fase] })
  }
  return ordered
})

const FASE_COLORS = {
  'Obra Civil':   { bg: '#fef9c3', color: '#92400e' },
  'OTB/AP':       { bg: '#dbeafe', color: '#1e40af' },
  'ONT/TA':       { bg: '#dcfce7', color: '#14532d' },
  'Interior':     { bg: '#ede9fe', color: '#4c1d95' },
  'Miscellaneous':{ bg: '#f1f5f9', color: '#334155' },
  'Averia HA':    { bg: '#fee2e2', color: '#7f1d1d' },
}
function faseBg(fase)    { return FASE_COLORS[fase]?.bg    || '#f1f5f9' }
function faseColor(fase) { return FASE_COLORS[fase]?.color || '#334155' }

function formatPhotoDate(dateStr) {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('es-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch {
    return dateStr
  }
}

// ===================================================================

function openImage(photo) {
  lightboxFile.value = photo
  lightboxVisible.value = true
}

function onImgError(e) {
  e.target.style.display = 'none'
}

function formatValue(val) {
  if (val === null || val === undefined) return '—'
  if (typeof val === 'object') return JSON.stringify(val)
  return String(val)
}

const HISTORY_HEADER_KEYS = new Set(['fecha','date','created_at','createdAt','usuario','user','nombre_usuario','accion','action','descripcion','description','comentario','comment'])
function historyExtraFields(h) {
  return Object.fromEntries(Object.entries(h).filter(([k]) => !HISTORY_HEADER_KEYS.has(k)))
}

onMounted(async () => {
  try {
    const res = await api.getOrder(orderId.value)
    order.value = res.data
  } catch (e) {
    console.error('getOrder error', e)
  } finally {
    loading.value = false
  }
})
</script>
