import axios from "axios";

const api = axios.create({
  baseURL:
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "https://api.sodmaster.online",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API request failed", {
      url: error?.config?.url,
      status: error?.response?.status,
      message: error?.message,
    });
    return Promise.reject(error);
  },
);

export default api;
