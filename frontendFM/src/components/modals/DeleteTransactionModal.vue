<template>
  <div
    class="modal fade"
    id="deleteTransactionModal"
    tabindex="-1"
    aria-labelledby="deleteTransactionModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header bg-danger text-white">
          <h5 class="modal-title" id="deleteTransactionModalLabel">Delete Transaction</h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body text-center">
          <p class="fs-5">Are you sure you want to delete this transaction?</p>
          <p class="text-muted">This action cannot be undone.</p>
        </div>
        <div class="modal-footer justify-content-center">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-danger"
            @click="confirmDeletion"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import type { PropType } from 'vue';
import axiosInstance from '@/api/axiosInstance';
import { Modal } from 'bootstrap';
import { AxiosError } from 'axios'; // Import AxiosError type

export default defineComponent({
  name: 'DeleteTransactionModal',
  props: {
    transactionId: {
      type: [Number, null] as PropType<number | null>, // Обновить тип для поддержки null
      required: true,
    },
  },
  setup(props, { emit }) {
    const confirmDeletion = async () => {
      try {
        if (props.transactionId === null) {
          console.error("Transaction ID is null");
          return;
        }

        // Отправляем запрос на удаление транзакции
        const response = await axiosInstance.delete(`/api/transactions/${props.transactionId}/delete/`);
        emit('transaction-deleted');

        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
          backdrop.remove();
        }

        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';

        // Закрываем модальное окно программно
        const modalElement = document.getElementById('deleteTransactionModal');
        if (modalElement) {
          // Используем getOrCreateInstance вместо getInstance
          const modalInstance = Modal.getOrCreateInstance(modalElement);
          modalInstance.hide();
        }
      } catch (error: unknown) {
        // Type assertion to AxiosError
        if (error instanceof AxiosError) {
          console.error('Error deleting transaction:', error.response?.data || error.message);
        } else {
          console.error('An unexpected error occurred:', error);
        }
      }
    };

    return {
      confirmDeletion,
    };
  },
});
</script>


<style scoped>
.modal-body {
  text-align: center;
}
</style>
