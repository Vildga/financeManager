<template>
  <div class="modal fade" id="createTableModal" tabindex="-1" aria-labelledby="createTableModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="createTableModalLabel">Create New Table</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createTable">
            <div class="mb-3">
              <label for="table-name" class="form-label">Table Name</label>
              <input type="text" class="form-control" id="table-name" v-model="tableName" required />
            </div>
            <div class="mb-3">
              <label for="table-description" class="form-label">Table Description</label>
              <textarea class="form-control" id="table-description" v-model="tableDescription" rows="3"></textarea>
            </div>
            <button type="submit" class="btn btn-add-transaction w-100">Create Table</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import axios from 'axios';
import * as bootstrap from 'bootstrap'; // Импорт Bootstrap JS

export default defineComponent({
  name: 'CreateTableModal',
  setup(_, { emit }) {
    // Поля формы
    const tableName = ref('');
    const tableDescription = ref('');

    // Функция создания таблицы
    const createTable = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          alert('You are not authenticated. Please log in.');
          return;
        }

        const response = await axios.post(
          'http://localhost:8000/api/tables/add/',
          {
            name: tableName.value,
            description: tableDescription.value,
          },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.status === 201) {
          alert('Table created successfully!');
          emit('table-created');

          // Закрываем модальное окно вручную
          const modalElement = document.getElementById('createTableModal');
          if (modalElement) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) modal.hide();
          }

          // Сбрасываем поля формы
          tableName.value = '';
          tableDescription.value = '';
        }
      } catch (error) {
        alert('Failed to create table.');
      }
    };

    // Обработка события закрытия модального окна
    onMounted(() => {
      const modalElement = document.getElementById('createTableModal');
      if (modalElement) {
        modalElement.addEventListener('hidden.bs.modal', () => {
          const backdrop = document.querySelector('.modal-backdrop');
          if (backdrop) backdrop.remove();
          document.body.classList.remove('modal-open');
        });
      }
    });

    return {
      tableName,
      tableDescription,
      createTable,
    };
  },
});
</script>



<style scoped>
.modal-content {
  border-radius: 8px;
}

.modal-header {
  background-color: #626cd6;
  color: white;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.btn-add-transaction {
  background-color: #198754;
  color: white;
  border-radius: 5px;
  padding: 10px 15px;
  font-weight: bold;
}
</style>
