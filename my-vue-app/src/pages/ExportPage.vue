<!-- 
somehow need to obtain class ID from route and using that 
information we can make an API call with that ID and display 
and update the proper information 
-->

<template>
    <div class="flex justify-center">
        <img class="h-96 mt-12 text-2xl font-bold" src="../assets/uno-logo.png"></img>
    </div>
    <div class="mt-22 text-2xl font-bold w-full flex justify-center">
        <button class="w-96 rounded-xl bg-sky-500 px-12 py-4 hover:bg-green-500 cursor-pointer" type="button"
        @click="exportToFile">Export CSV</button>
    </div>
</template>

<script setup>
import axios from 'axios';
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const classData = ref(null);
const route = useRoute();

const exportToFile = async () => {
    try {
        const response = await axios.get(`http://127.0.0.1:5000/export`);
    } catch (error) {
        console.error('Could not export data.', error);
    }
}
</script>