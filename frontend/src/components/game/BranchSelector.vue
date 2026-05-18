<template>
  <div class="branch-selector">
    <p class="branch-prompt">{{ prompt }}</p>
    <div class="branch-options">
      <button
        v-for="(branch, i) in branches"
        :key="i"
        class="branch-btn"
        @click="$emit('select', branch.target_scene_id)"
      >
        {{ branch.text }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  prompt: { type: String, default: '选择你的行动：' },
  branches: { type: Array, default: () => [] }
})
defineEmits(['select'])
</script>

<style scoped>
.branch-selector {
  margin-top: 24px;
  text-align: center;
  width: 100%;
  max-width: 500px;
}
.branch-prompt {
  color: rgba(255,255,255,0.6);
  font-size: 14px;
  margin-bottom: 12px;
}
.branch-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.branch-btn {
  padding: 14px 24px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.06);
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  transition: 0.25s;
  text-align: center;
}
.branch-btn:hover {
  background: rgba(108,92,231,0.25);
  border-color: #6c5ce7;
  transform: translateY(-1px);
}
</style>
