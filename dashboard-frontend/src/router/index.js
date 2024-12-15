import { createRouter, createWebHistory } from "vue-router";
import LoginPage from "../views/LoginPage.vue";
import RegisterPage from "../views/RegisterPage.vue";
import HomePage from "../views/HomePage.vue";

const routes = [
  {
    path: "/login",
    name: "loginPage",
    component: LoginPage,
  },
  {
    path: "/register",
    name: "registerPage",
    component: RegisterPage,
  },
  {
    path: "/homePage",
    name: "homePage",
    component: HomePage,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
