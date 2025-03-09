<template>
    <div class="overflow-scroll h-screen">
        <!-- Header with title that contains a search bar -->
        <div class="flex items-center justify-between bg-red-700 py-3 h-20 px-8 top-0 fixed w-screen">
            <span class="font-semibold text-xl">PKI Class Search</span>
            <input 
            type="text" 
            placeholder="Search by course name or title..." 
            class="mr-32 px-3 py-2 rounded-lg border border-gray-300 w-96 text-white" 
            v-model="search"
            @keyup.enter="searchCourses"
            />
        </div>
        <!-- Grid for clickable classes -->
        <div v-if="filteredCourses.length > 0" class="flex grid grid-cols-8 gap-4 mt-24 m-8">
            <router-link
            v-for="course in filteredCourses"
            :key="course.id"
            :to="'/class/' + course.id"
            class="bg-red-300 rounded-lg flex text-black items-center justify-center hover:bg-red-400 h-40 w-full p-6 border-black border-2"
            style="color: black;
            font-weight: bold;
            font-size: 1.3rem;"
            >
            {{ course.courseName }} - Section ({{ course.section }}) 
            </router-link>
        </div>

        <div v-else>
            <p class="text-red-600">No classes found.</p>
        </div>
    </div>

</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

// make a reactive variable for courses 
// currently will just mimic data 
// that we are going to get from the database
const courses = ref([])
// another reactive variable is needed
// for the search text to update
const search = ref("")
// filterd courses holds the courses that match the search
// if there happens to be a search
const filteredCourses = ref([])

const searchCourses = async () => {
    if (search.value === "") {
        filteredCourses.value = courses.value;
    } else {
        filteredCourses.value = courses.value.filter(course => {
            return course.courseName.toLowerCase().includes(search.value.toLowerCase()) ||
            course.courseTitle.toLowerCase().includes(search.value.toLowerCase());
        });
    }
}

const fetchCourses = async () => {
    try {
        const response = await axios.get('http://127.0.0.1:5000/classes');
        courses.value = response.data;
        searchCourses();
    } catch (error) {
        courses.value = null;
    }
}

onMounted(() => {
    fetchCourses();
});
</script>