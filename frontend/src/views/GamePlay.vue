<template>
  <div class="game-page">
    <template v-if="!playerName">
      <NameInput @confirm="onNameConfirm" />
    </template>

    <template v-else>
      <div class="game-header">
        <span class="player-name">玩家: {{ playerName }}</span>
        <div class="header-actions">
          <span v-if="roomCode" class="room-badge">房间: {{ roomCode }}</span>
          <button class="nav-btn logout" @click="logout">退出</button>
        </div>
      </div>
    </template>

    <template v-if="showModeSelect">
      <div class="mode-select">
        <div class="mode-panel">
          <h2>欢迎，{{ playerName }}！</h2>
          <p class="mode-desc">{{ playerCount }}人模式</p>
          <button class="mode-btn" @click="startSinglePlayer">单人进行</button>
          <button class="mode-btn create" @click="createRoomDirect">创建房间</button>
          <button class="mode-btn join" @click="showRoomJoin = true">加入房间</button>
        </div>
      </div>
    </template>

    <RoomJoin
      v-else-if="showRoomJoin"
      :playerName="playerName"
      @joined="handleRoomJoined"
      @back="showRoomJoin = false"
    />

    <template v-else-if="showChapterSelect && !loading">
      <div class="chapter-select-screen">
        <div class="chapter-select-panel">
          <h2>选择章节</h2>
          <div class="chapter-list">
            <button v-for="ch in chapters" :key="ch.id" @click="selectChapterForRoom(ch.id)">
              {{ ch.title }}
            </button>
          </div>
          <button class="back-btn" @click="showChapterSelect = false; showModeSelect = true">返回</button>
        </div>
      </div>
    </template>

      <RoomLobby
        v-else-if="roomCode && !gameStarted"
        :roomCode="roomCode"
        :members="roomMembers"
        :maxPlayers="roomMaxPlayers"
        :hostId="roomHostId"
        :isHost="isRoomHost"
        @start="handleStartGame"
        @leave="handleLeaveRoom"
      />

      <template v-else-if="showChapterSelect && roomCode && !gameStarted">
        <div class="chapter-select-screen">
          <div class="chapter-select-panel">
            <h2>选择章节</h2>
            <div class="chapter-list">
              <button v-for="ch in chapters" :key="ch.id" @click="startGameWithChapter(ch.id)">
                {{ ch.title }}
              </button>
            </div>
            <button class="back-btn" @click="showChapterSelect = false">返回</button>
          </div>
        </div>
      </template>

    <template v-else-if="gameStarted">
      <div class="game-content">
        <div v-if="loading" class="loading">加载中...</div>

        <template v-else-if="!currentScene">
          <div class="chapter-select" v-if="chapters.length > 0">
            <h2>选择章节</h2>
            <div class="chapter-list">
              <button v-for="ch in chapters" :key="ch.id" @click="selectChapter(ch.id)">
                {{ ch.title }}
              </button>
            </div>
          </div>
          <div v-else class="no-content">
            <p>暂无章节内容</p>
          </div>
        </template>

        <template v-else>
          <RoomWaiting
            v-if="isMultiplayer && waitingForOthers"
            :members="roomMembers"
          />
          <SceneManager
            v-else
            :scene="currentScene"
            :isMultiplayer="isMultiplayer"
            :roomCode="roomCode"
            @puzzle-solved="onPuzzleSolvedInRoom"
          />
        </template>
      </div>
    </template>

    <div class="overlay" v-if="showRejoinPrompt">
      <div class="rejoin-dialog">
        <h3>检测到进行中的房间</h3>
        <p>房间号: <strong>{{ pendingRoom?.code }}</strong></p>
        <p>状态: {{ pendingRoom?.status === 'playing' ? '游戏中' : '等待中' }}</p>
        <div class="rejoin-actions">
          <button class="rejoin-btn" @click="rejoinRoom">加入房间</button>
          <button class="rejoin-btn dismiss" @click="dismissRejoin">不加入</button>
        </div>
      </div>
    </div>

    <div v-if="createError" class="toast error">{{ createError }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import NameInput from '../components/game/NameInput.vue'
import RoomLobby from '../components/game/RoomLobby.vue'
import RoomJoin from '../components/game/RoomJoin.vue'
import RoomWaiting from '../components/game/RoomWaiting.vue'
import SceneManager from '../components/game/SceneManager.vue'
import { useGameStore } from '../stores/gameStore'
import * as roomsApi from '../api/rooms'
import * as chaptersApi from '../api/chapters'

const router = useRouter()
const store = useGameStore()

const playerName = ref(localStorage.getItem('playerName') || '')
const playerCount = ref(parseInt(localStorage.getItem('playerCount') || '1'))
const showModeSelect = ref(false)
const showRoomJoin = ref(false)
const showChapterSelect = ref(false)

const roomCode = ref('')
const roomMembers = ref([])
const roomMaxPlayers = ref(2)
const roomHostId = ref(null)
const isRoomHost = ref(false)
const gameStarted = ref(false)
const isMultiplayer = ref(false)
const waitingForOthers = ref(false)
const createError = ref('')

const showRejoinPrompt = ref(false)
const pendingRoom = ref(null)

const chapters = ref([])
const loading = ref(false)
let pollTimer = null

const currentScene = computed(() => store.currentScene)

onMounted(async () => {
  const user = localStorage.getItem('user')
  if (user) {
    try {
      const u = JSON.parse(user)
      localStorage.setItem('userId', u.id)
    } catch (e) { /* ignore */ }
  }
  await loadChapters()
  if (playerName.value) {
    if (playerCount.value === 1) {
      startSinglePlayer()
    } else {
      const rejoined = await tryRejoinActiveRoom()
      if (!rejoined) showModeSelect.value = true
    }
  }
})

onUnmounted(() => stopPolling())

async function loadChapters() {
  try {
    const res = await chaptersApi.getChapters()
    chapters.value = res.data
  } catch (e) { /* ignore */ }
}

async function onNameConfirm(data) {
  playerName.value = data.name
  playerCount.value = data.playerCount
  localStorage.setItem('playerName', data.name)
  localStorage.setItem('playerCount', String(data.playerCount))
  if (data.playerCount === 1) {
    startSinglePlayer()
  } else {
    const rejoined = await tryRejoinActiveRoom()
    if (!rejoined) showModeSelect.value = true
  }
}

async function tryRejoinActiveRoom() {
  try {
    const res = await roomsApi.getMyActiveRoom()
    if (!res.data?.room) return false
    pendingRoom.value = res.data.room
    showRejoinPrompt.value = true
    return true
  } catch (e) {
    return false
  }
}

function rejoinRoom() {
  if (!pendingRoom.value) return
  const room = pendingRoom.value
  showRejoinPrompt.value = false
  pendingRoom.value = null
  roomCode.value = room.code
  roomMembers.value = room.members || []
  roomMaxPlayers.value = room.max_players
  roomHostId.value = room.host_id
  isRoomHost.value = room.host_id === parseInt(localStorage.getItem('userId') || '0')
  store.playerName = playerName.value
  startPolling()
  if (room.status === 'playing') {
    enterRoomGame(room)
  }
}

function dismissRejoin() {
  showRejoinPrompt.value = false
  pendingRoom.value = null
  showModeSelect.value = true
}

async function startSinglePlayer() {
  showModeSelect.value = false
  isMultiplayer.value = false
  store.playerName = playerName.value
  gameStarted.value = true
  await store.loadProgress()
}

async function createRoomDirect() {
  showModeSelect.value = false
  loading.value = true
  try {
    const res = await roomsApi.createRoom(playerCount.value, null, playerName.value)
    setupRoom(res.data, true)
  } catch (e) {
    const roomCode = e.response?.data?.room_code
    if (roomCode) {
      try {
        const res = await roomsApi.getRoom(roomCode)
        setupRoom(res.data, true)
      } catch (e2) {
        createError.value = '获取房间信息失败'
        setTimeout(() => createError.value = '', 3000)
        showModeSelect.value = true
      }
    } else {
      createError.value = e.response?.data?.error || '创建房间失败'
      setTimeout(() => createError.value = '', 3000)
      showModeSelect.value = true
    }
  }
  loading.value = false
}

function handleRoomJoined(roomData) {
  setupRoom(roomData, false)
  showRoomJoin.value = false
}

function setupRoom(room, isHost) {
  roomCode.value = room.code
  roomMembers.value = room.members || []
  roomMaxPlayers.value = room.max_players
  roomHostId.value = room.host_id
  isRoomHost.value = isHost
  store.playerName = playerName.value
  startPolling()

  if (room.status === 'playing') {
    enterRoomGame(room)
  }
}

function enterRoomGame(room) {
  gameStarted.value = true
  isMultiplayer.value = true
  store.currentChapter = room.chapter_id
  loadRoomScenes(room)
  startPolling()
}

async function loadRoomScenes(room) {
  loading.value = true
  await store.loadScenes(room.chapter_id)
  const idx = store.scenes.findIndex(s => s.id === room.current_scene_id)
  if (idx !== -1) store.currentSceneIndex = idx
  loading.value = false
}

async function handleStartGame() {
  if (!roomCode.value) return
  showChapterSelect.value = true
  await loadChapters()
}

async function startGameWithChapter(chapterId) {
  showChapterSelect.value = false
  loading.value = true
  try {
    const res = await roomsApi.startGame(roomCode.value, chapterId)
    enterRoomGame(res.data)
  } catch (e) {
    createError.value = e.response?.data?.error || '开始失败'
    setTimeout(() => createError.value = '', 3000)
  }
  loading.value = false
}

async function handleLeaveRoom() {
  try { await roomsApi.leaveRoom(roomCode.value) } catch (e) { /* ignore */ }
  stopPolling()
  resetRoom()
}

function resetRoom() {
  roomCode.value = ''
  roomMembers.value = []
  gameStarted.value = false
  isMultiplayer.value = false
  waitingForOthers.value = false
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(pollRoomStatus, 2000)
}

function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

async function pollRoomStatus() {
  if (!roomCode.value) return
  try {
    roomsApi.heartbeat(roomCode.value).catch(() => {})
    const res = await roomsApi.getRoom(roomCode.value)
    const room = res.data
    roomMembers.value = room.members || []

    if (!gameStarted.value) return

    if (room.current_scene_id && room.current_scene_id !== store.currentScene?.id) {
      const idx = store.scenes.findIndex(s => s.id === room.current_scene_id)
      if (idx !== -1) {
        store.currentSceneIndex = idx
        waitingForOthers.value = false
      }
    }

    const isPuzzle = store.currentScene &&
      ['puzzle_text', 'puzzle_choice', 'puzzle_image'].includes(store.currentScene.scene_type)
    if (isPuzzle) {
      const myId = parseInt(localStorage.getItem('userId') || '0')
      const me = room.members.find(m => m.user_id === myId)
      if (me?.puzzle_completed) {
        const allDone = room.members.every(m => m.puzzle_completed === 1)
        waitingForOthers.value = !allDone
      }
    }
  } catch (e) { /* ignore */ }
}

async function onPuzzleSolvedInRoom() {
  if (!roomCode.value) return
  try {
    await roomsApi.puzzleDone(roomCode.value)
    waitingForOthers.value = true
    startPolling()
  } catch (e) { /* ignore */ }
}

async function selectChapter(chapterId) {
  loading.value = true
  store.currentChapter = chapterId
  await store.loadScenes(chapterId)
  loading.value = false
}

function logout() {
  stopPolling()
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('userId')
  localStorage.removeItem('playerName')
  localStorage.removeItem('playerCount')
  router.push('/login')
}

watch(currentScene, (ns) => {
  if (ns && !['puzzle_text', 'puzzle_choice', 'puzzle_image'].includes(ns.scene_type)) {
    waitingForOthers.value = false
  }
})
</script>

<style scoped>
.game-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  color: #fff;
}
.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: rgba(0,0,0,0.3);
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.player-name { color: rgba(255,255,255,0.7); font-size: 14px; }
.header-actions { display: flex; gap: 8px; align-items: center; }
.room-badge {
  font-size: 12px;
  background: rgba(108,92,231,0.2);
  color: #a29bfe;
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid rgba(108,92,231,0.3);
}
.nav-btn {
  padding: 6px 16px; border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.7);
  font-size: 13px; cursor: pointer;
}
.nav-btn.logout { color: #ff7675; border-color: rgba(214,48,49,0.3); }
.game-content {
  display: flex; justify-content: center; align-items: center;
  padding: 40px 20px; min-height: calc(100vh - 60px);
}
.loading, .no-content { color: rgba(255,255,255,0.5); }
.chapter-select { text-align: center; }
.chapter-select h2 { margin-bottom: 24px; font-size: 24px; }
.chapter-list { display: flex; flex-direction: column; gap: 12px; align-items: center; }
.chapter-list button {
  padding: 16px 48px; border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.06);
  color: #fff; font-size: 18px; cursor: pointer;
  min-width: 300px; transition: 0.2s;
}
.chapter-list button:hover { background: rgba(255,255,255,0.12); border-color: #6c5ce7; }

.mode-select {
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
}
.mode-panel {
  text-align: center; padding: 48px 40px;
  background: rgba(255,255,255,0.08);
  border-radius: 20px; backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.15);
  max-width: 360px; width: 100%;
}
.mode-panel h2 { color: #fff; font-size: 22px; margin-bottom: 6px; }
.mode-desc { color: rgba(255,255,255,0.4); font-size: 14px; margin-bottom: 24px; }
.mode-btn {
  display: block; width: 100%; padding: 14px;
  border-radius: 10px; border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.05);
  color: #fff; font-size: 16px; cursor: pointer; margin-bottom: 10px;
}
.mode-btn.create { border-color: rgba(0,184,148,0.3); color: #55efc4; }
.mode-btn.join { border-color: rgba(108,92,231,0.3); color: #a29bfe; }

.chapter-select-screen {
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh;
}
.chapter-select-panel {
  text-align: center; padding: 48px 40px;
  background: rgba(255,255,255,0.08);
  border-radius: 20px; backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.15);
  max-width: 400px; width: 100%;
}
.chapter-select-panel h2 { color: #fff; font-size: 22px; margin-bottom: 20px; }
.back-btn {
  margin-top: 16px; padding: 8px 24px;
  border-radius: 6px; border: 1px solid rgba(255,255,255,0.15);
  background: none; color: rgba(255,255,255,0.5); cursor: pointer;
}
.toast {
  position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
  padding: 10px 24px; border-radius: 8px; font-size: 14px; z-index: 999;
}
.toast.error { background: rgba(214,48,49,0.9); color: #fff; }

.overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.6);
  display: flex; align-items: center; justify-content: center;
}
.rejoin-dialog {
  background: #1e1e2e; padding: 36px 40px;
  border-radius: 16px; text-align: center;
  border: 1px solid rgba(255,255,255,0.1);
  max-width: 360px; width: 100%;
}
.rejoin-dialog h3 {
  color: #fff; font-size: 20px; margin-bottom: 16px;
}
.rejoin-dialog p {
  color: rgba(255,255,255,0.6); font-size: 14px; margin-bottom: 6px;
}
.rejoin-dialog p strong {
  color: #a29bfe; letter-spacing: 4px;
}
.rejoin-actions {
  display: flex; gap: 12px; justify-content: center; margin-top: 24px;
}
.rejoin-btn {
  padding: 10px 28px; border-radius: 8px; border: none;
  background: #6c5ce7; color: #fff; font-size: 15px; cursor: pointer;
}
.rejoin-btn.dismiss {
  background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.5);
  border: 1px solid rgba(255,255,255,0.1);
}
.rejoin-btn:hover { opacity: 0.85; }
</style>
