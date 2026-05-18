import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export function getGameChapters() {
  return api.get('/game/chapters')
}

export function getGameScenes(chapterId) {
  return api.get(`/game/chapter/${chapterId}/scenes`)
}

export function getGameScene(sceneId) {
  return api.get(`/game/scene/${sceneId}`)
}

export function verifyAnswer(sceneId, answer) {
  return api.post(`/game/verify/${sceneId}`, { answer })
}
