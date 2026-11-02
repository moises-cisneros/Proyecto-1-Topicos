/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        sentinel: {
          dark: '#2b2d42',
          gray: '#8d99ae',
          white: '#edf2f4',
          danger: '#ef233c',
          primary: '#4361ee',
          canvasDark: '#1e2030',
          cardSubtleDark: '#232537',
          canvasLight: '#edf2f4',
          cardLight: '#ffffff',
          cardSubtleLight: '#f4f7f8',
          phishDarkBg: '#3a1017',
          phishLightBg: '#ffebee',
          hamDarkBg: '#1c2e28',
          hamLightBg: '#e8f0fe',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
};
