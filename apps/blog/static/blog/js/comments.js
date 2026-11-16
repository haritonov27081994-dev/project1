import { postAction } from "./utils.js"
import { formatDate } from "./format-dates.js"

class CommentManager {
  constructor() {
    this.init()
  }

  init() {
    // Обработчик основной формы комментария (если пользователь авторизован)
    const commentFormElement = document.getElementById('commentForm')
    if (commentFormElement) {
      commentFormElement.addEventListener('submit', (e) => this.handleMainCommentSubmit(e))
    }

    // Обработчики для кнопок "Ответить" и "Отмена"
    document.addEventListener('click', (e) => {
      if (e.target.closest('.reply-btn')) {
        this.handleReplyClick(e.target.closest('.reply-btn'))
      }
      if (e.target.closest('.cancel-reply-btn')) {
        this.handleCancelReplyClick(e.target.closest('.cancel-reply-btn'))
      }
    })

    // Обработчики для форм ответов
    document.addEventListener('submit', (e) => {
      if (e.target.closest('.reply-form')) {
        e.preventDefault()
        this.handleReplyFormSubmit(e.target.closest('.reply-form'))
      }
    })
  }

  // Обработчик основной формы комментария
  async handleMainCommentSubmit(event) {
    event.preventDefault()
    const formElement = event.target
    const formData = new FormData(formElement)
    const url = formElement.dataset.addCommentUrl

    // Скрываем предыдущие ошибки
    const commentErrorsElement = document.getElementById('commentErrors')
    commentErrorsElement.classList.add('d-none')
    commentErrorsElement.textContent = ''

    try {
      const data = await postAction(url, formData)
      if (!data) return

      if (data.success) {
        // Очищаем текстовое поле
        formElement.querySelector('textarea').value = ''

        // Добавляем новый комментарий в начало списка
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

        // Увеличиваем offset на 1, так как добавили новый комментарий
        if (window.commentsBatchLoader) {
          window.commentsBatchLoader.offset += 1
        }

        // Обновляем счетчик комментариев в заголовке
        const commentsTitleElement = document.querySelector('#commentsTitle')
        commentsTitleElement.textContent = `Комментарии (${data.comments_count})`
      } else {
        // Показываем ошибку
        commentErrorsElement.textContent = data.error
        commentErrorsElement.classList.remove('d-none')
      }
    } catch (error) {
      console.error('Ошибка при добавлении комментария:', error)
      commentErrorsElement.textContent = 'Произошла ошибка при отправке комментария'
      commentErrorsElement.classList.remove('d-none')
    }
  }

  handleReplyClick(replyBtnElement) {
    const replyFormElement = document.getElementById(`replyForm${replyBtnElement.dataset.commentId}`)
    // Скрываем все другие открытые формы
    document.querySelectorAll('.reply-form-container').forEach(form => {
      form.classList.add('d-none')
    })
    // Показываем текущую форму
    replyFormElement.classList.remove('d-none')
    // Фокусируемся на текстовом поле
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
      // Очищаем текстовое поле и скрываем форму
      textareaElement.value = ''
      formElement.closest('.reply-form-container').classList.add('d-none')

      // Добавляем ответ в блок ответов
      const repliesContainerElement = formElement.closest('.comment-container').querySelector('.replies')
      repliesContainerElement.insertAdjacentHTML('beforeend', data.comment_html)

      // Форматируем дату нового ответа
      const dateElement = repliesContainerElement.lastElementChild.querySelector('.date-field')
      if (dateElement && typeof formatDate === 'function') {
        formatDate(dateElement)
      }

      // Обновляем счетчик комментариев в заголовке
      const commentsTitleElement = document.querySelector('#commentsTitle')
      commentsTitleElement.textContent = `Комментарии (${data.comments_count})`
    } else {
      alert(data.error)
    }
  }
}

new CommentManager()
