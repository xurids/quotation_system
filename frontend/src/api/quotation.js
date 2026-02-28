import axios from 'axios'

const api = axios.create({ 
  baseURL: '/api', 
  timeout: 30000 
})

export const projects = {
  list: () => api.get('/projects/'),
  get: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects/', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`)
}

export const expenses = {
  getProjectSummary: (projectId) => api.get(`/expenses/projects/${projectId}/summary`),
  batchUpdate: (projectId, modules) => api.put(`/projects/${projectId}/batch-update`, modules)
}

export const clients = {
  list: () => api.get('/clients/'),
  get: (id) => api.get(`/clients/${id}`),
  create: (data) => api.post('/clients/', data),
  update: (id, data) => api.put(`/clients/${id}`, data),
  delete: (id) => api.delete(`/clients/${id}`)
}

export const quotations = {
  list: () => api.get('/quotations/'),
  createVersion: (projectId, data) => api.post(`/quotations/create-version/${projectId}`, data),
  exportExcel: (projectId, selectedIds) => api.post(`/projects/${projectId}/export-excel`, selectedIds, { responseType: 'blob' })
}

export const templates = {
  list: () => api.get('/templates/')
}

export default api
