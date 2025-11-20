import axios from "axios";

const fallbackApiUrl = "https://api.sodmaster.online";
const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim();
const baseURL = configuredApiUrl && configuredApiUrl.length > 0 ? configuredApiUrl : fallbackApiUrl;

const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

export default api;
