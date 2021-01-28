window.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('logoutForm')
  document.getElementById('logoutLink').addEventListener('click', function() {
    form.submit()
  })
})
