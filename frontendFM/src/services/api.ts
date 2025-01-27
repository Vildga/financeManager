import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/", // Ваш бэкенд
  withCredentials: true, // Включаем отправку куков (если используется сессия)
});

// Интерцептор для добавления токена в заголовки
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token"); // Берём токен из localStorage
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
