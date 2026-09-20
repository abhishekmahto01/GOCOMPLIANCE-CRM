/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#0f172a',
          navy: '#0b2b68',
          deepBlue: '#0c38bf',
          royalBlue: '#1557df',
          electricBlue: '#0066FF',
          cyan: '#00D2FF',
          teal: '#2dd4bf',
        }
      },
      boxShadow: {
        'brand-glow': '0 0 40px -10px rgba(0, 102, 255, 0.5)',
        'card-soft': '0 10px 30px -5px rgba(0, 20, 60, 0.06)',
        'button-glow': '0 10px 25px -5px rgba(37, 99, 235, 0.4)',
      },
    },
  },
  plugins: [],
}
