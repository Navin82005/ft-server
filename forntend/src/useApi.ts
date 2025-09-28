// src/api.js
import axios from "axios";
export const api = axios.create({ baseURL: "/", timeout: 120000 });

// optional: attach token if you later add auth
api.interceptors.request.use((cfg) => {
  const t = localStorage.getItem("token");
  if (t) cfg.headers.Authorization = `Bearer ${t}`;
  return cfg;
});
