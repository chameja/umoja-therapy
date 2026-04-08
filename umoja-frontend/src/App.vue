<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from './store' // Import our new store

const router = useRouter()
const showDropdown = ref(false)

// Check if user is logged in when the app first loads
onMounted(() => {
  authStore.fetchUser()
})

const handleLogout = () => {
  authStore.logout()
  showDropdown.value = false
  router.push('/login')
}
</script>

<template>
  <div>
    <nav class="bg-blue-900 text-white p-4 shadow-md relative z-50">
      <div class="max-w-5xl mx-auto flex justify-between items-center">
        <div class="text-xl font-bold tracking-wider">
          <router-link to="/">UMOJA THERAPY</router-link>
        </div>
        
        <div class="flex items-center space-x-6">
          <router-link to="/" class="hover:text-blue-200 transition-colors">Home</router-link>
          
          <div v-if="authStore.isLoggedIn && authStore.user" class="relative">
            <button @click="showDropdown = !showDropdown" class="flex items-center focus:outline-none">
              <div class="h-10 w-10 bg-white text-blue-900 rounded-full flex items-center justify-center font-bold text-lg border-2 border-transparent hover:border-blue-300 transition-colors cursor-pointer shadow-sm">
                {{ authStore.user.name.charAt(0).toUpperCase() }}
              </div>
            </button>

            <div v-if="showDropdown" class="absolute right-0 mt-3 w-48 bg-white rounded-xl shadow-xl py-2 border border-gray-100 transition-all origin-top-right">
              <div class="px-4 py-3 border-b border-gray-50">
                <p class="text-sm font-semibold text-gray-900 truncate">{{ authStore.user.name }}</p>
                <p class="text-xs text-gray-500 capitalize mt-0.5">{{ authStore.user.role }} Account</p>
              </div>
              <router-link to="/dashboard" @click="showDropdown = false" class="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700 font-medium">
                My Dashboard
              </router-link>
              <button @click="handleLogout" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 font-medium border-t border-gray-50 mt-1">
                Sign Out
              </button>
            </div>
          </div>

          <router-link v-else to="/login" class="bg-white text-blue-900 px-5 py-2 rounded-lg font-semibold hover:bg-blue-50 transition-colors shadow-sm">
            Login
          </router-link>

        </div>
      </div>
    </nav>

    <main>
      <router-view></router-view>
    </main>

    <div v-if="showDropdown" @click="showDropdown = false" class="fixed inset-0 z-40"></div>
  </div>
</template>