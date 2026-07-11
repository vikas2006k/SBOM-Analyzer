/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cyber: {
          dark: '#0b0f19',      // Dark deep background
          darker: '#06080e',    // Even darker sidebar/cards background
          card: '#111827',      // Card background
          lightCard: '#f8fafc', // Light card background
          border: '#1f2937',    // Border line color
          accent: '#4f46e5',    // Brand Indigo
          emerald: '#10b981',   // Clean status color
          rose: '#f43f5e',      // Risk critical color
          amber: '#f59e0b',     // Medium risk warning color
          textMuted: '#9ca3af', // Gray text
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
