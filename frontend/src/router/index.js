import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue') },
  { path: '/game', name: 'Game', component: () => import('../views/GamePlay.vue') },
  { path: '/admin/login', name: 'AdminLogin', component: () => import('../views/AdminLogin.vue') },
  { path: '/admin', name: 'Admin', component: () => import('../views/AdminDashboard.vue') },
  { path: '/admin/chapters/:id', name: 'ChapterEdit', component: () => import('../views/ChapterEdit.vue') },
  { path: '/admin/characters', name: 'Characters', component: () => import('../views/CharacterManage.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const adminRoutes = ['Admin', 'ChapterEdit', 'Characters']

router.beforeEach((to, from, next) => {
  if (to.path === '/' || to.path === '/login' || to.path === '/register' || to.path === '/admin/login') {
    next()
    return
  }

  if (adminRoutes.includes(to.name)) {
    const adminToken = localStorage.getItem('admin_token')
    if (!adminToken) {
      next('/admin/login')
      return
    }
    next()
    return
  }

  const token = localStorage.getItem('token')
  if (!token) {
    next('/login')
  } else {
    next()
  }
})

export default router
