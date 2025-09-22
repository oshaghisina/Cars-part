import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Dashboard",
    component: () => import("../views/Dashboard.vue"),
  },
  {
    path: "/parts",
    name: "Parts",
    component: () => import("../views/Parts.vue"),
  },
  {
    path: "/orders",
    name: "Orders",
    component: () => import("../views/Orders.vue"),
  },
  {
    path: "/orders/:id",
    name: "OrderDetail",
    component: () => import("../views/OrderDetail.vue"),
    props: true,
  },
  {
    path: "/leads",
    name: "Leads",
    component: () => import("../views/Leads.vue"),
  },
  {
    path: "/settings",
    name: "Settings",
    component: () => import("../views/Settings.vue"),
  },
  {
    path: "/vehicles",
    name: "Vehicles",
    component: () => import("../views/vehicles/Vehicles.vue"),
  },
  {
    path: "/categories",
    name: "Categories",
    component: () => import("../views/categories/Categories.vue"),
  },
  {
    path: "/users",
    name: "Users",
    component: () => import("../views/users/Users.vue"),
  },
  {
    path: "/analytics",
    name: "Analytics",
    component: () => import("../views/Analytics.vue"),
  },
  {
    path: "/ai-dashboard",
    name: "AIDashboard",
    component: () => import("../views/AIDashboard.vue"),
  },
  {
    path: "/ai-chat",
    name: "AIChat",
    component: () => import("../views/AIChat.vue"),
  },
  {
    path: "/test-advanced-nav",
    name: "TestAdvancedNav",
    component: () => import("../views/TestAdvancedNav.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
