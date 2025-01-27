<template>
  <div>
    <!-- Navbar -->
    <Navbar />

    <!-- Main Content -->
    <div class="container py-4">
      <!-- Buttons to open modals -->
      <div class="d-flex justify-content-center mb-4">
        <div class="button-container d-flex gap-3">
          <button class="btn btn-success w-25" data-bs-toggle="modal" data-bs-target="#addTransactionModal">
            Add Transaction
          </button>
          <button class="btn btn-secondary w-25" data-bs-toggle="modal" data-bs-target="#manageCategoriesModal">
            Manage Categories
          </button>
        </div>
      </div>

      <!-- Expense Summary -->
      <div class="row">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h5>Expense Summary</h5>
            </div>
            <div class="card-body">
              <table class="table">
                <thead>
                  <tr>
                    <th>Category</th>
                    <th>Total Expense</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="expense in expenseSummary" :key="expense.category__name">
                    <td>{{ expense.category__name }}</td>
                    <td>{{ expense.total }}</td>
                  </tr>
                  <tr class="table-dark">
                    <td><strong>Total Expenses</strong></td>
                    <td><strong>{{ totalExpense }}</strong></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Income Summary -->
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h5>Income Summary</h5>
            </div>
            <div class="card-body">
              <table class="table">
                <thead>
                  <tr>
                    <th>Category</th>
                    <th>Total Income</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="income in incomeSummary" :key="income.category__name">
                    <td>{{ income.category__name }}</td>
                    <td>{{ income.total }}</td>
                  </tr>
                  <tr class="table-dark">
                    <td><strong>Total Income</strong></td>
                    <td><strong>{{ totalIncome }}</strong></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Pie Charts -->
      <div class="row mt-4">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h5>Expense Breakdown</h5>
            </div>
            <div class="card-body">
              <canvas id="expenseChart"></canvas>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h5>Income Breakdown</h5>
            </div>
            <div class="card-body">
              <canvas id="incomeChart"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Transactions Table -->
      <div class="card mt-4">
        <div class="card-header">
          <h5>Transactions</h5>
        </div>
        <div class="card-body">
          <table class="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Category</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Description</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="transaction in transactions"
                :key="transaction.id"
                @click="setSelectedTransaction(transaction)"
              >
                <td>{{ transaction.date }}</td>
                <td>{{ transaction.category.name }}</td>
                <td>{{ transaction.type }}</td>
                <td>{{ transaction.amount }}</td>
                <td>{{ transaction.description }}</td>
                <td class="text-center">
                  <div class="d-flex justify-content-center gap-2">
                    <button
                      class="btn btn-outline-warning btn-sm"
                      data-bs-toggle="modal"
                      data-bs-target="#editTransactionModal"
                    >
                      Edit
                    </button>
                    <button
                      class="btn btn-outline-danger btn-sm"
                      data-bs-toggle="modal"
                      data-bs-target="#deleteTransactionModal"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Modals -->
      <AddTransactionModal
        :table_id="id"
        @transaction-added="fetchTableDetails"
        @categories-updated="fetchCategories"
      />
      <ManageCategoriesModal
        :table_id="id"
        @categories-updated="fetchCategories"
      />

      <EditTransactionModal
        :transaction="selectedTransaction"
        :categories="categories"
        @transaction-updated="fetchTableDetails"
      />
      <DeleteTransactionModal
        :transactionId="selectedTransactionId"
        @transaction-deleted="fetchTableDetails"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, PropType } from 'vue';
import axiosInstance from '@/api/axiosInstance';
import Navbar from '@/components/Navbar.vue';
import AddTransactionModal from '@/components/modals/AddTransactionModal.vue';
import ManageCategoriesModal from '@/components/modals/ManageCategoriesModal.vue';
import EditTransactionModal from '@/components/modals/EditTransactionModal.vue';
import DeleteTransactionModal from '@/components/modals/DeleteTransactionModal.vue';
import Chart from 'chart.js/auto';

interface Expense {
  category__name: string;
  total: number;
}

interface Income {
  category__name: string;
  total: number;
}

interface Transaction {
  id: number;
  date: string;
  category: { name: string };
  type: string;
  amount: number;
  description: string;
}

let expenseChartInstance: Chart | null = null;
let incomeChartInstance: Chart | null = null;

export default defineComponent({
  name: 'TableDetail',
  components: {
    Navbar,
    AddTransactionModal,
    ManageCategoriesModal,
    EditTransactionModal,
    DeleteTransactionModal,
  },
  props: {
    id: {
      type: Number,
      required: true,
    },
  },
  setup(props) {
    const expenseSummary = ref<Expense[]>([]);
    const incomeSummary = ref<Income[]>([]);
    const transactions = ref<Transaction[]>([]);
    const categories = ref([]);
    const totalExpense = ref(0);
    const totalIncome = ref(0);
    const selectedTransaction = ref<Transaction | null>(null);
    const selectedTransactionId = ref<number | null>(null);

    const fetchTableDetails = async () => {
      try {
        const response = await axiosInstance.get(`/api/tables/${props.id}/`);
        const data = response.data;

        expenseSummary.value = data.expense_summary;
        incomeSummary.value = data.income_summary;
        transactions.value = data.transactions;
        categories.value = data.categories;
        totalExpense.value = data.total_expense;
        totalIncome.value = data.total_income;

        renderCharts();
      } catch (error) {
        console.error('Error fetching table details:', error);
      }
    };

    const setSelectedTransaction = (transaction: Transaction) => {
      selectedTransaction.value = transaction;
      selectedTransactionId.value = transaction.id;
    };

    const renderCharts = () => {
      if (expenseChartInstance) expenseChartInstance.destroy();
      if (incomeChartInstance) incomeChartInstance.destroy();

      if (expenseSummary.value.length > 0) {
        const expenseCtx = (document.getElementById('expenseChart') as HTMLCanvasElement)?.getContext('2d');
        expenseChartInstance = new Chart(expenseCtx, {
          type: 'pie',
          data: {
            labels: expenseSummary.value.map((item) => item.category__name),
            datasets: [
              {
                data: expenseSummary.value.map((item) => item.total),
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'],
              },
            ],
          },
          options: { responsive: true, plugins: { legend: { position: 'top' } } },
        });
      }

      if (incomeSummary.value.length > 0) {
        const incomeCtx = (document.getElementById('incomeChart') as HTMLCanvasElement)?.getContext('2d');
        incomeChartInstance = new Chart(incomeCtx, {
          type: 'pie',
          data: {
            labels: incomeSummary.value.map((item) => item.category__name),
            datasets: [
              {
                data: incomeSummary.value.map((item) => item.total),
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'],
              },
            ],
          },
          options: { responsive: true, plugins: { legend: { position: 'top' } } },
        });
      }
    };

    onMounted(fetchTableDetails);

    return {
      expenseSummary,
      incomeSummary,
      transactions,
      categories,
      totalExpense,
      totalIncome,
      fetchTableDetails,
      setSelectedTransaction,
      selectedTransaction,
      selectedTransactionId,
    };
  },
});
</script>

<style scoped>
/* Основные стили контейнера */
.container {
  margin-top: 70px;
}

/* Стили для кнопок */
.button-container {
  display: flex;
  gap: 10px;
}

/* Стили для таблицы транзакций */
table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  text-align: left; /* Выравнивание по левому краю */
  vertical-align: middle; /* Вертикальное выравнивание по центру */
  padding: 12px; /* Отступ внутри ячеек */
}

th {
  background-color: #f8f9fa;
  font-weight: bold;
}

tr:nth-child(even) {
  background-color: #f2f2f2;
}

tr:hover {
  background-color: #e9ecef;
}

/* Стили для кнопок действий */
.btn-outline-warning {
  color: #856404;
  border-color: #ffeeba;
  background-color: #fff5db;
}

.btn-outline-warning:hover {
  color: #856404;
  background-color: #ffeeba;
  border-color: #ffeeba;
}

.btn-outline-danger {
  color: #721c24;
  border-color: #f5c6cb;
  background-color: #f8d7da;
}

.btn-outline-danger:hover {
  color: #721c24;
  background-color: #f5c6cb;
  border-color: #f5c6cb;
}

/* Минимальная ширина кнопок */
.button-container button {
  min-width: 200px;
}

th, td {
  text-align: center;
}

/* Центрирование кнопок внутри ячеек */
.d-flex {
  justify-content: center;
}
</style>
