<template>
  <body>
    <div class="login_form">
      <form @submit.prevent="handleLogin">
        <h3>Log in with</h3>

        <!-- Social login options -->
        <div class="login_option">
          <div class="option">
            <a
              href="http://localhost:8000/social-auth/login/google-oauth2/"
              class="social-button google-button"
            >
              <img src="@/assets/google.png" alt="Google" class="google-logo" />
              <span>Sign in with Google</span>
            </a>
          </div>
        </div>

        <p class="separator"><span>or</span></p>

        <!-- Input fields for username and password -->
        <div class="input_box">
          <label for="username">Username</label>
          <input
            type="text"
            id="username"
            v-model="username"
            placeholder="Enter your username"
            required
          />
        </div>

        <div class="input_box">
          <div class="password_title">
            <label for="password">Password</label>
            <a href="#">Forgot Password?</a>
          </div>
          <input
            type="password"
            id="password"
            v-model="password"
            placeholder="Enter your password"
            required
          />
        </div>

        <!-- Submit button -->
        <button type="submit">Log In</button>

        <!-- Link to registration page -->
        <p class="sign_up">
          Don't have an account?
          <router-link to="/register">Sign up</router-link>
        </p>
      </form>
    </div>
  </body>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'LoginForm',
  setup() {
    const router = useRouter();
    const username = ref('');
    const password = ref('');

    const handleLogin = async () => {
      try {
        const response = await axios.post('http://localhost:8000/api/login/', {
          username: username.value,
          password: password.value,
        });

        // Зберігаємо токени в localStorage
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('refreshToken', response.data.refresh);

        // Перенаправляємо на головну сторінку
        router.push('/');
      } catch (error) {
        console.log(error);
        // alert('Invalid username or password.');
      }
    };

    return {
      username,
      password,
      handleLogin,
    };
  },
});
</script>

<style scoped>
@import '@/assets/log-reg-style.css';

/* Google Login Button Styling */
.google-button {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  color: #757575;
  font-size: 16px;
  font-weight: bold;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 12px 16px;
  width: 100%;
  height: 50px; /* Робимо кнопку прямокутною */
  text-align: center;
  text-decoration: none;
  transition: background-color 0.3s ease;
}

.google-button:hover {
  background-color: #f1f1f1;
}

.google-logo {
  width: 24px;
  height: 24px;
  margin-right: 10px;
}
</style>
