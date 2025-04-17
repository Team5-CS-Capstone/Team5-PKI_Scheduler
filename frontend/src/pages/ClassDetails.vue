<template>
    <!-- Pop-up modal for classroom reassignment options -->
    <div v-if="reassignmentModalVisible" class="fixed inset-0 flex items-center justify-center bg-black/40">
        <div class="bg-white p-4 h- w-4/12 rounded shadow">
            <div class="flex flex-col justify-between h-full items-center bg-white">
                <div v-if="possibleReassignments.length" class="w-full p-4 space-y-4 bg-white border rounded">
                    <h3 class="text-2xl font-bold mb-2 text-gray-800">Available Reassignments</h3>
                    <ul class="space-y-2 border-2 border-gray-300 rounded-lg p-4 max-h-96 overflow-y-scroll">
                        <li v-for="room in possibleReassignments" :key="room"
                            class="flex justify-between items-center p-4 bg-white rounded hover:bg-gray-200 transition-colors">
                            <span class="font-medium text-lg text-gray-700">
                                {{ room }}
                            </span>
                            <button @click="selectReassignment(room)"
                                class="bg-blue-600 text-white px-4 py-1 text-sm font-semibold rounded hover:bg-blue-500 focus:outline-none transition-colors">
                                Select
                            </button>
                        </li>
                    </ul>
                </div>


                <button @click="ToggleReassignmentModal"
                    class="mt-4 w-42 bg-red-500 text-white py-2 px-4 rounded cursor-pointer hover:bg-red-400">Close</button>
            </div>
        </div>
    </div>

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
            <p v-if="professors" class="text-2xl"><strong>Professors: </strong>
                <span v-for="professor in professors" :key="professor.id" class="text-2xl"> 
                    {{ professor.first_name }} {{ professor.last_name }} 
                </span>
            </p>
        </div>

        <!-- Error state -->
        <div v-else>
            <p class="text-red-600">Class not found.</p>
        </div>

        <div v-if="classData" class="flex flex-col justify-between w-96 space-y-4 w-50">
            <div class="flex space-x-4">
                <button @click="updateEnrollment('add')"
                    class="font-semibold bg-green-300 py-3 w-60 rounded-xl hover:bg-green-500 cursor-pointer border-2">Add
                    Student</button>
                <button @click="updateEnrollment('remove')"
                    class="font-semibold bg-red-300 py-3 w-60 rounded-xl hover:bg-red-500 cursor-pointer border-2">Remove
                    Student</button>
            </div>

            <div v-if="classData && classData.currentEnrollment > classData.maxEnrollment" class="flex w-full">
                <span @click="ToggleReassignmentModal"
                    class="hover:bg-yellow-500 flex items-center justify-center font-semibold w-full h-10  bg-yellow-200 rounded-xl text-center border-2 border-yellow-700 cursor-pointer">
                    Check Reassignment Options
                </span>
            </div>
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
            reassignmentModalVisible: false,
            /**
             * The list of possible reassignments for the class.
             * @vue-data {string[]}
             */
            possibleReassignments: ['class 1', 'class 2', 'class 3', 'class 4', 'class 5', 'class 6', 'class 7'],
            /**
             * The list of professors associated with the class.
             * @vue-data {Object[]}
             */
            professors: null,
        };
    },
    methods: {
        /**
         * Toggles the visibility of the reassignment modal.
         * This method is a placeholder and should be implemented as needed.
         *
         * @vue-method
         */
        ToggleReassignmentModal() {
            // Placeholder for modal toggle logic
            this.reassignmentModalVisible = !this.reassignmentModalVisible;
        },
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
        /**
         * Fetches the list of professors associated with the class.
         * Updates the `professors` reactive property with the fetched data.
         *
         * @vue-method
         * @async
         * @returns {Promise<void>} Resolves after setting the professors data.
         */
        async getProfessors() {
            try {
                const response = await axios.get(`http://127.0.0.1:5000/class/${this.$route.params.id}/professors`);
                this.professors = response.data;
            } catch (error) {
                console.error("Failed to load professors:", error);                
            }
        }
    },
    /**
     * Lifecycle hook: called after the component is mounted.
     * Triggers the initial fetch of class details.
     */
    mounted() {
        this.fetchClassDetails();
        this.getProfessors();
    },
};
</script>