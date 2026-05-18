import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as gameApi from '../api/game'
import * as progressApi from '../api/progress'

export const useGameStore = defineStore('game', () => {
  const playerName = ref('')
  const chapters = ref([])
  const currentChapter = ref(null)
  const scenes = ref([])
  const currentSceneIndex = ref(0)
  const completedScenes = ref([])
  const puzzleFails = ref({})
  const showAnswer = ref(false)
  const loading = ref(false)

  const currentScene = computed(() => {
    if (scenes.value.length === 0) return null
    return scenes.value[currentSceneIndex.value] || null
  })

  const isLastScene = computed(() => {
    return currentSceneIndex.value >= scenes.value.length - 1
  })

  async function loadChapters() {
    const res = await gameApi.getGameChapters()
    chapters.value = res.data
  }

  async function loadScenes(chapterId) {
    const res = await gameApi.getGameScenes(chapterId)
    scenes.value = res.data
    currentSceneIndex.value = 0
  }

  async function loadProgress() {
    try {
      const res = await progressApi.getProgress()
      const data = res.data
      completedScenes.value = data.completed_scenes || []
      puzzleFails.value = data.puzzle_fails || {}
      if (data.current_chapter_id) {
        currentChapter.value = data.current_chapter_id
      }
    } catch (e) {
      console.error('加载进度失败:', e)
    }
  }

  async function saveCurrentProgress() {
    try {
      await progressApi.saveProgress({
        current_chapter_id: currentChapter.value,
        current_scene_id: currentScene.value?.id,
        completed_scenes: completedScenes.value,
        puzzle_fails: puzzleFails.value
      })
    } catch (e) {
      console.error('保存进度失败:', e)
    }
  }

  function nextScene() {
    if (currentSceneIndex.value < scenes.value.length - 1) {
      currentSceneIndex.value++
    }
  }

  function goToScene(sceneId) {
    const idx = scenes.value.findIndex(s => s.id === sceneId)
    if (idx !== -1) currentSceneIndex.value = idx
  }

  function markSceneCompleted(sceneId) {
    if (!completedScenes.value.includes(sceneId)) {
      completedScenes.value.push(sceneId)
    }
  }

  function recordPuzzleFail(sceneId) {
    if (!puzzleFails.value[sceneId]) {
      puzzleFails.value[sceneId] = 0
    }
    puzzleFails.value[sceneId]++
    showAnswer.value = puzzleFails.value[sceneId] >= 3
  }

  function resetPuzzleFails(sceneId) {
    puzzleFails.value[sceneId] = 0
    showAnswer.value = false
  }

  return {
    playerName, chapters, currentChapter, scenes,
    currentSceneIndex, completedScenes, puzzleFails,
    showAnswer, loading, currentScene, isLastScene,
    loadChapters, loadScenes, loadProgress, saveCurrentProgress,
    nextScene, goToScene, markSceneCompleted,
    recordPuzzleFail, resetPuzzleFails
  }
})
