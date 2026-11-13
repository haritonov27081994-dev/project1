import { getAction } from "./utils.js"
import { formatDatesInHTML } from "./format-dates.js"

class BatchLoader {
  constructor(containerId) {
    this.container = document.getElementById(containerId)
    if (!this.container) return

    this.offset = Number(this.container.dataset.initialOffset)
    this.hasMore = this.container.dataset.hasMore === 'True'
    this.batchSize = Number(this.container.dataset.batchSize)
    this.loadMoreUrl = this.container.dataset.loadMoreUrl
    this.loading = false

    this.init()
  }

  init() {
    window.addEventListener('scroll', () => {
      if ((window.scrollY + window.innerHeight) > (document.documentElement.scrollHeight - 1)) {
        this.loadMore()
      }
    })
  }

  async loadMore() {
    if (this.loading || !this.hasMore) return

    this.loading = true
    document.getElementById("loadingSpinner")?.classList.remove("d-none")

    try {
      const data = await getAction(`${this.loadMoreUrl}?offset=${this.offset}`)
      if (!data) return

      // Форматируем даты в подгруженных карточках
      const html = formatDatesInHTML(data.html)

      this.container.insertAdjacentHTML("beforeend", html)
      this.offset += this.batchSize
      this.hasMore = data.has_more
    } catch (error) {
      console.error("Ошибка загрузки:", error)
    } finally {
      this.loading = false
      document.getElementById("loadingSpinner")?.classList.add("d-none")
    }
  }
}

export default BatchLoader
