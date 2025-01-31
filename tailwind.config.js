/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ["./templates/**/*.{html,js}"],
  theme: {
    extend: {
      spacing: {
        18: "4.5rem", // 18 in Tailwind spacing scale
      },
    },
  },
  plugins: [require('tailwind-hamburgers')],
}

