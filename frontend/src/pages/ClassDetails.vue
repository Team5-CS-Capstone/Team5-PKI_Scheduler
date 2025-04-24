<template>
    <!-- Pop-up modal for classroom reassignment options -->
    <div v-if="reassignmentModalVisible && !loadingReassignments"
        class="fixed inset-0 flex items-center justify-center bg-black/40">
        <div class="bg-white p-4 h- w-8/12 rounded shadow">
            <div class="flex flex-col justify-between h-full items-center bg-white">
                <div class="w-full p-4 space-y-4 bg-white border rounded">
                    <p v-if="noReassignments" class="text-2xl text-red-600">No available class swaps.</p>
                    <div v-else>
                        <p class="text-2xl text-gray-600 font-semibold pb-4">Select a room to reassign the class:</p>
                        <!-- Column Headers -->
                        <div class="grid grid-cols-[3fr_3fr_3fr_1fr] p-4 bg-gray-400 rounded-t-4xl w-full">
                            <span class="px-2 font-bold text-sm text-gray-700">Course Number</span>
                            <span class="font-bold text-sm text-gray-700">Room and Meeting Pattern</span>
                            <span class="font-bold text-sm text-gray-700">Enrollment / Max Enrollment</span>
                            <span class="font-bold text-sm text-gray-700"></span>
                        </div>
                        <ul
                            class="grid grid-cols-[3fr_3fr_3fr_1fr] gap-y-2 border-2 border-gray-300 rounded-lg max-h-96 overflow-y-scroll">
                            <li v-for="(options, index) in possibleReassignments" :key="options.room" class="contents">
                                <span class="p-4 font-medium text-sm text-gray-700">Option {{ index + 1 }} - {{
                                    options.course_number }}</span>
                                <span class="p-4 font-medium text-sm text-gray-700">{{ options.room }} {{
                                    options.meeting_pattern }}</span>
                                <span class="p-4 font-medium text-sm text-gray-700 truncate">Enrollment: {{
                                    options.enrollment }} / {{ options.max_enrollment }}</span>
                                <span class="p-4 flex justify-end">
                                    <button @click="selectReassignment(options)"
                                        class="bg-blue-600 text-white px-2 py-1 text-sm font-semibold rounded hover:bg-blue-500">Select</button>
                                </span>
                            </li>
                        </ul>

                    </div>

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
            <p class="text-2xl">
                <strong>Enrollment:</strong>
                <!-- Dropdown for updating class enrollment numbers instead of using increments -->
                <select v-if="classData" v-model.number="classData.currentEnrollment" @change="updateEnrollment($event.target.value)"
                    class="mx-1 text-black rounded bg-gray-100 border px-1 cursor-pointer">
                    <!-- loops 1 … maxEnrollment -->
                    <option v-for="i in classData.maxEnrollment + 10" :key="i" :value="i - 1">{{ i - 1}}</option>
                </select>
                / {{ classData.maxEnrollment }}
            </p>

            <p v-if="professors" class="text-2xl"><strong>Professors: </strong>
                <span v-for="(professor, index) in professors" :key="professor.id" class="text-2xl">
                    {{ professor.first_name }} {{ professor.last_name }}<span v-if="index < professors.length - 1">,
                    </span>
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
                    class="font-semibold bg-red-300 py-3 w-60 rounded-xl hover:bg-red-500 cursor-pointer border-2">
                    Remove Student
                </button>
            </div>

            <div v-if="classData" class="flex flex-col hover:bg-yellow-500 w-full bg-yellow-200  border-2 border-yellow-700 cursor-pointer" @click="fetchPossibleReassignments(classData.id)">
                <span 
                    class="flex items-center justify-center font-semibold w-full h-10 rounded-xl text-center">
                    Possible Manual Reassignments
                </span>
                <span class="text-black text-xs text-wrap text-center text-align-center p-2"> 
                    (Keep in mind that this only considers simple swaps and doesn't find BEST swaps.)
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
            /**
             * The visibility state of the reassignment modal.
             * @vue-data {boolean}
             */
            reassignmentModalVisible: false,
            /**
             * The list of possible reassignments for the class.
             * @vue-data {string[]}
             */
            possibleReassignments: null,
            noReassignments: false,
            loadingReassignments: false,
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
        async fetchPossibleReassignments(class_id) {
            try {
                this.loadingReassignments = true;
                const response = await axios.get(`http://127.0.0.1:5000/class/${class_id}/possible-reassignments`);
                this.possibleReassignments = response.data;
                this.ToggleReassignmentModal();
                if (this.possibleReassignments.length === 0) {
                    this.noReassignments = true;
                } else {
                    this.noReassignments = false;
                }
            } catch (error) {
                console.error("Failed to load reassignments:", error);
            } finally {
                this.loadingReassignments = false;
            }
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
        },

        /**
         * Sends an action to swap the current class with the selected class.
         * If a successful swap happens, it updates the current class info and closes the swap selection box.
         * 
         * @vue-method
         * @async
         * @param room The selected room to swap with
         */
        async selectReassignment(swap_id) {
            try {
                // Swap class information
                await axios.post(`http://127.0.0.1:5000/class/${this.$route.params.id}/swap/${swap_id.id}`);
                console.log('Swapped classes', this.$route.params.id, ' and ', swap_id.id, ' successfully');
                alert('Successfully swapped classes!');

                // Update current class
                this.fetchClassDetails();

                // Close the swap selection box
                this.ToggleReassignmentModal();
            } catch (error) {
                console.error("Failed to switch classes:", error);
                alert('Failed to swap classes.');
            }
        },
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