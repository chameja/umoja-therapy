import { reactive } from 'vue'

export const authStore = reactive({
  isLoggedIn: false,
  user: null,

  // Function to fetch the user profile from FastAPI
  async fetchUser() {
    const token = localStorage.getItem('umoja_token')
    if (!token) {
      this.logout()
      return
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/users/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        this.user = await response.json()
        this.isLoggedIn = true
      } else {
        this.logout()
      }
    } catch (error) {
      this.logout()
    }
  },

  // Function to clear data on logout
  logout() {
    localStorage.removeItem('umoja_token')
    this.isLoggedIn = false
    this.user = null
  }
})
