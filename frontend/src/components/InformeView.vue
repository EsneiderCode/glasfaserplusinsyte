<template>
  <div class="informe-list">
    <!-- Toolbar: sort + extra cols -->
    <div class="informe-toolbar">
      <button class="informe-sort-btn" @click="toggleDateSort" :title="ordersStore.sortOrder === 'asc' ? 'Fecha: más antigua primero' : 'Fecha: más reciente primero'">
        <i class="pi pi-calendar" style="font-size: 0.72rem;"></i>
        <span>Fecha</span>
        <i :class="ordersStore.sortOrder === 'asc' ? 'pi pi-sort-amount-up-alt' : 'pi pi-sort-amount-down-alt'" style="font-size: 0.72rem;"></i>
        <span style="font-size: 0.68rem; color: #94a3b8; font-weight: 400;">{{ ordersStore.sortOrder === 'asc' ? 'antigua → reciente' : 'reciente → antigua' }}</span>
      </button>
      <div style="width: 1px; height: 18px; background: #e2e8f0; margin: 0 0.25rem;"></div>
      <span style="font-size: 0.75rem; color: #94a3b8;">Columnas extra:</span>
      <MultiSelect
        v-model="extraCols"
        :options="EXTRA_COLS_OPTIONS"
        optionLabel="header"
        optionValue="field"
        placeholder="Agregar columnas"
        display="chip"
        :maxSelectedLabels="0"
        :selectedItemsLabel="extraCols.length + ' columnas'"
        style="max-width: 260px; font-size: 0.78rem;"
        @change="saveExtraCols"
        panelStyle="max-height: 400px"
      />
    </div>

    <!-- Empty state -->
    <div v-if="!orders.length" class="empty-state">
      <i class="pi pi-inbox"></i>
      <p>No hay ordenes con los filtros aplicados.</p>
    </div>

    <!-- Order cards -->
    <div v-for="order in orders" :key="order.id" class="informe-card">
      <!-- Header strip -->
      <div class="informe-header">
        <span class="informe-id">{{ order.address_id || '—' }}</span>
        <span v-if="order.home_id" class="informe-secondary" style="font-family: monospace;">{{ order.home_id }}</span>
        <span v-if="order.street" class="informe-secondary">{{ order.street }}</span>
        <span v-if="order.appoin_date" class="informe-secondary">
          <i class="pi pi-calendar" style="font-size: 0.6rem; margin-right: 3px; opacity: 0.6;"></i>{{ order.appoin_date }}<span v-if="order.appoin_slot"> · {{ order.appoin_slot }}</span>
        </span>
        <span style="flex: 1;"></span>
        <span v-if="order.building_type_label" class="status-badge" style="background: #f5f3ff; color: #5b21b6;">{{ order.building_type_label }}</span>
        <span v-if="order.classification" class="status-badge informe-classif-pill" :style="classifStyle(order.classification)">{{ classLabel(order.classification) }}</span>
        <span v-if="order.insyte_status_label" class="status-badge" style="background: #f0f9ff; color: #0369a1;">{{ order.insyte_status_label }}</span>
      </div>

      <!-- Notes -->
      <div v-if="order.insyte_notes || order.approve_notes" class="informe-notes">
        <div v-if="order.insyte_notes" class="informe-note-block">
          <div class="informe-note-label">Technician Notes</div>
          <div class="informe-note-text">{{ order.insyte_notes }}</div>
        </div>
        <div v-if="order.approve_notes" class="informe-note-block">
          <div class="informe-note-label">Approve Notes</div>
          <div class="informe-note-text">{{ order.approve_notes }}</div>
        </div>
      </div>

      <!-- Extra cols chips -->
      <div v-if="extraCols.length" class="informe-extra-cols">
        <template v-for="col in extraCols">
          <span v-if="order[col] !== null && order[col] !== undefined && order[col] !== ''" :key="col" class="informe-chip">
            <span class="informe-chip-label">{{ colHeader(col) }}</span>
            <span class="informe-chip-val">{{ order[col] }}</span>
          </span>
        </template>
      </div>

      <!-- Photos section -->
      <div class="informe-photos-bar">
        <button class="informe-photos-toggle" @click="togglePhotos(order)">
          <i :class="expandedPhotos.has(order.id) ? 'pi pi-chevron-up' : 'pi pi-images'" style="font-size: 0.65rem;"></i>
          <span v-if="!expandedPhotos.has(order.id)">Ver fotos</span>
          <span v-else>Ocultar fotos</span>
        </button>

        <!-- Expanded photos -->
        <div v-if="expandedPhotos.has(order.id)" style="margin-top: 0.6rem;">
          <div v-if="photoCache[order.id]?.loading" style="font-size: 0.78rem; color: #94a3b8; padding: 0.25rem 0;">
            <i class="pi pi-spin pi-spinner" style="font-size: 0.75rem; margin-right: 4px;"></i>Cargando fotos...
          </div>
          <div v-else-if="!photoCache[order.id]?.grupos?.length" style="font-size: 0.78rem; color: #cbd5e1; font-style: italic;">
            Sin fotos disponibles
          </div>
          <div v-else>
            <div v-for="grupo in photoCache[order.id].grupos" :key="grupo.fase" style="margin-bottom: 0.75rem;">
              <div class="informe-fase-label" :style="{ color: faseColor(grupo.fase), background: faseBg(grupo.fase) }">
                {{ grupo.fase }} <span style="opacity: 0.6; font-weight: 400;">({{ grupo.fotos.length }})</span>
              </div>
              <div class="informe-photo-strip">
                <img
                  v-for="photo in grupo.fotos"
                  :key="photo.filename"
                  :src="photo.url"
                  class="informe-photo-thumb"
                  :alt="photo.filename"
                  @click="openLightbox(photo)"
                  @error="e => e.target.style.display='none'"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer actions -->
      <div class="informe-footer">
        <Button
          icon="pi pi-tag"
          label="Clasificar"
          size="small"
          text
          :style="order.classification ? 'color: #8b5cf6;' : 'color: #94a3b8;'"
          @click.stop="openClassifyMenu(order, $event)"
        />
        <Button
          icon="pi pi-arrow-right"
          label="Ver detalle"
          size="small"
          text
          style="color: #3b82f6;"
          iconPos="right"
          @click="router.push('/workorders/' + order.id)"
        />
      </div>
    </div>

    <!-- Classify popup -->
    <div v-if="classifyMenu.visible" class="classify-popup" :style="{ top: classifyMenu.y + 'px', left: classifyMenu.x + 'px' }" @click.stop>
      <!-- Step 1: pick category -->
      <template v-if="classifyMenu.step === 1">
        <div class="classify-popup-title">Clasificar orden</div>
        <button
          v-for="cat in CLASSIFICATIONS"
          :key="cat"
          class="classify-option"
          :class="{ active: classifyMenu.order?.classification === cat }"
          @click="selectCategory(cat)"
        >{{ classLabel(cat) }}</button>
        <div class="classify-divider"></div>
        <button
          v-if="classifyMenu.order?.classification"
          class="classify-option classify-remove"
          @click="applyClassification(null, null)"
        ><i class="pi pi-times"></i> Quitar clasificacion</button>
        <button class="classify-option classify-cancel" @click="classifyMenu.visible = false">Cancelar</button>
      </template>
      <!-- Step 2: add comment -->
      <template v-else>
        <div class="classify-popup-title">Comentario (opcional)</div>
        <div style="padding: 0.4rem 0.9rem 0.5rem;">
          <div style="font-size: 0.75rem; font-weight: 600; color: #475569; margin-bottom: 0.4rem;">{{ classifyMenu.selectedCat }}</div>
          <textarea
            v-model="classifyMenu.note"
            class="classify-note-input"
            placeholder="Agregar comentario..."
            rows="3"
            autofocus
          ></textarea>
        </div>
        <div style="display: flex; gap: 0.4rem; padding: 0 0.9rem 0.5rem;">
          <button class="classify-confirm-btn" @click="applyClassification(classifyMenu.selectedCat, classifyMenu.note)">Confirmar</button>
          <button class="classify-option classify-cancel" style="flex:1;" @click="classifyMenu.step = 1">Volver</button>
        </div>
      </template>
    </div>
    <div v-if="classifyMenu.visible" class="classify-backdrop" @click="classifyMenu.visible = false"></div>

    <!-- Lightbox -->
    <Dialog
      :visible="lightboxVisible"
      @update:visible="v => lightboxVisible = v"
      :header="lightboxPhoto?.filename"
      :modal="true"
      :maximizable="true"
      style="max-width: 95vw; max-height: 95vh;"
    >
      <img
        v-if="lightboxPhoto"
        :src="lightboxPhoto.url"
        :alt="lightboxPhoto.filename"
        style="max-width: 100%; max-height: 80vh; object-fit: contain; display: block; margin: auto;"
      />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import { useOrdersStore } from '../stores/orders'
import Button from 'primevue/button'
import MultiSelect from 'primevue/multiselect'
import Dialog from 'primevue/dialog'

const ordersStore = useOrdersStore()

function toggleDateSort() {
  const newOrder = ordersStore.sortOrder === 'asc' ? 'desc' : 'asc'
  ordersStore.setSort('appoin_date', newOrder)
  ordersStore.fetchOrders()
}

const props = defineProps({
  orders: { type: Array, required: true },
})

const router = useRouter()

// ── Classifications ────────────────────────────────────────────────────────
const CLASSIFICATIONS = [
  'YA CERTIFICADOS',
  'PENDIENTES POR CERTIFICAR',
  'PENDIENTES POR REVISION',
  'DEVUELTOS',
  'POR HACER',
  'PEND POR NUEVA VISITA',
  'SIN SUBIRSE',
  'CANCELADOS',
]

const CLASSIF_STYLES = {
  'YA CERTIFICADOS':           'background: #dcfce7; color: #166534;',
  'PENDIENTES POR CERTIFICAR': 'background: #fef9c3; color: #854d0e;',
  'PENDIENTES POR REVISION':   'background: #dbeafe; color: #1e40af;',
  'DEVUELTOS':                 'background: #ffe4e6; color: #9f1239;',
  'POR HACER':                 'background: #f1f5f9; color: #475569;',
  'PEND POR NUEVA VISITA':     'background: #ede9fe; color: #5b21b6;',
  'SIN SUBIRSE':               'background: #fff7ed; color: #9a3412;',
  'CANCELADOS':                'background: #fce7f3; color: #9d174d;',
}
function classifStyle(cat) { return CLASSIF_STYLES[cat] || 'background: #f1f5f9; color: #475569;' }

const CLASSIFICATION_LABELS = {
  'YA CERTIFICADOS': 'APROBADOS',
}
function classLabel(cat) { return CLASSIFICATION_LABELS[cat] || cat }

// ── Extra columns ──────────────────────────────────────────────────────────
const EXTRA_COLS_OPTIONS = [
  { field: 'name',                    header: 'Name' },
  { field: 'city',                    header: 'City' },
  { field: 'area',                    header: 'Area' },
  { field: 'dp',                      header: 'DP' },
  { field: 'pop',                     header: 'POP' },
  { field: 'hz',                      header: 'HZ' },
  { field: 'hzz',                     header: 'HZZ' },
  { field: 'building_hp',             header: 'Building HP' },
  { field: 'building_wo',             header: 'Building WO' },
  { field: 'building_type_label',     header: 'Building Type' },
  { field: 'workgroup_label',         header: 'Appoin Team' },
  { field: 'appoin_status_label',     header: 'Appoin Status' },
  { field: 'approve_status_label',    header: 'Approve Status' },
  { field: 'approve_work',            header: 'Approve Work' },
  { field: 'install_status_label',    header: 'Install Status' },
  { field: 'hc_status_label',         header: 'HC Status' },
  { field: 'deploy_status_label',     header: 'Deploy Status' },
  { field: 'operational_status_label',header: 'Operational Status' },
  { field: 'pop_status_label',        header: 'POP Status' },
  { field: 'ticket_status_label',     header: 'Ticket Status' },
  { field: 'priority_label',          header: 'Priority' },
  { field: 'origen_label',            header: 'Origen' },
  { field: 'work_type',               header: 'Work Type' },
  { field: 'phone',                   header: 'Phone' },
  { field: 'mail',                    header: 'Mail' },
]

const EXTRA_COLS_STORAGE_KEY = 'wo_informe_extra_cols'
function loadExtraCols() {
  try {
    const saved = localStorage.getItem(EXTRA_COLS_STORAGE_KEY)
    if (saved) return JSON.parse(saved)
  } catch { /* ignore */ }
  return []
}

const extraCols = ref(loadExtraCols())
function saveExtraCols() {
  localStorage.setItem(EXTRA_COLS_STORAGE_KEY, JSON.stringify(extraCols.value))
}

function colHeader(field) {
  return EXTRA_COLS_OPTIONS.find(c => c.field === field)?.header || field
}

// ── Photo logic ────────────────────────────────────────────────────────────
const PHOTO_STEPS = [
  { id: '1.1', insyte_fase: 'Obra Civil' },
  { id: '1.2', insyte_fase: 'Obra Civil' },
  { id: '2.1', insyte_fase: 'Obra Civil' },
  { id: '2.2', insyte_fase: 'Obra Civil' },
  { id: '3.1', insyte_fase: 'OTB/AP' },
  { id: '3.2', insyte_fase: 'OTB/AP' },
  { id: '3.3', insyte_fase: 'OTB/AP' },
  { id: '5.1', insyte_fase: 'OTB/AP' },
  { id: '5.4', insyte_fase: 'OTB/AP' },
  { id: '4.1', insyte_fase: 'ONT/TA' },
  { id: '4.2', insyte_fase: 'ONT/TA' },
  { id: '4.3', insyte_fase: 'ONT/TA' },
  { id: '20.1', insyte_fase: 'ONT/TA' },
  { id: '21.2', insyte_fase: 'ONT/TA' },
  { id: '5.2', insyte_fase: 'Interior' },
  { id: '5.3', insyte_fase: 'Interior' },
  { id: '5.5', insyte_fase: 'Interior' },
  { id: '5.6', insyte_fase: 'Interior' },
  { id: '5.7', insyte_fase: 'Interior' },
  { id: '6.1', insyte_fase: 'Miscellaneous' },
  { id: '7.1', insyte_fase: 'Miscellaneous' },
  { id: '8.1', insyte_fase: 'Miscellaneous' },
  { id: '9.1', insyte_fase: 'Miscellaneous' },
  { id: '0.0', insyte_fase: 'Miscellaneous' },
  { id: '0.1', insyte_fase: 'Miscellaneous' },
  { id: '10.1', insyte_fase: 'Averia HA' },
]
const FASE_ORDER = ['Obra Civil', 'OTB/AP', 'ONT/TA', 'Interior', 'Miscellaneous', 'Averia HA']

const FASE_COLORS = {
  'Obra Civil':    { bg: '#fef9c3', color: '#92400e' },
  'OTB/AP':        { bg: '#dbeafe', color: '#1e40af' },
  'ONT/TA':        { bg: '#dcfce7', color: '#14532d' },
  'Interior':      { bg: '#ede9fe', color: '#4c1d95' },
  'Miscellaneous': { bg: '#f1f5f9', color: '#334155' },
  'Averia HA':     { bg: '#fee2e2', color: '#7f1d1d' },
}
function faseBg(fase)    { return FASE_COLORS[fase]?.bg    || '#f1f5f9' }
function faseColor(fase) { return FASE_COLORS[fase]?.color || '#334155' }

function groupPhotosByFase(photos) {
  const groups = {}
  for (const photo of photos) {
    const fase = photo.insyte_fase || 'Sin clasificar'
    if (!groups[fase]) groups[fase] = []
    groups[fase].push(photo)
  }
  for (const fase in groups) {
    groups[fase].sort((a, b) => parseFloat(a.fotoId || '99') - parseFloat(b.fotoId || '99'))
  }
  const ordered = []
  for (const fase of FASE_ORDER) {
    if (groups[fase]) ordered.push({ fase, fotos: groups[fase] })
  }
  for (const fase in groups) {
    if (!FASE_ORDER.includes(fase)) ordered.push({ fase, fotos: groups[fase] })
  }
  return ordered
}

// photoCache: { [orderId]: { loading: bool, grupos: [...] } }
const photoCache = ref({})
const expandedPhotos = ref(new Set())

async function togglePhotos(order) {
  const id = order.id
  const expanded = expandedPhotos.value.has(id)
  if (expanded) {
    expandedPhotos.value = new Set([...expandedPhotos.value].filter(x => x !== id))
    return
  }
  // Add to expanded
  const newSet = new Set(expandedPhotos.value)
  newSet.add(id)
  expandedPhotos.value = newSet

  // Fetch if not cached
  if (!photoCache.value[id]) {
    photoCache.value = { ...photoCache.value, [id]: { loading: true, grupos: [] } }
    try {
      const res = await api.getOrder(id)
      const photos = res.data.photos || []
      photoCache.value = {
        ...photoCache.value,
        [id]: { loading: false, grupos: groupPhotosByFase(photos) },
      }
    } catch (e) {
      console.error('fetchPhotos error', e)
      photoCache.value = { ...photoCache.value, [id]: { loading: false, grupos: [] } }
    }
  }
}

// ── Lightbox ───────────────────────────────────────────────────────────────
const lightboxVisible = ref(false)
const lightboxPhoto = ref(null)
function openLightbox(photo) {
  lightboxPhoto.value = photo
  lightboxVisible.value = true
}

// ── Classify ───────────────────────────────────────────────────────────────
const classifyMenu = reactive({ visible: false, order: null, x: 0, y: 0, step: 1, selectedCat: null, note: '' })

function openClassifyMenu(order, event) {
  const rect = event.target.closest('button').getBoundingClientRect()
  classifyMenu.order = order
  classifyMenu.x = Math.min(rect.left, window.innerWidth - 240)
  const popupHeight = 340
  const spaceBelow = window.innerHeight - rect.bottom
  classifyMenu.y = spaceBelow >= popupHeight ? rect.bottom + 4 : Math.max(8, rect.top - popupHeight - 4)
  classifyMenu.step = 1
  classifyMenu.selectedCat = null
  classifyMenu.note = ''
  classifyMenu.visible = true
}

function selectCategory(cat) {
  classifyMenu.selectedCat = cat
  classifyMenu.note = ''
  classifyMenu.step = 2
}

async function applyClassification(value, note) {
  if (!classifyMenu.order) return
  const order = classifyMenu.order
  const wasUnclassified = !order.classification
  classifyMenu.visible = false
  try {
    await api.setClassification(order.id, value, note)
    // Update totalUnclassified counter
    if (wasUnclassified && value) ordersStore.totalUnclassified = Math.max(0, ordersStore.totalUnclassified - 1)
    else if (!wasUnclassified && !value) ordersStore.totalUnclassified += 1
    if (ordersStore.filters.hide_classified) {
      const idx = ordersStore.orders.findIndex(o => o.id === order.id)
      if (idx !== -1) ordersStore.orders.splice(idx, 1)
    } else {
      order.classification = value
      order.classification_note = note || null
    }
  } catch (e) {
    console.error('setClassification error', e)
  }
}
</script>
