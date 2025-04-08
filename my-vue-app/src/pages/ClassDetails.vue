<template>
    <span class=" text-black text-2xl font-semibold mb-4 text-start"></span>
    <div class="flex flex-col space-y-4 text-black text-start h-full pl-6">
        <!-- Display class details when data is available -->
        <div v-if="classData">
            <p class="text-5xl font-bold mb-10" style="color: red;"> {{ classData.courseName }}</p>
            <h2 class="text-3xl">{{ classData.name }}</h2>
            <p class="text-2xl"><strong>Term:</strong> {{ classData.term }}</p>
            <p class="text-2xl"><strong>Section:</strong> {{ classData.section }}</p>
            <p class="text-2xl"><strong>Room:</strong> {{ classData.room }}</p>
            <p class="text-2xl"><strong>Time:</strong> {{ classData.time }}</p>
            <p class="text-2xl"><strong>Enrollment:</strong> {{ classData.currentEnrollment }} / {{
                classData.maxEnrollment }}</p>
        </div>

        <!-- Error state -->
        <div v-else>
            <p class="text-red-600">Class not found.</p>
        </div>

        <div v-if="classData" class="flex justify-between w-96 space-x-4">
            <button @click="updateEnrollment('add')"
                class="font-semibold bg-green-300 px-4 py-3 w-60 rounded-xl hover:bg-green-500 cursor-pointer border-2">Add
                Student</button>
            <button @click="updateEnrollment('remove')"
                class="font-semibold bg-red-300 px-4 py-3 w-60 rounded-xl hover:bg-red-500 cursor-pointer border-2">Remove
                Student</button>
        </div>
    </div>

</template>

<script>
import axios from "axios";

/**
 * ClassDetails component displays details for a specific class and allows enrollment updates.
 */
export default {
    name: "ClassDetails",
    data() {
        return {
            /**
             * The class data fetched from the backend.
             * @vue-data {Object|null}
             */
            classData: null,
        };
    },
    methods: {
        /**
         * Fetches details for a specific class using the ID from the current route.
         * Updates the `classData` reactive property with the fetched data or null if there's an error.
         *
         * @vue-method
         * @async
         * @returns {Promise<void>} Resolves after setting the class data.
         */
        async fetchClassDetails() {
            try {
                const response = await axios.get(`http://127.0.0.1:5000/class/${this.$route.params.id}`);
                this.classData = response.data;
            } catch (error) {
                this.classData = null;
            }
        },
        /**
         * Sends an action to update the enrollment count for the class.
         * Supports incrementing or decrementing based on the "add" or "remove" action.
         * Refreshes the class data after updating.
         *
         * @vue-method
         * @async
         * @param {"add"|"remove"} action - The type of enrollment update.
         * @returns {Promise<void>} Resolves after the update and refetch.
         */
        async updateEnrollment(action) {
            try {
                await axios.post(`http://127.0.0.1:5000/class/${this.$route.params.id}/update-enrollment`, { action });
                // Fetch updated class details
                this.fetchClassDetails();
            } catch (error) {
                console.error(error);
            }
        },
    },
    /**
     * Lifecycle hook: called after the component is mounted.
     * Triggers the initial fetch of class details.
     */
    mounted() {
        this.fetchClassDetails();
    },
};
</script>