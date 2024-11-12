<template>
  <div class="login">
    <div class="card mx-auto mt-5 shadow-sm" style="max-width: 400px">
      <div class="card-header text-center">
        <h3 class="mb-0">Register</h3>
      </div>
      <div class="card-body">
        <form @submit.prevent="loginUser">
          <!-- Email Field -->
          <div class="mb-3">
            <label for="email" class="form-label">Email:</label>
            <input
              type="email"
              v-model="email"
              class="form-control"
              id="email"
              placeholder="Enter your email"
              required
            />
          </div>

          <!-- Password Field -->
          <div class="mb-3">
            <label for="password" class="form-label">Password:</label>
            <input
              type="password"
              v-model="password"
              class="form-control"
              id="password"
              placeholder="Enter your password"
              required
            />
          </div>

          <!-- Name Field -->
          <div class="mb-3">
            <label for="name" class="form-label">Name:</label>
            <input
              type="text"
              v-model="name"
              class="form-control"
              id="name"
              placeholder="Enter your name"
              required
            />
          </div>

          <!-- Login Button -->
          <button type="submit" class="btn btn-primary w-100">Login</button>
        </form>
      </div>

      <!-- User Info (Optional) -->
      <div v-if="userInfo" class="card-footer text-center bg-light">
        <h5>User Info</h5>
        <p><strong>User ID:</strong> {{ userInfo.user_id }}</p>
        <p><strong>Email:</strong> {{ userInfo.email }}</p>
        <p><strong>Token:</strong> {{ userInfo.token }}</p>
        <p><strong>Name:</strong> {{ userInfo.name }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      email: "",
      password: "",
      name: "",
      userInfo: null,
      error: null,
    };
  },
  methods: {
    async loginUser() {
      try {
        const response = await axios.post("/api/users/register", {
          email: this.email,
          password: this.password,
          name: this.name,
        });

        this.userInfo = response.data.user_info;
      } catch (error) {
        this.userInfo = null;
      }
    },
  },
};
</script>

<style scoped>
.login {
  max-width: 400px;
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

.card-footer {
  background-color: #f8f9fa;
  border-top: 1px solid #ddd;
}

.form-label {
  font-weight: 600;
}

.form-control {
  border-radius: 8px;
}

.btn {
  border-radius: 8px;
  padding: 12px;
  font-weight: 600;
}

.btn-primary {
  background-color: #007bff;
  border-color: #007bff;
}

.btn-primary:hover {
  background-color: #0056b3;
  border-color: #004085;
}

input::placeholder {
  color: #6c757d;
}

input:focus {
  box-shadow: 0 0 0 0.25rem rgba(38, 143, 255, 0.5);
  border-color: #007bff;
}
</style>
