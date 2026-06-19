import { defineStore } from 'pinia'
import api from '../services/api'

export const useOrdersStore = defineStore('orders', {
  state: () => ({
    orders: [],
    total: 0,
    totalUnclassified: 0,
    boardTotal: 0,
    page: 1,
    pageSize: 200,
    loading: false,
    masters: {},
    sortBy: 'appoin_date',
    sortOrder: 'desc',
    filters: {
      search: '',
      appoin_status: null,
      priority: null,
      workgroup: null,
      install_status: null,
      insyte_status: null,
      approve_status: null,
      hc_status: null,
      building_type: null,
      date_from: null,
      date_to: null,
      hide_classified: false,
    },
    sync: {
      running: false,
      status: 'idle',
      orders_synced: 0,
      files_downloaded: 0,
      message: '',
      error: null,
    },
    lastSyncedAt: null,
    groupedView: false,
  }),

  getters: {
    masterList: (state) => (key) => {
      const master = state.masters[key]
      if (!master) return []
      return (master.maestroData || master) || []
    },
  },

  actions: {
    async fetchOrders() {
      this.loading = true
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize,
          sort_by: this.sortBy,
          sort_order: this.sortOrder,
        }
        // Add active filters
        Object.entries(this.filters).forEach(([k, v]) => {
          if (k === 'hide_classified') {
            if (v) params[k] = true
          } else if (v !== null && v !== '' && v !== undefined) {
            params[k] = v
          }
        })
        if (this.groupedView) params.grouped = true
        const res = await api.getOrders(params)
        this.orders = res.data.data
        this.total = res.data.total
        this.totalUnclassified = res.data.total_unclassified ?? 0
      } catch (e) {
        console.error('fetchOrders error', e)
      } finally {
        this.loading = false
      }
    },

    async fetchMasters() {
      try {
        const res = await api.getMasters()
        this.masters = res.data
      } catch (e) {
        console.error('fetchMasters error', e)
      }
    },

    setFilter(key, value) {
      this.filters[key] = value
      this.page = 1
    },

    clearFilters() {
      Object.keys(this.filters).forEach(k => { this.filters[k] = null })
      this.filters.search = ''
      this.filters.hide_classified = false
      this.page = 1
    },

    setPage(p) {
      this.page = p
    },

    setSort(field, order) {
      this.sortBy = field
      this.sortOrder = order
      this.page = 1
    },

    async triggerSync() {
      try {
        await api.triggerSync()
        this.listenSyncProgress()
      } catch (e) {
        console.error('triggerSync error', e)
      }
    },

    listenSyncProgress() {
      const es = new EventSource(api.syncProgressUrl)
      es.onmessage = (event) => {
        const data = JSON.parse(event.data)
        this.sync = data
        if (!data.running && (data.status === 'completed' || data.status === 'error')) {
          es.close()
          if (data.status === 'completed') {
            this.lastSyncedAt = new Date()
            this.fetchOrders()
            this.fetchMasters()
          }
        }
      }
      es.onerror = () => es.close()
    },

    async checkSyncStatus() {
      try {
        const res = await api.getSyncStatus()
        this.sync = res.data
        if (res.data.running) {
          this.listenSyncProgress()
        }
      } catch (e) {
        console.error('checkSyncStatus error', e)
      }
    },
  },
})
