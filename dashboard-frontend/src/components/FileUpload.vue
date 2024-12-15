<template>
  <div>
    <h2>Upload a File</h2>
    <input type="file" @change="uploadFile" />
  </div>
</template>

<script>
import axios from "axios";

export default {
  methods: {
    async uploadFile(event) {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await axios.post("/api/resume/upload", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        if (response.status === 200) {
          // Check the HTTP status code
          this.$emit("fileUploaded");
        } else {
          alert("File upload failed.");
        }
      } catch (error) {
        this.$message.error("File upload failed.");
        console.error(error); // Log the error for debugging
      }
    },
  },
};
</script>

<style>
div {
  margin-bottom: 20px;
}
</style>
