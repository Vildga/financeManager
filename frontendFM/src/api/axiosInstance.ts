import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// Create an axios instance
const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000/',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercept requests
axiosInstance.interceptors.request.use(async (config: AxiosRequestConfig) => {
  const token = localStorage.getItem('token'); // Use const

  // Check if the token is present
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// Intercept responses
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    // If the token has expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) throw new Error('No refresh token found');

        // Refresh the token
        const { data } = await axios.post('http://localhost:8000/api/token/refresh/', {
          refresh: refreshToken,
        });

        // Save the new access token
        localStorage.setItem('token', data.access);

        // Retry the original request
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
