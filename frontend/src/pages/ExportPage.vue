<!-- 
somehow need to obtain class ID from route and using that 
information we can make an API call with that ID and display 
and update the proper information 
-->

<template>
    <div class="flex justify-center">
        <img class="h-96 mt-12 text-2xl font-bold" src="../assets/uno-logo.png"></img>
    </div>
    <div class="mt-22 text-2xl font-bold w-full flex justify-center">
        <button class="w-96 rounded-xl bg-sky-500 px-12 py-4 hover:bg-green-500 cursor-pointer" type="button"
            @click="exportToFile">Export CSV</button>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: "ExportComponent",
    data() {
        return {
            /**
             * Data for the class (if needed).
             * @vue-data {Object|null}
             */
            classData: null,
        };
    },
    methods: {
        /**
         * Exports data by calling the export endpoint.
         *
         * @vue-method
         * @async
         * @returns {Promise<void>} Resolves when the export call completes.
         */
        async exportToFile() {
            try {
                const response = await axios.put(`http://127.0.0.1:5000/export`);
                alert('Successfully exported data to CSV! Please locate the file on your Desktop.');
                // Process response as needed.
            } catch (error) {
                console.error('Could not export data.', error);
            }
        },
    },
    mounted() {
        // nothing needed yet on mount
    },
};
</script>