import adminApi from './admin'

export function getCharacters() {
  return adminApi.get('/characters')
}

export function createCharacter(formData) {
  return adminApi.post('/characters', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function updateCharacter(id, formData) {
  return adminApi.put(`/characters/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function deleteCharacter(id) {
  return adminApi.delete(`/characters/${id}`)
}
