/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bgDark: "#0B0E14",
        cardDark: "#151A22",
        borderDark: "#232936",
        accentGreen: "#00E676",
        accentRed: "#FF5252",
        accentBlue: "#2979FF",
        accentGold: "#FFD700",
        terminalMuted: "#8B949E",
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"],
      }
    },
  },
  plugins: [],
}
