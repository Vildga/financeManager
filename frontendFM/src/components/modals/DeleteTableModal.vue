<template>
  <div class="modal fade" id="deleteTableModal" tabindex="-1" aria-labelledby="deleteTableModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="deleteTableModalLabel">Confirm Deletion</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          Are you sure you want to delete this table?
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="button" class="btn btn-danger" @click="deleteTable">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import axios from 'axios';
import * as bootstrap from 'bootstrap'; // Импорт Bootstrap JS

export default defineComponent({
  name: 'DeleteTableModal',
  setup(_, { emit }) {
    const deleteTable = async () => {
      const tableId = document.getElementById('deleteTableModal')?.getAttribute('data-table-id');
      if (!tableId) {
        alert('Table ID is missing.');
        return;
      }

      try {
        const token = localStorage.getItem('accessToken');
        const response = await axios.delete(`http://localhost:8000/api/tables/delete/${tableId}/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.status === 204) {
          alert('Table deleted successfully!');
          emit('table-deleted');

          // Закрытие модального окна вручную
          const modalElement = document.getElementById('deleteTableModal');
          if (modalElement) {
            const modalElement = document.getElementById('deleteTableModal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) modal.hide();
          }
        }
      } catch (error) {
        alert('Failed to delete table.');
      }
    };

    return {
      deleteTable,
    };
  },
});
</script>

