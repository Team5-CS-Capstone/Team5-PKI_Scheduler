<!-- CsvUploadAndAlgo.vue -->
<template>
  <div class="flex flex-col items-center h-screen overflow-scroll bg-gray-100">
    <!-- UNO logo -->
    <img src="../assets/uno-logo.png" class="h-96 mt-12" alt="UNO logo" />

    <!-- Action buttons -->
    <div class="space-y-4 mt-12 flex flex-col items-center">
      <button
        type="button"
        class="w-96 font-semibold rounded-xl bg-sky-500 px-12 py-4 hover:bg-green-500"
        @click="openFilePicker"> Import CSV
      </button>

      <button
        class="w-72 font-semibold rounded-xl bg-yellow-500 px-12 py-4 hover:bg-yellow-800"
        @click="runAlgorithm"> RUN ALGORITHM
      </button>
    </div>

    <div class="text-black h-96" v-if="algoResults">
      <h2 class="mt-12 text-2xl font-semibold">Algorithm Results</h2>
      <div class="mt-4 bg-gray-100 p-4 rounded-lg shadow-md">
        <h3 class="text-red-500 text-2xl font-semibold">Same Slot Recommendations</h3>
        <div
          v-for="(recs, slot) in algoResults.same_slot_swaps"
          :key="slot"
          class="mt-4">          
          <h3 class="font-semibold">{{ slot }}</h3>
          <ul class="list-disc pl-6">
            <li
              v-for="rec in recs"
              :key="rec.crowded_id + '-' + rec.target_id">
              {{ rec.crowded_class_name }} ({{ rec.crowded_room }})
              → {{ rec.target_class_name }} ({{ rec.target_room }})
            </li>
          </ul>
        </div>
        <h3 class="mt-12 text-red-500 text-2xl font-semibold">Cross Slot Recommendations</h3>
        <div
          v-for="(recs, slot) in algoResults.cross_slot_recommendations"
          :key="slot"
          class="mt-4">          
          <h3 class="font-semibold">{{ slot }}</h3>
          <ul class="list-disc pl-6">
            <li
              v-for="rec in recs"
              :key="rec.crowded_id + '-' + rec.target_id">
              {{ rec.crowded_class_name }} ({{ rec.crowded_room }})
              → {{ rec.target_class_name }} ({{ rec.target_room }})
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Hidden native file input -->
    <input
      ref="fileInput"
      type="file"
      accept=".csv"
      style="display: none"
      @change="handleFileUpload"
    />

    <!-- Error popup -->
    <div v-if="errorMessage" class="error-popup mt-4">
      <p>{{ errorMessage }}</p>
      <button class="underline" @click="errorMessage = ''">Close</button>
    </div>
  </div>
</template>

<script>
import axios from "axios";

/**
 * Upload a CSV file to the backend and run the swap‑recommendation algorithm.
 */
export default {
  name: "CsvUploadAndAlgo",

  data() {
    return {
      /** Error message shown in the popup (empty means no error). */
      errorMessage: "",
      algoResults: null,
    };
  },

  methods: {
    /** Programmatically open the hidden file picker. */
    openFilePicker() {
      this.$refs.fileInput.click();
    },

    /**
     * POST the selected CSV to the Flask `/upload` endpoint.
     * @param {File} file - CSV file chosen by the user.
     */
    async uploadCSV(file) {
      const formData = new FormData();
      formData.append("file", file);

      try {
        const { data } = await axios.post(
          "http://localhost:5000/upload",
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
        );
        console.log("Upload successful:", data);
        alert("File uploaded successfully!");
      } catch (err) {
        console.error("Upload error:", err);
        this.errorMessage = "Failed to upload the file.";
      }
    },

    /**
     * Validate the chosen file, then forward it to `uploadCSV`.
     * @param {Event} e - Change event from the file input.
     */
    async handleFileUpload(e) {
      const file = e.target.files[0];
      if (!file) return;

      if (!file.name.endsWith(".csv")) {
        this.errorMessage = "Invalid file type. Please upload a CSV file.";
        return;
      }

      await this.uploadCSV(file);
    },

    /** GET `/swap-recommendations` to run the scheduling algorithm. */
    async runAlgorithm() {
      try {
        const { data } = await axios.get(
          "http://localhost:5000/swap-recommendations"
        );
        this.algoResults = data;
      } catch (err) {
        console.error("Algorithm error:", err);
        this.errorMessage = "Failed to run the algorithm.";
      }
    },
  },
};
</script>

<style scoped>
.error-popup {
  background-color: #ffcccc;
  padding: 15px;
  border: 1px solid red;
  border-radius: 5px;
}
</style>
