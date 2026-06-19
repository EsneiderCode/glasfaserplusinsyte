<template>
  <div>
    <!-- Filter Panel -->
    <div class="filter-panel">
      <!-- Global search -->
      <div>
        <span class="filter-label">Buscar</span>
        <IconField>
          <InputIcon class="pi pi-search" />
          <InputText
            v-model="searchInput"
            placeholder="Nombre, ID, telefono..."
            style="width: 220px;"
            @keyup.enter="applySearch"
            @input="debouncedSearch"
          />
        </IconField>
      </div>

      <!-- Appoin Status -->
      <div>
        <span class="filter-label">Appoin Status</span>
        <Dropdown
          v-model="filters.appoin_status"
          :options="masterOptions('Appoin_status_master')"
          optionLabel="label"
          optionValue="id"
          placeholder="Todos"
          style="width: 200px"
          showClear
          @change="applyFilters"
        />
      </div>

      <!-- Workgroup -->
      <div>
        <span class="filter-label">Work Group</span>
        <Dropdown
          v-model="filters.workgroup"
          :options="masterOptions('workgroups_master')"
          optionLabel="label"
          optionValue="id"
          placeholder="Todos"
          style="width: 180px"
          showClear
          @change="applyFilters"
        />
      </div>

      <!-- Priority -->
      <div>
        <span class="filter-label">Prioridad</span>
        <Dropdown
          v-model="filters.priority"
          :options="masterOptions('priority_master')"
          optionLabel="label"
          optionValue="id"
          placeholder="Todas"
          style="width: 150px"
          showClear
          @change="applyFilters"
        />
      </div>

      <!-- Install Status -->
      <div>
        <span class="filter-label">Install Status</span>
        <Dropdown
          v-model="filters.install_status"
          :options="masterOptions('install_status_master')"
          optionLabel="label"
          optionValue="id"
          placeholder="Todos"
          style="width: 160px"
          showClear
          @change="applyFilters"
        />
      </div>

      <!-- HC Status -->
      <div>
        <span class="filter-label">HC Status</span>
        <Dropdown
          v-model="filters.hc_status"
          :options="masterOptions('HC_status_master')"
          optionLabel="label"
          optionValue="id"
          placeholder="Todos"
          style="width: 160px"
          showClear
          @change="applyFilters"
        />
      </div>

      <!-- Approve Status -->
      <div>
        <span class="filter-label">Approve Status</span>
        <Dropdown
          v-model="filters.approve_status"
          :options="masterOptions('approve_status_master')"
          optionLabel="label"
          optionValue="id"
          placeholder="Todos"
          style="width: 160px"
          showClear
          @change="applyFilters"
        />
      </div>

      <!-- Building Type -->
      <div>
        <span class="filter-label">Building Type</span>
        <Dropdown
          v-model="filters.building_type"
          :options="masterOptions('building_type_master')"
          optionLabel="label"
          optionValue="id"
          placeholder="Todos"
          style="width: 160px"
          showClear
          @change="applyFilters"
        />
      </div>

      <!-- Date From -->
      <div>
        <span class="filter-label">Cita desde</span>
        <Calendar
          v-model="dateFrom"
          dateFormat="yy-mm-dd"
          placeholder="Desde"
          style="width: 150px"
          showClear
          @date-select="applyFilters"
          @clear-click="applyFilters"
        />
      </div>

      <!-- Date To -->
      <div>
        <span class="filter-label">Cita hasta</span>
        <Calendar
          v-model="dateTo"
          dateFormat="yy-mm-dd"
          placeholder="Hasta"
          style="width: 150px"
          showClear
          @date-select="applyFilters"
          @clear-click="applyFilters"
        />
      </div>

      <!-- Hide classified toggle -->
      <div style="align-self: flex-end;">
        <Button
          :label="ordersStore.filters.hide_classified ? 'Mostrando sin clasificar' : 'Ocultar clasificados'"
          :icon="ordersStore.filters.hide_classified ? 'pi pi-eye-slash' : 'pi pi-eye'"
          :severity="ordersStore.filters.hide_classified ? 'contrast' : 'secondary'"
          outlined
          size="small"
          @click="toggleHideClassified"
        />
      </div>

      <Button
        label="Limpiar"
        icon="pi pi-times"
        severity="secondary"
        outlined
        size="small"
        @click="clearFilters"
        style="align-self: flex-end;"
      />
    </div>

    <!-- Table/Informe card -->
    <div class="card">
      <!-- Table toolbar -->
      <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.6rem 1rem 0; gap: 0.5rem;">
        <!-- View mode toggle -->
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <div class="view-mode-toggle">
            <button
              class="view-mode-btn"
              :class="{ active: viewMode === 'table' }"
              @click="setViewMode('table')"
            ><i class="pi pi-table" style="font-size: 0.75rem; margin-right: 4px;"></i>Tabla</button>
            <button
              class="view-mode-btn"
              :class="{ active: viewMode === 'informe' }"
              @click="setViewMode('informe')"
            ><i class="pi pi-list" style="font-size: 0.75rem; margin-right: 4px;"></i>Informe</button>
          </div>
          <div v-if="viewMode === 'table'" class="view-mode-toggle">
            <button
              class="view-mode-btn"
              :class="{ active: !ordersStore.groupedView }"
              @click="setGroupedView(false)"
              title="Vista original idéntica a Insyte"
            ><i class="pi pi-list" style="font-size: 0.75rem; margin-right: 4px;"></i>Insyte</button>
            <button
              class="view-mode-btn"
              :class="{ active: ordersStore.groupedView }"
              @click="setGroupedView(true)"
              title="Agrupar por dirección (address_id)"
            ><i class="pi pi-sitemap" style="font-size: 0.75rem; margin-right: 4px;"></i>Agrupada</button>
          </div>
        </div>

        <div v-if="viewMode === 'table'" style="display: flex; align-items: center; gap: 0.5rem;">
          <span style="font-size: 0.75rem; color: #94a3b8;">Columnas:</span>
          <MultiSelect
            v-model="selectedCols"
            :options="ALL_COLUMNS"
            optionLabel="header"
            optionValue="field"
            placeholder="Seleccionar columnas"
            display="chip"
            :maxSelectedLabels="0"
            :selectedItemsLabel="selectedCols.length + ' columnas'"
            style="max-width: 220px; font-size: 0.78rem;"
            @change="saveColPrefs"
            panelStyle="max-height: 400px"
          />
        </div>
      </div>

      <!-- Informe view -->
      <template v-if="viewMode === 'informe'">
        <InformeView :orders="ordersStore.orders" style="padding: 0.75rem 1rem;" />
        <!-- Informe pagination -->
        <div v-if="ordersStore.total > ordersStore.pageSize" style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; padding: 0.75rem 1rem; border-top: 1px solid #f1f5f9;">
          <Button icon="pi pi-angle-double-left" text size="small" :disabled="ordersStore.page === 1" @click="informePage(1)" />
          <Button icon="pi pi-angle-left" text size="small" :disabled="ordersStore.page === 1" @click="informePage(ordersStore.page - 1)" />
          <span style="font-size: 0.8rem; color: #64748b;">{{ ordersStore.page }} / {{ Math.ceil(ordersStore.total / ordersStore.pageSize) }} &nbsp;·&nbsp; {{ ordersStore.total }} ordenes</span>
          <Button icon="pi pi-angle-right" text size="small" :disabled="ordersStore.page >= Math.ceil(ordersStore.total / ordersStore.pageSize)" @click="informePage(ordersStore.page + 1)" />
          <Button icon="pi pi-angle-double-right" text size="small" :disabled="ordersStore.page >= Math.ceil(ordersStore.total / ordersStore.pageSize)" @click="informePage(Math.ceil(ordersStore.total / ordersStore.pageSize))" />
        </div>
      </template>

      <DataTable v-if="viewMode === 'table'"
        :value="ordersStore.orders"
        :loading="ordersStore.loading"
        dataKey="id"
        :expandedRows="expandedRows"
        @update:expandedRows="expandedRows = $event"
        @row-expand="onRowExpand"
        lazy
        :rows="ordersStore.pageSize"
        :totalRecords="ordersStore.total"
        paginator
        :rowsPerPageOptions="[200, 500, 1000]"
        @page="onPage"
        removableSort
        :sortField="ordersStore.sortBy"
        :sortOrder="ordersStore.sortOrder === 'asc' ? 1 : -1"
        @sort="onSort"
        stripedRows
        scrollable
        scrollHeight="calc(100vh - 300px)"
        selectionMode="single"
        @row-click="onRowClick"
        rowHover
        class="p-datatable-sm"
        paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
        currentPageReportTemplate="{first} - {last} de {totalRecords}"
        style="-webkit-overflow-scrolling: touch;"
        reorderableColumns
        @column-reorder="onColumnReorder"
      >
        <!-- EXPANDER (solo en vista agrupada) -->
        <Column v-if="ordersStore.groupedView" expander style="width: 3rem; flex: none;" />

        <!-- ACCION -->
        <Column header="" frozen style="width: 52px; text-align: center; flex: none;">
          <template #body="{ data }">
            <Button
              icon="pi pi-eye"
              rounded
              text
              size="small"
              @click.stop="onRowClick({ data })"
              style="color: #3b82f6;"
            />
          </template>
        </Column>

        <!-- CLASIFICAR -->
        <Column header="" frozen style="width: 44px; text-align: center; flex: none;">
          <template #body="{ data }">
            <div style="position: relative;">
              <Button
                :icon="data.classification ? 'pi pi-tag' : 'pi pi-tag'"
                rounded
                text
                size="small"
                :style="data.classification ? 'color: #8b5cf6;' : 'color: #94a3b8;'"
                :title="classLabel(data.classification) || 'Clasificar'"
                @click.stop="openClassifyMenu(data, $event)"
              />
            </div>
          </template>
        </Column>

        <!-- DYNAMIC COLUMNS -->
        <template v-for="col in visibleColumns">
          <!-- Appoin Status: special badge rendering -->
          <Column v-if="col.field === 'appoin_status_label'" :key="col.field" :field="col.field" :header="col.header" sortField="appoin_status" :sortable="true" style="min-width: 180px">
            <template #body="{ data }">
              <span v-if="data.appoin_status_label" :class="['status-badge', appointClass(data.appoin_status)]">
                <i :class="appointIcon(data.appoin_status)" style="font-size: 0.65rem;"></i>
                {{ data.appoin_status_label }}
              </span>
              <span v-else style="color: #cbd5e1;">—</span>
            </template>
          </Column>

          <!-- Appoin Date + Slot combined -->
          <Column v-else-if="col.field === 'appoin_date'" :key="col.field" :field="col.field" :header="col.header" :sortable="true" style="min-width: 160px">
            <template #body="{ data }">
              <div v-if="data.appoin_date">
                <div style="font-size: 0.85rem; font-weight: 600; color: #1e293b;">{{ data.appoin_date }}</div>
                <div v-if="data.appoin_slot && !selectedCols.includes('appoin_slot')" style="font-size: 0.75rem; color: #64748b;">{{ data.appoin_slot }}</div>
              </div>
              <span v-else style="color: #cbd5e1;">—</span>
            </template>
          </Column>

          <!-- Name + Phone combined -->
          <Column v-else-if="col.field === 'name'" :key="col.field" :field="col.field" :header="col.header" :sortable="true" style="min-width: 180px">
            <template #body="{ data }">
              <div>
                <div style="font-weight: 600; color: #1e293b; font-size: 0.875rem;">{{ data.name || '-' }}</div>
                <div v-if="data.phone && !selectedCols.includes('phone')" style="font-size: 0.75rem; color: #64748b;">{{ data.phone }}</div>
              </div>
            </template>
          </Column>

          <!-- address_id monospace -->
          <Column v-else-if="col.field === 'address_id'" :key="col.field" :field="col.field" :header="col.header" style="min-width: 130px">
            <template #body="{ data }">
              <span style="font-family: monospace; font-size: 0.8rem; color: #475569; font-weight: 600;">{{ data.address_id || '—' }}</span>
            </template>
          </Column>

          <!-- home_id monospace -->
          <Column v-else-if="col.field === 'home_id'" :key="col.field" :field="col.field" :header="col.header" style="min-width: 120px">
            <template #body="{ data }">
              <span style="font-family: monospace; font-size: 0.8rem; color: #475569;">{{ data.home_id || '—' }}</span>
            </template>
          </Column>

          <!-- Appoin Team badge -->
          <Column v-else-if="col.field === 'workgroup_label'" :key="col.field" :field="col.field" :header="col.header" style="min-width: 130px">
            <template #body="{ data }">
              <span v-if="data.workgroup_label" class="status-badge" style="background: #f0fdf4; color: #166534;">{{ data.workgroup_label }}</span>
              <span v-else style="color: #cbd5e1;">—</span>
            </template>
          </Column>

          <!-- Insyte Status badge -->
          <Column v-else-if="col.field === 'insyte_status_label'" :key="col.field" :field="col.field" :header="col.header" style="min-width: 140px">
            <template #body="{ data }">
              <span v-if="data.insyte_status_label" class="status-badge" style="background: #f0f9ff; color: #0369a1;">{{ data.insyte_status_label }}</span>
              <span v-else style="color: #cbd5e1;">—</span>
            </template>
          </Column>

          <!-- Approve Status badge -->
          <Column v-else-if="col.field === 'approve_status_label'" :key="col.field" :field="col.field" :header="col.header" style="min-width: 140px">
            <template #body="{ data }">
              <span v-if="data.approve_status_label" class="status-badge" style="background: #fef9c3; color: #854d0e;">{{ data.approve_status_label }}</span>
              <span v-else style="color: #cbd5e1;">—</span>
            </template>
          </Column>

          <!-- Building Type badge -->
          <Column v-else-if="col.field === 'building_type_label'" :key="col.field" :field="col.field" :header="col.header" style="min-width: 130px">
            <template #body="{ data }">
              <span v-if="data.building_type_label" class="status-badge" style="background: #f5f3ff; color: #5b21b6;">{{ data.building_type_label }}</span>
              <span v-else style="color: #cbd5e1;">—</span>
            </template>
          </Column>

          <!-- Origen badge -->
          <Column v-else-if="col.field === 'origen_label'" :key="col.field" :field="col.field" :header="col.header" style="min-width: 110px">
            <template #body="{ data }">
              <span v-if="data.origen_label || data.origen" class="status-badge" style="background: #f1f5f9; color: #475569;">{{ data.origen_label || data.origen }}</span>
              <span v-else style="color: #cbd5e1;">—</span>
            </template>
          </Column>

          <!-- Generic fallback -->
          <Column v-else :key="col.field" :field="col.field" :header="col.header" :sortable="SORTABLE_FIELDS.has(col.field)" :style="col.minWidth ? `min-width: ${col.minWidth}` : 'min-width: 110px'">
            <template #body="{ data }">
              <span v-if="data[col.field] !== null && data[col.field] !== undefined && data[col.field] !== ''" style="font-size: 0.85rem; color: #334155;">{{ data[col.field] }}</span>
              <span v-else style="color: #cbd5e1;">—</span>
            </template>
          </Column>
        </template>

        <!-- EXPANSION: sub-ordenes -->
        <template #expansion="{ data }">
          <div v-if="data.sub_orders && data.sub_orders.length" style="padding: 0.5rem 1rem 0.75rem 3rem; background: #f8fafc;">
            <div style="font-size: 0.72rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem;">
              {{ data.sub_orders.length }} sub-orden{{ data.sub_orders.length > 1 ? 'es' : '' }} — mismo address_id
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.82rem;">
              <thead>
                <tr style="border-bottom: 1px solid #e2e8f0;">
                  <th style="text-align: left; padding: 0.25rem 0.5rem; color: #94a3b8; font-weight: 600;">ID</th>
                  <th style="text-align: left; padding: 0.25rem 0.5rem; color: #94a3b8; font-weight: 600;">Fecha cita</th>
                  <th style="text-align: left; padding: 0.25rem 0.5rem; color: #94a3b8; font-weight: 600;">Nombre</th>
                  <th style="text-align: left; padding: 0.25rem 0.5rem; color: #94a3b8; font-weight: 600;">Appoin Status</th>
                  <th style="text-align: left; padding: 0.25rem 0.5rem; color: #94a3b8; font-weight: 600;">Clasificación</th>
                  <th style="width: 44px;"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sub in data.sub_orders" :key="sub.id" style="border-bottom: 1px solid #f1f5f9; cursor: pointer;" @click="onRowClick({ data: sub })">
                  <td style="padding: 0.3rem 0.5rem; font-family: monospace; font-size: 0.78rem; color: #475569;">{{ sub.id }}</td>
                  <td style="padding: 0.3rem 0.5rem; color: #334155;">{{ sub.appoin_date ? sub.appoin_date.split(' ')[0] : '—' }}</td>
                  <td style="padding: 0.3rem 0.5rem; color: #1e293b; font-weight: 500;">{{ sub.name || '—' }}</td>
                  <td style="padding: 0.3rem 0.5rem;">
                    <span v-if="sub.appoin_status_label" :class="['status-badge', appointClass(sub.appoin_status)]" style="font-size: 0.72rem;">
                      {{ sub.appoin_status_label }}
                    </span>
                    <span v-else style="color: #cbd5e1;">—</span>
                  </td>
                  <td style="padding: 0.3rem 0.5rem;">
                    <span v-if="sub.classification" style="font-size: 0.72rem; background: #f3e8ff; color: #7c3aed; padding: 2px 6px; border-radius: 4px;">{{ classLabel(sub.classification) }}</span>
                    <span v-else style="color: #cbd5e1;">—</span>
                  </td>
                  <td style="padding: 0.3rem 0.5rem; text-align: center;">
                    <button style="background: none; border: none; cursor: pointer; color: #3b82f6; padding: 2px 4px;" @click.stop="onRowClick({ data: sub })">
                      <i class="pi pi-eye" style="font-size: 0.8rem;"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

        <template #empty>
          <div class="empty-state">
            <i class="pi pi-inbox"></i>
            <p v-if="ordersStore.total === 0 && !ordersStore.loading">
              No hay ordenes. Usa "Sincronizar" para descargar datos del portal.
            </p>
            <p v-else>No se encontraron resultados con los filtros aplicados.</p>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Classification dropdown popup -->
    <div v-if="classifyMenu.visible" class="classify-popup" :style="{ top: classifyMenu.y + 'px', left: classifyMenu.x + 'px' }" @click.stop>
      <!-- Step 1: pick category -->
      <template v-if="classifyMenu.step === 1">
        <div class="classify-popup-title">Clasificar orden</div>
        <button
          v-for="cat in CLASSIFICATIONS"
          :key="cat"
          class="classify-option"
          :class="{ active: classifyMenu.order && classifyMenu.order.classification === cat }"
          @click="selectCategory(cat)"
        >{{ classLabel(cat) }}</button>
        <div class="classify-divider"></div>
        <button
          v-if="classifyMenu.order && classifyMenu.order.classification"
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
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useOrdersStore } from '../stores/orders'
import api from '../services/api'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import Calendar from 'primevue/calendar'
import InformeView from '../components/InformeView.vue'

// ── View mode ───────────────────────────────────────────────────────────────
const VIEW_MODE_KEY = 'wo_view_mode'
const viewMode = ref(localStorage.getItem(VIEW_MODE_KEY) || 'table')
function setViewMode(mode) {
  viewMode.value = mode
  localStorage.setItem(VIEW_MODE_KEY, mode)
}

const expandedRows = ref({})

function setGroupedView(value) {
  expandedRows.value = {}
  ordersStore.groupedView = value
  ordersStore.page = 1
  ordersStore.fetchOrders()
}

async function onRowExpand(event) {
  const order = event.data
  if (order.sub_orders && order.sub_orders.length > 0) return  // ya cargados
  if (!order.sub_orders_count) return  // no tiene sub_orders
  try {
    const res = await api.getSubOrders(order.id)
    const idx = ordersStore.orders.findIndex(o => o.id === order.id)
    if (idx !== -1) ordersStore.orders[idx].sub_orders = res.data
  } catch (e) {
    console.error('Error loading sub_orders', e)
  }
}

function informePage(page) {
  ordersStore.setPage(page)
  ordersStore.fetchOrders()
}

const ordersStore = useOrdersStore()
const router = useRouter()

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

const CLASSIFICATION_LABELS = {
  'YA CERTIFICADOS': 'APROBADOS',
}

function classLabel(cat) {
  return CLASSIFICATION_LABELS[cat] || cat
}

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
  const orderId = classifyMenu.order.id
  const wasUnclassified = !classifyMenu.order.classification
  classifyMenu.visible = false
  try {
    await api.setClassification(orderId, value, note)
    if (wasUnclassified && value) ordersStore.totalUnclassified = Math.max(0, ordersStore.totalUnclassified - 1)
    else if (!wasUnclassified && !value) ordersStore.totalUnclassified += 1
    if (ordersStore.filters.hide_classified) {
      const idx = ordersStore.orders.findIndex(o => o.id === orderId)
      if (idx !== -1) ordersStore.orders.splice(idx, 1)
    } else {
      const o = ordersStore.orders.find(o => o.id === orderId)
      if (o) { o.classification = value; o.classification_note = note || null }
    }
  } catch (e) {
    console.error('setClassification error', e)
  }
}

function toggleHideClassified() {
  ordersStore.setFilter('hide_classified', !ordersStore.filters.hide_classified)
  ordersStore.fetchOrders()
}

// ── All available columns ──────────────────────────────────────────────────
const ALL_COLUMNS = [
  { field: 'address_id',          header: 'ADDRESS ID' },
  { field: 'home_id',             header: 'HOME ID' },
  { field: 'name',                header: 'Name' },
  { field: 'city',                header: 'City' },
  { field: 'area',                header: 'Area' },
  { field: 'street',              header: 'Street' },
  { field: 'state',               header: 'State' },
  { field: 'appoin_date',         header: 'Appoin Date' },
  { field: 'appoin_slot',         header: 'Appoin Slot' },
  { field: 'appoin_status_label', header: 'Appoin Status' },
  { field: 'workgroup_label',     header: 'Appoin Team' },
  { field: 'appoin_subco_label',  header: 'Appoin Subco' },
  { field: 'approve_status_label',header: 'Approve Status' },
  { field: 'approve_notes',       header: 'Approve Notes' },
  { field: 'approve_work',        header: 'Approve Work' },
  { field: 'building_type_label', header: 'Building Type' },
  { field: 'building_hp',         header: 'Building HP' },
  { field: 'building_wo',         header: 'Building WO' },
  { field: 'dp',                  header: 'DP' },
  { field: 'pop',                 header: 'POP' },
  { field: 'hz',                  header: 'HZ' },
  { field: 'hzz',                 header: 'HZZ' },
  { field: 'insyte_status_label', header: 'Insyte Status' },
  { field: 'insyte_notes',        header: 'Insyte Notes' },
  { field: 'install_status_label',header: 'Install Status' },
  { field: 'hc_status_label',     header: 'HC Status' },
  { field: 'deploy_status_label', header: 'Deployment Status' },
  { field: 'operational_status_label', header: 'Operational Status' },
  { field: 'pop_status_label',    header: 'POP Status' },
  { field: 'ticket_status_label', header: 'Ticket Status' },
  { field: 'priority_label',      header: 'Priority' },
  { field: 'origen_label',        header: 'Origen' },
  { field: 'work_type',           header: 'Work Type' },
  { field: 'mail',                header: 'Mail' },
  { field: 'phone',               header: 'Phone' },
]

const DEFAULT_COLS = [
  'address_id', 'home_id', 'name', 'appoin_date', 'appoin_slot',
  'appoin_status_label', 'workgroup_label', 'approve_notes', 'approve_status_label',
  'approve_work', 'area', 'building_hp', 'building_type_label', 'building_wo',
  'city', 'dp', 'hz', 'hzz', 'insyte_notes', 'insyte_status_label', 'pop', 'street', 'work_type',
]

const STORAGE_KEY = 'wo_selected_cols'

function loadColPrefs() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) return JSON.parse(saved)
  } catch { /* ignore */ }
  return DEFAULT_COLS
}

const selectedCols = ref(loadColPrefs())

function saveColPrefs() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(selectedCols.value))
}

const SORTABLE_FIELDS = new Set([
  'appoin_date', 'appoin_slot', 'name', 'address_id',
  'appoin_status_label', 'workgroup_label', 'insyte_status_label',
  'approve_status_label', 'install_status_label', 'synced_at',
])

const visibleColumns = computed(() =>
  selectedCols.value
    .map(field => ALL_COLUMNS.find(c => c.field === field))
    .filter(Boolean)
)

function onColumnReorder(event) {
  // Frozen columns (eye + tag) are excluded from reorder indices by PrimeVue
  // Only non-frozen fixed columns count: expander (grouped view only)
  const fixedCount = ordersStore.groupedView ? 1 : 0
  const from = event.dragIndex - fixedCount
  const to = event.dropIndex - fixedCount
  if (from < 0 || to < 0 || from >= selectedCols.value.length || to >= selectedCols.value.length) return
  const cols = [...selectedCols.value]
  const [moved] = cols.splice(from, 1)
  cols.splice(to, 0, moved)
  selectedCols.value = cols
  saveColPrefs()
}

// ── Filters ────────────────────────────────────────────────────────────────
const searchInput = ref('')
const dateFrom = ref(null)
const dateTo = ref(null)

const filters = reactive({
  appoin_status: null,
  workgroup: null,
  priority: null,
  install_status: null,
  hc_status: null,
  approve_status: null,
  building_type: null,
})

let searchTimer = null
function debouncedSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => applySearch(), 500)
}

function applySearch() {
  ordersStore.setFilter('search', searchInput.value)
  ordersStore.fetchOrders()
}

function applyFilters() {
  Object.entries(filters).forEach(([k, v]) => ordersStore.setFilter(k, v))
  ordersStore.setFilter('date_from', dateFrom.value ? formatDate(dateFrom.value) : null)
  ordersStore.setFilter('date_to', dateTo.value ? formatDate(dateTo.value) : null)
  ordersStore.fetchOrders()
}

function clearFilters() {
  searchInput.value = ''
  dateFrom.value = null
  dateTo.value = null
  Object.keys(filters).forEach(k => { filters[k] = null })
  ordersStore.clearFilters()
  ordersStore.fetchOrders()
}

function onPage(event) {
  ordersStore.pageSize = event.rows
  ordersStore.setPage(event.page + 1)
  ordersStore.fetchOrders()
}

function onSort(event) {
  // sortField may be the label field; map to the backend field
  const fieldMap = {
    appoin_status_label: 'appoin_status',
    insyte_status_label: 'insyte_status',
    workgroup_label: 'workgroup',
    approve_status_label: 'approve_status',
    install_status_label: 'install_status',
  }
  const backendField = fieldMap[event.sortField] || event.sortField
  const order = event.sortOrder === 1 ? 'asc' : 'desc'
  ordersStore.setSort(backendField, order)
  ordersStore.fetchOrders()
}

function onRowClick({ data }) {
  router.push(`/workorders/${data.id}`)
}

function masterOptions(key) {
  const master = ordersStore.masters[key]
  if (!master) return []
  return master.maestroDataEnabled || master.maestroData || (Array.isArray(master) ? master : [])
}

const appointClassMap = {
  1: 'status-appoin-1', 2: 'status-appoin-2', 3: 'status-appoin-3',
  4: 'status-appoin-4', 5: 'status-appoin-5', 6: 'status-appoin-6', 7: 'status-appoin-7',
}
function appointClass(status) { return appointClassMap[status] || 'status-appoin-default' }

const appointIconMap = {
  1: 'pi pi-clock', 2: 'pi pi-check-circle', 3: 'pi pi-spin pi-spinner',
  4: 'pi pi-times-circle', 5: 'pi pi-calendar', 6: 'pi pi-pause-circle', 7: 'pi pi-ban',
}
function appointIcon(status) { return appointIconMap[status] || 'pi pi-circle' }

function formatDate(d) {
  if (!d) return null
  return new Date(d).toISOString().split('T')[0]
}
</script>
