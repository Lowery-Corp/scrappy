import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    host: "0.0.0.0",
    allowedHosts: ["localhost", "scrappys-house.local", "dscrappy.johnmgrubbs.io", "scrappy.johnmgrubbs.io"],
  }
});