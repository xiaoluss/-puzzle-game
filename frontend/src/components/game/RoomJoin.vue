<template>
  <div class="room-join">
    <div class="join-panel">
      <h2>加入房间</h2>
      <p class="subtitle">输入房主给你的房间号</p>
      <div class="input-group">
        <input
          v-model="code"
          placeholder="输入6位房间号"
          maxlength="6"
          class="code-input"
          :disabled="loading"
          @keyup.enter="join"
        />
      </div>
      <p v-if="error" class="error">{{ error }}</p>
      <div class="actions">
        <button class="join-btn" :disabled="code.length < 6 || loading" @click="join">
          {{ loading ? '加入中...' : '加入' }}
        </button>
        <button class="back-btn" :disabled="loading" @click="$emit('back')">返回</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { joinRoom } from '../../api/rooms'

const props = defineProps({
  playerName: { type: String, default: '' }
})
const emit = defineEmits(['joined', 'back'])
const code = ref('')
const error = ref('')
const loading = ref(false)

async function join() {
  code.value = code.value.toUpperCase().replace(/[^A-Z0-9]/g, '')
  if (code.value.length < 6) return

  loading.value = true
  error.value = ''

  try {
    const res = await joinRoom(code.value, props.playerName || '玩家')
    emit('joined', res.data)
  } catch (e) {
    error.value = e.response?.data?.error || '加入房间失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.room-join {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
}
.join-panel {
  text-align: center;
  padding: 48px 40px;
  background: rgba(255,255,255,0.08);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.15);
  max-width: 380px;
  width: 100%;
}
.join-panel h2 {
  color: #fff;
  font-size: 24px;
  margin-bottom: 8px;
}
.subtitle {
  color: rgba(255,255,255,0.5);
  font-size: 14px;
  margin-bottom: 24px;
}
.code-input {
  padding: 14px 20px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.08);
  color: #fff;
  font-size: 28px;
  width: 220px;
  outline: none;
  text-align: center;
  letter-spacing: 6px;
  text-transform: uppercase;
}
.code-input:disabled {
  opacity: 0.5;
}
.code-input::placeholder {
  font-size: 14px;
  letter-spacing: 1px;
  color: rgba(255,255,255,0.3);
}
.error {
  color: #ff7675;
  font-size: 13px;
  margin-top: 8px;
}
.actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}
.join-btn {
  padding: 10px 32px;
  border-radius: 8px;
  border: none;
  background: #6c5ce7;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  transition: 0.2s;
}
.join-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.join-btn:not(:disabled):hover {
  background: #5a4bd1;
}
.back-btn {
  padding: 10px 24px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.15);
  background: none;
  color: rgba(255,255,255,0.6);
  font-size: 16px;
  cursor: pointer;
  transition: 0.2s;
}
.back-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
