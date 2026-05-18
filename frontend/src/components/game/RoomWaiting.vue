<template>
  <div class="room-waiting">
    <div class="waiting-panel">
      <div class="spinner"></div>
      <h3>等待其他玩家...</h3>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: percent + '%' }"></div>
      </div>
      <p class="progress-text">{{ completedCount }} / {{ totalCount }} 人已完成解谜</p>
      <div class="member-status">
        <div v-for="m in members" :key="m.id" class="member-row">
          <span class="member-name">{{ m.player_name }}</span>
          <span v-if="m.puzzle_completed" class="status-done">已完成</span>
          <span v-else class="status-wait">解谜中...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  members: { type: Array, default: () => [] }
})

const completedCount = computed(() => props.members.filter(m => m.puzzle_completed).length)
const totalCount = computed(() => props.members.length)
const percent = computed(() =>
  totalCount.value ? Math.round((completedCount.value / totalCount.value) * 100) : 0
)
</script>

<style scoped>
.room-waiting {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  width: 100%;
}
.waiting-panel {
  text-align: center;
  padding: 40px;
  background: rgba(0,0,0,0.5);
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.08);
  max-width: 380px;
  width: 100%;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255,255,255,0.1);
  border-top-color: #6c5ce7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.waiting-panel h3 {
  color: #fff;
  font-size: 18px;
  margin-bottom: 16px;
}
.progress-bar {
  height: 6px;
  background: rgba(255,255,255,0.08);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6c5ce7, #a29bfe);
  border-radius: 3px;
  transition: width 0.5s ease;
}
.progress-text {
  color: rgba(255,255,255,0.5);
  font-size: 13px;
  margin-bottom: 16px;
}
.member-status {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.member-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 12px;
  background: rgba(255,255,255,0.03);
  border-radius: 6px;
}
.member-name {
  color: #ddd;
  font-size: 14px;
}
.status-done {
  color: #55efc4;
  font-size: 13px;
}
.status-wait {
  color: #fdcb6e;
  font-size: 13px;
}
</style>
