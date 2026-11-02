/**
 * SMS Sentinel - Design Tokens & Constants (DESIGN.md)
 * Paleta canónica: https://coolors.co/2b2d42-8d99ae-edf2f4-ef233c-4361ee
 */

export const PALETTE = {
  spaceCadet: '#2b2d42',
  coolGray: '#8d99ae',
  antiflashWhite: '#edf2f4',
  redPantone: '#ef233c',
  techBlue: '#4361ee',
  techBlueHover: '#3751d8',
} as const;

export const SEMANTIC_COLORS = {
  dark: {
    canvas: '#1e2030',
    card: '#2b2d42',
    cardSubtle: '#232537',
    borderSubtle: 'rgba(141, 153, 174, 0.3)',
    borderProminent: '#8d99ae',
    textPrimary: '#edf2f4',
    textSecondary: '#8d99ae',
    textMuted: '#6b778c',
    phishingBg: '#3a1017',
    phishingBorder: '#ef233c',
    phishingText: '#ef233c',
    safeBg: '#1c2e28',
    safeBorder: '#8d99ae',
    safeText: '#a8dadc',
    warningBg: '#2d2415',
    warningBorder: '#f4a261',
    warningText: '#f4a261',
  },
  light: {
    canvas: '#edf2f4',
    card: '#ffffff',
    cardSubtle: '#f4f7f8',
    borderSubtle: 'rgba(141, 153, 174, 0.4)',
    borderProminent: '#8d99ae',
    textPrimary: '#2b2d42',
    textSecondary: '#576275',
    textMuted: '#8d99ae',
    phishingBg: '#ffebee',
    phishingBorder: '#ef233c',
    phishingText: '#ef233c',
    safeBg: '#e8f0fe',
    safeBorder: '#8d99ae',
    safeText: '#2b2d42',
    warningBg: '#fff3e0',
    warningBorder: '#f4a261',
    warningText: '#b25e00',
  },
} as const;

export const TYPOGRAPHY = {
  sans: "Inter, system-ui, -apple-system, sans-serif",
  mono: "'JetBrains Mono', 'Fira Code', monospace",
} as const;
