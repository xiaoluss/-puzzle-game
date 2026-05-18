<template>
  <div class="puzzle-input">
    <p class="question">{{ question }}</p>
    <div v-if="imageUrl" class="puzzle-image">
      <img :src="imageUrl" />
    </div>
    <div class="answer-area">
      <input
        v-model="userAnswer"
        placeholder="输入你的答案..."
        @keyup.enter="submit"
        :disabled="locked"
      />
      <button @click="submit" :disabled="locked || !userAnswer.trim()">
        确认
      </button>
    </div>
    <div v-if="feedback" class="feedback" :class="{ correct: isCorrect, wrong: !isCorrect }">
      {{ feedback }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { validateTextAnswer } from '../../utils/validators'

const props = defineProps({
  question: String,
  imageUrl: { type: String, default: '' },
  sceneId: { type: [Number, String], required: true }
})

const emit = defineEmits(['correct', 'wrong'])
const userAnswer = ref('')
const feedback = ref('')
const isCorrect = ref(false)
const locked = ref(false)

async function submit() {
  if (!userAnswer.value.trim() || locked.value) return

  const { verifyAnswer } = await import('../../api/game')
  try {
    const res = await verifyAnswer(props.sceneId, userAnswer.value.trim())
    if (res.data.correct) {
      isCorrect.value = true
      feedback.value = '回答正确！'
      locked.value = true
      setTimeout(() => emit('correct', res.data.success_next_scene_id), 1000)
    } else {
      isCorrect.value = false
      feedback.value = '答案不对，再想想...'
      emit('wrong')
    }
  } catch (e) {
    feedback.value = '验证失败，请重试'
  }
}
</script>

<style scoped>
.puzzle-input {
  padding: 24px;
  background: rgba(0,0,0,0.6);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.1);
  max-width: 600px;
  width: 100%;
}
.question {
  color: #fff;
  font-size: 18px;
  margin-bottom: 16px;
  line-height: 1.6;
}
.puzzle-image {
  margin-bottom: 16px;
}
.puzzle-image img {
  max-width: 100%;
  border-radius: 8px;
}
.answer-area {
  display: flex;
  gap: 8px;
}
.answer-area input {
  flex: 1;
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.1);
  color: #fff;
  font-size: 15px;
  outline: none;
}
.answer-area input:disabled {
  opacity: 0.5;
}
.answer-area button {
  padding: 10px 24px;
  border-radius: 8px;
  border: none;
  background: #00b894;
  color: #fff;
  font-size: 15px;
  cursor: pointer;
}
.answer-area button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.feedback {
  margin-top: 12px;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
}
.feedback.correct {
  background: rgba(0,184,148,0.2);
  color: #55efc4;
}
.feedback.wrong {
  background: rgba(214,48,49,0.2);
  color: #ff7675;
}
</style>
