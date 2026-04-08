<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from '../store'

const router = useRouter()

// --- UI State ---
const isLoginMode = ref(true) // Toggle between Login and Register
const userType = ref('client') // 'client' or 'therapist'

// --- Form Data ---
const name = ref('')
const email = ref('')
const password = ref('')

// --- Feedback State ---
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// --- Dynamic Text ---
const formTitle = computed(() => isLoginMode.value ? 'Welcome Back' : 'Create Account')
const submitText = computed(() => {
  if (loading.value) return 'Please wait...'
  return isLoginMode.value ? 'Sign In' : 'Sign Up'
})

// --- API Logic ---
const handleSubmit = async () => {
    console.log("submitting")
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    if (isLoginMode.value) {
      // 1. LOGIN LOGIC (FastAPI OAuth2 expects Form Data, not JSON)
      const formData = new URLSearchParams()
      formData.append('username', email.value) // FastAPI defaults to 'username' for the email field
      formData.append('password', password.value)

      // const response = await fetch(`${import.meta.env.VITE_API_URL}/token`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      //   body: formData
      // })

      const response = await fetch(`${import.meta.env.VITE_API_URL}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      })

      if (!response.ok) throw new Error('Invalid email or password')

      const data = await response.json()

      console.log("Login success")
      
      // Save the token securely in the browser's local storage
      localStorage.setItem('umoja_token', data.access_token)
      await authStore.fetchUser()
      
      // Redirect to the home page (or dashboard later)
      router.push('/dashboard')
      
    } else {
      // 2. REGISTER LOGIC (Expects JSON)
      const endpoint = userType.value === 'client' 
        ? `${import.meta.env.VITE_API_URL}/register/client` 
        : `${import.meta.env.VITE_API_URL}/register/therapist`

      const payload = {
        email: email.value,
        password: password.value,
        // Send the correct name field based on user type
        ...(userType.value === 'client' ? { client_name: name.value } : { therapist_name: name.value })
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      const data = await response.json()

      if (!response.ok) throw new Error(data.detail || 'Registration failed')

      // Success! Switch them back to the login screen to sign in
      successMessage.value = 'Account created successfully! Please log in.'
      isLoginMode.value = true
      password.value = '' // Clear password for security
    }
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
    
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <h2 class="mt-6 text-center text-3xl font-extrabold text-blue-900">
        {{ formTitle }}
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        {{ isLoginMode ? 'New to Umoja Therapy?' : 'Already have an account?' }}
        <button @click="isLoginMode = !isLoginMode; errorMessage = ''; successMessage = ''" class="font-medium text-blue-600 hover:text-blue-500">
          {{ isLoginMode ? 'Create an account' : 'Sign in instead' }}
        </button>
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow-xl sm:rounded-2xl sm:px-10 border border-gray-100">
        
        <div v-if="errorMessage" class="mb-4 bg-red-50 text-red-600 p-3 rounded-lg text-sm text-center">
          {{ errorMessage }}
        </div>
        <div v-if="successMessage" class="mb-4 bg-green-50 text-green-600 p-3 rounded-lg text-sm text-center">
          {{ successMessage }}
        </div>

        <form class="space-y-6" @submit.prevent="handleSubmit">
          
          <div v-if="!isLoginMode" class="flex justify-center space-x-4 mb-6">
            <label class="flex items-center cursor-pointer">
              <input type="radio" v-model="userType" value="client" class="form-radio text-blue-600 focus:ring-blue-500 h-4 w-4">
              <span class="ml-2 text-gray-700">I am a Client</span>
            </label>
            <label class="flex items-center cursor-pointer">
              <input type="radio" v-model="userType" value="therapist" class="form-radio text-blue-600 focus:ring-blue-500 h-4 w-4">
              <span class="ml-2 text-gray-700">I am a Therapist</span>
            </label>
          </div>

          <div v-if="!isLoginMode">
            <label for="name" class="block text-sm font-medium text-gray-700">Full Name</label>
            <div class="mt-1">
              <input id="name" v-model="name" type="text" required class="appearance-none block w-full px-3 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="e.g. Jane Doe">
            </div>
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">Email address</label>
            <div class="mt-1">
              <input id="email" v-model="email" type="email" autocomplete="email" required class="appearance-none block w-full px-3 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="you@example.com">
            </div>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <div class="mt-1">
              <input id="password" v-model="password" type="password" autocomplete="current-password" required class="appearance-none block w-full px-3 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="••••••••">
            </div>
          </div>

          <div>
            <button type="submit" :disabled="loading" class="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
              {{ submitText }}
            </button>
          </div>
          
        </form>
      </div>
    </div>
  </div>
</template>