<template>
  <div class="character-page">
    <div class="header">
      <button class="back-btn" @click="$router.push('/admin')">← 返回</button>
      <h1>角色管理</h1>
    </div>

    <div class="character-form">
      <h2>{{ editingCharacter ? '编辑角色' : '添加角色' }}</h2>
      <div class="form-row">
        <input v-model="form.name" placeholder="角色名称" />
        <input v-model="form.description" placeholder="角色简介" />
        <input type="file" accept="image/*" @change="onFileChange" />
        <button @click="saveCharacter" :disabled="!form.name.trim()">
          {{ editingCharacter ? '保存修改' : '添加角色' }}
        </button>
      </div>
    </div>

    <div class="character-grid">
      <div v-for="c in characters" :key="c.id" class="character-card">
        <div class="char-avatar">
          <img v-if="c.avatar" :src="c.avatar" />
          <div v-else class="char-placeholder">{{ c.name[0] }}</div>
        </div>
        <div class="char-info">
          <span class="char-name">{{ c.name }}</span>
          <span class="char-desc">{{ c.description || '暂无简介' }}</span>
        </div>
        <div class="char-actions">
          <button @click="editCharacter(c)">编辑</button>
          <button class="danger" @click="deleteCharacter(c.id)">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as charactersApi from '../api/characters'

const characters = ref([])
const editingCharacter = ref(null)
const form = ref({ name: '', description: '' })
const selectedFile = ref(null)

onMounted(loadCharacters)

async function loadCharacters() {
  const res = await charactersApi.getCharacters()
  characters.value = res.data
}

function onFileChange(e) {
  selectedFile.value = e.target.files[0] || null
}

function editCharacter(c) {
  editingCharacter.value = c
  form.value.name = c.name
  form.value.description = c.description
  selectedFile.value = null
}

async function saveCharacter() {
  const fd = new FormData()
  fd.append('name', form.value.name.trim())
  fd.append('description', form.value.description)
  if (selectedFile.value) {
    fd.append('avatar', selectedFile.value)
  }

  if (editingCharacter.value) {
    await charactersApi.updateCharacter(editingCharacter.value.id, fd)
  } else {
    await charactersApi.createCharacter(fd)
  }

  form.value = { name: '', description: '' }
  editingCharacter.value = null
  selectedFile.value = null
  await loadCharacters()
}

async function deleteCharacter(id) {
  if (!confirm('确定删除？')) return
  await charactersApi.deleteCharacter(id)
  await loadCharacters()
}
</script>

<style scoped>
.character-page {
  min-height: 100vh;
  background: #1a1a2e;
  color: #eee;
  padding: 24px 32px;
}
.header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 28px;
}
.header h1 {
  font-size: 24px;
  color: #a29bfe;
}
.back-btn {
  padding: 6px 16px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.7);
  cursor: pointer;
}
.character-form {
  background: rgba(255,255,255,0.03);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 28px;
  border: 1px solid rgba(255,255,255,0.06);
}
.character-form h2 {
  font-size: 18px;
  margin-bottom: 16px;
  color: rgba(255,255,255,0.8);
}
.form-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}
.form-row input[type="text"] {
  padding: 10px 14px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  color: #fff;
  font-size: 14px;
  outline: none;
  flex: 1;
  min-width: 150px;
}
.form-row input[type="file"] {
  color: rgba(255,255,255,0.6);
  font-size: 13px;
}
.form-row button {
  padding: 10px 24px;
  border-radius: 6px;
  border: none;
  background: #6c5ce7;
  color: #fff;
  cursor: pointer;
  white-space: nowrap;
}
.form-row button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.character-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
}
.character-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: rgba(255,255,255,0.03);
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.06);
}
.char-avatar img {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  object-fit: cover;
}
.char-placeholder {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #6c5ce7;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: #fff;
}
.char-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.char-name {
  font-size: 16px;
  color: #fff;
}
.char-desc {
  font-size: 12px;
  color: rgba(255,255,255,0.4);
}
.char-actions {
  display: flex;
  gap: 6px;
}
.char-actions button {
  padding: 5px 12px;
  border-radius: 4px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.05);
  color: #bbb;
  font-size: 12px;
  cursor: pointer;
}
.char-actions button.danger {
  color: #ff7675;
  border-color: rgba(214,48,49,0.3);
}
</style>
