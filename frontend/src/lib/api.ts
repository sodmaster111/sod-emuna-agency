import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://backend:8000",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

export default api;
