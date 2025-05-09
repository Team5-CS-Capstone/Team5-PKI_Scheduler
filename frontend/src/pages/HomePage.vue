<!-- CsvUploadAndAlgo.vue -->
<template>
  <div class="flex flex-col items-center h-screen overflow-scroll">
    <template v-if="algoResults === null">
      <!-- UNO logo -->
      <img src="../assets/uno-logo.png" class="h-96 mt-12" alt="UNO logo" />

      <!-- Action buttons -->
      <div class="space-y-4 mt-12 flex flex-col items-center">
        <button type="button" class="w-96 font-semibold rounded-xl bg-sky-500 px-12 py-4 hover:bg-green-500"
          @click="openFilePicker"> Import CSV
        </button>

        <button class="w-72 font-semibold rounded-xl bg-yellow-500 px-12 py-4 hover:bg-yellow-800"
          @click="runAlgorithm">
          RUN ALGORITHM
        </button>
      </div>
    </template>

    <div class="text-black bg-gray-100 h-auto mt-20 shadow-lg rounded-xl w-3/4" v-if="algoResults">
      <h2 class="mt-6 text-4xl font-semibold">Algorithm Results</h2>
      <div class="mt-4 p-4 rounded-lg">
        <!-- Same‑slot -->
        <template v-if="hasSameSlot">
          <h3 class="text-red-500 text-2xl font-semibold">
            Same Slot Recommendations
          </h3>
          <!-- loop ONLY when hasSameSlot is true -->
          <div class="bg-gray-300 mt-4">
            <div
              class="grid grid-cols-[3fr_3fr_1fr] text-white bg-gray-500 text-black justify-between px-5 py-2 rounded-lg">
              <span class="font-semibold justify-self-start">From Classroom</span>
              <span class="font-semibold justify-self-start ml-5">To Classroom</span>
              <span class="font-semibold justify-self-start">Initiate Swap</span>
            </div>
            <div v-for="(recs, slot) in algoResults.same_slot_swaps" :key="slot">
              <div v-for="rec in recs" :key="rec.crowded_id + '-' + rec.target_id"
                class="grid grid-cols-[3fr_3fr_1fr] gap-4 bg-gray-300 text-black justify-between px-5 py-2 rounded-lg">
                <span class="font-semibold justify-self-start h-12">{{ rec.crowded_class_name }} ({{ rec.crowded_room
                  }}) →</span>
                <span class="font-semibold justify-self-start">{{ rec.target_class_name }} ({{ rec.target_room
                  }})</span>
                <button
                  class="px-6 h-10 align-center bg-blue-300 rounded-xl cursor-pointer font-semibold hover:bg-blue-500"
                  @click="swapClassrooms(rec.crowded_id, rec.target_id)">Swap</button>
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <h3 class="text-gray-500 text-2xl font-semibold">
            No Same Slot Recommendations Available
          </h3>
        </template>

        <!-- Cross‑slot -->
        <template v-if="hasCrossSlot">
          <h3 class="mt-6 text-red-500 text-2xl font-semibold">
            Cross Slot Recommendations
          </h3>
          <div class="bg-gray-300 mt-4">
            <div
              class="grid grid-cols-[3fr_3fr_1fr] text-white bg-gray-500 text-black justify-between px-5 py-2 rounded-lg">
              <span class="font-semibold justify-self-start">From Classroom</span>
              <span class="font-semibold justify-self-start ml-5">To Classroom</span>
                <span class="font-semibold justify-self-start">Initiate Swap</span>
              </div>
              <div v-for="(recs, slot) in algoResults.cross_slot_recommendations" :key="slot">
                <div v-for="rec in recs" :key="rec.crowded_id + '-' + rec.target_id"
                class="grid grid-cols-[3fr_3fr_1fr] gap-4 bg-gray-300 text-black justify-between px-5 py-2 rounded-lg">
                <span class="font-semibold justify-self-start h-12">{{ rec.crowded_class_name }} ({{ rec.crowded_room
                  }}) →</span>
                <span class="font-semibold justify-self-start">{{ rec.target_class_name }} ({{ rec.target_room
                  }})</span>
                <button
                  class="px-6 h-10 align-center bg-blue-300 rounded-xl cursor-pointer font-semibold hover:bg-blue-500"
                  @click="swapClassrooms(rec.crowded_id, rec.target_id, true)">Swap</button>
                </div>
              </div>
          </div>
        </template>
        <template v-else>
          <h3 class="text-gray-500 text-2xl mt-4 font-semibold">
            No Cross Slot Recommendations Available
          </h3>
        </template>
      </div>
    </div>
    <!-- Hidden native file input -->
    <input ref="fileInput" type="file" accept=".csv" style="display: none" @change="handleFileUpload" />
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
  computed: {
    // Check if any same slot swaps exist in the algo results
    hasSameSlot() {
      return this.algoResults && this.algoResults.same_slot_swaps &&
        Object.keys(this.algoResults.same_slot_swaps).length > 0;
    },
    // Check if any cross slot swaps exist in the algo results
    hasCrossSlot() {
      return this.algoResults && this.algoResults.cross_slot_recommendations &&
        Object.keys(this.algoResults.cross_slot_recommendations).length > 0;
    },
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

    async swapClassrooms(crowdedId, targetId, differentTimeSlot) {
      try {
        const { data } = await axios.post(
          "http://localhost:5000/swap-classrooms",
          {
            crowded_id: crowdedId,
            target_id: targetId,
            different_timeslot: differentTimeSlot,
          }
        );
        console.log("Swap successful:", data);
        alert("Classrooms swapped successfully!");     
      } catch (err) {
        console.error("Swap error:", err);
        this.errorMessage = "Failed to swap classrooms.";
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
