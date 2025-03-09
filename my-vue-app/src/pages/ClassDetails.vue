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
            <button class="font-semibold bg-green-300 px-4 py-3 w-60 rounded-xl">Add Student</button>
            <button class="font-semibold bg-red-300 px-4 py-3 w-60 rounded-xl">Remove Student</button>
        </div>
    </div>

</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";

const classData = ref(null);
const route = useRoute();

const fetchClassDetails = async () => {
    try {
        const response = await axios.get(`http://127.0.0.1:5000/class/${route.params.id}`);
        classData.value = response.data;
    } catch (error) {
        classData.value = null;
    }
};

const addStudent = async () => {
    // Add student to class
    
};

const removeStudent = async () => {
    // Remove student from class
};

// Load data when component mounts
onMounted(() => {
    fetchClassDetails();
});

</script>
