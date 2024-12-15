<template>
  <div id="app">
    <el-container>
      <h2>Filli AI</h2>
      <el-header>
        <div class="header-buttons" v-if="!isLoggedIn">
          <el-button type="primary" @click="navigateTo('loginPage')">
            Login
          </el-button>
          <el-button type="success" @click="navigateTo('registerPage')">
            Sign Up
          </el-button>
        </div>
        <div class="header-user" v-else>
          <span>Welcome, {{ userInfo.name }}!</span>
          <el-button type="danger" @click="logout">Logout</el-button>
        </div>
      </el-header>
      <el-main>
        <!-- Render routed pages -->
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: "App",
  data() {
    return {
      isLoggedIn: false,
      userInfo: null,
    };
  },
  methods: {
    // Navigate to the page (login or register)
    navigateTo(page) {
      this.$router.push({ name: page });
    },
    handleLoginSuccess(userInfo) {
      this.isLoggedIn = true;
      this.userInfo = userInfo;
    },
    logout() {
      this.isLoggedIn = false;
      this.userInfo = null;
      this.$router.push({ name: "loginPage" });
    },
  },
};
</script>

<style lang="scss">
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
}

.header-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.header-user {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  align-items: center;
}

el-header {
  background-color: #42b983;
  color: white;
  padding: 10px;
}

el-main {
  padding: 20px;
}
</style>
