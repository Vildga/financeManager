<template>
  <div
    class="modal fade"
    id="manageCategoriesModal"
    tabindex="-1"
    aria-labelledby="manageCategoriesModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content rounded shadow">
        <!-- Custom Header -->
        <div class="modal-header custom-header">
          <h5 class="modal-title text-white" id="manageCategoriesModalLabel">Manage Categories</h5>
          <button
            type="button"
            class="btn-close btn-close-white"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>

        <!-- Form Body -->
        <div class="modal-body">
          <!-- Форма добавления категории -->
          <form @submit.prevent="addCategory">
            <div class="mb-3">
              <label for="categoryName" class="form-label">Category Name</label>
              <input type="text" class="form-control" v-model="categoryName" required />
            </div>
            <div class="mb-3">
              <label for="categoryType" class="form-label">Category Type</label>
              <select class="form-select" v-model="categoryType" required>
                <option value="income">Income</option>
                <option value="expense">Expense</option>
              </select>
            </div>
            <button type="submit" class="btn btn-success w-100">Add Category</button>
          </form>

          <hr />

          <!-- Список категорий -->
          <div v-if="categories.length > 0">
            <!-- Доходы -->
            <h6 class="text-success mt-3">Income Categories</h6>
            <ul class="list-group">
              <li
                v-for="category in incomeCategories"
                :key="category.id"
                class="list-group-item d-flex justify-content-between align-items-center"
              >
                {{ category.name }}
                <button class="btn btn-danger btn-sm" @click="deleteCategory(category.id)">
                  Delete
                </button>
              </li>
            </ul>

            <!-- Расходы -->
            <h6 class="text-danger mt-3">Expense Categories</h6>
            <ul class="list-group">
              <li
                v-for="category in expenseCategories"
                :key="category.id"
                class="list-group-item d-flex justify-content-between align-items-center"
              >
                {{ category.name }}
                <button class="btn btn-danger btn-sm" @click="deleteCategory(category.id)">
                  Delete
                </button>
              </li>
            </ul>
          </div>

          <!-- Сообщение, если категорий нет -->
          <p v-else class="text-muted">No categories available.</p>

          <!-- Кнопка для загрузки стандартных категорий -->
          <button class="btn btn-secondary mb-3 w-100 load-btn" @click="loadDefaultCategories">
            Load Default Categories
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import axiosInstance from '@/api/axiosInstance';

// Define the Category interface
interface Category {
  id: number;
  name: string;
  type: 'income' | 'expense';  // Add any other properties you expect
}

export default defineComponent({
  name: 'ManageCategoriesModal',
  props: {
    table_id: {
      type: Number,
      required: true,
    },
  },
  setup(props, { emit }) {
    const categories = ref<Category[]>([]);
    const categoryName = ref('');
    const categoryType = ref('income');

    const incomeCategories = ref<Category[]>([]);
    const expenseCategories = ref<Category[]>([]);

    const fetchCategories = async () => {
      try {
        const response = await axiosInstance.get(`/api/categories/${props.table_id}/`);
        categories.value = response.data;
        incomeCategories.value = categories.value.filter((cat) => cat.type === 'income');
        expenseCategories.value = categories.value.filter((cat) => cat.type === 'expense');
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    };

    const addCategory = async () => {
      try {
        await axiosInstance.post(`/api/categories/add/${props.table_id}/`, {
          name: categoryName.value,
          type: categoryType.value,
        });
        fetchCategories();
        emit('categories-updated');
        categoryName.value = '';
        categoryType.value = 'income';
      } catch (error) {
        console.error('Error adding category:', error);
      }
    };

    const deleteCategory = async (categoryId: number) => {  // Specify type here
      try {
        await axiosInstance.delete(`/api/categories/delete/${categoryId}/`);
        fetchCategories();
        emit('categories-updated');
      } catch (error) {
        console.error('Error deleting category:', error);
      }
    };

    const loadDefaultCategories = async () => {
      try {
        await axiosInstance.post(`/api/categories/load-default/${props.table_id}/`);
        fetchCategories();
        emit('categories-updated');
      } catch (error) {
        console.error('Error loading default categories:', error);
      }
    };

    onMounted(fetchCategories);

    return {
      categories,
      categoryName,
      categoryType,
      incomeCategories,
      expenseCategories,
      fetchCategories,
      addCategory,
      loadDefaultCategories,
      deleteCategory,
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
