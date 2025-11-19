import { useMemo, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import salesData from './data/sales-data.json'
import './App.css'

function App() {
  const [selectedContentType, setSelectedContentType] = useState('All')
  const [selectedProduct, setSelectedProduct] = useState('All')
  
  // Only include products that drive sales (exclude free gifts)
  const mainProducts = ['COF1', 'spr/x1', 'HERCOF1', 'VGOMX']
  const filteredSalesData = useMemo(() => {
    return salesData.filter(item => mainProducts.includes(item.sku))
  }, [])
  
  // Process data for visualizations
  const { contentTypeData, productData, filteredData, chartData, chartContentTypes, summary } = useMemo(() => {
    // Aggregate by content type
    const contentTypeMap = {}
    const productMap = {}
    
    filteredSalesData.forEach(item => {
      const contentType = item.content_type || 'Unknown'
      const product = item.sku
      const qty = item.quantity_sold || 0
      const rev = item.revenue || 0
      
      // Aggregate by content type
      if (!contentTypeMap[contentType]) {
        contentTypeMap[contentType] = { quantity: 0, revenue: 0 }
      }
      contentTypeMap[contentType].quantity += qty
      contentTypeMap[contentType].revenue += rev
      
      // Aggregate by product
      if (!productMap[product]) {
        productMap[product] = { quantity: 0, revenue: 0 }
      }
      productMap[product].quantity += qty
      productMap[product].revenue += rev
    })
    
    // Convert to arrays
    const contentTypeData = Object.entries(contentTypeMap)
      .map(([name, data]) => ({ 
        name, 
        quantity: Math.round(data.quantity),
        revenue: Math.round(data.revenue * 100) / 100
      }))
      .sort((a, b) => b.quantity - a.quantity)
    
    const productData = Object.entries(productMap)
      .map(([name, data]) => ({ 
        name, 
        quantity: Math.round(data.quantity),
        revenue: Math.round(data.revenue * 100) / 100
      }))
      .sort((a, b) => b.quantity - a.quantity)
    
    // Filter data based on selections
    let filtered = filteredSalesData
    if (selectedContentType !== 'All') {
      filtered = filtered.filter(item => item.content_type === selectedContentType)
    }
    if (selectedProduct !== 'All') {
      filtered = filtered.filter(item => item.sku === selectedProduct)
    }
    
    // Aggregate filtered data by content type and product
    const filteredAgg = {}
    filtered.forEach(item => {
      const key = `${item.content_type}|||${item.sku}`
      if (!filteredAgg[key]) {
        filteredAgg[key] = {
          content_type: item.content_type,
          product: item.sku,
          quantity: 0,
          revenue: 0
        }
      }
      filteredAgg[key].quantity += item.quantity_sold || 0
      filteredAgg[key].revenue += item.revenue || 0
    })
    
    const filteredData = Object.values(filteredAgg)
      .map(item => ({
        ...item,
        quantity: Math.round(item.quantity),
        revenue: Math.round(item.revenue * 100) / 100
      }))
      .sort((a, b) => {
        if (a.content_type !== b.content_type) {
          return a.content_type.localeCompare(b.content_type)
        }
        return b.quantity - a.quantity
      })
    
    // Transform data for grouped bar chart (Product Quantity by Content Type)
    // Group by product, with each content type as a separate dataKey
    const groupedByProduct = {}
    filtered.forEach(item => {
      const product = item.sku
      const contentType = item.content_type || 'Unknown'
      const qty = item.quantity_sold || 0
      const rev = item.revenue || 0
      
      if (!groupedByProduct[product]) {
        groupedByProduct[product] = { product }
      }
      groupedByProduct[product][contentType] = (groupedByProduct[product][contentType] || 0) + qty
      groupedByProduct[product][`${contentType}_revenue`] = (groupedByProduct[product][`${contentType}_revenue`] || 0) + rev
    })
    
    const chartData = Object.values(groupedByProduct)
      .map(item => ({
        ...item,
        // Round all values
        ...Object.keys(item).reduce((acc, key) => {
          if (key !== 'product') {
            acc[key] = typeof item[key] === 'number' ? Math.round(item[key] * 100) / 100 : item[key]
          }
          return acc
        }, {})
      }))
      .sort((a, b) => {
        // Sort by total quantity
        const totalA = Object.keys(a).filter(k => !k.includes('_revenue') && k !== 'product').reduce((sum, k) => sum + (a[k] || 0), 0)
        const totalB = Object.keys(b).filter(k => !k.includes('_revenue') && k !== 'product').reduce((sum, k) => sum + (b[k] || 0), 0)
        return totalB - totalA
      })
    
    // Get unique content types for the chart
    const chartContentTypes = [...new Set(filtered.map(item => item.content_type).filter(Boolean))].sort()
    
    const totalQuantity = Object.values(contentTypeMap).reduce((sum, data) => sum + data.quantity, 0)
    const totalRevenue = Object.values(contentTypeMap).reduce((sum, data) => sum + data.revenue, 0)
    
    // Ensure chartData and chartContentTypes are arrays
    const safeChartData = Array.isArray(chartData) ? chartData : []
    const safeChartContentTypes = Array.isArray(chartContentTypes) ? chartContentTypes : []
    
    return {
      contentTypeData,
      productData,
      filteredData,
      chartData: safeChartData,
      chartContentTypes: safeChartContentTypes,
      summary: {
        totalQuantity: Math.round(totalQuantity),
        totalRevenue: Math.round(totalRevenue * 100) / 100,
        totalContentTypes: contentTypeData.length,
        totalProducts: productData.length
      }
    }
  }, [selectedContentType, selectedProduct, filteredSalesData])
  
  // Get unique values for filters
  const contentTypes = useMemo(() => {
    const unique = [...new Set(filteredSalesData.map(item => item.content_type))].filter(Boolean).sort()
    return ['All', ...unique]
  }, [filteredSalesData])
  
  const products = useMemo(() => {
    const unique = [...new Set(filteredSalesData.map(item => item.sku))].filter(Boolean).sort()
    return ['All', ...unique]
  }, [filteredSalesData])
  
  // Colors for charts
  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00', '#0088fe', '#00c49f', '#ffbb28', '#ff8042']
  
  // Format currency
  const formatCurrency = (value) => `RM ${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

  return (
    <div className="app">
      <header className="app-header">
        <h1>TikTok Sales Dashboard</h1>
        <p>Product Sales by Content Type</p>
      </header>
      
      {/* Filters */}
      <div className="filters-section">
        <div className="filter-group">
          <label htmlFor="contentTypeFilter">Content Type:</label>
          <select 
            id="contentTypeFilter"
            value={selectedContentType} 
            onChange={(e) => setSelectedContentType(e.target.value)}
            className="filter-select"
          >
            {contentTypes.map(ct => (
              <option key={ct} value={ct}>{ct}</option>
            ))}
          </select>
        </div>
        
        <div className="filter-group">
          <label htmlFor="productFilter">Product:</label>
          <select 
            id="productFilter"
            value={selectedProduct} 
            onChange={(e) => setSelectedProduct(e.target.value)}
            className="filter-select"
          >
            {products.map(p => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>
      </div>
      
      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card">
          <h3>Total Quantity Sold</h3>
          <p className="summary-value">{summary.totalQuantity.toLocaleString()}</p>
          <span className="summary-label">units</span>
        </div>
        <div className="summary-card">
          <h3>Total Revenue</h3>
          <p className="summary-value">{formatCurrency(summary.totalRevenue)}</p>
          <span className="summary-label">sales</span>
        </div>
        <div className="summary-card">
          <h3>Content Types</h3>
          <p className="summary-value">{summary.totalContentTypes}</p>
          <span className="summary-label">types</span>
        </div>
        <div className="summary-card">
          <h3>Products</h3>
          <p className="summary-value">{summary.totalProducts}</p>
          <span className="summary-label">SKUs</span>
        </div>
      </div>
      
      {/* Main Chart: Product Quantity by Content Type */}
      <div className="chart-section main-chart">
        <h2>Product Quantity Sold by Content Type</h2>
        <ResponsiveContainer width="100%" height={500}>
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="product" 
              angle={-45}
              textAnchor="end"
              height={120}
              tick={{ fontSize: 11 }}
            />
            <YAxis />
            <Tooltip 
              formatter={(value, name) => {
                return [value.toLocaleString(), name]
              }}
              labelFormatter={(label) => `Product: ${label}`}
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="custom-tooltip">
                      <p className="tooltip-label">{`Product: ${label}`}</p>
                      {payload.map((entry, index) => (
                        <p key={index} className="tooltip-value">
                          {entry.name}: {entry.value.toLocaleString()}
                        </p>
                      ))}
                    </div>
                  )
                }
                return null
              }}
            />
            <Legend />
            {chartContentTypes.map((contentType, index) => (
              <Bar 
                key={contentType} 
                dataKey={contentType} 
                fill={colors[index % colors.length]} 
                name={contentType}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      {/* Revenue Chart */}
      <div className="chart-section">
        <h2>Product Revenue by Content Type</h2>
        <ResponsiveContainer width="100%" height={500}>
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="product" 
              angle={-45}
              textAnchor="end"
              height={120}
              tick={{ fontSize: 11 }}
            />
            <YAxis />
            <Tooltip 
              formatter={(value) => formatCurrency(value)}
              labelFormatter={(label) => `Product: ${label}`}
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="custom-tooltip">
                      <p className="tooltip-label">{`Product: ${label}`}</p>
                      {payload.map((entry, index) => (
                        <p key={index} className="tooltip-value">
                          {entry.name}: {formatCurrency(entry.value)}
                        </p>
                      ))}
                    </div>
                  )
                }
                return null
              }}
            />
            <Legend />
            {chartContentTypes.map((contentType, index) => (
              <Bar 
                key={contentType} 
                dataKey={`${contentType}_revenue`} 
                fill={colors[index % colors.length]} 
                name={contentType}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      {/* Content Type Distribution */}
      <div className="charts-container">
        <div className="chart-section">
          <h2>Sales by Content Type (Quantity)</h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={contentTypeData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip 
                formatter={(value) => value.toLocaleString()}
              />
              <Legend />
              <Bar dataKey="quantity" fill="#8884d8" name="Quantity Sold" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="chart-section">
          <h2>Sales by Content Type (Revenue)</h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={contentTypeData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip 
                formatter={(value) => formatCurrency(value)}
              />
              <Legend />
              <Bar dataKey="revenue" fill="#82ca9d" name="Revenue (RM)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Data Table */}
      <div className="table-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h2 style={{ margin: 0 }}>Product Sales by Content Type (Detailed View)</h2>
          <button 
            className="export-button"
            onClick={() => {
              // Convert filteredData to CSV
              const headers = ['Content Type', 'Product', 'Quantity Sold', 'Revenue (RM)']
              const csvRows = [
                headers.join(','),
                ...filteredData.map(row => [
                  `"${row.content_type}"`,
                  `"${row.product}"`,
                  row.quantity,
                  row.revenue.toFixed(2)
                ].join(','))
              ]
              const csvContent = csvRows.join('\n')
              
              // Create download link
              const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
              const link = document.createElement('a')
              const url = URL.createObjectURL(blob)
              link.setAttribute('href', url)
              link.setAttribute('download', `sales_by_content_type_${new Date().toISOString().split('T')[0]}.csv`)
              link.style.visibility = 'hidden'
              document.body.appendChild(link)
              link.click()
              document.body.removeChild(link)
            }}
          >
            Export to CSV
          </button>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Content Type</th>
              <th>Product</th>
              <th>Quantity Sold</th>
              <th>Revenue (RM)</th>
            </tr>
          </thead>
          <tbody>
            {filteredData.map((item, index) => (
              <tr key={index}>
                <td>{item.content_type}</td>
                <td>{item.product}</td>
                <td className="number-cell">{item.quantity.toLocaleString()}</td>
                <td className="number-cell">{formatCurrency(item.revenue)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default App
