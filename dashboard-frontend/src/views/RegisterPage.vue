<template>
  <div>
    <el-input placeholder="Name" v-model="name" class="input-field" />
    <el-input placeholder="Email" v-model="email" class="input-field" />
    <el-input
      type="password"
      placeholder="Password"
      v-model="password"
      class="input-field"
    />
    <el-button type="primary" @click="registerUser">Sign Up</el-button>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "RegisterPage",
  data() {
    return {
      name: "",
      email: "",
      password: "",
    };
  },
  methods: {
    async registerUser() {
      try {
        await axios.post("/api/users/register", {
          name: this.name,
          email: this.email,
          password: this.password,
        });
        this.$message.success("Registration successful! Please log in.");
        this.$router.push({ name: "loginPage" });
      } catch (error) {
        this.$message.error("Registration failed. Please try again.");
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
