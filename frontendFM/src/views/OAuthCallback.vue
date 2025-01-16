<template>
  <div>
    <h2>Processing authentication...</h2>
  </div>
</template>

<script lang="ts">
import { useRouter } from "vue-router";
import axios from "axios";

export default {
  name: "OAuthCallback",
  setup() {
    const router = useRouter();

    const handleOAuth = async () => {
      // Извлекаем код из строки запроса
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get("code");

      if (!code) {
        alert("Authorization code not found.");
        router.push("/login");
        return;
      }

      try {
        // Отправляем код на backend
        const response = await axios.post("http://localhost:8000/api/social-login/", {
          code,
          redirect_uri: "http://localhost:5173/oauth/callback",
        });

        // Сохраняем токены
        localStorage.setItem("accessToken", response.data.accessToken);
        localStorage.setItem("refreshToken", response.data.refreshToken);

        // Перенаправляем на главную страницу
        router.push("/");
      } catch (error) {
        console.error("Error:", error);
        alert("Authentication failed.");
        router.push("/login");
      }
    };

    handleOAuth();
    return {};
  },
};
</script>
