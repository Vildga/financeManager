<template>
  <div
    class="modal fade"
    id="addTransactionModal"
    tabindex="-1"
    aria-labelledby="addTransactionModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content rounded shadow">
        <!-- Custom Header -->
        <div class="modal-header custom-header">
          <h5 class="modal-title text-white" id="addTransactionModalLabel">Add Transaction</h5>
          <button
            type="button"
            class="btn-close btn-close-white"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>

        <!-- Form Body -->
        <div class="modal-body">
          <form @submit.prevent="submitTransaction">
            <!-- Date -->
            <div class="mb-3">
              <label for="date" class="form-label">Date</label>
              <input type="date" class="form-control" v-model="form.date" required />
            </div>

            <!-- Type -->
            <div class="mb-3">
              <label for="type" class="form-label">Type</label>
              <select class="form-select" v-model="form.type" @change="filterCategories" required>
                <option value="income">Income</option>
                <option value="expense">Expense</option>
              </select>
            </div>

            <!-- Category -->
            <div class="mb-3">
              <label for="category" class="form-label">Category</label>
              <select class="form-select" v-model="form.category_id" required>
                <option v-for="category in filteredCategories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
            </div>

            <!-- Amount -->
            <div class="mb-3">
              <label for="amount" class="form-label">Amount</label>
              <input type="number" class="form-control" v-model="form.amount" step="0.01" required />
            </div>

            <!-- Description -->
            <div class="mb-3">
              <label for="description" class="form-label">Description</label>
              <textarea class="form-control" v-model="form.description" rows="2"></textarea>
            </div>

            <!-- Submit button -->
            <div class="modal-footer justify-content-center">
              <button type="submit" class="btn btn-success w-100">Add Transaction</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import axiosInstance from '@/api/axiosInstance';


export default defineComponent({
  name: 'AddTransactionModal',
  props: {
    table_id: {
      type: Number,
      required: true,
    },
  },
  setup(props, { emit }) {
    const form = ref({
      date: '',
      type: 'income',
      category_id: null,
      amount: 0,
      description: '',
    });

    const categories = ref([]);
    const filteredCategories = ref([]);

    // Fetch categories from the server
    const fetchCategories = async () => {
      try {
        if (!props.table_id) {
          return;
        }
        const response = await axiosInstance.get(`/api/categories/${props.table_id}/`);
        categories.value = response.data;
        filterCategories();
      } catch (error) {
        console.error('Failed to load categories:', error);
      }
    };

    // Filter categories based on the selected type
    const filterCategories = () => {
      if (form.value.type === 'income') {
        filteredCategories.value = categories.value.filter((cat) => cat.type === 'income');
      } else {
        filteredCategories.value = categories.value.filter((cat) => cat.type === 'expense');
      }
    };

    const handleCategoriesUpdated = () => {
      fetchCategories(); // Обновляем категории
    };


    onMounted(fetchCategories);

    // Submit the transaction
    const submitTransaction = async () => {
      try {
        await axiosInstance.post(`/api/transactions/add/${props.table_id}/`, {
          date: form.value.date,
          type: form.value.type,
          category: form.value.category_id,
          amount: form.value.amount,
          description: form.value.description,
        });
        emit('transaction-added'); // Эмитим событие для обновления таблицы
        resetForm(); // Сбрасываем форму
        hide(); // Закрываем модальное окно
      } catch (error) {
        console.error('Failed to add transaction:', error);
      }
    };

    // Reset the form
    const resetForm = () => {
      form.value = {
        date: '',
        type: 'income',
        category_id: null,
        amount: 0,
        description: '',
      };
    };

    // Hide the modal
    const hide = () => {
      const modalElement = document.getElementById('addTransactionModal');
      if (modalElement) {
        let bootstrapModal = window.bootstrap.Modal.getInstance(modalElement);
        if (!bootstrapModal) {
          bootstrapModal = new window.bootstrap.Modal(modalElement);
        }
        bootstrapModal.hide();
      }
    };

    // Fetch categories when the component is mounted
    onMounted(fetchCategories);

    return {
      form,
      categories,
      filteredCategories,
      submitTransaction,
      hide,
      filterCategories,
      handleCategoriesUpdated,
    };
  },
});
</script>

<style scoped>
/* Custom Header Style */
.custom-header {
  background-color: #6c63ff;
  border-bottom: none;
}

/* Modal Content Styling */
.modal-content {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.modal-body {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}
</style>
