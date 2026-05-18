<template>
  <div class="hint-area">
    <button v-if="showHintBtn" class="hint-btn" @click="showCurrentHint">
      提示 ({{ currentHint + 1 }}/{{ hints.length }})
    </button>
    <button v-if="showAnswerBtn" class="answer-btn" @click="$emit('showAnswer')">
      查看答案
    </button>
    <div v-if="currentHintText" class="hint-text">
      💡 {{ currentHintText }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  hints: { type: Array, default: () => [] },
  showAnswerBtn: Boolean
})

defineEmits(['showAnswer'])

const currentHint = ref(-1)
const currentHintText = ref('')

const showHintBtn = computed(() => props.hints.length > 0)

function showCurrentHint() {
  if (currentHint.value < props.hints.length - 1) {
    currentHint.value++
    currentHintText.value = props.hints[currentHint.value]
  } else {
    currentHintText.value = '没有更多提示了'
  }
}
</script>

<style scoped>
.hint-area {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.hint-btn, .answer-btn {
  padding: 8px 20px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: 0.2s;
}
.hint-btn {
  background: rgba(253,203,110,0.2);
  color: #fdcb6e;
  border: 1px solid rgba(253,203,110,0.3);
}
.hint-btn:hover {
  background: rgba(253,203,110,0.3);
}
.answer-btn {
  background: rgba(214,48,49,0.2);
  color: #ff7675;
  border: 1px solid rgba(214,48,49,0.3);
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 0.8; }
  50% { opacity: 1; }
}
.hint-text {
  color: #fdcb6e;
  font-size: 14px;
  padding: 8px 16px;
  background: rgba(253,203,110,0.1);
  border-radius: 6px;
  max-width: 400px;
  text-align: center;
}
</style>
