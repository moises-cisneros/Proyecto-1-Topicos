/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Paleta Canónica Oficial (DESIGN.md)
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
        // Tokens Semánticos Dinámicos
        surface: {
          canvas: 'var(--surface-canvas)',
          card: 'var(--surface-card)',
          subtle: 'var(--surface-subtle)',
        },
        border: {
          subtle: 'var(--border-subtle)',
          prominent: 'var(--border-prominent)',
        },
        text: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          muted: 'var(--text-muted)',
        },
        brand: {
          primary: 'var(--brand-primary)',
          primaryHover: 'var(--brand-primary-hover)',
          danger: 'var(--brand-danger)',
          dark: 'var(--brand-dark)',
          gray: 'var(--brand-gray)',
          light: 'var(--brand-light)',
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
