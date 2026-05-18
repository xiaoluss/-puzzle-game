import adminApi from './admin'

export function getChapters() {
  return adminApi.get('/chapters')
}

export function getChapter(id) {
  return adminApi.get(`/chapters/${id}`)
}

export function createChapter(title) {
  return adminApi.post('/chapters', { title })
}

export function updateChapter(id, data) {
  return adminApi.put(`/chapters/${id}`, data)
}

export function deleteChapter(id) {
  return adminApi.delete(`/chapters/${id}`)
}

export function duplicateChapter(id) {
  return adminApi.post(`/chapters/${id}/duplicate`)
}

export function reorderChapters(data) {
  return adminApi.put('/chapters/reorder', data)
}
