<template>
  <div class="scene-manager" @click="onClickAnywhere">
    <div v-if="!scene" class="no-scene">
      <p>没有更多剧情了</p>
    </div>

    <template v-else>
      <div v-if="scene.scene_type === 'dialog'" class="scene-dialog" @click.stop>
        <DialogBox
          :character="scene.character"
          :text="dialogText"
          :isTyping="isTypingDialog"
          :showNext="showDialogNext"
          @next="advanceDialog"
        />
        <BranchSelector
          v-if="showBranches"
          :branches="scene.branches"
          @select="onBranchSelect"
        />
      </div>

      <div v-else-if="scene.scene_type === 'narrative'" class="scene-narrative" @click.stop>
        <NarrativeText
          :text="narrativeText"
          :isTyping="isTypingNarrative"
          :showNext="showNarrativeNext"
          @next="onNarrativeDone"
        />
      </div>

      <div v-else-if="scene.scene_type === 'puzzle_text'" class="scene-puzzle" @click.stop>
        <PuzzleInput
          :question="scene.question"
          :imageUrl="scene.image_url"
          :sceneId="scene.id"
          @correct="onPuzzleCorrect"
          @wrong="onPuzzleWrong"
        />
      </div>

      <div v-else-if="scene.scene_type === 'puzzle_choice'" class="scene-puzzle" @click.stop>
        <ChoicePuzzle
          :question="scene.question"
          :options="scene.choices"
          :imageUrl="scene.image_url"
          :sceneId="scene.id"
          @correct="onPuzzleCorrect"
          @wrong="onPuzzleWrong"
        />
      </div>

      <div v-else-if="scene.scene_type === 'puzzle_image'" class="scene-puzzle" @click.stop>
        <ImagePuzzle
          :question="scene.question"
          :imageUrl="scene.image_url"
          :clickAreas="scene.image_areas"
          :sceneId="scene.id"
          @correct="onPuzzleCorrect"
          @wrong="onPuzzleWrong"
        />
      </div>

      <div v-if="isPuzzleScene && hintsVisible" @click.stop>
        <HintButton
          :hints="scene.hints || []"
          :showAnswerBtn="store.showAnswer"
          @showAnswer="onShowAnswer"
        />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import DialogBox from './DialogBox.vue'
import NarrativeText from './NarrativeText.vue'
import PuzzleInput from './PuzzleInput.vue'
import ChoicePuzzle from './ChoicePuzzle.vue'
import ImagePuzzle from './ImagePuzzle.vue'
import HintButton from './HintButton.vue'
import BranchSelector from './BranchSelector.vue'
import { useTypewriter } from '../../utils/typewriter'
import { useGameStore } from '../../stores/gameStore'
import { verifyAnswer } from '../../api/game'

const props = defineProps({
  scene: Object,
  isMultiplayer: { type: Boolean, default: false },
  roomCode: { type: String, default: '' }
})

const emit = defineEmits(['puzzle-solved'])

const store = useGameStore()
const tw = useTypewriter(45)

const dialogLineIndex = ref(0)
const showDialogNext = ref(false)
const dialogText = ref('')

const showNarrativeNext = ref(false)
const narrativeText = ref('')
const isTypingNarrative = ref(false)
const isTypingDialog = ref(false)

const hintsVisible = ref(false)
const showBranches = ref(false)

const isPuzzleScene = computed(() =>
  ['puzzle_text', 'puzzle_choice', 'puzzle_image'].includes(props.scene?.scene_type)
)

const isDialogOrNarrative = computed(() =>
  ['dialog', 'narrative'].includes(props.scene?.scene_type)
)

watch(() => props.scene, () => {
  dialogLineIndex.value = 0
  showDialogNext.value = false
  showNarrativeNext.value = false
  showBranches.value = false
  hintsVisible.value = false
  dialogText.value = ''
  narrativeText.value = ''
  isTypingDialog.value = false
  isTypingNarrative.value = false

  nextTick(() => {
    if (props.scene?.scene_type === 'dialog') {
      startDialog()
    } else if (props.scene?.scene_type === 'narrative') {
      startNarrative()
    }
  })
}, { immediate: true })

function onClickAnywhere() {
  if (!props.scene || !isDialogOrNarrative.value) return
  if (showBranches.value) return

  if (props.scene.scene_type === 'dialog') {
    advanceDialog()
  } else if (props.scene.scene_type === 'narrative') {
    onNarrativeDone()
  }
}

function startDialog() {
  dialogLineIndex.value = 0
  showDialogNext.value = false
  showBranches.value = false
  typeLine(0)
}

function typeLine(index) {
  const lines = props.scene.lines || []
  if (index >= lines.length) {
    showDialogEnd()
    return
  }

  isTypingDialog.value = true
  let text = lines[index].replace(/\{playerName\}/g, store.playerName)

  tw.type(text, () => {
    isTypingDialog.value = false
    showDialogNext.value = true
  })
}

function showDialogEnd() {
  const branches = props.scene.branches
  if (branches && branches.length > 0) {
    showBranches.value = true
    showDialogNext.value = false
  } else {
    showDialogNext.value = true
  }
}

watch(tw.displayText, (val) => {
  if (props.scene?.scene_type === 'dialog') {
    dialogText.value = val
  } else if (props.scene?.scene_type === 'narrative') {
    narrativeText.value = val
  }
})

function advanceDialog() {
  if (showBranches.value) return
  if (tw.isTyping.value) {
    const lines = props.scene.lines || []
    let fullText = lines[dialogLineIndex.value].replace(/\{playerName\}/g, store.playerName)
    tw.skip(fullText)
    dialogText.value = fullText
    isTypingDialog.value = false
    showDialogNext.value = true
    return
  }

  dialogLineIndex.value++
  const lines = props.scene.lines || []
  if (dialogLineIndex.value < lines.length) {
    showDialogNext.value = false
    typeLine(dialogLineIndex.value)
  } else {
    showDialogEnd()
  }
}

function startNarrative() {
  isTypingNarrative.value = true
  showNarrativeNext.value = false
  let text = (props.scene.text || '').replace(/\{playerName\}/g, store.playerName)

  tw.type(text, () => {
    isTypingNarrative.value = false
    showNarrativeNext.value = true
  })
}

function onNarrativeDone() {
  if (tw.isTyping.value) {
    let text = (props.scene.text || '').replace(/\{playerName\}/g, store.playerName)
    tw.skip(text)
    narrativeText.value = text
    isTypingNarrative.value = false
    showNarrativeNext.value = true
    return
  }
  store.markSceneCompleted(props.scene.id)
  store.saveCurrentProgress()
  store.nextScene()
}

function onBranchSelect(targetSceneId) {
  store.markSceneCompleted(props.scene.id)
  store.saveCurrentProgress()
  if (targetSceneId) {
    store.goToScene(targetSceneId)
  } else {
    store.nextScene()
  }
}

function onPuzzleCorrect(nextSceneId) {
  store.markSceneCompleted(props.scene.id)
  store.resetPuzzleFails(props.scene.id)
  store.saveCurrentProgress()

  if (props.isMultiplayer) {
    emit('puzzle-solved')
    return
  }

  if (nextSceneId) {
    store.goToScene(nextSceneId)
  } else {
    store.nextScene()
  }
}

function onPuzzleWrong() {
  store.recordPuzzleFail(props.scene.id)
  hintsVisible.value = true
  store.saveCurrentProgress()
}

async function onShowAnswer() {
  try {
    const res = await verifyAnswer(props.scene.id, props.scene.answer || '')
    if (res.data.correct) {
      onPuzzleCorrect(res.data.success_next_scene_id)
    }
  } catch (e) {
    console.error('答案自动提交失败:', e)
  }
}
</script>

<style scoped>
.scene-manager {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  min-height: 300px;
  cursor: default;
}
.no-scene {
  color: rgba(255,255,255,0.5);
  padding: 40px;
}
.scene-dialog, .scene-narrative, .scene-puzzle {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>
