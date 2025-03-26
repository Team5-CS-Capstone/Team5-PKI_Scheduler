<template>
    <span class=" text-black text-2xl font-semibold mb-4 text-start"></span>
    <div class="flex flex-col space-y-4 text-black text-start h-full pl-6">
        <!-- Display class details when data is available -->
        <div v-if="classData">
            <p class="text-5xl font-bold mb-10"
            style="color: red;"> {{ classData.courseName }}</p>
            <h2 class="text-3xl">{{ classData.name }}</h2>
            <p class="text-2xl"><strong>Term:</strong> {{ classData.term }}</p>
            <p class="text-2xl"><strong>Section:</strong> {{ classData.section }}</p>
            <p class="text-2xl"><strong>Room:</strong> {{ classData.room }}</p>
            <p class="text-2xl"><strong>Time:</strong> {{ classData.time }}</p>
            <p class="text-2xl"><strong>Enrollment:</strong> {{ classData.currentEnrollment }} / {{ classData.maxEnrollment }}</p>
        </div>

        <!-- Error state -->
        <div v-else>
            <p class="text-red-600">Class not found.</p>
        </div>

        <div class="flex justify-between w-96 space-x-4">
            <button @click="updateEnrollment('add')" class="font-semibold bg-green-300 px-4 py-3 w-60 rounded-xl">Add Student</button>
            <button @click="updateEnrollment('remove')" class="font-semibold bg-red-300 px-4 py-3 w-60 rounded-xl">Remove Student</button>
        </div>
    </div>

</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";

const classData = ref(null);
const route = useRoute();

/**
 * @function fetchClassDetails
 * @description 
 *  Accesses a specific API endpoint using the class ID from the URL,
 *  retrieves all data for that class from the database, and stores it
 *  in the `classData` reactive variable.
 */
const fetchClassDetails = async () => {
    try {
        const response = await axios.get(`http://127.0.0.1:5000/class/${route.params.id}`);
        classData.value = response.data;
    } catch (error) {
        classData.value = null;
    }
};

/**
 * @function updateEnrollment
 * @description 
 *  Uses the provided `action` (e.g. "add" or "remove") to update
 *  the enrollment number of a specific class (just how many students
 *  are enrolled, since we have no access to live data..)
 * @param {string} action 
 *  The action type for enrollment, either "add" or "remove".
 * @returns {void}
 *  A promise that resolves once the enrollment is updated and
 *  `fetchClassDetails` is re-called to refresh data.
 */
const updateEnrollment = async (action) => {
    try {
        const response = await axios.post(`http://127.0.0.1:5000/class/${route.params.id}/update-enrollment`, { action: action });
        // Fetch updated class details
        fetchClassDetails();
    } catch (error) {
        console.error(error);
    }
};

// Load data when component mounts
onMounted(() => {
    fetchClassDetails();
});

</script>
