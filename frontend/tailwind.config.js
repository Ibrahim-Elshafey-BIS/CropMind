/**
 * CropMind - Tailwind CSS Configuration
 * Professional natural green theme for farm management dashboard
 * 
 * Primary: Emerald green (natural/agricultural)
 * Accent: Warm amber (soil/harvest)
 * 
 * Author: CropMind Team
 * Date: 2026
 */

import defaultTheme from 'tailwindcss/defaultTheme';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary: Emerald green - main brand color
        // Used for buttons, navigation bars, active states, and primary CTAs
        primary: {
          50: '#ecfdf5',   // Very light green - backgrounds
          100: '#d1fae5',  // Light green - light card backgrounds
          200: '#a7f3d0',  // Soft mint - secondary backgrounds
          300: '#6ee7b7',  // Medium green - borders, highlights
          400: '#34d399',  // Bright green - icons, badges
          500: '#10b981',  // Emerald 500 - primary buttons, main CTAs
          600: '#059669',  // Dark green - hover states, active nav
          700: '#047857',  // Deep green - headers, footers, dark elements
          800: '#065f46',  // Very dark green - text on light backgrounds
          900: '#064e3b',  // Almost black green - heavy text, high contrast
        },
        
        // Accent: Warm amber - secondary accent color
        // Represents soil/earth/harvest, used sparingly for highlights
        accent: {
          50: '#fffbeb',   // Very light amber - subtle accent backgrounds
          100: '#fef3c7',  // Light amber - light accent cards
          200: '#fde68a',  // Soft amber - accent borders
          300: '#fcd34d',  // Medium amber - highlights, attention
          400: '#fbbf24',  // Bright amber - important icons
          500: '#f59e0b',  // Amber 500 - accent buttons, warnings
          600: '#d97706',  // Dark amber - hover on accent elements
          700: '#b45309',  // Deep amber - text on light accent backgrounds
        },
        
        // Success: For positive indicators (crop health >70, profit, completed tasks)
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          700: '#15803d',
        },
        
        // Warning: For medium alerts (health 40-70, low stock, attention needed)
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          700: '#b45309',
        },
        
        // Danger: For critical alerts (health <40, anomalies, urgent issues)
        danger: {
          50: '#fef2f2',
          500: '#ef4444',
          700: '#b91c1c',
        },
        
        // Neutral: Warm grays (not blue/cool) for text and neutral backgrounds
        // Warm grays feel more natural and agricultural
        neutral: {
          50: '#fafaf9',   // Very warm white - page backgrounds
          100: '#f5f5f4',  // Light warm gray - card backgrounds
          200: '#e7e5e4',  // Soft warm gray - borders, dividers
          300: '#d6d3d1',  // Medium warm gray - secondary text, disabled
          400: '#a8a29e',  // Darker warm gray - tertiary text
          500: '#78716c',  // Warm gray 500 - body text
          600: '#57534e',  // Dark warm gray - strong body text
          700: '#44403c',  // Very dark warm gray - headings
          800: '#292524',  // Almost black warm gray - heavy headings
          900: '#1c1917',  // Black warm gray - darkest text
        },
      },
      
      fontFamily: {
        // Cairo - Arabic-friendly sans-serif font
        // Will be loaded from Google Fonts in index.css
        cairo: ['Cairo', ...defaultTheme.fontFamily.sans],
      },
      
      borderRadius: {
        // Custom card radius for consistent rounded corners on cards and panels
        'card': '1rem',
      },
    },
  },
  plugins: [],
};
