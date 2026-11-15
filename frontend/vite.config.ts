import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // dev-режим вне docker: проксируем API на бэкенд
      "/health": "http://localhost:8001",
      "/dialer": "http://localhost:8001",
    },
  },
});
