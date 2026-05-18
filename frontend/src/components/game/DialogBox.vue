<template>
  <div class="dialog-box">
    <div v-if="character" class="character-info">
      <img v-if="character.avatar" :src="character.avatar" class="avatar" />
      <div v-else class="avatar-placeholder">{{ character.name[0] }}</div>
      <span class="character-name">{{ character.name }}</span>
    </div>
    <div class="dialog-content">
      <span class="dialog-text">{{ text }}</span>
      <span v-if="isTyping" class="cursor">|</span>
      <button v-if="showNext" class="next-btn" @click="$emit('next')">▼</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  character: Object,
  text: String,
  isTyping: Boolean,
  showNext: Boolean
})

defineEmits(['next'])
</script>

<style scoped>
.dialog-box {
  background: rgba(0,0,0,0.7);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255,255,255,0.1);
  max-width: 700px;
  width: 100%;
}
.character-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255,255,255,0.2);
}
.avatar-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #6c5ce7;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
}
.character-name {
  color: #a29bfe;
  font-size: 18px;
  font-weight: bold;
}
.dialog-content {
  position: relative;
  min-height: 60px;
}
.dialog-text {
  color: #eee;
  font-size: 16px;
  line-height: 1.8;
  white-space: pre-wrap;
}
.cursor {
  color: #6c5ce7;
  animation: blink 0.8s infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
.next-btn {
  position: absolute;
  right: 0;
  bottom: -30px;
  background: none;
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  animation: bounce 1s infinite;
}
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(5px); }
}
</style>
