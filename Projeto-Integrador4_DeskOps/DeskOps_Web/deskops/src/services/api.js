import axios from "axios";

// URL base do backend Django
const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api/",
});

// Interceptor: adiciona automaticamente o token JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
