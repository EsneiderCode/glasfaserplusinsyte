<template>
  <div class="board-page">
    <!-- Header -->
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem;">
      <div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #1e293b;">Tablero de Clasificacion</div>
        <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 2px;">
          {{ totalClassified }} ordenes clasificadas
        </div>
      </div>
      <div style="display: flex; gap: 0.5rem;">
        <Button
          icon="pi pi-download"
          label="Exportar Excel"
          severity="secondary"
          outlined
          size="small"
          :loading="exporting"
          :disabled="loading"
          @click="exportToExcel"
        />
        <Button
          icon="pi pi-refresh"
          label="Actualizar"
          severity="secondary"
          outlined
          size="small"
          :loading="loading"
          @click="loadBoard"
        />
      </div>
    </div>

    <div v-if="loading" style="text-align: center; padding: 3rem; color: #94a3b8;">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem;"></i>
    </div>

    <div v-else class="board-scroll-wrapper">
      <div class="board-scroll-hint">
        <i class="pi pi-arrow-right"></i>
        <span>Desliza para ver más columnas</span>
        <i class="pi pi-arrow-right"></i>
      </div>
    <div class="board-grid" ref="boardGridRef" @scroll="onBoardScroll">
      <div
        v-for="col in COLUMNS"
        :key="col.key"
        class="board-column"
        :class="col.cssClass"
      >
        <div class="board-column-header">
          <span>{{ col.label }}</span>
          <span style="font-size: 0.85rem; opacity: 0.7;">{{ (grouped[col.key] || []).length }}</span>
        </div>
        <div class="board-column-body">
          <div
            v-for="order in (grouped[col.key] || [])"
            :key="order.id"
            class="board-card"
          >
            <div class="board-card-id">{{ order.address_id || '—' }}</div>
            <div class="board-card-name">{{ order.name || '—' }}</div>
            <div class="board-card-date">{{ order.appoin_date || 'Sin fecha' }}</div>
            <div v-if="order.workgroup_label" class="board-card-team">{{ order.workgroup_label }}</div>
            <div v-if="order.classification_note" class="board-card-note">
              <i class="pi pi-comment" style="font-size: 0.65rem; opacity: 0.6; flex-shrink: 0; margin-top: 2px;"></i>
              <span>{{ order.classification_note }}</span>
            </div>
            <div class="board-card-actions">
              <Button
                icon="pi pi-eye"
                rounded
                text
                size="small"
                style="color: #3b82f6; width: 28px; height: 28px;"
                title="Ver detalle"
                @click="router.push(`/workorders/${order.id}`)"
              />
              <Button
                icon="pi pi-arrows-h"
                rounded
                text
                size="small"
                style="color: #8b5cf6; width: 28px; height: 28px;"
                title="Mover a..."
                @click="openMoveMenu(order, $event)"
              />
              <Button
                icon="pi pi-times"
                rounded
                text
                size="small"
                style="color: #dc2626; width: 28px; height: 28px;"
                title="Quitar clasificacion"
                @click="removeClassification(order)"
              />
            </div>
          </div>
          <div v-if="!(grouped[col.key] || []).length" style="text-align: center; padding: 1.5rem 0.5rem; color: #cbd5e1; font-size: 0.78rem;">
            Sin ordenes
          </div>
        </div>
      </div>
    </div>
    <div class="board-fade-right" :class="{ hidden: scrolledToEnd }"></div>
    </div>

    <!-- Move popup -->
    <div v-if="moveMenu.visible" class="classify-popup" :style="{ top: moveMenu.y + 'px', left: moveMenu.x + 'px' }" @click.stop>
      <div class="classify-popup-title">Mover a...</div>
      <button
        v-for="col in COLUMNS"
        :key="col.key"
        class="classify-option"
        :class="{ active: moveMenu.order && moveMenu.order.classification === col.key }"
        @click="moveOrder(col.key)"
      >{{ col.label }}</button>
      <div class="classify-divider"></div>
      <button class="classify-option classify-cancel" @click="moveMenu.visible = false">Cancelar</button>
    </div>
    <div v-if="moveMenu.visible" class="classify-backdrop" @click="moveMenu.visible = false"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import Button from 'primevue/button'
import { useOrdersStore } from '../stores/orders'

const router = useRouter()
const ordersStore = useOrdersStore()
const loading = ref(false)
const exporting = ref(false)
const grouped = ref({})
const boardStats = ref({ total_orders: 0, total_classified: 0, total_unclassified: 0 })
const boardGridRef = ref(null)
const scrolledToEnd = ref(false)

function onBoardScroll() {
  const el = boardGridRef.value
  if (!el) return
  scrolledToEnd.value = el.scrollLeft + el.clientWidth >= el.scrollWidth - 8
}

const COLUMNS = [
  { key: 'YA CERTIFICADOS',         label: 'Aprobados',          cssClass: 'board-col-cert' },
  { key: 'PENDIENTES POR REVISION', label: 'Pend. por Revision', cssClass: 'board-col-rev' },
  { key: 'DEVUELTOS',               label: 'Devueltos',           cssClass: 'board-col-dev' },
  { key: 'POR HACER',               label: 'Por Hacer',           cssClass: 'board-col-todo' },
  { key: 'SIN SUBIRSE',             label: 'Sin Subirse',         cssClass: 'board-col-sin' },
  { key: 'CANCELADOS',              label: 'Cancelados',          cssClass: 'board-col-cancel' },
]

const totalClassified = computed(() =>
  COLUMNS.reduce((sum, col) => sum + (grouped.value[col.key] || []).length, 0)
)

const moveMenu = reactive({ visible: false, order: null, x: 0, y: 0 })

async function loadBoard() {
  loading.value = true
  try {
    const res = await api.getBoard()
    grouped.value = res.data.grouped
    boardStats.value = {
      total_orders: res.data.total_orders,
      total_classified: res.data.total_classified,
      total_unclassified: res.data.total_unclassified,
    }
    ordersStore.boardTotal = res.data.total_classified
  } catch (e) {
    console.error('loadBoard error', e)
  } finally {
    loading.value = false
  }
}

function openMoveMenu(order, event) {
  const rect = event.target.closest('button').getBoundingClientRect()
  moveMenu.order = order
  moveMenu.x = Math.min(rect.left, window.innerWidth - 240)
  moveMenu.y = rect.bottom + 4
  moveMenu.visible = true
}

async function moveOrder(newClassification) {
  if (!moveMenu.order) return
  const order = moveMenu.order
  moveMenu.visible = false
  try {
    await api.setClassification(order.id, newClassification)
    await loadBoard()
  } catch (e) {
    console.error('moveOrder error', e)
  }
}

async function removeClassification(order) {
  try {
    await api.setClassification(order.id, null)
    await loadBoard()
  } catch (e) {
    console.error('removeClassification error', e)
  }
}

// ─── Excel Export ────────────────────────────────────────────────────────────

const COL_META = {
  'YA CERTIFICADOS':         { color: '1E8E3E', tabColor: 'FF1E8E3E' },
  'PENDIENTES POR REVISION': { color: '1A73E8', tabColor: 'FF1A73E8' },
  'DEVUELTOS':               { color: 'D93025', tabColor: 'FFD93025' },
  'POR HACER':               { color: '7C3AED', tabColor: 'FF7C3AED' },
  'SIN SUBIRSE':             { color: '64748B', tabColor: 'FF64748B' },
  'CANCELADOS':              { color: '374151', tabColor: 'FF374151' },
}

function xlFill(argb) {
  return { type: 'pattern', pattern: 'solid', fgColor: { argb } }
}

function xlFont(opts = {}) {
  return { name: 'Calibri', size: opts.size || 11, bold: opts.bold || false,
           italic: opts.italic || false, color: { argb: opts.color || 'FF0A0B0D' } }
}

function xlBorder(color = 'FFDED8CA') {
  const s = { style: 'thin', color: { argb: color } }
  return { top: s, left: s, bottom: s, right: s }
}

function xlAlign(horizontal = 'left', vertical = 'middle') {
  return { horizontal, vertical, wrapText: true }
}

async function exportToExcel() {
  exporting.value = true
  try {
    const ExcelJS = (await import('exceljs')).default
    const wb = new ExcelJS.Workbook()
    wb.creator = 'Workorders Agent · GF+'
    wb.created = new Date()

    const now = new Date()
    const dateStr = now.toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' })
    const timeStr = now.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
    const stats = boardStats.value
    const coveragePct = stats.total_orders > 0 ? stats.total_classified / stats.total_orders : 0

    // ── Sheet 1: Resumen ──────────────────────────────────────────────────────
    const ws0 = wb.addWorksheet('Resumen', {
      properties: { tabColor: { argb: 'FFFF4D2E' } },
    })
    ws0.pageSetup = { paperSize: 9, orientation: 'portrait', fitToPage: true, fitToWidth: 1 }

    // Title block
    ws0.mergeCells('A1:E1')
    const t1 = ws0.getCell('A1')
    t1.value = 'TABLERO DE CLASIFICACIÓN'
    t1.fill = xlFill('FFFF4D2E')
    t1.font = xlFont({ size: 16, bold: true, color: 'FFFFFFFF' })
    t1.alignment = xlAlign('center')
    t1.border = xlBorder('FFFF4D2E')
    ws0.getRow(1).height = 32

    ws0.mergeCells('A2:E2')
    const t2 = ws0.getCell('A2')
    t2.value = `Exportado el ${dateStr} a las ${timeStr}`
    t2.fill = xlFill('FFEAE6DC')
    t2.font = xlFont({ size: 10, italic: true, color: 'FF646660' })
    t2.alignment = xlAlign('center')
    ws0.getRow(2).height = 18

    ws0.getRow(3).height = 10

    // ── KPI coverage block (rows 4-6) ─────────────────────────────────────────
    const kpiDefs = [
      { label: 'Total en Insyte',  value: stats.total_orders,       sub: 'Órdenes en la base de datos',   color: 'FF1A73E8', fmt: '#,##0' },
      { label: 'Clasificados',     value: stats.total_classified,    sub: 'Con categoría asignada',         color: 'FF1E8E3E', fmt: '#,##0' },
      { label: 'Sin Clasificar',   value: stats.total_unclassified,  sub: 'Pendientes de clasificar',       color: 'FFD93025', fmt: '#,##0' },
      { label: 'Cobertura',        value: coveragePct,               sub: `${(coveragePct * 100).toFixed(1)}% del total clasificado`, color: 'FF7C3AED', fmt: '0.0%' },
    ]
    const kpiCols = ['A', 'B', 'C', 'D']
    ws0.mergeCells('D4:E4')
    ws0.mergeCells('D5:E5')
    ws0.mergeCells('D6:E6')

    kpiDefs.forEach((kpi, i) => {
      const col = kpiCols[i]
      const hc = ws0.getCell(`${col}4`)
      hc.value = kpi.label
      hc.fill = xlFill(kpi.color)
      hc.font = xlFont({ size: 10, bold: true, color: 'FFFFFFFF' })
      hc.alignment = xlAlign('center')
      hc.border = xlBorder(kpi.color)

      const vc = ws0.getCell(`${col}5`)
      vc.value = kpi.value
      vc.fill = xlFill('FFFFFFFF')
      vc.font = { name: 'Calibri', size: 20, bold: true, color: { argb: kpi.color } }
      vc.alignment = xlAlign('center')
      vc.border = xlBorder(kpi.color)
      vc.numFmt = kpi.fmt

      const sc = ws0.getCell(`${col}6`)
      sc.value = kpi.sub
      sc.fill = xlFill('FFF5F3EE')
      sc.font = xlFont({ size: 9, italic: true, color: 'FF646660' })
      sc.alignment = xlAlign('center')
      sc.border = xlBorder(kpi.color)
    })
    ws0.getRow(4).height = 20
    ws0.getRow(5).height = 34
    ws0.getRow(6).height = 16
    ws0.getRow(7).height = 10

    // ── Category table (row 8+) ────────────────────────────────────────────────
    const TABLE_START = 8
    ws0.getRow(TABLE_START).height = 22
    ;['Categoría', 'Órdenes', '% del Clasificado', 'Estado', 'Indicador visual'].forEach((label, i) => {
      const c = ws0.getCell(TABLE_START, i + 1)
      c.value = label
      c.fill = xlFill('FF0A0B0D')
      c.font = xlFont({ bold: true, color: 'FFFFFFFF', size: 11 })
      c.alignment = xlAlign(i === 0 ? 'left' : 'center')
      c.border = xlBorder('FF0A0B0D')
    })

    COLUMNS.forEach((col, idx) => {
      const orders = grouped.value[col.key] || []
      const count = orders.length
      const pct = stats.total_classified > 0 ? count / stats.total_classified : 0
      const rowNum = TABLE_START + 1 + idx
      const bg = idx % 2 === 0 ? 'FFFFFFFF' : 'FFF5F3EE'
      const meta = COL_META[col.key] || {}
      const catColor = 'FF' + (meta.color || '64748B')

      ws0.getRow(rowNum).height = 20

      const cA = ws0.getCell(`A${rowNum}`)
      cA.value = col.label
      cA.fill = xlFill(bg)
      cA.font = xlFont({ bold: true, color: catColor })
      cA.alignment = xlAlign('left')
      cA.border = xlBorder()

      const cB = ws0.getCell(`B${rowNum}`)
      cB.value = count
      cB.fill = xlFill(bg)
      cB.font = xlFont({ bold: count > 0 })
      cB.alignment = xlAlign('center')
      cB.border = xlBorder()
      cB.numFmt = '#,##0'

      const cC = ws0.getCell(`C${rowNum}`)
      cC.value = pct
      cC.fill = xlFill(bg)
      cC.font = xlFont({ color: 'FF646660' })
      cC.alignment = xlAlign('center')
      cC.border = xlBorder()
      cC.numFmt = '0.0%'

      const cD = ws0.getCell(`D${rowNum}`)
      cD.value = count === 0 ? 'Sin órdenes' : count > 10 ? 'Activo' : 'Bajo volumen'
      cD.fill = xlFill(bg)
      cD.font = xlFont({
        color: count === 0 ? 'FF9A9A94' : count > 10 ? 'FF1E8E3E' : 'FFD97706',
        italic: count === 0,
      })
      cD.alignment = xlAlign('center')
      cD.border = xlBorder()

      const cE = ws0.getCell(`E${rowNum}`)
      const bar = count === 0 ? '—' : '█'.repeat(Math.min(Math.round(pct * 100 / 5), 20))
      cE.value = bar
      cE.fill = xlFill(bg)
      cE.font = { name: 'Courier New', size: 10, color: { argb: catColor } }
      cE.alignment = xlAlign('left')
      cE.border = xlBorder()
    })

    // Total row
    const totalRowNum = TABLE_START + 1 + COLUMNS.length
    ws0.getRow(totalRowNum).height = 22
    const tA = ws0.getCell(`A${totalRowNum}`)
    tA.value = 'TOTAL CLASIFICADOS'
    tA.fill = xlFill('FFDED8CA')
    tA.font = xlFont({ bold: true })
    tA.alignment = xlAlign('left')
    tA.border = xlBorder('FF0A0B0D')

    const tB = ws0.getCell(`B${totalRowNum}`)
    tB.value = stats.total_classified
    tB.fill = xlFill('FFDED8CA')
    tB.font = xlFont({ bold: true })
    tB.alignment = xlAlign('center')
    tB.border = xlBorder('FF0A0B0D')
    tB.numFmt = '#,##0'

    const tC = ws0.getCell(`C${totalRowNum}`)
    tC.value = 1
    tC.fill = xlFill('FFDED8CA')
    tC.font = xlFont({ bold: true })
    tC.alignment = xlAlign('center')
    tC.border = xlBorder('FF0A0B0D')
    tC.numFmt = '0.0%'

    ;['D', 'E'].forEach(col => {
      const c = ws0.getCell(`${col}${totalRowNum}`)
      c.fill = xlFill('FFDED8CA')
      c.border = xlBorder('FF0A0B0D')
    })

    // Footer
    const footerRow = totalRowNum + 2
    ws0.mergeCells(`A${footerRow}:E${footerRow}`)
    const foot = ws0.getCell(`A${footerRow}`)
    foot.value = 'Workorders Agent · GF+ · Field Operations'
    foot.font = xlFont({ size: 9, italic: true, color: 'FF9A9A94' })
    foot.alignment = xlAlign('center')

    ws0.columns = [
      { width: 30 },
      { width: 12 },
      { width: 18 },
      { width: 16 },
      { width: 22 },
    ]

    // ── Sheets per category ───────────────────────────────────────────────────
    const SHEET_HEADERS = ['#', 'Address ID', 'Home ID', 'Address', 'Fecha', 'Building WO', 'Building Type',
      'Notas del Técnico', 'Approve Notes', 'Approve Status', 'Comentarios WO Agent']
    const SHEET_COLS = [
      { width: 5 },   // #
      { width: 16 },  // Address ID
      { width: 14 },  // Home ID
      { width: 30 },  // Address
      { width: 13 },  // Fecha
      { width: 16 },  // Building WO
      { width: 18 },  // Building Type
      { width: 42 },  // Notas del Técnico
      { width: 42 },  // Approve Notes
      { width: 20 },  // Approve Status
      { width: 38 },  // Comentarios WO Agent
    ]

    for (const col of COLUMNS) {
      const orders = grouped.value[col.key] || []
      const meta = COL_META[col.key] || {}
      const catArgb = 'FF' + (meta.color || '374151')
      const sheetName = col.label.replace(/\//g, '-').substring(0, 31)

      const ws = wb.addWorksheet(sheetName, {
        properties: { tabColor: { argb: catArgb } },
      })
      ws.pageSetup = { paperSize: 9, orientation: 'landscape', fitToPage: true, fitToWidth: 1 }

      // Title rows
      ws.mergeCells('A1:K1')
      const h1 = ws.getCell('A1')
      h1.value = col.label.toUpperCase()
      h1.fill = xlFill(catArgb)
      h1.font = xlFont({ size: 14, bold: true, color: 'FFFFFFFF' })
      h1.alignment = xlAlign('center')
      ws.getRow(1).height = 30

      ws.mergeCells('A2:K2')
      const h2 = ws.getCell('A2')
      h2.value = orders.length === 0
        ? 'Sin órdenes en esta categoría'
        : `${orders.length} orden${orders.length !== 1 ? 'es' : ''} · Exportado el ${dateStr}`
      h2.fill = xlFill('FFEAE6DC')
      h2.font = xlFont({ size: 10, italic: true, color: 'FF646660' })
      h2.alignment = xlAlign('center')
      ws.getRow(2).height = 18
      ws.getRow(3).height = 6

      // Column headers
      SHEET_HEADERS.forEach((label, i) => {
        const c = ws.getCell(4, i + 1)
        c.value = label
        c.fill = xlFill('FF0A0B0D')
        c.font = xlFont({ bold: true, color: 'FFFFFFFF', size: 10 })
        c.alignment = xlAlign(i === 0 ? 'center' : 'left')
        c.border = xlBorder('FF0A0B0D')
      })
      ws.getRow(4).height = 20
      ws.views = [{ state: 'frozen', ySplit: 4 }]

      // Data rows
      if (orders.length === 0) {
        ws.mergeCells('A5:K5')
        const empty = ws.getCell('A5')
        empty.value = 'Sin órdenes registradas en esta categoría'
        empty.fill = xlFill('FFFFFFFF')
        empty.font = xlFont({ italic: true, color: 'FF9A9A94' })
        empty.alignment = xlAlign('center')
        ws.getRow(5).height = 22
      } else {
        orders.forEach((order, idx) => {
          const rowNum = 5 + idx
          const bg = idx % 2 === 0 ? 'FFFFFFFF' : 'FFF5F3EE'

          const rawDate = order.appoin_date || ''
          const fmtDate = /^\d{4}-\d{2}-\d{2}/.test(rawDate)
            ? rawDate.replace(/^(\d{4})-(\d{2})-(\d{2}).*/, '$3/$2/$1')
            : rawDate || '—'

          // Build address: prefer full_address, fallback to street + hz + hzz, city
          let addr = order.full_address || ''
          if ((!addr || addr === order.street) && order.street && order.hz) {
            addr = order.street + ' ' + order.hz + (order.hzz || '')
            if (order.city) addr += ', ' + order.city
          }

          const vals = [
            idx + 1,
            order.address_id || '—',
            order.home_id || '—',
            addr || order.street || '—',
            fmtDate,
            order.building_wo || '—',
            order.building_type_label || '—',
            order.insyte_notes || '',
            order.approve_notes || '',
            order.approve_status_label || '—',
            order.classification_note || '',
          ]

          const noteLines = Math.max(
            (order.insyte_notes || '').split('\n').length,
            (order.approve_notes || '').split('\n').length,
            1,
          )
          ws.getRow(rowNum).height = Math.max(20, noteLines * 15)

          vals.forEach((val, ci) => {
            const c = ws.getCell(rowNum, ci + 1)
            c.value = val
            c.fill = xlFill(bg)
            c.border = xlBorder()
            if (ci === 0) {
              c.font = xlFont({ bold: true, color: catArgb, size: 10 })
              c.alignment = xlAlign('center')
            } else if (ci === 7 || ci === 8) {
              c.font = xlFont({ size: 10, color: 'FF646660' })
              c.alignment = { horizontal: 'left', vertical: 'top', wrapText: true }
            } else if (ci === 10) {
              c.font = xlFont({ size: 10, color: 'FF7C3AED', italic: true })
              c.alignment = { horizontal: 'left', vertical: 'top', wrapText: true }
            } else {
              c.font = xlFont({ size: 10, color: 'FF0A0B0D' })
              c.alignment = xlAlign('left')
            }
          })
        })
      }

      ws.columns = SHEET_COLS
    }

    // ── Download ──────────────────────────────────────────────────────────────
    const buf = await wb.xlsx.writeBuffer()
    const blob = new Blob([buf], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `tablero-clasificacion-${now.toISOString().slice(0, 10)}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('exportToExcel error', e)
  } finally {
    exporting.value = false
  }
}

// ─────────────────────────────────────────────────────────────────────────────

onMounted(async () => {
  await loadBoard()
  await nextTick()
  onBoardScroll()
})
</script>
