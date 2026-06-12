import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: "#060c1a",
          800: "#0a1020",
          700: "#0d1528",
          600: "#111d33",
          500: "#162340",
        },
        accent: {
          DEFAULT: "#00d4aa",
          dark: "#00a882",
          light: "#33ddb8",
        },
        bio: {
          green: "#22c55e",
          blue: "#3b82f6",
          purple: "#a855f7",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "Courier New", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
