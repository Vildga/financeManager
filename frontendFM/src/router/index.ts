import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '@/components/HomePage.vue';
import AboutPage from '@/components/AboutPage.vue';
import LoginPage from '@/components/LoginForm.vue';
import RegisterPage from '@/components/RegisterForm.vue';
import TableDetail from '@/components/TableDetailPage.vue';
import OAuthCallback from '@/components/OAuthCallback.vue';


const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: { requiresAuth: true },
  },
  {
    path: '/about',
    name: 'About',
    component: AboutPage,
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
  },
  {
    path: '/table/:id',
    name: 'TableDetail',
    component: TableDetail,
    meta: { requiresAuth: true },
    props: true, // Добавлено props: true
  },
  {
    path: '/oauth/callback',
    name: 'OAuthCallback',
    component: OAuthCallback,
    meta: {requiresAuth: false}
  }

];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Добавляем навигационный guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token'); // Проверяем токен
  console.log('Token in localStorage:', token); // Отладка
  const isAuthenticated = !!token;

  console.log('Is Authenticated:', isAuthenticated); // Отладка

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else {
    next();
  }
});




export default router;
