import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#0f172a",
          accent: "#22c55e"
        },
        sod: {
          primary: "#0F766E",
          primarySoft: "#CCFBF1",
          accent: "#F59E0B",
          bg: "#F9FAFB",
          text: "#0F172A"
        }
      },
      fontFamily: {
        heading: ["Rubik", "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"]
      }
    }
  },
  plugins: []
};

export default config;
