import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export function createRoom(maxPlayers, chapterId, playerName) {
  return api.post('/rooms/create', { max_players: maxPlayers, chapter_id: chapterId, player_name: playerName })
}

export function joinRoom(code, playerName) {
  return api.post('/rooms/join', { code, player_name: playerName })
}

export function getRoom(code) {
  return api.get(`/rooms/${code}`)
}

export function startGame(code, chapterId) {
  return api.post(`/rooms/${code}/start`, { chapter_id: chapterId })
}

export function puzzleDone(code) {
  return api.post(`/rooms/${code}/puzzle-done`)
}

export function advanceScene(code) {
  return api.post(`/rooms/${code}/advance-scene`)
}

export function leaveRoom(code) {
  return api.post(`/rooms/${code}/leave`)
}

export function heartbeat(code) {
  return api.post(`/rooms/${code}/heartbeat`)
}

export function getMyActiveRoom() {
  return api.get('/rooms/my-active')
}
