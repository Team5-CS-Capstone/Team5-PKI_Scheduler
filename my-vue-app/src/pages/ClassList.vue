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
        <div v-if="filteredCourses && filteredCourses.length > 0" class="flex grid grid-cols-8 gap-4 mt-24 m-8">
            <router-link
            v-for="course in filteredCourses"
            :key="course.id"
            :to="'/class/' + course.id"
            :class=" course.currentEnrollment > course.maxEnrollment ? 'bg-red-300 rounded-lg flex text-black items-center justify-center hover:bg-red-400 h-40 w-full p-6 border-black border-2' : 'bg-blue-300 rounded-lg flex text-black items-center justify-center hover:bg-blue-400 h-40 w-full p-6 border-black border-2'"
            style="color: black;
            font-weight: bold;
            font-size: 1.3rem;"
            >
            {{ course.courseName }} - Section ({{ course.section }}) 
            </router-link>
        </div>

        <div v-else>
            <p class="mt-20 py-2 font-semibold bg-red-300  ">No classes found.</p>
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
// filtered courses holds the courses that match the search
// if there happens to be a search
const filteredCourses = ref([])

/**
 * @function searchCourses
 * @description 
 *  If the value of search is populated (from the UI by user) then
 *  set filteredCourses to whatever classes from all courses (from db)
 *  include whatever is in the search string (lowercased). If the search is
 *  empty filteredCourses contains all courses, otherwise it contains
 *  filtered courses.  
 * @returns {void}
 *  Returns nothing but it updates filteredCourses which then updates the 
 *  UI accordingly
 */
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
/**
 * @function fetchCourses
 * @description 
 *  Fetches a list of all available courses from the backend and updates 
 *  the reactive `courses` variable. Also triggers the search filter by calling 
 *  `searchCourses()`. If an error occurs, `courses` and `filteredCourses` are 
 *  set to `null` and the UI displays this accordingly.
 */
const fetchCourses = async () => {
    try {
        const response = await axios.get('http://127.0.0.1:5000/classes');
        courses.value = response.data;
        searchCourses();
    } catch (error) {
        courses.value = null;
        filteredCourses.value = null;
    }
}

// After the component renders, fetch courses and 
// update the UI accordingly
onMounted(() => {
    fetchCourses();
});
</script>