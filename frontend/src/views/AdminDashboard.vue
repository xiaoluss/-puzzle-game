<template>
  <div class="admin-page">
    <div class="admin-header">
      <h1>管理后台</h1>
      <div class="header-actions">
        <router-link to="/game" class="nav-link">返回游戏</router-link>
        <button class="nav-link logout" @click="logout">退出</button>
      </div>
    </div>

    <div class="admin-nav">
      <button :class="{ active: tab === 'chapters' }" @click="tab = 'chapters'">章节管理</button>
      <button :class="{ active: tab === 'characters' }" @click="tab = 'characters'">角色管理</button>
      <button :class="{ active: tab === 'settings' }" @click="tab = 'settings'">设置</button>
    </div>

    <div class="admin-content">
      <div v-if="tab === 'chapters'" class="chapter-manage">
        <div class="toolbar">
          <input v-model="newChapterTitle" placeholder="新章节标题" @keyup.enter="addChapter" />
          <button @click="addChapter">添加章节</button>
        </div>
        <div class="list">
          <div v-for="ch in chapters" :key="ch.id" class="list-item">
            <template v-if="editingChapterId === ch.id">
              <input v-model="editingChapterTitle" class="inline-input" @keyup.enter="saveChapterTitle(ch.id)" />
              <button @click="saveChapterTitle(ch.id)">保存</button>
              <button @click="editingChapterId = null">取消</button>
            </template>
            <template v-else>
              <span class="item-title">{{ ch.title }}</span>
              <span class="item-meta">{{ ch.scene_count }} 个场景</span>
              <div class="item-actions">
                <button @click="startEditTitle(ch)">重命名</button>
                <button @click="editChapter(ch.id)">编辑</button>
                <button @click="duplicateChapter(ch.id)">复制</button>
                <button class="danger" @click="deleteChapter(ch.id)">删除</button>
              </div>
            </template>
          </div>
        </div>
      </div>

      <div v-if="tab === 'characters'" class="character-manage">
        <router-link to="/admin/characters" class="goto-btn">管理角色 →</router-link>
      </div>

      <div v-if="tab === 'settings'" class="settings-panel">
        <h2>修改管理员密码</h2>
        <div class="form-group">
          <label>当前密码</label>
          <input v-model="oldPassword" type="password" placeholder="输入当前密码" />
        </div>
        <div class="form-group">
          <label>新密码</label>
          <input v-model="newPassword" type="password" placeholder="输入新密码（至少4位）" />
        </div>
        <div class="form-group">
          <label>确认新密码</label>
          <input v-model="confirmPassword" type="password" placeholder="再次输入新密码" />
        </div>
        <p v-if="pwError" class="error">{{ pwError }}</p>
        <p v-if="pwSuccess" class="success">{{ pwSuccess }}</p>
        <button class="save-settings-btn" :disabled="!oldPassword || !newPassword" @click="savePassword">
          保存密码
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as chaptersApi from '../api/chapters'
import { changePassword } from '../api/admin'

const router = useRouter()
const tab = ref('chapters')
const chapters = ref([])
const newChapterTitle = ref('')
const editingChapterId = ref(null)
const editingChapterTitle = ref('')
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const pwError = ref('')
const pwSuccess = ref('')

onMounted(loadChapters)

async function loadChapters() {
  const res = await chaptersApi.getChapters()
  chapters.value = res.data
}

async function addChapter() {
  if (!newChapterTitle.value.trim()) return
  try {
    await chaptersApi.createChapter(newChapterTitle.value.trim())
    newChapterTitle.value = ''
    await loadChapters()
  } catch (e) {
    alert(e.response?.data?.error || '添加失败')
  }
}

function startEditTitle(ch) {
  editingChapterId.value = ch.id
  editingChapterTitle.value = ch.title
}

async function saveChapterTitle(id) {
  if (!editingChapterTitle.value.trim()) return
  try {
    await chaptersApi.updateChapter(id, { title: editingChapterTitle.value.trim() })
    editingChapterId.value = null
    await loadChapters()
  } catch (e) {
    alert(e.response?.data?.error || '保存失败')
  }
}

async function duplicateChapter(id) {
  await chaptersApi.duplicateChapter(id)
  await loadChapters()
}

async function deleteChapter(id) {
  if (!confirm('确定删除这个章节吗？')) return
  await chaptersApi.deleteChapter(id)
  await loadChapters()
}

function editChapter(id) {
  router.push(`/admin/chapters/${id}`)
}

async function savePassword() {
  pwError.value = ''
  pwSuccess.value = ''
  if (newPassword.value !== confirmPassword.value) {
    pwError.value = '两次输入的密码不一致'
    return
  }
  try {
    const res = await changePassword(oldPassword.value, newPassword.value)
    pwSuccess.value = res.data.message
    oldPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (e) {
    pwError.value = e.response?.data?.error || '修改失败'
  }
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('admin_token')
  router.push('/login')
}
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #1a1a2e;
  color: #eee;
}
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 32px;
  background: #16213e;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.admin-header h1 {
  font-size: 24px;
  color: #a29bfe;
}
.header-actions {
  display: flex;
  gap: 12px;
}
.nav-link {
  padding: 6px 16px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.7);
  font-size: 13px;
  cursor: pointer;
  text-decoration: none;
  transition: 0.2s;
}
.nav-link:hover {
  background: rgba(255,255,255,0.12);
}
.nav-link.logout {
  color: #ff7675;
}
.admin-nav {
  display: flex;
  gap: 0;
  padding: 0 32px;
  background: #16213e;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.admin-nav button {
  padding: 12px 24px;
  border: none;
  background: none;
  color: rgba(255,255,255,0.6);
  font-size: 15px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: 0.2s;
}
.admin-nav button.active {
  color: #a29bfe;
  border-bottom-color: #a29bfe;
}
.admin-content {
  padding: 24px 32px;
}
.toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}
.toolbar input {
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.06);
  color: #fff;
  font-size: 14px;
  width: 280px;
  outline: none;
}
.toolbar button {
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  background: #6c5ce7;
  color: #fff;
  cursor: pointer;
}
.list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: rgba(255,255,255,0.03);
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.06);
}
.inline-input {
  padding: 6px 10px;
  border-radius: 5px;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.08);
  color: #fff;
  font-size: 15px;
  flex: 1;
  outline: none;
}
.item-title {
  flex: 1;
  font-size: 16px;
}
.item-meta {
  color: rgba(255,255,255,0.4);
  font-size: 13px;
}
.item-actions {
  display: flex;
  gap: 6px;
}
.item-actions button {
  padding: 5px 14px;
  border-radius: 5px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  color: #ccc;
  font-size: 12px;
  cursor: pointer;
}
.item-actions button.danger {
  color: #ff7675;
  border-color: rgba(214,48,49,0.3);
}
.goto-btn {
  display: inline-block;
  padding: 12px 24px;
  border-radius: 8px;
  background: #6c5ce7;
  color: #fff;
  text-decoration: none;
}
.settings-panel {
  max-width: 400px;
}
.settings-panel h2 {
  font-size: 20px;
  color: #a29bfe;
  margin-bottom: 20px;
}
.form-group {
  margin-bottom: 14px;
}
.form-group label {
  display: block;
  color: rgba(255,255,255,0.5);
  font-size: 13px;
  margin-bottom: 4px;
}
.form-group input {
  width: 100%;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  color: #fff;
  font-size: 14px;
  outline: none;
}
.error {
  color: #ff7675;
  font-size: 13px;
  margin-bottom: 8px;
}
.success {
  color: #00b894;
  font-size: 13px;
  margin-bottom: 8px;
}
.save-settings-btn {
  padding: 10px 28px;
  border-radius: 8px;
  border: none;
  background: #00b894;
  color: #fff;
  font-size: 15px;
  cursor: pointer;
}
.save-settings-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
