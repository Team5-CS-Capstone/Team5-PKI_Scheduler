<script setup>
import { ref } from 'vue'

defineProps({
  msg: String,
})

const count = ref(0)
</script>

<template>
  <h1>{{ msg }}</h1>
  <div>
    <img class="h-96" src="../assets/uno-logo.png"></img>
  </div>
  <div class="mt-12 text-2xl font-bold w-full">
    <button class="w-96" type="button" @click="">Import</button>
  </div>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
</style>
