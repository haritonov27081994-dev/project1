export function formatDate(el) {
  const rawDate = el.textContent.trim()
  if (!rawDate) return
  const parsed = new Date(rawDate)
  if (!isNaN(parsed.getTime())) {
    el.textContent = parsed.toLocaleString()
  }
}

export function formatDatesInHTML(htmlString) {
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = htmlString
  tempDiv.querySelectorAll(".date-field").forEach(el => {
    formatDate(el)
  })
  return tempDiv.innerHTML
}

document.querySelectorAll(".date-field").forEach(el => {
  formatDate(el)
})
