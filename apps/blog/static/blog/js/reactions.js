import { postAction } from "./utils.js"

const postReactions = document.querySelector("#postReactions")

if (postReactions) {
  postReactions.addEventListener('click', async (event) => {
    const btn = event.target.closest('.js-reaction-btn')
    if (!btn) return

    const isAuthenticated = postReactions.dataset.isAuthenticated === 'true'
    if (!isAuthenticated) {
      window.location.href = postReactions.dataset.loginUrl
      return
    }

    const url = btn.dataset.url
    const data = await postAction(url)
    if (!data) return

    document.querySelector("#likesCount").textContent = data.likes_count
    document.querySelector("#dislikesCount").textContent = data.dislikes_count

    const likeBtn = document.querySelector('#likeBtn')
    const dislikeBtn = document.querySelector('#dislikeBtn')

    // Управление лайком
    const likeFill = likeBtn.querySelector('.js-icon-fill')
    const likeEmpty = likeBtn.querySelector('.js-icon-empty')
    if (data.has_liked) {
      likeBtn.classList.replace('btn-outline-primary', 'btn-primary')
      likeFill.classList.remove('d-none')
      likeEmpty.classList.add('d-none')
    } else {
      likeBtn.classList.replace('btn-primary', 'btn-outline-primary')
      likeFill.classList.add('d-none')
      likeEmpty.classList.remove('d-none')
    }

    // Управление дизлайком
    const dislikeFill = dislikeBtn.querySelector('.js-icon-fill')
    const dislikeEmpty = dislikeBtn.querySelector('.js-icon-empty')
    if (data.has_disliked) {
      dislikeBtn.classList.replace('btn-outline-danger', 'btn-danger')
      dislikeFill.classList.remove('d-none')
      dislikeEmpty.classList.add('d-none')
    } else {
      dislikeBtn.classList.replace('btn-danger', 'btn-outline-danger')
      dislikeFill.classList.add('d-none')
      dislikeEmpty.classList.remove('d-none')
    }
  })
}
