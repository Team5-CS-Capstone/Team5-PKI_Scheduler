<script setup>
import HomePage from './pages/HomePage.vue'
import Sidebar from './components/Sidebar.vue'
</script>

<template>
  <div class="flex h-screen w-screen bg-gray-300">
    <!-- Sidebar -->
    <Sidebar class="h-full bg-gray-400" />

    <!-- Main Content Area -->
    <div class="p-6 flex flex-col justify-center w-full">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
