/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                void: "#05070A",      // Deepest Space Blue
                slate: "#1E293B",     // Deep Slate Surface
                violet: "#6B46C1",    // Star-Trail Violet
                ethereal: "#F8FAFC",  // Ghostly White Highlight
                text: "#E2E8F0",      // Celestial Grey Text
                amber: "#B79051",     // Keeps amber as a secondary accent if needed
            },
            fontFamily: {
                serif: ['"Cormorant Garamond"', 'serif'],
                mono: ['"JetBrains Mono"', 'monospace'],
                sans: ['Inter', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
