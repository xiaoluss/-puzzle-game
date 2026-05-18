export function validateTextAnswer(userAnswer, correctAnswer, acceptedAnswers = [], caseSensitive = false) {
  let answer = userAnswer.trim()
  let correct = correctAnswer.trim()

  if (!caseSensitive) {
    answer = answer.toLowerCase()
    correct = correct.toLowerCase()
  }

  if (answer === correct) return true

  for (const acc of acceptedAnswers) {
    let a = acc.trim()
    if (!caseSensitive) a = a.toLowerCase()
    if (answer === a) return true
  }

  return false
}

export function validateChoiceAnswer(userAnswer, correctAnswer) {
  return String(userAnswer) === String(correctAnswer)
}

export function validateImageAnswer(userAnswer, correctAnswer) {
  return String(userAnswer) === String(correctAnswer)
}
