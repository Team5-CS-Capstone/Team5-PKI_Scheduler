<template>
    <div class="overflow-scroll h-screen">
        <!-- Header with title that contains a search bar -->
        <div class="flex items-center justify-between bg-red-700 py-3 h-20 px-8 top-0 fixed w-screen">
            <span class="font-semibold text-xl">PKI Class Search</span>
            <input type="text" placeholder="Search for class..." class="mr-32 px-3 py-2 rounded-lg border border-gray-300" />
        </div>
        <!-- Grid for clickable classes -->
        <div class="flex grid grid-cols-3 gap-4 h-3/4 mt-24 m-8 text-white">
            <router-link
            v-for="course in courses"
            :key="course.id"
            :to="'/class/' + course.id"
            class="bg-red-300 rounded-lg flex items-center justify-center hover:bg-red-400"
            >
            {{ course.name }}
            </router-link>
        </div>
    </div>

</template>

<script setup>
import { ref, computed } from "vue";

// make a reactive variable for courses 
// currently will just mimic data 
// that we are going to get from the database
const courses = ref([
    { id: 2400, name: "CSCI 2400" },
    { id: 2500, name: "CSCI 2500" },
    { id: 2600, name: "CSCI 2600" },
    { id: 2400, name: "CSCI 2400" },
    { id: 2500, name: "CSCI 2500" },
    { id: 2600, name: "CSCI 2600" },
    { id: 2400, name: "CSCI 2400" },
    { id: 2500, name: "CSCI 2500" },
    { id: 2600, name: "CSCI 2600" },
])

// another reactive variable is needed
// for the search text to update
const search = ref("")
</script>