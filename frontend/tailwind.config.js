/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ["class"],
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",
        "./public/index.html"
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                heading: ['Manrope', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace']
            },
            colors: {
                'bg-primary': '#030712',
                'bg-surface': '#111827',
                'bg-surface-highlight': '#1f2937',
            },
            keyframes: {
                'fade-in': {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' }
                },
            },
            animation: {
                'fade-in': 'fade-in 0.3s ease-out',
            }
        }
    },
    plugins: [require("tailwindcss-animate")],
};
