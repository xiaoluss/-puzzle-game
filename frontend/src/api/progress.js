import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export function getProgress() {
  return api.get('/progress')
}

export function saveProgress(data) {
  return api.put('/progress', data)
}
