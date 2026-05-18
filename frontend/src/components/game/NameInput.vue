<template>
  <div class="name-input">
    <div class="panel">
      <h1 class="title">解谜之旅</h1>
      <p class="subtitle">选择游玩人数</p>

      <div class="player-count-select">
        <button
          v-for="n in 5"
          :key="n"
          :class="['count-btn', { active: playerCount === n }]"
          @click="playerCount = n"
        >
          {{ n }}人
        </button>
      </div>

      <p class="subtitle" style="margin-top:24px">请输入你的名字</p>
      <div class="input-group">
        <input v-model="name" placeholder="输入你的名字..." maxlength="20" @keyup.enter="confirm" />
        <button :disabled="!name.trim()" @click="confirm">确认</button>
      </div>

      <p v-if="playerCount >= 2" class="room-hint">
        选择 {{ playerCount }} 人模式，将创建房间等待其他玩家加入
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['confirm'])
const playerCount = ref(1)
const name = ref('')

function confirm() {
  if (name.value.trim()) {
    emit('confirm', { name: name.value.trim(), playerCount: playerCount.value })
  }
}
</script>

<style scoped>
.name-input {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
}
.panel {
  text-align: center;
  padding: 60px 40px;
  background: rgba(255,255,255,0.08);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.15);
  max-width: 420px;
  width: 100%;
}
.title {
  font-size: 42px;
  color: #fff;
  margin-bottom: 20px;
  text-shadow: 0 0 20px rgba(100,100,255,0.5);
}
.subtitle {
  color: rgba(255,255,255,0.6);
  margin-bottom: 12px;
  font-size: 15px;
}
.player-count-select {
  display: flex;
  gap: 8px;
  justify-content: center;
}
.count-btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.04);
  color: rgba(255,255,255,0.6);
  font-size: 16px;
  cursor: pointer;
  transition: 0.2s;
  min-width: 60px;
}
.count-btn.active {
  background: rgba(108,92,231,0.3);
  border-color: #6c5ce7;
  color: #fff;
}
.count-btn:hover {
  background: rgba(255,255,255,0.1);
}
.input-group {
  display: flex;
  gap: 8px;
  justify-content: center;
}
.input-group input {
  padding: 12px 20px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.1);
  color: #fff;
  font-size: 16px;
  width: 220px;
  outline: none;
}
.input-group input::placeholder {
  color: rgba(255,255,255,0.4);
}
.input-group button {
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  background: #6c5ce7;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  transition: 0.2s;
}
.input-group button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.input-group button:not(:disabled):hover {
  background: #5a4bd1;
}
.room-hint {
  margin-top: 16px;
  color: #fdcb6e;
  font-size: 13px;
}
</style>
