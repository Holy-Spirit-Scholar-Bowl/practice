import { createModule, extractVuexModule, createProxy } from 'vuex-class-component'
import { modulesStore } from '../main'

import Mythology from '@/assets/Frequency Lists/02e9c3ee9be2e658386ec2fe831c53b27a0477a096fb25ea82d299570fbe23f0.json'
import Religion from '@/assets/Frequency Lists/db240efe97d942b5a407200c4b5a6ab64a629d95e9104b1d6278e8b255b351d5.json'
import Literature from '@/assets/Frequency Lists/b7ccae4a106917a8bd3ebaa7c8694154632aa9ebdd4f2abf42b74a38a69af0b6.json'
import Science from '@/assets/Frequency Lists/d05dc5ab0191d9353b8a3d6e08dfea4dc03077e90c8c68d1c261ea17246bdd6f.json'
import History from '@/assets/Frequency Lists/cc57c3ee8661fd4481f4c0fbf24f398c0a555ce955b6057653d56c598e315746.json'
import FineArts from '@/assets/Frequency Lists/35884c1331fc44be52f64aa292b7493146e7dc606fb7e142de4ab5df41b4c5ef.json'
import Trash from '@/assets/Frequency Lists/cc066b4b3647485e57a9c912963f54ee55eed4c79c7e6cef8eb5414a18df9a98.json'
import Philospohy from '@/assets/Frequency Lists/83fb27ee2106499505c497994804fa7c7a152f428e49e095d9f5a4e2025d98a9.json'
import Geography from '@/assets/Frequency Lists/b50c089ae1e5a97c5084912af65b577a6aee4c7049f04835cfd40d92dd5a757c.json'
import SocialScience from '@/assets/Frequency Lists/c0d0c71d5b0510caeab7ce3c0bbe7bf4c483d57f19e9863dc5450f74b88e99be.json'

const freqLists = { Mythology, Religion, Literature, Science, History, FineArts, Trash, Philospohy, Geography, SocialScience }

const VuexModule = createModule({
  namespaced: 'practice'
})
export class PracticeModule extends VuexModule {
  constructor () {
    super()

    this.frequencyLists = Object.fromEntries(Object.entries(freqLists).map((entry) => {
      const [key, value] = entry
      const val: { answer: string, questions: string[]}[] = Object.entries(value).map((ans) => {
        return { answer: ans[0], questions: ans[1] }
      })
      val.sort((a, b) => b.questions.length - a.questions.length)
      return [key, val]
    })) as { [k in keyof typeof freqLists]: { answer: string, questions: string[] }[] }
  }

  frequencyLists: { [k in keyof typeof freqLists]: { answer: string, questions: string[] }[] }

  frequencyListFilter: keyof typeof freqLists | '' = ''
  lowerBoundFilter = 0
  upperBoundFilter = 50
  excludeFilter: string[] = []
  exclude = false

  get validQuestions (): { answer: string, questions: string[]}[] {
    if (this.frequencyListFilter === '') {
      return []
    }
    return this.frequencyLists[this.frequencyListFilter]
      .slice(this.lowerBoundFilter, this.upperBoundFilter)
      .filter((e) => !this.excludeFilter.length || this.exclude !== !this.excludeFilter.includes(e.answer))
  }

  get validAnswers (): string[] {
    return this.validQuestions.map((question) => question.answer)
  }
}

// Register the module in the store
modulesStore.registerModule(['practice'], extractVuexModule(PracticeModule).practice)

// Create a proxy to the connected module
export default createProxy(modulesStore, PracticeModule)
