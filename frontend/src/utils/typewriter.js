import { ref } from 'vue'

export function useTypewriter(speed = 50) {
  const displayText = ref('')
  const isTyping = ref(false)
  let timer = null

  function type(text, callback) {
    stop()
    displayText.value = ''
    isTyping.value = true
    let index = 0

    function tick() {
      if (index < text.length) {
        displayText.value += text[index]
        index++
        timer = setTimeout(tick, speed)
      } else {
        isTyping.value = false
        if (callback) callback()
      }
    }

    tick()
  }

  function stop() {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
    isTyping.value = false
  }

  function skip(text) {
    stop()
    displayText.value = text
  }

  return { displayText, isTyping, type, stop, skip }
}
