/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        octant: {
          primary: '#6366f1',
          secondary: '#8b5cf6',
          accent: '#a78bfa',
          bg: '#0f172a',
          surface: '#1e293b',
          text: '#f8fafc',
          muted: '#94a3b8',
        },
      },
    },
  },
  plugins: [],
}
