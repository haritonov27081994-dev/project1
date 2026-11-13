import { postAction } from "./utils.js"

// Делегирование событий на контейнере
document.addEventListener('click', async (event) => {
  if (event.target.closest('.favorite-btn')) {
    const favoriteBtnElement = event.target.closest('.favorite-btn')
    const isAuthenticated = favoriteBtnElement.dataset.isAuthenticated === 'true'
    if (!isAuthenticated) {
      window.location.href = favoriteBtnElement.dataset.loginUrl
      return
    }
    const url = favoriteBtnElement.dataset.postFavoriteToggleUrl
    const postCardElement = favoriteBtnElement.closest('.post-card')
    
    // Находим обе иконки конкретно внутри этой кнопки
    const iconEmpty = favoriteBtnElement.querySelector('.icon-empty')
    const iconFilled = favoriteBtnElement.querySelector('.icon-filled')
    const favoritesCountElement = postCardElement.querySelector('.favorites-count')

    const data = await postAction(url)
    if (!data) return

    if (data.is_favorite) {
      iconEmpty.classList.add('d-none')
      iconFilled.classList.remove('d-none')
    } else {
      iconEmpty.classList.remove('d-none')
      iconFilled.classList.add('d-none')
      removePostFromFavorites(postCardElement)
    }
    favoritesCountElement.textContent = data.favorites_count
  }
})

// Функция для удаления поста со страницы избранных
function removePostFromFavorites(postCardElement) {
  if (document.querySelector('[data-page-type="favorite-posts"]') !== null) {
    postCardElement.remove()
    const remainingPosts = document.querySelectorAll('.post-card')
    if (remainingPosts.length === 0) {
      const container = document.querySelector('.container')
      container.innerHTML = '<p class="text-center text-muted fs-5">Пока нет избранных постов.</p>'
    }
  }
}
