/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.{js,ts,jsx,tsx}",
    "./layouts/**/*.{js,ts,jsx,tsx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#0d7ab3",
        accent: "#b1cae3",
        background: "#ffffff",
        surface: "#f3f6fb",
        border: "#000000",
        text: "#000000",
        muted: "#4b4b4b",
        bar: "#e5eaf2",
        chart: "#0d7ab3",
        success: "#22c55e",
        warning: "#facc15",
        error: "#ef4444",
        info: "#38bdf8",
        archived: "#9ca3af",
        highlight: "#B1CAE3",
        row:"#d9d9d96b"

      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};