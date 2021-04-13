<template>
<div>
  <p style="min-height: 100px">{{ questionRead.join(' ') }}</p>
  <button @click="guess">Answer</button>
  <button @click="next">Next</button>
  <br>
  <br>
  Answers:<br>
  {{ store.validAnswers.join(", ") }}
  <br>
  Frequency list:<br>
  <select v-model="store.frequencyListFilter">
    <option value='FineArts'>Fine Arts</option>
    <option>Science</option>
    <option>History</option>
    <option value='SocialScience'>Social Science</option>
    <option>Geography</option>
    <option>Mythology</option>
    <option>Religon</option>
    <option>Philosophy</option>
    <option>Trash</option>
    <option>Literature</option>
  </select>
  <br>
  Range of items on the list:<br>
  <input type=number v-model="store.lowerBoundFilter">
  -
  <input type=number v-model="store.upperBoundFilter">
  <br>
  {{ store.exclude ? 'Exclude' : 'Include'}} answers:<br>
  <textarea @input="updateExclude" :value="store.excludeFilter" />
  <br>
  {{ !store.exclude ? 'Exclude' : 'Include only '}} these answers <input type="checkbox" v-model="store.exclude">
</div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component'
import store from '@/store/index'

@Options({
})
export default class HelloWorld extends Vue {
  get store (): typeof store {
    return store
  }

  updateExclude (e: InputEvent): void {
    store.excludeFilter = (e.target as HTMLInputElement).value.split(/, ?/)
  }

  questionLeft: string[] = []

  questionRead: string[] = []

  questionAndAnswer = store.validQuestions[Math.floor(store.validQuestions.length * Math.random())]

  readingQuestion = false

  readQuestion (): void {
    if (this.readingQuestion) this.questionRead.push(this.questionLeft.pop() ?? ' ')

    setTimeout(this.readQuestion, 200)
  }

  next (): void {
    this.readingQuestion = true
    this.questionRead = []
    this.questionAndAnswer = store.validQuestions[Math.floor(store.validQuestions.length * Math.random())]
    this.questionLeft = this.questionAndAnswer.questions[Math.floor(this.questionAndAnswer.questions.length * Math.random())].split(' ').reverse()
  }

  distance (a: string, b: string): number {
    if (a.length === 0) return b.length
    if (b.length === 0) return a.length

    var matrix = []

    // increment along the first column of each row
    var i
    for (i = 0; i <= b.length; i++) {
      matrix[i] = [i]
    }

    // increment each column in the first row
    var j
    for (j = 0; j <= a.length; j++) {
      matrix[0][j] = j
    }

    // Fill in the rest of the matrix
    for (i = 1; i <= b.length; i++) {
      for (j = 1; j <= a.length; j++) {
        if (b.charAt(i - 1) === a.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1]
        } else {
          matrix[i][j] = Math.min(matrix[i - 1][j - 1] + 1, // substitution
            Math.min(matrix[i][j - 1] + 1, // insertion
              matrix[i - 1][j] + 1)) // deletion
        }
      }
    }

    return matrix[b.length][a.length]
  }

  guess (): void {
    const answer = prompt('What is your answer?') ?? ''
    if (this.distance(answer, this.questionAndAnswer.answer) < 5) {
      alert('Correct!')
      this.questionRead = []
      this.questionLeft = []
      this.readingQuestion = false
    } else {
      alert('Incorrect')
      this.readingQuestion = true
    }
  }

  created (): void {
    this.readQuestion()
  }
}
</script>
