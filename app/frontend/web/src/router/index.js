import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue'),
  },
  {
    path: '/part/:id',
    name: 'PartDetail',
    component: () => import('../views/PartDetail.vue'),
    props: true,
  },
  {
    path: '/quote',
    name: 'Quote',
    component: () => import('../views/Quote.vue'),
  },
  {
    path: '/track',
    name: 'Track',
    component: () => import('../views/Track.vue'),
  },
  {
    path: '/order/:id',
    name: 'OrderDetail',
    component: () => import('../views/OrderDetail.vue'),
    props: true,
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue'),
  },
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('../views/Contact.vue'),
  },
  {
    path: '/auth/telegram/callback',
    name: 'TelegramCallback',
    component: () => import('../views/TelegramCallback.vue'),
  }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes,
})

export default router
