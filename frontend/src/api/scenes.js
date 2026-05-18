import adminApi from './admin'

export function createScene(data) {
  return adminApi.post('/scenes', data)
}

export function updateScene(id, data) {
  return adminApi.put(`/scenes/${id}`, data)
}

export function deleteScene(id) {
  return adminApi.delete(`/scenes/${id}`)
}

export function duplicateScene(id) {
  return adminApi.post(`/scenes/${id}/duplicate`)
}

export function reorderScenes(data) {
  return adminApi.put('/scenes/reorder', data)
}

export function getAvailableNextScenes(chapterId) {
  return adminApi.get('/scenes/available-next', { params: { chapter_id: chapterId } })
}
