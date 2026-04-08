<script setup>
// We don't need any complex fetching logic here yet, 
// as this is just the static landing page to welcome users!
</script>

<template>
  <div class="flex flex-col min-h-screen bg-white">
    
    <section class="bg-blue-50 py-12 px-6 sm:px-12 lg:px-24 flex-grow flex flex-col justify-center text-center md:text-left md:flex-row md:items-center gap-10">
      
      <div class="md:w-1/2 space-y-6">
        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-blue-900 leading-tight">
          Find the Right Therapist for Your Journey.
        </h1>
        <p class="text-lg text-gray-600">
          Umoja Therapy connects you with licensed professionals tailored to your unique needs. Start your healing journey today in a safe, secure space.
        </p>
        
        <div class="flex flex-col sm:flex-row gap-4 pt-4">
          <router-link to="/login" class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-xl text-center transition-colors shadow-sm">
            Find a Therapist
          </router-link>
          <router-link to="/login" class="bg-white border-2 border-blue-600 text-blue-600 hover:bg-blue-50 font-semibold py-4 px-6 rounded-xl text-center transition-colors shadow-sm">
            I am a Therapist
          </router-link>
        </div>
      </div>

    </section>

    <section class="py-16 px-6 sm:px-12 lg:px-24 bg-white">
      <h2 class="text-3xl font-bold text-center text-blue-900 mb-12">How Umoja Works</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="bg-gray-50 p-8 rounded-2xl text-center border border-gray-100 hover:shadow-md transition-shadow">
          <div class="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl">📝</div>
          <h3 class="text-xl font-semibold text-gray-800 mb-3">1. Tell Us About You</h3>
          <p class="text-gray-600">Complete a secure intake form so we can understand your specific needs, goals, and preferences.</p>
        </div>

        <div class="bg-gray-50 p-8 rounded-2xl text-center border border-gray-100 hover:shadow-md transition-shadow">
          <div class="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl">🤝</div>
          <h3 class="text-xl font-semibold text-gray-800 mb-3">2. Get Matched</h3>
          <p class="text-gray-600">Our matching service connects you with the ideal therapist whose expertise aligns perfectly with your journey.</p>
        </div>

        <div class="bg-gray-50 p-8 rounded-2xl text-center border border-gray-100 hover:shadow-md transition-shadow">
          <div class="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl">💬</div>
          <h3 class="text-xl font-semibold text-gray-800 mb-3">3. Start Healing</h3>
          <p class="text-gray-600">Request sessions, manage your schedule, and begin your therapy in a safe environment.</p>
        </div>
      </div>
    </section>

  </div>
</template>