import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export default {
  // Orders
  getOrders(params = {}) {
    return api.get('/orders', { params })
  },
  getOrder(id) {
    return api.get(`/orders/${id}`)
  },
  getSubOrders(id) {
    return api.get(`/orders/${id}/sub-orders`)
  },

  // Masters
  getMasters() {
    return api.get('/masters')
  },

  // Sync
  triggerSync() {
    return api.post('/sync')
  },
  fixLabels() {
    return api.post('/sync/fix-labels')
  },
  getSyncStatus() {
    return api.get('/sync/status')
  },
  getSyncLogs() {
    return api.get('/sync/logs')
  },

  // Classification / Board
  setClassification(id, classification, note) {
    return api.patch(`/orders/${id}/classification`, { classification, note: note || null })
  },
  getBoard() {
    return api.get('/board')
  },

  // SSE progress URL (used with EventSource)
  syncProgressUrl: '/api/sync/progress',
}
