<template>
  <div>
    <!-- Navbar -->
    <Navbar />

    <!-- Main Content -->
    <div class="container-fluid py-4">
      <div class="row">
        <!-- Sidebar -->
        <nav class="col-md-3 col-lg-2 bg-light sidebar py-3">
          <div class="text-center mb-4">
            <h3 class="fw-bold text-primary">Your Tables</h3>
            <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#createTableModal">
              + Create Table
            </button>
          </div>
          <ul class="list-group list-group-flush">
            <li
              v-for="table in tables"
              :key="table.id"
              class="list-group-item d-flex justify-content-between align-items-center"
            >
              <router-link :to="'/table/' + table.id" class="text-decoration-none text-dark w-100">
                <div class="d-flex flex-column w-100">
                  <strong>{{ table.name }}</strong>
                  <p class="text-muted small mb-0">{{ table.description }}</p>
                </div>
              </router-link>
              <button class="btn btn-outline-danger" @click="openDeleteModal(table.id)">Delete</button>
            </li>
            <li v-if="tables.length === 0" class="list-group-item text-center text-muted">You have no tables yet.</li>
          </ul>
        </nav>

        <!-- Main Content -->
        <main class="col-md-9 col-lg-10 d-flex flex-column align-items-center justify-content-center text-center">
          <h1 class="display-5">Welcome, {{ username }}!</h1>
          <p class="lead">Select a table to manage your data or create a new one using the button on the left.</p>
        </main>
      </div>

      <!-- Modals -->
      <CreateTableModal @table-created="fetchTables" />
      <DeleteTableModal @table-deleted="fetchTables" />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import axiosInstance from '@/api/axiosInstance'; // Кастомный axios

import Navbar from '@/components/Navbar.vue';
import CreateTableModal from '@/components/modals/CreateTableModal.vue';
import DeleteTableModal from '@/components/modals/DeleteTableModal.vue';
import * as bootstrap from 'bootstrap'; // Подключаем Bootstrap JS

export default defineComponent({
  name: 'HomePage',
  components: {
    Navbar,
    CreateTableModal,
    DeleteTableModal,
  },
  setup() {
    // Состояния
    const tables = ref([]);
    const username = ref('User');

    // Получаем данные пользователя
    const fetchUserInfo = async () => {
      try {
        const response = await axiosInstance.get('/api/user/');
        username.value = response.data.username;
      } catch (error) {
        console.error('Error fetching user info:', error);
        if (error.response && error.response.status === 401) {
          alert('Your session has expired. Please log in again.');
          window.location.href = '/login';
        } else {
          alert('Failed to fetch user info.');
        }
      }
    };

    // Получаем таблицы с API
    const fetchTables = async () => {
      try {
        const response = await axiosInstance.get('/api/tables/');
        tables.value = response.data;
      } catch (error) {
        console.error('Error fetching tables:', error);
        if (error.response && error.response.status === 401) {
          alert('Your session has expired. Please log in again.');
          window.location.href = '/login';
        } else {
          alert('Failed to fetch tables.');
        }
      }
    };

    // Открытие модального окна удаления таблицы
    const openDeleteModal = (tableId) => {
      const modalElement = document.getElementById('deleteTableModal');
      if (modalElement) {
        modalElement.setAttribute('data-table-id', tableId);
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
      }
    };

    // При монтировании компонента
    onMounted(() => {
      fetchUserInfo();
      fetchTables();
    });

    return {
      tables,
      username,
      fetchTables,
      openDeleteModal,
    };
  },
});
</script>

<style scoped>
.container-fluid {
  margin-top: 70px; /* Высота навбара */
}
.sidebar {
  height: 90vh;
  position: sticky;
  top: 0;
  background-color: #f8f9fa;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  padding: 20px;
}
.sidebar h3 {
  font-size: 1.5em;
  color: #626cd6;
  font-weight: bold;
  margin-bottom: 20px;
}
.btn-success {
  background-color: #198754;
  color: white;
  border-radius: 5px;
  padding: 10px 20px;
}
</style>
