import { createRouter, createWebHistory } from "vue-router";
import HomePage from "../pages/HomePage.vue";
import SearchPage from "../pages/SearchPage.vue";
import ExportPage from "../pages/ExportPage.vue";

const routes = [
    { path: "/", component: HomePage},
    { path: "/search", component: SearchPage},
    { path: "/export", component: ExportPage},
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;