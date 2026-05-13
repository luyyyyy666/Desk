import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: {
          50: "#fffaf0",
          100: "#f7efd9",
          200: "#e9ddbf",
          300: "#d8c59d",
        },
        ink: "#242015",
        orange: "#f4a51c",
        moss: "#7f9448",
        pond: "#2f7f97",
      },
      boxShadow: {
        ink: "6px 6px 0 rgba(36, 32, 21, 0.22)",
        "ink-lg": "12px 12px 0 rgba(36, 32, 21, 0.22)",
      },
      fontFamily: {
        sans: [
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Microsoft YaHei",
          "Noto Sans CJK SC",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};

export default config;
