// src/models.ts

export interface Category {
    id: number;
    name: string;
    type: 'income' | 'expense';
}

export interface Transaction {
    id: number;
    date: string;
    category: Category;
    type: 'income' | 'expense';
    amount: number;
    description?: string;
}

export interface Table {
    id: number;
    name: string;
    description?: string;
    user: number;
}

export interface Summary {
    category__name: string;
    total: number;
}

export interface TableDetailResponse {
    table: Table;
    transactions: Transaction[];
    expense_summary: Summary[];
    income_summary: Summary[];
    categories: Category[];
    total_income: number;
    total_expense: number;
    net_total: number;
}
