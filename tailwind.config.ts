import type { Config } from "tailwindcss"

const config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
    "*.{js,ts,jsx,tsx,mdx}",
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))", // Основной фон приложения
        foreground: "hsl(var(--foreground))", // Основной цвет текста
        primary: {
          // Глубокая вода: фон верхней панели, заголовки, фон основного экрана.
          DEFAULT: "#003B46", // Глубокая вода
          foreground: "#C4DFE6", // Морская пена (для текста на primary фоне)
        },
        secondary: {
          // Океан: основные кнопки и активные элементы.
          DEFAULT: "#07575B", // Океан
          foreground: "#C4DFE6", // Морская пена (для текста на secondary фоне)
        },
        accent: {
          // Волна: второстепенные кнопки, прогресс-бар.
          DEFAULT: "#66A5AD", // Волна
          foreground: "#003B46", // Глубокая вода (для текста на accent фоне)
        },
        muted: {
          // Морская пена: фон счётчика минут, фон уведомлений, подложки для информации.
          DEFAULT: "#C4DFE6", // Морская пена
          foreground: "#003B46", // Глубокая вода (для текста на muted фоне)
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config

export default config
