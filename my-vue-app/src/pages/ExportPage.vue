<script setup>
import { ref } from 'vue'
</script>

<template>
  <div class="container">
    <img class="uno-logo" src="../assets/uno-logo.png"></img>
  </div>
  <div class="mt-22 text-2xl font-bold w-full flex justify-center">
    <button class="w-96 rounded-xl bg-sky-500 px-12 py-4 hover:bg-green-500 cursor-pointer" type="button" @click="">Export CSV</button>
  </div>
</template>

<style scoped>
.uno-logo {
  position: absolute;
  top: 10px;
  left: 120px;
  width: 150px;
  height: auto;
}
</style>
