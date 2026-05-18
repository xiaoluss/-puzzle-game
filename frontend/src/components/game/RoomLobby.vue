<template>
  <div class="room-lobby">
    <div class="lobby-panel">
      <h2>等待玩家加入</h2>
      <div class="room-code-box">
        <span class="code-label">房间号</span>
        <span class="code-value">{{ roomCode }}</span>
      </div>

      <div class="player-list">
        <div
          v-for="(m, i) in memberSlots"
          :key="m?.id ?? i"
          :class="['player-item', { empty: !m }]"
        >
          <div class="player-avatar">{{ m ? m.player_name[0] : '?' }}</div>
          <span class="player-name">{{ m ? m.player_name : '等待加入...' }}</span>
          <span v-if="m && isHostUser(m)" class="host-badge">队长</span>
          <span v-else-if="m" class="member-badge">队员</span>
          <span v-if="m" :class="['status-dot', m.online ? 'online' : 'offline']" :title="m.online ? '在线' : '离线'"></span>
        </div>
      </div>

      <p class="player-count">{{ memberCount }} / {{ maxPlayers }} 人</p>

      <div v-if="isHost" class="host-actions">
        <button class="start-btn" :disabled="memberCount < 2" @click="$emit('start')">
          开始游戏
        </button>
      </div>
      <div v-else>
        <p class="waiting-text">等待房主开始游戏...</p>
      </div>

      <button class="leave-btn" @click="$emit('leave')">离开房间</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  roomCode: String,
  members: { type: Array, default: () => [] },
  maxPlayers: { type: Number, default: 2 },
  hostId: Number,
  isHost: Boolean
})
defineEmits(['start', 'leave'])

function isHostUser(m) {
  return m.user_id === props.hostId
}

const memberCount = computed(() => props.members.length)

const memberSlots = computed(() => {
  const slots = props.members.map(m => ({
    ...m,
    online: m.last_heartbeat && Date.now() - new Date(m.last_heartbeat).getTime() < 12000
  }))
  while (slots.length < props.maxPlayers) {
    slots.push(null)
  }
  return slots
})
</script>

<style scoped>
.room-lobby {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
}
.lobby-panel {
  text-align: center;
  padding: 48px 40px;
  background: rgba(255,255,255,0.08);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.15);
  max-width: 400px;
  width: 100%;
}
.lobby-panel h2 {
  color: #fff;
  font-size: 22px;
  margin-bottom: 20px;
}
.room-code-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
}
.code-label {
  color: rgba(255,255,255,0.4);
  font-size: 12px;
  margin-bottom: 4px;
}
.code-value {
  font-size: 40px;
  font-weight: bold;
  color: #a29bfe;
  letter-spacing: 8px;
  text-shadow: 0 0 20px rgba(108,92,231,0.4);
  user-select: all;
}
.player-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}
.player-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: rgba(255,255,255,0.04);
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.06);
}
.player-item.empty {
  opacity: 0.4;
  border-style: dashed;
}
.player-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #6c5ce7;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #fff;
  flex-shrink: 0;
}
.player-name {
  flex: 1;
  color: #eee;
  font-size: 15px;
  text-align: left;
}
.host-badge,
.member-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
}
.host-badge {
  background: rgba(253,203,110,0.2);
  color: #fdcb6e;
}
.member-badge {
  background: rgba(116,185,255,0.2);
  color: #74b9ff;
}
.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.online {
  background: #00b894;
  box-shadow: 0 0 8px rgba(0,184,148,0.6);
}
.status-dot.offline {
  background: #636e72;
}
.player-count {
  color: rgba(255,255,255,0.4);
  font-size: 13px;
  margin-bottom: 20px;
}
.host-actions {
  margin-bottom: 12px;
}
.start-btn {
  padding: 12px 48px;
  border-radius: 10px;
  border: none;
  background: #00b894;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  transition: 0.2s;
}
.start-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.start-btn:not(:disabled):hover {
  background: #00a381;
}
.waiting-text {
  color: rgba(255,255,255,0.4);
  font-size: 14px;
  margin-bottom: 12px;
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}
.leave-btn {
  padding: 8px 20px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.04);
  color: rgba(255,255,255,0.5);
  font-size: 13px;
  cursor: pointer;
}
</style>
