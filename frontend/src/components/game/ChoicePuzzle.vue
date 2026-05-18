<template>
  <div class="choice-puzzle">
    <p class="question">{{ question }}</p>
    <div v-if="imageUrl" class="puzzle-image">
      <img :src="imageUrl" />
    </div>
    <div class="options">
      <button
        v-for="(opt, i) in options"
        :key="i"
        :class="['option', { selected: selected === i, correct: locked && i === correctIdx, wrong: locked && selected === i && i !== correctIdx }]"
        :disabled="locked"
        @click="select(i)"
      >
        {{ opt }}
      </button>
    </div>
    <div v-if="feedback" class="feedback" :class="{ correct: isCorrect, wrong: !isCorrect }">
      {{ feedback }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  question: String,
  options: { type: Array, default: () => [] },
  imageUrl: { type: String, default: '' },
  sceneId: { type: [Number, String], required: true }
})

const emit = defineEmits(['correct', 'wrong'])
const selected = ref(null)
const correctIdx = ref(-1)
const feedback = ref('')
const isCorrect = ref(false)
const locked = ref(false)

async function select(index) {
  if (locked.value) return
  selected.value = index
  locked.value = true

  const { verifyAnswer } = await import('../../api/game')
  try {
    const res = await verifyAnswer(props.sceneId, index)
    if (res.data.correct) {
      isCorrect.value = true
      correctIdx.value = index
      feedback.value = '回答正确！'
      setTimeout(() => emit('correct', res.data.success_next_scene_id), 1000)
    } else {
      isCorrect.value = false
      correctIdx.value = -1
      feedback.value = '答案不对，再想想...'
      emit('wrong')
      setTimeout(() => {
        locked.value = false
        selected.value = null
        feedback.value = ''
      }, 800)
    }
  } catch (e) {
    feedback.value = '验证失败'
    locked.value = false
  }
}
</script>

<style scoped>
.choice-puzzle {
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
}
.puzzle-image {
  margin-bottom: 16px;
}
.puzzle-image img {
  max-width: 100%;
  border-radius: 8px;
}
.options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.option {
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.05);
  color: #eee;
  font-size: 15px;
  cursor: pointer;
  text-align: left;
  transition: 0.2s;
}
.option:hover:not(:disabled) {
  background: rgba(255,255,255,0.12);
}
.option.selected {
  border-color: #6c5ce7;
}
.option.correct {
  background: rgba(0,184,148,0.3);
  border-color: #00b894;
}
.option.wrong {
  background: rgba(214,48,49,0.3);
  border-color: #d63031;
}
.option:disabled {
  cursor: default;
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
