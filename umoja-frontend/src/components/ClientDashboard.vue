<script setup>
import { ref, onMounted, computed } from 'vue'
import { authStore } from '../store'
import { useRouter } from 'vue-router'

const router = useRouter()

// --- UI State ---
const isIntakeModalOpen = ref(false)
const isBookingModalOpen = ref(false)
const isLoading = ref(true)

// --- Intake Form State ---
const formQuestions = ref([])
const isSubmittingIntake = ref(false)
const intakeFeedback = ref('')

// --- Booking State ---
const myRequests = ref([])
const therapists = ref([])
const isSubmittingBooking = ref(false)
const bookingFeedback = ref('')
const bookingForm = ref({
  therapist_id: '',
  datetime: ''
})

// --- Computed Properties (Fixed for Python Enum Title Case) ---
const pendingRequests = computed(() => {
  const now = new Date()
  return myRequests.value.filter(req => {
    // Calculate when the session ends
    const sessionEndTime = req.end_time ? new Date(req.end_time) : new Date(new Date(req.start_time).getTime() + 60 * 60 * 1000)
    
    return req.status === 'Open' && sessionEndTime > now
  })
})

const upcomingSessions = computed(() => {
  const now = new Date()
  return myRequests.value.filter(req => {
    const sessionEndTime = req.end_time ? new Date(req.end_time) : new Date(new Date(req.start_time).getTime() + 60 * 60 * 1000)
    
    return req.status === 'Accepted' && sessionEndTime > now
  })
})

// Helper to get minimum datetime for the booking input (prevents past bookings)
const minDateTime = computed(() => {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  return now.toISOString().slice(0, 16)
})

// --- Methods ---
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// 1. Fetch Intake Data
const fetchIntakeData = async () => {
  const token = localStorage.getItem('umoja_token')
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/my-intake`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      const data = await response.json()
      formQuestions.value = data.answers
    }
  } catch (error) {
    console.error("Failed to fetch intake data", error)
  }
}

// 2. Fetch Client's Session Requests
const fetchMyRequests = async () => {
  const token = localStorage.getItem('umoja_token')
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/session-requests/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      myRequests.value = await response.json()
    }
  } catch (error) {
    console.error("Failed to fetch sessions", error)
  }
}

// 3. Fetch Therapist Directory (for the dropdown)
const fetchTherapists = async () => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/therapists/`)
    if (response.ok) {
      therapists.value = await response.json()
    }
  } catch (error) {
    console.error("Failed to fetch therapists", error)
  }
}

// Helper to get therapist name from ID
const getTherapistName = (id) => {
  const therapist = therapists.value.find(t => t.therapist_id === id)
  return therapist ? therapist.therapist_name : `Therapist #${id}`
}

// 4. Submit Updated Intake Form
const submitIntakeForm = async () => {
  isSubmittingIntake.value = true
  intakeFeedback.value = ''
  const token = localStorage.getItem('umoja_token')

  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/my-intake`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ answers: formQuestions.value })
    })

    if (!response.ok) throw new Error('Failed to save changes.')
    
    intakeFeedback.value = 'Goals updated successfully!'
    setTimeout(() => {
      isIntakeModalOpen.value = false
      intakeFeedback.value = ''
    }, 1500)
  } catch (error) {
    intakeFeedback.value = error.message
  } finally {
    isSubmittingIntake.value = false
  }
}

// 5. Submit New Session Booking
const submitBooking = async () => {
  isSubmittingBooking.value = true
  bookingFeedback.value = ''
  const token = localStorage.getItem('umoja_token')

  try {
    const startTime = new Date(bookingForm.value.datetime)
    const endTime = new Date(startTime.getTime() + 60 * 60 * 1000)

    const payload = {
      therapist_id: parseInt(bookingForm.value.therapist_id),
      start_time: startTime.toISOString(),
      end_time: endTime.toISOString()
    }

    const response = await fetch(`${import.meta.env.VITE_API_URL}/session-requests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(payload)
    })

    if (!response.ok) throw new Error('Failed to book session.')
    
    bookingFeedback.value = 'Session requested successfully!'
    await fetchMyRequests() // Refresh the list
    
    setTimeout(() => {
      isBookingModalOpen.value = false
      bookingFeedback.value = ''
      bookingForm.value = { therapist_id: '', datetime: '' } // Reset form
    }, 1500)
  } catch (error) {
    bookingFeedback.value = error.message
  } finally {
    isSubmittingBooking.value = false
  }
}

// Helper function to format dates
const formatDateTime = (dateString) => {
  const options = { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }
  return new Date(dateString).toLocaleDateString('en-US', options)
}

// Load everything on mount
onMounted(async () => {
  await Promise.all([fetchIntakeData(), fetchMyRequests(), fetchTherapists()])
  isLoading.value = false
})
</script>

<template>
  <div class="space-y-6 font-sans">
    
    <div class="bg-white p-6 rounded-2xl shadow-sm border border-blue-100 flex flex-col sm:flex-row items-center sm:justify-between gap-4">
      <div class="text-center sm:text-left">
        <h1 class="text-2xl font-bold text-gray-900">Hello, {{ authStore.user?.name || 'Client' }}</h1>
        <p class="text-blue-600 font-medium tracking-wide text-sm mt-1 uppercase">Client Portal</p>
      </div>
      <button @click="handleLogout" class="w-full sm:w-auto px-6 py-2.5 bg-red-50 text-red-600 hover:bg-red-100 font-semibold rounded-xl transition-colors">
        Sign Out
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col h-full">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-gray-800">My Sessions</h2>
          <button @click="isBookingModalOpen = true" class="bg-blue-50 text-blue-700 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-100 transition-colors border border-blue-100">
            + Book Session
          </button>
        </div>

        <div v-if="isLoading" class="flex justify-center py-8">
          <svg class="animate-spin h-6 w-6 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        </div>
        
        <div v-else-if="myRequests.length === 0" class="text-gray-500 py-10 bg-gray-50 rounded-xl text-center border border-dashed border-gray-200 flex-1 flex flex-col justify-center items-center">
          <span class="text-3xl mb-2">📅</span>
          <p>You have no upcoming sessions or pending requests.</p>
        </div>
        
        <div v-else class="space-y-3 overflow-y-auto pr-2">
          
          <div v-for="session in upcomingSessions" :key="'up-'+session.session_request_id" class="p-4 border border-green-100 bg-white shadow-sm rounded-xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:border-green-300 transition-colors">
            <div>
              <p class="font-bold text-gray-900">{{ getTherapistName(session.therapist_id) }}</p>
              <p class="text-sm text-gray-600 mt-1">🕒 {{ formatDateTime(session.start_time) }}</p>
            </div>
            <div class="flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto">
              <span class="text-xs font-bold text-green-700 bg-green-100 px-3 py-1 rounded-full whitespace-nowrap">Confirmed</span>
              <router-link :to="`/room/${session.session_request_id}`" class="bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-xl text-sm font-semibold transition-colors w-full sm:w-auto text-center flex items-center justify-center gap-2 shadow-sm">
                <span>📹</span> Join Call
              </router-link>
            </div>
          </div>

          <div v-for="req in pendingRequests" :key="'req-'+req.session_request_id" class="p-4 border border-yellow-100 bg-yellow-50/40 rounded-xl flex justify-between items-center hover:border-yellow-200 transition-colors">
            <div>
              <p class="font-bold text-gray-900">{{ getTherapistName(req.therapist_id) }}</p>
              <p class="text-sm text-gray-600 mt-1">📅 {{ formatDateTime(req.start_time) }}</p>
            </div>
            <span class="text-xs font-bold text-yellow-700 bg-yellow-100 border border-yellow-200 px-3 py-1 rounded-full">Pending</span>
          </div>

        </div>
      </div>
      
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col h-full">
        <div>
          <h2 class="text-lg font-bold text-gray-800 mb-3">My Intake Form</h2>
          <div class="bg-blue-50 p-4 rounded-xl border border-blue-100 mb-4">
            <p class="text-blue-800 text-sm leading-relaxed">
              Keeping your therapy goals updated ensures your therapist can provide the best possible support during your sessions.
            </p>
          </div>
        </div>
        <div class="mt-auto pt-4 border-t border-gray-50">
          <button @click="isIntakeModalOpen = true" class="w-full text-center bg-gray-50 hover:bg-gray-100 text-gray-800 font-semibold py-3 rounded-xl transition-colors border border-gray-200 flex items-center justify-center gap-2">
            Update Intake Details <span>&rarr;</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="isBookingModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/60 backdrop-blur-sm p-4 transition-opacity">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden flex flex-col transform transition-all">
        <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
          <h3 class="text-xl font-bold text-gray-900">Request a Session</h3>
          <button @click="isBookingModalOpen = false" class="text-gray-400 hover:text-red-500 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        <form @submit.prevent="submitBooking" class="p-6">
          <div class="space-y-5">
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-2">Select Therapist</label>
              <select v-model="bookingForm.therapist_id" required class="w-full p-3.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white shadow-sm transition-shadow">
                <option value="" disabled>Choose a therapist...</option>
                <option v-for="t in therapists" :key="t.therapist_id" :value="t.therapist_id">
                  {{ t.therapist_name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-bold text-gray-700 mb-2">Date & Time</label>
              <input type="datetime-local" v-model="bookingForm.datetime" :min="minDateTime" required class="w-full p-3.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white shadow-sm transition-shadow">
              <p class="text-xs text-gray-500 mt-2 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                Sessions are scheduled for 60 minutes.
              </p>
            </div>
          </div>

          <div v-if="bookingFeedback" :class="bookingFeedback.includes('successfully') ? 'text-green-700 bg-green-50 border-green-200' : 'text-red-700 bg-red-50 border-red-200'" class="mt-5 p-3.5 rounded-xl text-sm font-semibold text-center border">
            {{ bookingFeedback }}
          </div>

          <div class="mt-8 flex justify-end gap-3 pt-4 border-t border-gray-50">
            <button type="button" @click="isBookingModalOpen = false" class="px-5 py-2.5 text-gray-600 font-bold hover:bg-gray-100 rounded-xl transition-colors">Cancel</button>
            <button type="submit" :disabled="isSubmittingBooking || !bookingForm.therapist_id || !bookingForm.datetime" class="px-6 py-2.5 bg-blue-600 text-white font-bold hover:bg-blue-700 rounded-xl disabled:opacity-50 transition-colors shadow-sm">
              <span v-if="isSubmittingBooking">Sending...</span>
              <span v-else>Send Request</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="isIntakeModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/60 backdrop-blur-sm p-4 transition-opacity">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-xl overflow-hidden flex flex-col max-h-[90vh]">
        <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
          <h3 class="text-xl font-bold text-gray-900">Update Intake Details</h3>
          <button @click="isIntakeModalOpen = false" class="text-gray-400 hover:text-red-500 transition-colors">
             <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        <div class="p-6 overflow-y-auto bg-gray-50/30">
          <p class="text-sm text-gray-600 mb-6 bg-blue-50 p-4 rounded-xl border border-blue-100">
            Please answer these questions honestly. Your responses are encrypted and only visible to the therapist you connect with.
          </p>
          
          <div v-for="(item, index) in formQuestions" :key="index" class="mb-6 bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <label class="block text-sm font-bold text-gray-800 mb-3">{{ item.question_text }}</label>
            <textarea v-model="item.response" rows="3" class="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none transition-shadow" placeholder="Your response..."></textarea>
          </div>

          <div v-if="intakeFeedback" :class="intakeFeedback.includes('successfully') ? 'text-green-700 bg-green-50 border-green-200' : 'text-red-700 bg-red-50 border-red-200'" class="mt-4 p-4 rounded-xl text-sm font-semibold text-center border">
            {{ intakeFeedback }}
          </div>
        </div>

        <div class="px-6 py-5 border-t border-gray-100 flex justify-end gap-3 bg-white">
          <button @click="isIntakeModalOpen = false" class="px-5 py-2.5 text-gray-600 font-bold hover:bg-gray-100 rounded-xl transition-colors">Cancel</button>
          <button @click="submitIntakeForm" :disabled="isSubmittingIntake" class="px-6 py-2.5 bg-blue-600 text-white font-bold hover:bg-blue-700 rounded-xl disabled:opacity-50 transition-colors shadow-sm">
            <span v-if="isSubmittingIntake">Saving...</span>
            <span v-else>Save Changes</span>
          </button>
        </div>
      </div>
    </div>

  </div>
</template>