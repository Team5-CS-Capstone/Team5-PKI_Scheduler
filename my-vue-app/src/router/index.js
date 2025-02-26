import { createRouter, createWebHistory } from "vue-router";
import HomePage from "../pages/HomePage.vue";
import ExportPage from "../pages/ExportPage.vue";
import ClassList from "../pages/ClassList.vue";
import ClassDetails from "../pages/ClassDetails.vue";

const routes = [
    { path: "/", component: HomePage},
    { path: "/class", component: ClassList},
    { path: "/export", component: ExportPage},
    { path: "/class/:id", component: ClassDetails, props: true},
    // { path: "/class", component: ClassList, props: true},
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;