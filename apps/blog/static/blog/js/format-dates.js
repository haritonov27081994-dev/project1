export function formatDate(el) {
  const rawDate = el.textContent.trim()
  if (!rawDate) return
  const parsed = new Date(rawDate)
  if (!isNaN(parsed.getTime())) {
    el.textContent = parsed.toLocaleString()
  }
}

document.querySelectorAll(".date-field").forEach(formatDate)
