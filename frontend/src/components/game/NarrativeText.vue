<template>
  <div class="narrative-box">
    <div class="narrative-content">
      <p class="narrative-text">{{ text }}</p>
      <span v-if="isTyping" class="cursor">|</span>
    </div>
    <button v-if="showNext" class="next-btn" @click="$emit('next')">继续 ▼</button>
  </div>
</template>

<script setup>
defineProps({
  text: String,
  isTyping: Boolean,
  showNext: Boolean
})
defineEmits(['next'])
</script>

<style scoped>
.narrative-box {
  background: rgba(0,0,0,0.5);
  border-radius: 12px;
  padding: 32px 24px;
  border: 1px solid rgba(255,255,255,0.08);
  max-width: 700px;
  width: 100%;
  text-align: center;
}
.narrative-content {
  min-height: 40px;
}
.narrative-text {
  color: #ddd;
  font-size: 18px;
  line-height: 2;
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
  margin-top: 20px;
  padding: 8px 24px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.05);
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  transition: 0.2s;
}
.next-btn:hover {
  background: rgba(255,255,255,0.12);
}
</style>
