<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>注册账号</h1>
      <p class="auth-desc">创建你的账号，开始解谜之旅</p>
      <div class="form">
        <input v-model="username" placeholder="用户名" />
        <input v-model="password" type="password" placeholder="密码" @keyup.enter="handleRegister" />
        <p v-if="error" class="error">{{ error }}</p>
        <button @click="handleRegister" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </div>
      <p class="switch">已有账号？<router-link to="/login">登录</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../api/auth'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  if (!username.value || !password.value) {
    error.value = '请填写用户名和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await register(username.value, password.value)
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    router.push('/game')
  } catch (e) {
    error.value = e.response?.data?.error || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
}
.auth-card {
  background: rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 48px 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.15);
  width: 380px;
  text-align: center;
}
.auth-card h1 {
  color: #fff;
  font-size: 32px;
  margin-bottom: 8px;
}
.auth-desc {
  color: rgba(255,255,255,0.5);
  margin-bottom: 28px;
  font-size: 14px;
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
.switch {
  margin-top: 20px;
  color: rgba(255,255,255,0.5);
  font-size: 13px;
}
.switch a {
  color: #a29bfe;
  text-decoration: none;
}
</style>
