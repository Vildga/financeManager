import axios from 'axios';

// Создаём экземпляр axios
const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000/',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Перехватываем запросы
axiosInstance.interceptors.request.use(async (config) => {
  const token = localStorage.getItem('token'); // Используем const

  // Проверяем, есть ли токен
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// Перехватываем ответы
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Если токен истёк
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) throw new Error('No refresh token found');

        // Обновляем токен
        const { data } = await axios.post('http://localhost:8000/api/token/refresh/', {
          refresh: refreshToken,
        });

        // Сохраняем новый access-токен
        localStorage.setItem('token', data.access);

        // Повторяем оригинальный запрос
        originalRequest.headers.Authorization = `Bearer ${data.access}`;
        return axiosInstance(originalRequest);
      } catch (err) {
        console.error('Token refresh failed:', err);
        alert('Your session has expired. Please log in again.');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;
