<template>
  <div>
    <el-input placeholder="Email" v-model="email" class="input-field" />
    <el-input
      type="password"
      placeholder="Password"
      v-model="password"
      class="input-field"
    />
    <el-button type="primary" @click="loginUser">Login</el-button>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "LoginPage",
  data() {
    return {
      email: "",
      password: "",
    };
  },
  methods: {
    async loginUser() {
      try {
        const response = await axios.post("/api/users/login", {
          email: this.email,
          password: this.password,
        });

        const userInfo = response.data.user_info;

        // Pass user info to parent component
        this.$emit("login-success", userInfo);

        // Redirect to the home page
        this.$router.push({ name: "homePage" });
      } catch (error) {
        this.$message.error("Login failed. Please check your credentials.");
      }
    },
  },
};
</script>

<style scoped>
.input-field {
  margin: 10px 0;
}
</style>
