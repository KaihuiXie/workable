import { createRouter, createWebHistory } from "vue-router";
import LoginCmpt from "../views/LoginCmpt.vue";
import RegisterCmpt from "../views/RegisterCmpt.vue";
import HomePageCmpt from "../views/HomePageCmpt.vue";

const routes = [
  {
    path: "/login",
    name: "login",
    component: LoginCmpt,
  },
  {
    path: "/register",
    name: "register",
    component: RegisterCmpt,
  },
  {
    path: "/homePage",
    name: "homePage",
    component: HomePageCmpt,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
