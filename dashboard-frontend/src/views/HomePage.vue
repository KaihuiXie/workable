<template>
  <div class="homePage">
    <div class="card mx-auto mt-5 shadow-sm" style="max-width: 600px">
      <div class="card-header text-center">
        <h3 class="mb-0">Welcome to the Dashboard</h3>
      </div>
      <div class="card-body text-center">
        <h4>Welcome back, {{ userName }}!</h4>
        <FileUpload @fileUploaded="fetchFiles" />
      </div>
    </div>
  </div>
</template>

<script>
import FileUpload from "../components/FileUpload.vue";

export default {
  data() {
    return {
      userName: "",
    };
  },
  components: {
    FileUpload,
  },
};
</script>

<style scoped>
.home {
  max-width: 600px;
  margin: 0 auto;
}

.card {
  border-radius: 15px;
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #ddd;
}

.card-body {
  padding: 20px;
}

.form-label {
  font-weight: 600;
}

.btn {
  border-radius: 8px;
  padding: 12px;
  font-weight: 600;
}

.btn-danger {
  background-color: #dc3545;
  border-color: #dc3545;
}

.btn-danger:hover {
  background-color: #c82333;
  border-color: #bd2130;
}

h3,
h4 {
  color: #007bff;
}
</style>
