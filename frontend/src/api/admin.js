import axios from 'axios'

const adminApi = axios.create({ baseURL: '/api' })

adminApi.interceptors.request.use(config => {
  const token = localStorage.getItem('admin_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export function adminLogin(username, password) {
  return axios.post('/api/admin/login', { username, password })
}

export function changePassword(oldPassword, newPassword) {
  return adminApi.post('/admin/change-password', { old_password: oldPassword, new_password: newPassword })
}

export default adminApi
