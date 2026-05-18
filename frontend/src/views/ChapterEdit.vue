<template>
  <div class="chapter-edit">
    <div class="edit-header">
      <button class="back-btn" @click="$router.push('/admin')">← 返回</button>
      <h1>{{ chapter?.title || '加载中...' }}</h1>
    </div>

    <div class="scene-toolbar">
      <select v-model="newSceneType" class="scene-type-select">
        <option value="dialog">对话场景</option>
        <option value="narrative">叙述场景</option>
        <option value="puzzle_text">解谜 - 填空</option>
        <option value="puzzle_choice">解谜 - 选择</option>
        <option value="puzzle_image">解谜 - 图片</option>
      </select>
      <button @click="addScene">添加场景</button>
    </div>

    <div class="scene-list">
      <div v-for="(scene, i) in scenes" :key="scene.id" class="scene-card">
        <div class="scene-header">
          <span class="scene-order">#{{ i + 1 }}</span>
          <span class="scene-type">{{ typeLabel(scene.scene_type) }}</span>
          <div class="scene-actions">
            <button @click="editScene(scene)">编辑</button>
            <button @click="duplicateScene(scene.id)">复制</button>
            <button class="danger" @click="deleteScene(scene.id)">删除</button>
          </div>
        </div>

        <div v-if="editingSceneId === scene.id" class="scene-editor">
          <template v-if="scene.scene_type === 'dialog'">
            <div class="form-group">
              <label>角色</label>
              <select v-model="editForm.character_id">
                <option :value="null">无</option>
                <option v-for="c in characters" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>台词 (一行一句)</label>
              <textarea v-model="editLinesText" rows="6"></textarea>
            </div>
            <div class="form-group">
              <label>分支选项 (对话结束后显示，每行格式: 选项文字 -> 场景ID)</label>
              <textarea v-model="editBranchesText" rows="3" placeholder="接受任务 -> 5&#10;拒绝任务 -> 6"></textarea>
              <small style="color:rgba(255,255,255,0.4)">留空则对话结束后自动进入下一场景</small>
            </div>
          </template>

          <template v-if="scene.scene_type === 'narrative'">
            <div class="form-group">
              <label>叙述文本</label>
              <textarea v-model="editForm.text" rows="6"></textarea>
            </div>
          </template>

          <template v-if="scene.scene_type.startsWith('puzzle_')">
            <div class="form-group">
              <label>问题</label>
              <input v-model="editForm.question" />
            </div>
            <div class="form-group">
              <label>正确答案</label>
              <input v-model="editForm.answer" />
            </div>
            <div class="form-group">
              <label>可接受的其他答案 (逗号分隔)</label>
              <input v-model="editAcceptedText" placeholder="答案1, 答案2" />
            </div>
            <div class="form-group" v-if="scene.scene_type === 'puzzle_choice'">
              <label>选项 (每行一个)</label>
              <textarea v-model="editChoicesText" rows="4"></textarea>
            </div>
            <div class="form-group" v-if="scene.scene_type === 'puzzle_image'">
              <label>图片URL</label>
              <input v-model="editForm.image_url" />
              <label style="margin-top:8px">点击区域 (JSON)</label>
              <textarea v-model="editImageAreasText" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label>提示 (每行一个)</label>
              <textarea v-model="editHintsText" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label>失败次数限制</label>
              <input v-model.number="editForm.fail_limit" type="number" min="1" />
            </div>
            <div class="form-group">
              <label>答对后跳转到场景 (留空=下一个)</label>
              <select v-model="editForm.success_next_scene_id">
                <option :value="null">下一个场景</option>
                <option v-for="s in scenes" :key="s.id" :value="s.id">
                  #{{ s.sort_order }} {{ typeLabel(s.scene_type) }}
                </option>
              </select>
            </div>
          </template>

          <div class="editor-actions">
            <button class="save-btn" @click="saveScene(scene.id)">保存</button>
            <button class="cancel-btn" @click="editingSceneId = null">取消</button>
          </div>
        </div>

        <div v-else class="scene-preview">
          <p v-if="scene.scene_type === 'dialog' && scene.character" class="preview-line">
            [{{ scene.character.name }}] {{ previewLines(scene.lines) }}
          </p>
          <p v-else-if="scene.scene_type === 'dialog' && !scene.character" class="preview-line">
            {{ previewLines(scene.lines) }}
          </p>
          <p v-else-if="scene.scene_type === 'narrative'" class="preview-line">
            {{ previewText(scene.text) }}
          </p>
          <p v-else-if="scene.scene_type.startsWith('puzzle_')" class="preview-line">
            ❓ {{ scene.question }}
          </p>
          <div v-if="scene.branches && scene.branches.length > 0" class="branch-indicator">
            ↳ {{ scene.branches.length }} 个分支
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import * as chaptersApi from '../api/chapters'
import * as scenesApi from '../api/scenes'
import * as charactersApi from '../api/characters'

const route = useRoute()
const chapterId = computed(() => parseInt(route.params.id))
const chapter = ref(null)
const scenes = ref([])
const characters = ref([])
const editingSceneId = ref(null)
const newSceneType = ref('dialog')

const editForm = ref({
  character_id: null,
  text: '',
  question: '',
  answer: '',
  accepted_answers: [],
  choices: [],
  image_areas: [],
  image_url: '',
  hints: [],
  fail_limit: 3,
  success_next_scene_id: null
})

const editLinesText = ref('')
const editAcceptedText = ref('')
const editChoicesText = ref('')
const editHintsText = ref('')
const editImageAreasText = ref('')
const editBranchesText = ref('')

onMounted(async () => {
  await loadChapter()
  await loadCharacters()
})

async function loadChapter() {
  const res = await chaptersApi.getChapter(chapterId.value)
  chapter.value = { id: res.data.id, title: res.data.title }
  scenes.value = res.data.scenes || []
}

async function loadCharacters() {
  const res = await charactersApi.getCharacters()
  characters.value = res.data
}

function typeLabel(type) {
  const map = {
    dialog: '💬 对话',
    narrative: '📖 叙述',
    puzzle_text: '❓ 填空',
    puzzle_choice: '❓ 选择',
    puzzle_image: '❓ 图片'
  }
  return map[type] || type
}

function previewLines(lines) {
  if (!lines || lines.length === 0) return '...'
  return lines[0].substring(0, 40) + (lines[0].length > 40 ? '...' : '')
}

function previewText(text) {
  if (!text) return '...'
  return text.substring(0, 50) + (text.length > 50 ? '...' : '')
}

async function addScene() {
  await scenesApi.createScene({ chapter_id: chapterId.value, scene_type: newSceneType.value })
  await loadChapter()
}

async function deleteScene(id) {
  if (!confirm('确定删除？')) return
  await scenesApi.deleteScene(id)
  await loadChapter()
}

async function duplicateScene(id) {
  await scenesApi.duplicateScene(id)
  await loadChapter()
}

function editScene(scene) {
  editingSceneId.value = scene.id
  editForm.value = {
    character_id: scene.character_id,
    text: scene.text,
    question: scene.question,
    answer: scene.answer,
    accepted_answers: scene.accepted_answers || [],
    choices: scene.choices || [],
    image_areas: scene.image_areas || [],
    image_url: scene.image_url,
    hints: scene.hints || [],
    fail_limit: scene.fail_limit || 3,
    success_next_scene_id: scene.success_next_scene_id
  }
  editLinesText.value = (scene.lines || []).join('\n')
  editAcceptedText.value = (scene.accepted_answers || []).join(', ')
  editChoicesText.value = (scene.choices || []).join('\n')
  editHintsText.value = (scene.hints || []).join('\n')
  editImageAreasText.value = JSON.stringify(scene.image_areas || [], null, 2)
  editBranchesText.value = (scene.branches || []).map(b => `${b.text} -> ${b.target_scene_id}`).join('\n')
}

async function saveScene(sceneId) {
  const branches = editBranchesText.value.split('\n')
    .filter(l => l.trim())
    .map(l => {
      const parts = l.split('->').map(s => s.trim())
      return { text: parts[0], target_scene_id: parts[1] ? parseInt(parts[1]) : null }
    })
    .filter(b => b.text && b.target_scene_id)

  const data = {
    ...editForm.value,
    lines: editLinesText.value.split('\n').filter(l => l.trim()),
    accepted_answers: editAcceptedText.value.split(',').map(a => a.trim()).filter(a => a),
    choices: editChoicesText.value.split('\n').filter(c => c.trim()),
    hints: editHintsText.value.split('\n').filter(h => h.trim()),
    branches
  }

  if (data.image_areas) {
    try {
      data.image_areas = JSON.parse(editImageAreasText.value)
    } catch (e) {
      data.image_areas = []
    }
  }

  await scenesApi.updateScene(sceneId, data)
  editingSceneId.value = null
  await loadChapter()
}
</script>

<style scoped>
.chapter-edit {
  min-height: 100vh;
  background: #1a1a2e;
  color: #eee;
}
.edit-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px 32px;
  background: #16213e;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.edit-header h1 {
  font-size: 22px;
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
.scene-toolbar {
  display: flex;
  gap: 8px;
  padding: 16px 32px;
  align-items: center;
}
.scene-type-select {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.06);
  color: #fff;
  font-size: 14px;
}
.scene-toolbar button {
  padding: 8px 20px;
  border-radius: 6px;
  border: none;
  background: #6c5ce7;
  color: #fff;
  cursor: pointer;
}
.scene-list {
  padding: 0 32px 40px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.scene-card {
  background: rgba(255,255,255,0.03);
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.08);
  overflow: hidden;
}
.scene-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: rgba(255,255,255,0.03);
}
.scene-order {
  color: #6c5ce7;
  font-weight: bold;
  font-size: 14px;
}
.scene-type {
  flex: 1;
  font-size: 14px;
  color: rgba(255,255,255,0.6);
}
.scene-actions {
  display: flex;
  gap: 6px;
}
.scene-actions button {
  padding: 4px 12px;
  border-radius: 4px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.05);
  color: #bbb;
  font-size: 12px;
  cursor: pointer;
}
.scene-actions button.danger {
  color: #ff7675;
  border-color: rgba(214,48,49,0.3);
}
.scene-preview {
  padding: 10px 20px 14px;
}
.preview-line {
  color: rgba(255,255,255,0.5);
  font-size: 13px;
}
.scene-editor {
  padding: 16px 20px;
  border-top: 1px solid rgba(255,255,255,0.06);
  background: rgba(255,255,255,0.02);
}
.form-group {
  margin-bottom: 12px;
}
.form-group label {
  display: block;
  color: rgba(255,255,255,0.6);
  font-size: 13px;
  margin-bottom: 4px;
}
.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  color: #fff;
  font-size: 14px;
  outline: none;
  font-family: inherit;
}
.form-group textarea {
  resize: vertical;
}
.editor-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}
.save-btn {
  padding: 8px 24px;
  border-radius: 6px;
  border: none;
  background: #00b894;
  color: #fff;
  cursor: pointer;
}
.cancel-btn {
  padding: 8px 24px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.15);
  background: none;
  color: rgba(255,255,255,0.6);
  cursor: pointer;
}
.branch-indicator {
  padding: 4px 20px 8px;
  font-size: 12px;
  color: #fdcb6e;
}
</style>
