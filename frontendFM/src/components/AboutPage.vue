<template>
  <div>
    <!-- Navbar -->
    <Navbar />

    <!-- Main Content -->
    <div class="about-container">
      <h1>About Finance Manager</h1>
      <p>
        Welcome to <strong>Finance Manager</strong> — a simple and convenient tool for managing your personal finances. Track your expenses, categorize your transactions, and make smarter financial decisions!
      </p>

      <h3>Need Help?</h3>
      <p>
        If you have any questions or need assistance, feel free to contact our support team.
        Click the link below to get in touch with us on Telegram:
      </p>
      <a href="https://t.me/vildga_support" target="_blank" class="support-link">
        👉 Contact Support
      </a>

      <h3>Join Our Community</h3>
      <p>
        Stay updated with the latest news, tips, and feature releases by joining our Telegram group:
      </p>
      <a href="https://t.me/FinanceManagerDigest" target="_blank" class="community-link">
        👉 Join Finance Manager Digest
      </a>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import Navbar from '@/components/Navbar.vue';

export default defineComponent({
  name: 'AboutPage',
  components: {
    Navbar,
  },
});
</script>

<style scoped>
.about-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  font-family: 'Arial', sans-serif;
  margin-top: 70px; /* Отступ, чтобы контент не сливался с Navbar */
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

p {
  line-height: 1.6;
  color: #555;
}

h3 {
  color: #444;
  margin-top: 20px;
}

a {
  display: inline-block;
  margin: 10px 0;
  padding: 10px 15px;
  background-color: #6c63ff;
  color: #fff;
  border-radius: 4px;
  text-decoration: none;
  font-weight: bold;
  transition: background-color 0.3s ease;
}

a:hover {
  background-color: #5751d9;
}

.support-link {
  margin-bottom: 20px;
}

.community-link {
  margin-top: 10px;
}
</style>
