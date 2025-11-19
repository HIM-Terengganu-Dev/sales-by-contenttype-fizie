# Sales by Content Type Dashboard

A React dashboard for analyzing TikTok sales data segmented by content type and product.

## Features

- **Product Sales Analysis**: View sales by content type (Live, Video, Showcase, External Traffic Programme)
- **Revenue Tracking**: Track revenue for main products (COF1, spr/x1, HERCOF1, VGOMX)
- **Interactive Filters**: Filter by content type and product
- **Data Export**: Export detailed sales data to CSV
- **Visualizations**: Bar charts and summary cards

## Data Processing

The `sales_analysis.py` script processes raw order data from:
- BigSeller Orders (TikTok marketplace orders)
- TikTok Shop fact tables (DrSamhanWellness, HIM Clinic)

### Key Features:
- Links orders via `order_no` and `Order ID`
- Maps combo SKUs to individual products
- Calculates weighted revenue for combo products
- Filters for October-November 2025 data
- Includes Completed, Shipped, and Processing orders

## Dashboard

The React dashboard is located in the `sales-dashboard` folder.

### Setup

```bash
cd sales-dashboard
npm install
npm run dev
```

### Build for Production

```bash
npm run build
```

## Deployment to Vercel

1. **Connect Repository to Vercel**:
   - Go to [Vercel](https://vercel.com)
   - Import the GitHub repository
   - Select the `sales-dashboard` folder as the root directory

2. **Build Settings**:
   - **Framework Preset**: Vite
   - **Root Directory**: `sales-dashboard`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

3. **Environment Variables**: None required

4. **Deploy**: Click "Deploy" and Vercel will automatically deploy your dashboard

## Data Files

- `final_sales_table_quantity.csv`: Final aggregated sales data
- `tiktok_orders_unknown_content_type.csv`: TikTok orders without content type mapping
- `sales-dashboard/src/data/sales-data.json`: Dashboard data (generated from CSV)

## Products Tracked

Only revenue-driving products are displayed:
- **COF1**: HIM Coffee (RM69 per unit)
- **spr/x1**: Spray Up (RM89 per unit)
- **HERCOF1**: HER Coffee (RM69 per unit)
- **VGOMX**: Vigomax (RM89 per unit)

Free gifts and promotional items are excluded from the dashboard.

## License

Internal use only.

