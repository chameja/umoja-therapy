<script setup>
import { ref, onMounted, computed } from 'vue'
import { authStore } from '../store'
import { useRouter } from 'vue-router'

const router = useRouter()

// --- State ---
const allRequests = ref([])
const isLoading = ref(true)
const feedbackMessage = ref('')

// --- Intake Modal State ---
const showIntakeModal = ref(false)
const selectedIntakeData = ref(null)

// --- Computed Properties (Fixed for Python Enum Title Case) ---
const pendingRequests = computed(() => {
  const now = new Date()
  return allRequests.value.filter(req => {
    // Calculate when the session ends (fallback to start_time + 60 mins if end_time is missing)
    const sessionEndTime = req.end_time ? new Date(req.end_time) : new Date(new Date(req.start_time).getTime() + 60 * 60 * 1000)
    
    return req.status === 'Open' && sessionEndTime > now
  })
})

const upcomingSessions = computed(() => {
  const now = new Date()
  return allRequests.value.filter(req => {
    const sessionEndTime = req.end_time ? new Date(req.end_time) : new Date(new Date(req.start_time).getTime() + 60 * 60 * 1000)
    
    return req.status === 'Accepted' && sessionEndTime > now
  })
})

// --- Methods ---
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// Fetch all requests assigned to this therapist
const fetchSessionRequests = async () => {
  const token = localStorage.getItem('umoja_token')
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/session-requests/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      allRequests.value = await response.json()
    }
  } catch (error) {
    console.error("Failed to fetch sessions", error)
  } finally {
    isLoading.value = false
  }
}

// Accept or Decline a request
const updateRequestStatus = async (requestId, newStatus) => {
  const token = localStorage.getItem('umoja_token')
  feedbackMessage.value = ''
  
  // Send the exact Title Case string that Pydantic expects
  const statusValue = newStatus === 'accepted' ? 'Accepted' : 'Declined' 

  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/session-requests/${requestId}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ status: statusValue }) 
    })

    if (!response.ok) {
      const errorData = await response.json()
      console.error("FastAPI Error Details:", errorData)
      if (response.status === 422) {
        throw new Error(`Validation Error: ${errorData.detail[0].msg}`)
      }
      throw new Error(`Failed to mark as ${newStatus}`)
    }
    
    // Refresh the list to move the card to the correct section
    await fetchSessionRequests()
    feedbackMessage.value = `Session successfully ${newStatus}!`
    
    // Clear success message after 3 seconds
    setTimeout(() => { feedbackMessage.value = '' }, 3000)

  } catch (error) {
    feedbackMessage.value = error.message
  }
}

// Helper function to format the scary ISO dates into readable text
const formatDateTime = (dateString) => {
  const options = { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }
  return new Date(dateString).toLocaleDateString('en-US', options)
}

// --- Intake Modal Methods ---
const openIntake = (request) => {
  selectedIntakeData.value = request.intake_answers || "No intake information provided."
  showIntakeModal.value = true
}

const closeIntake = () => {
  showIntakeModal.value = false
  selectedIntakeData.value = null
}

onMounted(() => {
  fetchSessionRequests()
})
</script>

<template>
  <div class="space-y-6 font-sans">
    
    <div class="bg-white p-6 rounded-2xl shadow-sm border border-green-100 flex flex-col sm:flex-row items-center sm:justify-between gap-4">
      <div class="text-center sm:text-left">
        <h1 class="text-2xl font-bold text-gray-900">Dr. {{ authStore.user?.name || 'Therapist' }}</h1>
        <p class="text-green-600 font-medium tracking-wide text-sm mt-1 uppercase">Therapist Portal</p>
      </div>
      
      <button @click="handleLogout" class="w-full sm:w-auto px-6 py-2.5 bg-red-50 text-red-600 hover:bg-red-100 font-semibold rounded-xl transition-colors">
        Sign Out
      </button>
    </div>

    <div v-if="feedbackMessage" :class="feedbackMessage.includes('successfully') ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200'" class="p-4 rounded-xl text-center font-medium border shadow-sm transition-all">
      {{ feedbackMessage }}
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col h-full">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-gray-800">New Requests</h2>
          <span v-if="pendingRequests.length > 0" class="bg-orange-100 text-orange-700 text-xs font-bold px-3 py-1 rounded-full border border-orange-200">
            {{ pendingRequests.length }} Pending
          </span>
        </div>

        <div v-if="isLoading" class="flex justify-center py-8">
          <svg class="animate-spin h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        </div>
        
        <div v-else-if="pendingRequests.length === 0" class="text-gray-500 py-10 bg-gray-50 rounded-xl text-center border border-dashed border-gray-200 flex-1 flex flex-col justify-center items-center">
          <span class="text-3xl mb-2">📥</span>
          <p>No new client requests at this time.</p>
        </div>

        <div v-else class="space-y-4 overflow-y-auto pr-2">
          <div v-for="req in pendingRequests" :key="req.session_request_id" class="p-5 border border-blue-100 bg-blue-50/40 rounded-xl hover:border-blue-200 transition-colors">
            <div class="flex justify-between items-start mb-4">
              <div>
                <p class="font-semibold text-gray-900">Client ID: {{ req.client_id }}</p>
                <div class="mt-2">
                  <p class="text-xs text-gray-500 uppercase tracking-wider font-semibold">Requested Time</p>
                  <p class="font-medium text-blue-700 mt-0.5">📅 {{ formatDateTime(req.start_time) }}</p>
                </div>
              </div>
            </div>

            <button @click="openIntake(req)" class="w-full mb-3 bg-blue-100/50 hover:bg-blue-100 text-blue-700 border border-blue-200 py-2 rounded-lg text-sm font-semibold transition-colors">
              View Intake Form
            </button>
            
            <div class="flex gap-3 pt-3 border-t border-blue-100">
              <button @click="updateRequestStatus(req.session_request_id, 'accepted')" class="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-semibold transition-colors shadow-sm">
                Accept
              </button>
              <button @click="updateRequestStatus(req.session_request_id, 'declined')" class="flex-1 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 py-2 rounded-lg text-sm font-semibold transition-colors">
                Decline
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col h-full">
        <h2 class="text-lg font-bold text-gray-800 mb-6">Upcoming Schedule</h2>
        
        <div v-if="isLoading" class="flex justify-center py-8">
          <svg class="animate-spin h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        </div>

        <div v-else-if="upcomingSessions.length === 0" class="text-gray-500 py-10 bg-gray-50 rounded-xl text-center border border-dashed border-gray-200 flex-1 flex flex-col justify-center items-center">
          <span class="text-3xl mb-2">🗓️</span>
          <p>Your schedule is clear.</p>
        </div>

        <div v-else class="space-y-3 overflow-y-auto pr-2">
          <div v-for="session in upcomingSessions" :key="session.session_request_id" class="p-4 border border-gray-100 bg-white shadow-sm rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 hover:border-green-300 transition-colors group">
            <div>
              <p class="font-semibold text-gray-900">Client ID: {{ session.client_id }}</p>
              <p class="text-sm text-gray-600 mt-1">🕒 {{ formatDateTime(session.start_time) }}</p>
            </div>
            
            <router-link :to="`/room/${session.session_request_id}`" class="w-full sm:w-auto bg-green-50 text-green-700 hover:bg-green-600 hover:text-white border border-green-200 hover:border-green-600 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 text-center flex items-center justify-center gap-2">
              <span>📹</span> Enter Room
            </router-link>
          </div>
        </div>
      </div>

    </div>

    <div v-if="showIntakeModal" class="fixed inset-0 bg-gray-900/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-lg shadow-xl">
        <div class="flex justify-between items-center mb-4 border-b pb-3">
          <h3 class="text-xl font-bold text-gray-900">Client Intake Form</h3>
          <button @click="closeIntake" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
        </div>
        
        <div class="space-y-4 max-h-[60vh] overflow-y-auto text-gray-800 p-4 bg-gray-50 rounded-xl border border-gray-100">
          <div v-if="typeof selectedIntakeData === 'object' && selectedIntakeData !== null">
             <div v-for="(answer, question) in selectedIntakeData" :key="question" class="mb-3 last:mb-0">
                <p class="font-semibold capitalize text-xs text-gray-500 uppercase tracking-wider">{{ question.replace(/_/g, ' ') }}</p>
                <p class="font-medium mt-1">{{ answer }}</p>
             </div>
          </div>
          <div v-else>
             {{ selectedIntakeData }}
          </div>
        </div>

        <div class="mt-6 flex justify-end">
          <button @click="closeIntake" class="px-5 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold rounded-xl transition-colors">
            Close
          </button>
        </div>
      </div>
    </div>

  </div>
</template>