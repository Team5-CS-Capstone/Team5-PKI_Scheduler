<script setup>
import { ref } from 'vue'
</script>

<template>
  <div class="flex justify-center">
    <img class="h-96 mt-12 text-2xl font-bold" src="../assets/uno-logo.png"></img>
  </div>
  <div class="mt-22 text-2xl font-bold w-full">
    <button class="w-96 rounded-xl bg-sky-500 px-12 py-4 hover:bg-green-500 cursor-pointer" type="button" @click="">Import CSV</button>
  </div>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
</style>
