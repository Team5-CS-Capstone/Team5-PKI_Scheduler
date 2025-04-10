<template>
    <div class="overflow-scroll h-screen">
        <!-- Header with title that contains a search bar -->
        <div class="flex items-center justify-between bg-red-700 py-3 h-20 px-8 top-0 fixed w-screen">
            <span class="font-semibold text-xl">PKI Class Search</span>
            <input type="text" placeholder="Search by course name or title..."
                class="mr-32 px-3 py-2 rounded-lg border border-gray-300 w-96 text-white" v-model="search"
                @keyup.enter="searchCourses" />
        </div>
        <!-- Grid for clickable classes -->
        <div v-if="filteredCourses && filteredCourses.length > 0" class="flex grid grid-cols-8 gap-4 mt-24 m-8">
            <router-link v-for="course in filteredCourses" :key="course.id" :to="'/class/' + course.id"
                class="bg-red-300 rounded-lg flex text-black items-center justify-center hover:bg-red-400 h-40 w-full p-6 border-black border-2"
                style="color: black;
            font-weight: bold;
            font-size: 1.0rem;">
                {{ course.courseName }} - Section ({{ course.section }})
            </router-link>
        </div>

        <div v-else>
            <p class="mt-20 py-2 font-semibold bg-red-300  ">No classes found.</p>
        </div>
    </div>

</template>

<script>
import axios from "axios";

/**
 * This component displays a list of courses fetched from the server
 * and filters them based on user input. 
 */
export default {
    name: "ClassList",

    /**
     * Vue data properties.
     * @vue-data
     * @returns {Object} The component data object.
     */
    data() {
        return {
            /**
             * A list of all courses fetched from the server.
             * @vue-data {Object[]}
             */
            courses: [],

            /**
             * The current search query string.
             * @vue-data {string}
             */
            search: "",

            /**
             * The filtered list of courses that match the user query.
             * @vue-data {Object[]}
             */
            filteredCourses: [],
        };
    },

    /**
     * Vue component methods.
     */
    methods: {
        /**
         * Filters the list of courses based on user search input.
         * Updates the `filteredCourses` data property.
         *
         * @vue-method
         * @returns {void}
         */
        async searchCourses() {
            if (this.search === "") {
                this.filteredCourses = this.courses;
            } else {
                this.filteredCourses = this.courses.filter(course => {
                    return (
                        course.courseName
                            .toLowerCase()
                            .includes(this.search.toLowerCase()) ||
                        course.courseTitle
                            .toLowerCase()
                            .includes(this.search.toLowerCase())
                    );
                });
            }
        },

        /**
         * Fetches all available courses from the backend and stores them in the `courses` data property.
         * Then triggers filtering to update `filteredCourses`.
         *
         * @vue-method
         * @async
         * @returns {Promise<void>} Updates `courses` and `filteredCourses`.
         */
        async fetchCourses() {
            try {
                const response = await axios.get("http://127.0.0.1:5000/classes");
                this.courses = response.data;
                this.searchCourses();
            } catch (error) {
                this.courses = null;
                this.filteredCourses = null;
            }
        },
    },

    /**
     * Called after the component is mounted.
     * Fetches courses immediately.
     */
    mounted() {
        this.fetchCourses();
    },
};
</script>