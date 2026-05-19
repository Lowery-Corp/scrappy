import axios from "axios";

const AUTH_URL = import.meta.env.VITE_SCRAPPYS_SCRAPYARD_URL;
console.log("API base URL:", AUTH_URL);

export const api = axios.create({
  baseURL: AUTH_URL,
  withCredentials: true,
});