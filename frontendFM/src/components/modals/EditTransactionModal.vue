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
                v-model="transactionData.category.id" <!-- Оновлено -->
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
import { defineComponent, ref, watch, onMounted } from 'vue';
import type { PropType } from 'vue';
import * as bootstrap from 'bootstrap';
import axiosInstance from '@/api/axiosInstance';
import type { Transaction, Category } from '@/models';


export default defineComponent({
  name: 'EditTransactionModal',
  props: {
    transaction: {
      type: Object as PropType<Transaction>,
      required: true,
    },
    categories: {
      type: Array as PropType<Category[]>,
      required: true,
    },
  },
  setup(props, { emit }) {
    const transactionData = ref<Transaction>({ ...props.transaction });
    const filteredCategories = ref<Category[]>([]);

    const filterCategories = () => {
      if (transactionData.value.type === 'income') {
        filteredCategories.value = props.categories.filter((cat) => cat.type === 'income');
      } else {
        filteredCategories.value = props.categories.filter((cat) => cat.type === 'expense');
      }
    };

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
      () => {
        filterCategories();
      }
    );

    const saveChanges = async () => {
      try {
        const updatedTransaction = {
          id: transactionData.value.id,
          date: transactionData.value.date,
          type: transactionData.value.type,
          amount: transactionData.value.amount,
          description: transactionData.value.description,
          category_id: transactionData.value.category.id, // Передаємо лише ID категорії
        };

        const response = await axiosInstance.put(`/api/transactions/${transactionData.value.id}/edit/`, updatedTransaction);
        emit('transaction-updated');

        const modalElement = document.getElementById('editTransactionModal');
        if (modalElement) {
          const modalInstance = bootstrap.Modal.getOrCreateInstance(modalElement);
          modalInstance.hide();
        }
      } catch (error) {
        if (error instanceof Error) {
          console.error('Error updating transaction:', error.message);
        }
      }
    };

    const resetForm = () => {
      transactionData.value = { ...props.transaction };
    };

    onMounted(() => {
      const modalElement = document.getElementById('editTransactionModal');
      if (modalElement) {
        modalElement.addEventListener('hidden.bs.modal', () => {
          const backdrop = document.querySelector('.modal-backdrop');
          if (backdrop) backdrop.remove();
          document.body.classList.remove('modal-open');
          document.body.style.overflow = '';
          document.body.style.paddingRight = '';
        });
      }
    });

    return {
      transactionData,
      saveChanges,
      filteredCategories,
      filterCategories,
      resetForm,
    };
  },
});
</script>

<style scoped>
/* Ваші стилі тут */
.modal-body {
  text-align: center;
}

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
