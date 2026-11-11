const alerts = document.querySelectorAll('.auto-dismiss')

alerts.forEach(alert => {
  const bsAlert = new bootstrap.Alert(alert)
  setTimeout(() => {
    bsAlert.close()
  }, 4000)
})
