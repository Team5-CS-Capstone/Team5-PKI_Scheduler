<script setup>
import { ref } from 'vue'
import axios from 'axios' 

const errorMessage = ref('')
const fileInput = ref(null)

// Open File Explorer
const openFilePicker = () => {
  fileInput.value.click()
}

// Send CSV File to Flask Backend
const uploadCSV = async (file) => {
  const formData = new FormData()
  formData.append('file', file)  // Append file to formData

  try {
    // Connect with the API post endpoint
    const response = await axios.post('http://localhost:5000/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
  })
    console.log('Upload Successful:', response.data)
    alert("File uploaded successfully!") 

  } catch (error) {
    console.error('Upload Error:', error)
    errorMessage.value = 'Failed to upload the file.'
  }

}

// Handle File Import
const handleFileUpload = async (e) => {
  const file = e.target.files[0] // Get the selected file

  if (file) {
    if (!file.name.endsWith('.csv')) {
      errorMessage.value = 'Invalid file type. Please upload a CSV file.'
      return
    }

    // Process and send the CSV to the backend
    await uploadCSV(file)
  }

}

</script>

<template>
  <div class="flex justify-center">
    <img class="h-96 mt-12 text-2xl font-bold" src="../assets/uno-logo.png"></img>
  </div>
  <div class="mt-22 text-2xl font-bold w-full">
    <!-- Button to trigger file input -->
    <button class="w-96 rounded-xl bg-sky-500 px-12 py-4 hover:bg-green-500 cursor-pointer" type="button" @click="openFilePicker">Import CSV</button>

    <!-- Handle File input-->
     <input
      type="file"
      ref="fileInput"
      accept=".csv"
      @change="handleFileUpload"
      style="display: none"
     />

    <!--Error Message Popup-->
    <div v-if="errorMessage" class="error-popup">
      <p>{{ errorMessage }}</p>
      <button @click="errorMessage = ''">Close</button>
    </div>

  </div>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
.error-popup {
  background-color: #ffcccc;
  padding: 15px;
  border: 1px solid red;
  border-radius: 5px;
  margin-top: 10px;
}
</style>
