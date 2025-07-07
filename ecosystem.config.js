module.exports = {
  apps: [
    {
      name: "vat-frontend",
      script: "npm",
      args: "run start",
      cwd: "/opt/vat",
      instances: 1,
      exec_mode: "fork",
      env: {
        NODE_ENV: "production",
        NEXT_PUBLIC_API_BASE_URL: "https://www.vertexassistant.ru/api",
        NEXT_PUBLIC_TELEGRAM_BOT_NAME: "VertexAIassistantBOT",
        PORT: 3000,
      },
      error_file: "/var/log/pm2/vat-frontend-error.log",
      out_file: "/var/log/pm2/vat-frontend-out.log",
      log_file: "/var/log/pm2/vat-frontend.log",
      time: true,
      max_memory_restart: "512M",
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: "10s",
    },
  ],
}
