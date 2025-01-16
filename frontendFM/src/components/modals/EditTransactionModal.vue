<template>
  <div
    class="modal fade"
    id="editTransactionModal"
    tabindex="-1"
    aria-labelledby="editTransactionModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <!-- Custom Header -->
        <div class="modal-header custom-header">
          <h5 class="modal-title text-white" id="editTransactionModalLabel">Edit Transaction</h5>
          <button
            type="button"
            class="btn-close btn-close-white"
            data-bs-dismiss="modal"
            aria-label="Close"
            @click="resetForm"
          ></button>
        </div>

        <!-- Form Body -->
        <form @submit.prevent="saveChanges">
          <div class="modal-body">
            <!-- Date -->
            <div class="mb-3">
              <label for="editTransactionDate" class="form-label">Date</label>
              <input
                type="date"
                class="form-control"
                v-model="transactionData.date"
                id="editTransactionDate"
                required
              />
            </div>

            <!-- Type -->
            <div class="mb-3">
              <label for="editTransactionType" class="form-label">Type</label>
              <select
                class="form-select"
                v-model="transactionData.type"
                id="editTransactionType"
                @change="filterCategories"
                required
              >
                <option value="income">Income</option>
                <option value="expense">Expense</option>
              </select>
            </div>

            <!-- Category -->
            <div class="mb-3">
              <label for="editTransactionCategory" class="form-label">Category</label>
              <select
                class="form-select"
                v-model="transactionData.category"
                id="editTransactionCategory"
                required
              >
                <option
                  v-for="category in filteredCategories"
                  :key="category.id"
                  :value="category.id"
                >
                  {{ category.name }}
                </option>
              </select>
            </div>

            <!-- Amount -->
            <div class="mb-3">
              <label for="editTransactionAmount" class="form-label">Amount</label>
              <input
                type="number"
                step="0.01"
                class="form-control"
                v-model="transactionData.amount"
                id="editTransactionAmount"
                required
              />
            </div>

            <!-- Description -->
            <div class="mb-3">
              <label for="editTransactionDescription" class="form-label">Description</label>
              <textarea
                class="form-control"
                v-model="transactionData.description"
                id="editTransactionDescription"
                rows="2"
                maxlength="50"
                placeholder="Add a description (optional)"
              ></textarea>
            </div>
          </div>

          <!-- Footer Buttons -->
          <div class="modal-footer justify-content-center">
            <button type="submit" class="btn btn-success w-100">Save Changes</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import axiosInstance from '@/api/axiosInstance';

export default defineComponent({
  name: 'EditTransactionModal',
  props: {
    transaction: {
      type: Object,
      required: true,
    },
    categories: {
      type: Array,
      required: true,
    },
  },
  setup(props, { emit }) {
    // Reactive transaction data
    const transactionData = ref({ ...props.transaction });
    const categories = ref(props.categories);
    const filteredCategories = ref([]);

    // Filter categories based on type
    const filterCategories = () => {
      if (transactionData.value.type === 'income') {
        filteredCategories.value = categories.value.filter((cat) => cat.type === 'income');
      } else {
        filteredCategories.value = categories.value.filter((cat) => cat.type === 'expense');
      }
    };

    // Watch for changes in props
    watch(
      () => props.transaction,
      (newTransaction) => {
        transactionData.value = { ...newTransaction };
        filterCategories();
      },
      { immediate: true }
    );

    watch(
      () => props.categories,
      (newCategories) => {
        categories.value = newCategories;
        filterCategories();
      }
    );

    // Save changes to the transaction
    const saveChanges = async () => {
      try {
        const updatedTransaction = {
          id: transactionData.value.id,
          date: transactionData.value.date,
          type: transactionData.value.type,
          amount: transactionData.value.amount,
          description: transactionData.value.description,
          category: transactionData.value.category,
        };

        console.log('Saving changes...', updatedTransaction);

        // Отправляем PUT запрос
        const response = await axiosInstance.put(`/api/transactions/${transactionData.value.id}/edit/`, updatedTransaction);

        console.log('Transaction updated:', response.data);

        // Эмитим событие для обновления списка транзакций
        emit('transaction-updated');

        // Удаляем модальный фон и сбрасываем стили
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
          backdrop.remove();
        }
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';

        // Закрываем модальное окно программно
        const modalElement = document.getElementById('editTransactionModal');
        if (modalElement) {
          // Используем getOrCreateInstance вместо getInstance
          const modalInstance = bootstrap.Modal.getOrCreateInstance(modalElement);
          modalInstance.hide();
        }
      } catch (error) {
        console.error('Error updating transaction:', error.response?.data || error.message);
      }
    };

    return {
      transactionData,
      saveChanges,
      filteredCategories,
      filterCategories,
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
