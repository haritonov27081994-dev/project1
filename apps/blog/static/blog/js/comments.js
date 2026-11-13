import { postAction } from "./utils.js"
import { formatDate } from "./format-dates.js"

const commentFormElement = document.getElementById('commentForm')

if (commentFormElement) {
  commentFormElement.addEventListener('submit', async function(event) {
    event.preventDefault()
    const formData = new FormData(this)
    const url = this.dataset.addCommentUrl

    const commentErrorsElement = document.getElementById('commentErrors')
    commentErrorsElement.classList.add('d-none')
    commentErrorsElement.textContent = ''

    try {
      const data = await postAction(url, formData)
      if (!data) return

      if (data.success) {
        this.querySelector('textarea').value = ''

        const commentsListElement = document.getElementById('commentsList')
        const emptyMessageElement = commentsListElement.querySelector('#emptyMessage')
        if (emptyMessageElement) {
          emptyMessageElement.remove()
        }

        commentsListElement.insertAdjacentHTML('afterbegin', data.comment_html)
        const newCommentElement = commentsListElement.firstElementChild
        const dateElement = newCommentElement.querySelector('.date-field')
        if (dateElement && typeof formatDate === 'function') {
          formatDate(dateElement)
        }

        // Увеличиваем offset на 1, так как добавили новый комментарий в начало списка
        if (window.commentsBatchLoader) {
          window.commentsBatchLoader.offset += 1
        }

        const commentsTitleElement = document.querySelector('#commentsTitle')
        commentsTitleElement.textContent = `Комментарии (${data.comments_count})`
      } else {
        commentErrorsElement.textContent = data.error
        commentErrorsElement.classList.remove('d-none')
      }
    } catch (error) {
      console.error('Ошибка при добавлении комментария:', error)
      commentErrorsElement.textContent = 'Произошла ошибка при отправке комментария'
      commentErrorsElement.classList.remove('d-none')
    }
  })
}
