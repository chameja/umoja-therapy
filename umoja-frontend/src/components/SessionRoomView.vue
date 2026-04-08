<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authStore } from '../store'

const route = useRoute()
const router = useRouter()
const sessionId = route.params.id

const isLoading = ref(true)
const errorMessage = ref('')
const roomData = ref(null)

// --- Jitsi Video State ---
const jitsiContainer = ref(null)
let jitsiApi = null

// --- Therapist Notes State ---
const sessionNotes = ref('')
const isSaving = ref(false)
const saveFeedback = ref('')

const fetchRoomDetails = async () => {
  const token = localStorage.getItem('umoja_token')
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/sessions/${sessionId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || "Failed to load session.")
    }
    
    roomData.value = await response.json()
    if (roomData.value.notes) sessionNotes.value = roomData.value.notes
    
    // Now that we have the room ID and user's name, boot up Jitsi!
    initJitsi()

  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}

// --- The Official Jitsi Integration ---
const initJitsi = () => {
  // 1. Inject the Jitsi script into the page
  if (!window.JitsiMeetExternalAPI) {
    const script = document.createElement('script')
    script.src = 'https://meet.jit.si/external_api.js'
    script.async = true
    script.onload = () => launchJitsi()
    document.head.appendChild(script)
  } else {
    launchJitsi()
  }
}

const launchJitsi = () => {
  if (!jitsiContainer.value) return;

  const domain = 'meet.jit.si';
  const options = {
    roomName: roomData.value.video_room_id,
    parentNode: jitsiContainer.value,
    userInfo: {
      displayName: roomData.value.my_name // Automatically sets their name in the video call!
    },
    configOverwrite: {
      prejoinPageEnabled: false, // Skips the annoying "Join Meeting" waiting screen
      startWithAudioMuted: false,
      startWithVideoMuted: false
    },
    interfaceConfigOverwrite: {
      SHOW_JITSI_WATERMARK: false
    }
  };
  
  jitsiApi = new window.JitsiMeetExternalAPI(domain, options);
}

// --- Notes Logic ---
const saveNotes = async () => {
  isSaving.value = true
  saveFeedback.value = ''
  const token = localStorage.getItem('umoja_token')

  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/sessions/${sessionId}/notes`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ notes: sessionNotes.value })
    })

    if (!response.ok) throw new Error("Failed to save notes.")
    
    saveFeedback.value = "Notes saved securely."
    setTimeout(() => saveFeedback.value = '', 3000)
  } catch (error) {
    saveFeedback.value = error.message
  } finally {
    isSaving.value = false
  }
}

// --- Cleanup Logic ---
const leaveRoom = () => {
  // If we don't dispose the API, the webcam light stays on when they route back to the dashboard!
  if (jitsiApi) jitsiApi.dispose() 
  router.push('/dashboard')
}

// Failsafe cleanup in case they hit the browser back button
onBeforeUnmount(() => {
  if (jitsiApi) jitsiApi.dispose()
})

onMounted(() => {
  if (!authStore.user) {
    authStore.fetchUser().then(() => fetchRoomDetails())
  } else {
    fetchRoomDetails()
  }
})
</script>

<template>
  <div class="h-screen w-full bg-gray-950 text-gray-100 flex flex-col overflow-hidden font-sans">
    
    <header class="bg-gray-900 border-b border-gray-800 px-6 py-4 flex justify-between items-center shrink-0 z-20 shadow-sm">
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-3">
          <div class="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
          <h1 class="text-xl font-bold tracking-wider text-blue-400">UMOJA CLINIC</h1>
        </div>
        <div class="h-6 w-px bg-gray-700 hidden sm:block"></div>
        <span v-if="roomData" class="text-sm font-medium text-gray-300 hidden sm:block">
          Session with <span class="text-white">{{ roomData.partner_name }}</span>
        </span>
      </div>

      <button @click="leaveRoom" class="bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/50 px-5 py-2 rounded-lg font-semibold transition-all duration-200 flex items-center gap-2">
        <span>Leave Room</span>
      </button>
    </header>

    <div v-if="isLoading" class="flex-1 flex flex-col justify-center items-center bg-gray-950">
      <svg class="animate-spin h-10 w-10 text-blue-500 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
      <p class="text-lg text-gray-400 font-medium">Establishing secure connection...</p>
    </div>
    
    <div v-else-if="errorMessage" class="flex-1 flex flex-col justify-center items-center space-y-4 bg-gray-950 px-4 text-center">
      <div class="h-20 w-20 bg-red-500/10 rounded-full flex items-center justify-center mb-2">
        <span class="text-red-500 text-4xl">⚠️</span>
      </div>
      <h2 class="text-2xl font-bold text-white">Connection Failed</h2>
      <p class="text-gray-400 max-w-md">{{ errorMessage }}</p>
      <button @click="leaveRoom" class="mt-4 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold transition-colors">
        Return to Dashboard
      </button>
    </div>

    <div v-else class="flex-1 flex flex-col lg:flex-row min-h-0">
      
      <div class="flex-1 p-4 lg:p-6 flex flex-col min-h-0 relative">
        <div class="w-full h-full bg-black rounded-2xl overflow-hidden shadow-2xl ring-1 ring-gray-800 relative group">
          
          <div ref="jitsiContainer" class="w-full h-full absolute inset-0"></div>

        </div>
      </div>

      <div v-if="authStore.user?.role === 'therapist'" class="w-full lg:w-[400px] bg-gray-900 border-l border-gray-800 flex flex-col h-full shrink-0">
        <div class="p-5 border-b border-gray-800 bg-gray-900 shrink-0">
          <h2 class="text-lg font-bold text-gray-100 flex items-center gap-2">
            <span>📝</span> Clinical Notes
          </h2>
          <p class="text-sm text-gray-400 mt-1 leading-relaxed">
            Record observations and treatment goals. These notes are encrypted and invisible to the client.
          </p>
        </div>
        
        <div class="flex-1 p-5 flex flex-col min-h-0 bg-gray-900/50">
          <textarea 
            v-model="sessionNotes" 
            placeholder="Type your session observations here..."
            class="flex-1 w-full bg-gray-950 border border-gray-800 rounded-xl p-4 text-gray-200 placeholder-gray-600 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none shadow-inner leading-relaxed"
          ></textarea>
          
          <div class="pt-4 mt-auto flex items-center justify-between shrink-0">
            <span :class="saveFeedback.includes('securely') ? 'text-green-400' : 'text-red-400'" class="text-sm font-medium transition-opacity duration-300" :style="{ opacity: saveFeedback ? 1 : 0 }">
              {{ saveFeedback || 'Ready' }}
            </span>
            <button @click="saveNotes" :disabled="isSaving" class="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2.5 rounded-xl font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/20 flex items-center gap-2">
              <span v-if="isSaving">Saving...</span>
              <span v-else>Save Notes</span>
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>