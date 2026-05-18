<template>
  <div class="image-puzzle">
    <p class="question">{{ question }}</p>
    <div class="image-container" ref="container" @click="handleClick">
      <img :src="imageUrl" />
      <div
        v-for="(area, i) in clickAreas"
        :key="i"
        class="click-marker"
        :style="{ left: area.x + '%', top: area.y + '%' }"
      >
        {{ i + 1 }}
      </div>
    </div>
    <button v-if="selectedArea !== null" class="confirm-btn" @click="submit">
      确认选择区域 {{ selectedArea + 1 }}
    </button>
    <div v-if="feedback" class="feedback" :class="{ correct: isCorrect, wrong: !isCorrect }">
      {{ feedback }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  question: String,
  imageUrl: String,
  clickAreas: { type: Array, default: () => [] },
  sceneId: { type: [Number, String], required: true }
})

const emit = defineEmits(['correct', 'wrong'])
const container = ref(null)
const selectedArea = ref(null)
const feedback = ref('')
const isCorrect = ref(false)
const locked = ref(false)

function handleClick(e) {
  if (locked.value) return
  const rect = container.value.getBoundingClientRect()
  const x = ((e.clientX - rect.left) / rect.width) * 100
  const y = ((e.clientY - rect.top) / rect.height) * 100

  let minDist = 15
  let nearest = null
  props.clickAreas.forEach((area, i) => {
    const dist = Math.sqrt((x - area.x) ** 2 + (y - area.y) ** 2)
    if (dist < minDist) {
      minDist = dist
      nearest = i
    }
  })

  if (nearest !== null) {
    selectedArea.value = nearest
  }
}

async function submit() {
  if (locked.value || selectedArea.value === null) return
  locked.value = true

  const { verifyAnswer } = await import('../../api/game')
  try {
    const res = await verifyAnswer(props.sceneId, selectedArea.value)
    if (res.data.correct) {
      isCorrect.value = true
      feedback.value = '回答正确！'
      setTimeout(() => emit('correct', res.data.success_next_scene_id), 1000)
    } else {
      isCorrect.value = false
      feedback.value = '不对，再观察一下...'
      emit('wrong')
      setTimeout(() => {
        locked.value = false
        selectedArea.value = null
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
.image-puzzle {
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
.image-container {
  position: relative;
  cursor: crosshair;
  margin-bottom: 12px;
}
.image-container img {
  max-width: 100%;
  border-radius: 8px;
  display: block;
}
.click-marker {
  position: absolute;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(108,92,231,0.7);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transform: translate(-50%, -50%);
  pointer-events: none;
}
.confirm-btn {
  padding: 10px 24px;
  border-radius: 8px;
  border: none;
  background: #fdcb6e;
  color: #2d3436;
  font-size: 15px;
  cursor: pointer;
  width: 100%;
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
