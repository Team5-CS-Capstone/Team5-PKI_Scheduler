<template>
    <span class=" text-black text-2xl font-semibold mb-4 text-start">CSCI {}</span>
    <div class="flex flex-col space-y-4 text-black text-start h-full">
        <!-- Display class details when data is available -->
        <div v-if="classData">
            <h2 class="text-2xl font-semibold">{{ classData.name }}</h2>
            <p><strong>Term:</strong> {{ classData.term }}</p>
            <p><strong>Section:</strong> {{ classData.section }}</p>
            <p><strong>Room:</strong> {{ classData.room }}</p>
            <p><strong>Time:</strong> {{ classData.time }}</p>
            <p><strong>Enrollment:</strong> {{ classData.currentEnrollment }} / {{ classData.maxEnrollment }}</p>
        </div>

        <!-- Error state -->
        <div v-else>
            <p class="text-red-600">Class not found.</p>
        </div>
    </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";

const classData = ref(null);
const route = useRoute();

const fetchClassDetails = async () => {
    try {
        const response = await axios.get(`http://127.0.0.1:5000/class/${route.params.id}`)
        classData.value = response.data;
    } catch (error) {
        console.error("Error fetching class details:", error);
        classData.value = null;
    }
};

// Load data when component mounts
onMounted(fetchClassDetails);
</script>
