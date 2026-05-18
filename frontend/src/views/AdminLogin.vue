<template>
  <div class="admin-login-page">
    <div class="login-card">
      <h1>管理后台</h1>
      <p class="desc">请输入管理员账号和密码</p>
      <div class="form">
        <input v-model="username" placeholder="管理员账号" />
        <input v-model="password" type="password" placeholder="密码" @keyup.enter="handleLogin" />
        <p v-if="error" class="error">{{ error }}</p>
        <button @click="handleLogin" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </div>
      <router-link to="/game" class="back-link">返回游戏</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { adminLogin } from '../api/admin'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = '请输入账号和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await adminLogin(username.value, password.value)
    localStorage.setItem('admin_token', res.data.token)
    router.push('/admin')
  } catch (e) {
    error.value = e.response?.data?.error || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.admin-login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
}
.login-card {
  background: rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 48px 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.15);
  width: 380px;
  text-align: center;
}
.login-card h1 {
  color: #a29bfe;
  font-size: 28px;
  margin-bottom: 8px;
}
.desc {
  color: rgba(255,255,255,0.5);
  font-size: 14px;
  margin-bottom: 28px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.form input {
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.1);
  color: #fff;
  font-size: 15px;
  outline: none;
}
.form input::placeholder {
  color: rgba(255,255,255,0.4);
}
.form button {
  padding: 12px;
  border-radius: 8px;
  border: none;
  background: #6c5ce7;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  transition: 0.2s;
}
.form button:hover:not(:disabled) {
  background: #5a4bd1;
}
.form button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.error {
  color: #ff7675;
  font-size: 13px;
}
.back-link {
  display: inline-block;
  margin-top: 20px;
  color: rgba(255,255,255,0.4);
  font-size: 13px;
  text-decoration: none;
}
</style>
