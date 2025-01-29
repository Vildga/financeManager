<template>
  <body>
    <div class="login_form">
      <!-- Registration form -->
      <form @submit.prevent="handleRegister">
        <h3>Sign up with</h3>

        <!-- Social login options -->
        <div class="login_option">
          <div class="option">
            <a
              href="http://localhost:8000/social-auth/login/google-oauth2/"
              class="social-button google-button"
            >
              <img src="@/assets/google.png" alt="Google" class="google-logo" />
              <span>Sign up with Google</span>
            </a>
          </div>
        </div>
        <p class="separator"><span>or</span></p>

        <!-- Username field -->
        <div class="input_box">
          <label for="username">Username</label>
          <input
            type="text"
            id="username"
            v-model="form.username"
            placeholder="Enter your username"
            required
          />
        </div>

        <!-- Email field -->
        <div class="input_box">
          <label for="email">Email</label>
          <input
            type="email"
            id="email"
            v-model="form.email"
            placeholder="Enter your email address"
            required
          />
        </div>

        <!-- Password field -->
        <div class="input_box">
          <label for="password">Password</label>
          <input
            type="password"
            id="password"
            v-model="form.password"
            placeholder="Enter your password"
            required
          />
        </div>

        <!-- Confirm Password field -->
        <div class="input_box">
          <label for="password2">Confirm Password</label>
          <input
            type="password"
            id="password2"
            v-model="form.password2"
            placeholder="Confirm your password"
            required
          />
        </div>

        <!-- Submit button -->
        <button type="submit">Sign Up</button>

        <!-- Link to login page -->
        <p class="sign_up">
          Already have an account?
          <router-link to="/login">Log in</router-link>
        </p>
      </form>
    </div>
  </body>
</template>

<script lang="ts">
import { defineComponent, reactive } from 'vue';
import axiosInstance from '@/api/axiosInstance';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'UserRegister',
  setup() {
    const router = useRouter();
    const form = reactive({
      username: '',
      email: '',
      password: '',
      password2: '',
    });

    const handleRegister = async () => {
      try {
        await axiosInstance.post('/api/register/', form);
        // alert('Registration successful!');
        router.push('/login');
      } catch (error: any) {  // Type error as any
        console.error('Registration error:', error.response?.data || error.message);
        // alert('Error: ' + (error.response?.data?.detail || 'Failed to register.'));
      }
    };

    return { form, handleRegister };
  },
});
</script>


<style scoped>
@import '@/assets/log-reg-style.css';
</style>
