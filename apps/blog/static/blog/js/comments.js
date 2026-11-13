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

class ReplyManager {
  constructor() {
    this.init()
  }

  init() {
    document.addEventListener('click', (e) => {
      if (e.target.closest('.reply-btn')) {
        this.handleReplyClick(e.target.closest('.reply-btn'))
      }
      if (e.target.closest('.cancel-reply-btn')) {
        this.handleCancelReplyClick(e.target.closest('.cancel-reply-btn'))
      }
    })

    document.addEventListener('submit', (e) => {
      if (e.target.closest('.reply-form')) {
        e.preventDefault()
        this.handleReplyFormSubmit(e.target.closest('.reply-form'))
      }
    })
  }

  handleReplyClick(replyBtnElement) {
    const replyFormElement = document.getElementById(`replyForm${replyBtnElement.dataset.commentId}`)
    document.querySelectorAll('.reply-form-container').forEach(form => {
      form.classList.add('d-none')
    })
    replyFormElement.classList.remove('d-none')
    replyFormElement.querySelector('textarea').focus()
  }

  handleCancelReplyClick(cancelBtnElement) {
    const replyFormElement = cancelBtnElement.closest('.reply-form-container')
    replyFormElement.classList.add('d-none')
    replyFormElement.querySelector('textarea').value = ''
  }

  async handleReplyFormSubmit(formElement) {
    const textareaElement = formElement.querySelector('textarea')
    const text = textareaElement.value.trim()
    const parentId = formElement.dataset.parentId
    const url = formElement.dataset.addCommentUrl

    const formData = new FormData()
    formData.append('text', text)
    formData.append('parent_id', parentId)

    const data = await postAction(url, formData)
    if (!data) return

    if (data.success) {
      textareaElement.value = ''
      formElement.closest('.reply-form-container').classList.add('d-none')

      const repliesContainerElement = formElement.closest('.comment-container').querySelector('.replies')
      repliesContainerElement.insertAdjacentHTML('beforeend', data.comment_html)

      const dateElement = repliesContainerElement.lastElementChild.querySelector('.date-field')
      if (dateElement && typeof formatDate === 'function') {
        formatDate(dateElement)
      }

      const commentsTitleElement = document.querySelector('#commentsTitle')
      commentsTitleElement.textContent = `Комментарии (${data.comments_count})`
    } else {
      alert(data.error)
    }
  }
}

new ReplyManager()
