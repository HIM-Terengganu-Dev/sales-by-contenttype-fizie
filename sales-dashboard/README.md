# Sales Dashboard - TikTok Sales Analysis

A React.js dashboard visualizing TikTok sales data by channel and product for October & November 2025.

## Features

- **Summary Cards**: Total quantity sold, number of sales channels, and products
- **Bar Charts**: Top 15 sales channels and all products
- **Data Tables**: Top 10 channels and products with percentages
- **Pie Charts**: Distribution of top 10 channels and products
- **Responsive Design**: Works on desktop and mobile devices

## Installation

```bash
npm install
```

## Running the Dashboard

```bash
npm run dev
```

The dashboard will open at `http://localhost:5173` (or the next available port).

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` folder.

## Data Source

The dashboard uses data from `src/data/sales-data.json`, which contains sales data segmented by:
- Sales Channel (first level)
- Product/SKU (second level)
- Quantity Sold (individual units)

## Technologies Used

- React
- Vite
- Recharts (for visualizations)
- CSS3 (for styling)
