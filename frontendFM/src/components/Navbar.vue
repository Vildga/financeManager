<template>
  <header class="header">
    <div class="container d-flex align-items-center">
      <!-- Логотип и название -->
      <div class="d-flex align-items-center flex-grow-1">
        <router-link to="/" class="navbar-brand d-flex align-items-center">
          <img src="@/assets/FinanceManager.png" alt="LogoFinanceManager" class="logo" />
          <span>Finance Manager</span>
        </router-link>
      </div>

      <!-- Навигация -->
      <nav class="navigation d-flex">
        <ul class="d-flex">
          <li>
            <router-link to="/about">About</router-link>
          </li>
          <li v-if="isAuthenticated">
            <a href="#" @click="handleLogout">Logout</a>
          </li>
          <li v-else>
            <router-link to="/login">Login</router-link>
            <router-link to="/register">Register</router-link>
          </li>
        </ul>
      </nav>
    </div>
  </header>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'NavbarPage',
  setup() {
    const router = useRouter();
    const isAuthenticated = ref(!!localStorage.getItem('token'));

    const handleLogout = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      // alert('You have been logged out.');
      router.push('/login');
    };

    return {
      isAuthenticated,
      handleLogout,
    };
  },
});
</script>

<style scoped>
/* Общие стили для шапки */
.header {
  background-color: #626cd6;
  padding: 10px 20px;
  position: fixed;
  width: 100%;
  top: 0;
  z-index: 1000;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

/* Логотип и название */
.navbar-brand {
  display: flex;
  align-items: center;
  font-size: 1.5rem;
  font-weight: bold;
  color: #fff;
  text-decoration: none;
}

.logo {
  height: 40px;
  width: auto;
  margin-right: 10px;
}

/* Навигация */
.navigation {
  margin-left: auto;
}

.navigation ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
}

.navigation ul li {
  margin-left: 20px;
}

.navigation ul li a {
  color: #f8f8fb;
  text-decoration: none;
  font-weight: 500;
  padding: 5px 10px;
  border-radius: 5px;
  transition: background-color 0.3s, color 0.3s;
}

.navigation ul li a:hover {
  background-color: #4954d0;
  color: #fff;
}
</style>
