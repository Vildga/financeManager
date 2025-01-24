<template>
  <div>
    <h2>Авторизация через Google...</h2>
    <p>Пожалуйста, подождите</p>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export default defineComponent({
  name: 'OAuthCallback',
  setup() {
    const route = useRoute();
    const router = useRouter();

    onMounted(() => {
      const token = route.query.token as string;
      const refresh = route.query.refresh as string;

      // console.log('Token =', token); // Отладка
      // console.log('Refresh =', refresh); // Отладка

      if (token) {
        localStorage.setItem('token', token);
        // console.log('Token saved in localStorage:', token); // Отладка
      }
      if (refresh) {
        localStorage.setItem('refreshToken', refresh);
        // console.log('Refresh token saved in localStorage:', refresh); // Отладка
      }

      // Перенаправляем пользователя на главную страницу
      router.push('/');
    });
  },
});
</script>
