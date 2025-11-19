import pandas as pd
import numpy as np
import re
from pathlib import Path
from datetime import datetime

# Product pricing (individual unit prices)
PRODUCT_PRICES = {
    'COF1': 69.0,           # HIM Coffee
    'HERCOF1': 69.0,        # HER Coffee
    'spr/x1': 89.0,         # Spray Up
    'VGOMX': 89.0,          # Vigomax
    'HBLISS': 89.0,         # HER Bliss
    'SHAKER': 0.0,          # Shaker (free item, no revenue)
    'COFFEE CUP V1': 0.0,   # Coffee Cup (free item, no revenue)
    'TP-COF': 0.0,          # Trial Pack (free item, no revenue)
    'TP-HERCOF': 0.0,       # Trial Pack (free item, no revenue)
}

# Function to calculate weighted price for combo products
def calculate_combo_revenue(breakdown, combo_price):
    """Calculate revenue contribution for each product in a combo based on individual prices"""
    if combo_price == 0 or not breakdown:
        return {}
    
    # Calculate total value of individual products
    total_individual_value = 0
    for sku, qty in breakdown:
        if sku in PRODUCT_PRICES:
            total_individual_value += PRODUCT_PRICES[sku] * qty
    
    # If total individual value is 0, distribute evenly
    if total_individual_value == 0:
        num_products = sum(qty for _, qty in breakdown)
        if num_products == 0:
            return {}
        price_per_unit = combo_price / num_products
        revenue_dict = {}
        for sku, qty in breakdown:
            if sku not in revenue_dict:
                revenue_dict[sku] = 0
            revenue_dict[sku] += price_per_unit * qty
        return revenue_dict
    
    # Calculate weight based on individual prices
    revenue_dict = {}
    for sku, qty in breakdown:
        if sku in PRODUCT_PRICES:
            individual_value = PRODUCT_PRICES[sku] * qty
            weight = individual_value / total_individual_value
            revenue_contribution = combo_price * weight
            if sku not in revenue_dict:
                revenue_dict[sku] = 0
            revenue_dict[sku] += revenue_contribution
    
    return revenue_dict

# Function to map combo SKUs to single SKUs
def create_sku_mapping():
    """Create mapping from combo SKUs to single SKUs with quantities"""
    mapping = {}
    
    # Load combo and single SKU files
    combo_sku = pd.read_excel('Data/Ref SKU/Combo SKU.xlsx')
    single_sku = pd.read_excel('Data/Ref SKU/Single SKU.xlsx')
    
    # Base single SKU mappings
    base_mapping = {
        'HIM': 'COF1',  # HIM Coffee base unit
        'HER': 'HERCOF1',  # HER Coffee base unit
        'COF': 'COF1',  # HIM Coffee (alternative)
        'SPU': 'spr/x1',  # Spray Up base unit
        'VGO': 'VGOMX',  # VIGOMAX base unit
    }
    
    # Process each combo SKU
    for _, row in combo_sku.iterrows():
        combo_name = str(row['SKU Name']).strip()
        title = str(row['Title']).upper() if pd.notna(row['Title']) else ''
        
        # Initialize breakdown
        breakdown = []
        
        # Skip if empty
        if not combo_name or combo_name == 'nan':
            continue
        
        # Pattern matching for common combo SKUs
        # HIM[number] pattern (e.g., HIM3 = 3 boxes of HIM Coffee)
        if re.match(r'^HIM(\d+)$', combo_name):
            num = int(re.match(r'^HIM(\d+)$', combo_name).group(1))
            breakdown.append(('COF1', num))
        
        # HER[number] pattern (e.g., HER3 = 3 boxes of HER Coffee)
        elif re.match(r'^HER(\d+)$', combo_name):
            num = int(re.match(r'^HER(\d+)$', combo_name).group(1))
            breakdown.append(('HERCOF1', num))
        
        # COF[number] pattern (e.g., COF3 = 3 boxes of HIM Coffee)
        elif re.match(r'^COF(\d+)$', combo_name):
            num = int(re.match(r'^COF(\d+)$', combo_name).group(1))
            breakdown.append(('COF1', num))
        
        # HERCOF[number] pattern
        elif re.match(r'^HERCOF(\d+)$', combo_name):
            num = int(re.match(r'^HERCOF(\d+)$', combo_name).group(1))
            breakdown.append(('HERCOF1', num))
        
        # SPU[number] pattern (e.g., SPU3 = 3 bottles of Spray Up)
        elif re.match(r'^SPU(\d+)$', combo_name):
            num = int(re.match(r'^SPU(\d+)$', combo_name).group(1))
            breakdown.append(('spr/x1', num))
        
        # SPU or SPU-A = 1 bottle of Spray Up
        elif combo_name == 'SPU' or combo_name.startswith('SPU-'):
            breakdown.append(('spr/x1', 1))
        
        # SPUHIM pattern (HIM Coffee + Spray Up)
        elif combo_name == 'SPUHIM' or combo_name.startswith('SPUHIM'):
            breakdown.append(('COF1', 1))
            breakdown.append(('spr/x1', 1))
        
        # SPUHIM-A pattern (similar)
        elif 'SPUHIM' in combo_name and '-A' in combo_name:
            breakdown.append(('COF1', 1))
            breakdown.append(('spr/x1', 1))
        
        # HIM1 or HIM1-A = 1 box of HIM Coffee
        elif combo_name == 'HIM1' or combo_name.startswith('HIM1-'):
            breakdown.append(('COF1', 1))
        
        # HER1 = 1 box of HER Coffee
        elif combo_name == 'HER1' or combo_name.startswith('HER1-'):
            breakdown.append(('HERCOF1', 1))
        
        # HIM2 = 2 boxes of HIM Coffee
        elif combo_name == 'HIM2' or combo_name.startswith('HIM2-'):
            breakdown.append(('COF1', 2))
        
        # HIMHER1 pattern (1 HIM + 1 HER)
        elif combo_name == 'HIMHER1':
            breakdown.append(('COF1', 1))
            breakdown.append(('HERCOF1', 1))
        
        # 2HIMVGO pattern (2 HIM Coffee + 1 VIGOMAX)
        elif combo_name == '2HIMVGO':
            breakdown.append(('COF1', 2))
            breakdown.append(('VGOMX', 1))
        
        # 3HIM3HER pattern (3 HIM Coffee + 3 HER Coffee)
        elif combo_name == '3HIM3HER':
            breakdown.append(('COF1', 3))
            breakdown.append(('HERCOF1', 3))
        
        # HIM3SHA-V2 pattern (3 HIM Coffee + Shaker)
        elif 'HIM3SHA' in combo_name:
            breakdown.append(('COF1', 3))
            breakdown.append(('SHAKER', 1))
        
        # HER3SHA-V2 pattern (3 HER Coffee + Shaker)
        elif 'HER3SHA' in combo_name:
            breakdown.append(('HERCOF1', 3))
            breakdown.append(('SHAKER', 1))
        
        # HIM3TP pattern (3 HIM Coffee + Trial Pack)
        elif combo_name == 'HIM3TP':
            breakdown.append(('COF1', 3))
            breakdown.append(('TP-COF', 1))
        
        # HER3TP pattern (3 HER Coffee + Trial Pack)
        elif combo_name == 'HER3TP':
            breakdown.append(('HERCOF1', 3))
            breakdown.append(('TP-HERCOF', 1))
        
        # TPHIM pattern (Trial Pack HIM)
        elif combo_name == 'TPHIM':
            breakdown.append(('TP-COF', 1))
        
        # TPHER pattern (Trial Pack HER)
        elif combo_name == 'TPHER':
            breakdown.append(('TP-HERCOF', 1))
        
        # COFFEECUP-V1 or COFFEE CUP V1 pattern
        elif 'COFFEECUP' in combo_name or 'COFFEE CUP' in combo_name:
            breakdown.append(('COFFEE CUP V1', 1))
        
        # SHA-V2 pattern (Shaker)
        elif 'SHA-V2' in combo_name or 'SHAKER' in combo_name:
            breakdown.append(('SHAKER', 1))
        
        # If no pattern matched, check if it's already a single SKU
        if not breakdown:
            # Check if it exists in single SKU list
            if combo_name in single_sku['SKU Name'].values:
                breakdown.append((combo_name, 1))
            else:
                # Default: keep as is (might be a combo we don't know how to break down)
                breakdown.append((combo_name, 1))
        
        mapping[combo_name] = breakdown
    
    return mapping

# Load all data files
print("Loading data files...")

# BigSeller Orders
print("Loading BigSeller Orders...")
bigseller = pd.read_csv('Data/BigSeller Orders/bigseller_orders.csv', low_memory=False)

# TikTok Shop Orders - DrSamhanWellness (FACT TABLE)
print("Loading TikTok Shop Orders - DrSamhanWellness (FACT TABLE)...")
tt_dr_oct = pd.read_csv('Data/DrSamhanWellness/creator_order_all_20251001000000_20251031235959_864265660.csv')
tt_dr_nov = pd.read_csv('Data/DrSamhanWellness/creator_order_all_20251101000000_20251118235959_800700552.csv')
tt_dr_oct['source'] = 'DrSamhanWellness'
tt_dr_nov['source'] = 'DrSamhanWellness'

# TikTok Shop Orders - HIM Clinic (FACT TABLE)
print("Loading TikTok Shop Orders - HIM Clinic (FACT TABLE)...")
tt_him_oct = pd.read_csv('Data/HIM Clinic/creator_order_all_20251001000000_20251031235959_2611784.csv')
tt_him_nov = pd.read_csv('Data/HIM Clinic/creator_order_all_20251101000000_20251119235959_462128984.csv')
tt_him_oct['source'] = 'HIM Clinic'
tt_him_nov['source'] = 'HIM Clinic'

# Combine TikTok orders from FACT TABLES only
tiktok_orders = pd.concat([tt_dr_oct, tt_dr_nov, tt_him_oct, tt_him_nov], ignore_index=True)
print(f"Total TikTok orders loaded from FACT TABLES: {len(tiktok_orders)}")

# Filter BigSeller for Oct-Nov 2025 and TikTok marketplace only
print("\nFiltering BigSeller for Oct-Nov 2025 and TikTok marketplace...")
bigseller['order_date'] = pd.to_datetime(bigseller['order_date'], errors='coerce')
bigseller_oct_nov = bigseller[
    (bigseller['order_date'] >= '2025-10-01') & 
    (bigseller['order_date'] <= '2025-11-30') &
    (bigseller['marketplace'] == 'TikTok')
].copy()
print(f"BigSeller Oct-Nov TikTok orders: {len(bigseller_oct_nov)}")

# Filter for Completed/Shipped/Processing status
print("\nFiltering for Completed/Shipped/Processing status...")
bigseller_filtered = bigseller_oct_nov[
    bigseller_oct_nov['order_status'].isin(['Completed', 'Shipped', 'Processing'])
].copy()
print(f"BigSeller Completed/Shipped/Processing TikTok: {len(bigseller_filtered)}")

tiktok_filtered = tiktok_orders[
    tiktok_orders['Order Status'].isin(['Completed', 'Shipped', 'Processing'])
].copy()
print(f"TikTok Completed/Shipped/Processing: {len(tiktok_filtered)}")

# Prepare TikTok data for merging
print("\nPreparing TikTok data for linking...")
tiktok_filtered['Order ID'] = tiktok_filtered['Order ID'].astype(str)
tiktok_filtered['sales_channel'] = tiktok_filtered.apply(
    lambda row: f"TikTok Shop - {row['Creator Username']} - {row['Content Type']}"
    if pd.notna(row['Creator Username']) and pd.notna(row['Content Type'])
    else f"TikTok Shop - {row['Creator Username']}" if pd.notna(row['Creator Username'])
    else "TikTok Shop - Unknown",
    axis=1
)
tiktok_filtered['sku'] = tiktok_filtered['Seller SKU'].astype(str)
tiktok_filtered['quantity'] = pd.to_numeric(tiktok_filtered['Quantity'], errors='coerce').fillna(0)

# Create lookup dictionaries for TikTok orders
# First, create lookup by Order ID only (for cases where SKU might not match exactly)
tiktok_order_lookup = tiktok_filtered.groupby('Order ID').agg({
    'Content Type': 'first',  # Get content type
    'Creator Username': 'first'
}).reset_index()

tiktok_order_content_type = {}
tiktok_order_creator = {}
def normalize_content_type(content_type):
    """Normalize content type variations"""
    if pd.isna(content_type) or content_type == '':
        return 'Unknown'
    content_type_str = str(content_type).strip()
    # Normalize variations
    if 'Livestream' in content_type_str or content_type_str == 'Live':
        return 'Live'
    if 'External Traffic Program' in content_type_str:
        return 'External Traffic Programme'
    return content_type_str

for _, row in tiktok_order_lookup.iterrows():
    order_id = str(row['Order ID'])
    tiktok_order_content_type[order_id] = normalize_content_type(row['Content Type'])
    tiktok_order_creator[order_id] = row['Creator Username'] if pd.notna(row['Creator Username']) else 'Unknown'

# Also create lookup by Order ID + SKU for more precise matching
tiktok_lookup = tiktok_filtered.groupby(['Order ID', 'sku']).agg({
    'sales_channel': 'first',
    'Content Type': 'first',
    'quantity': 'sum'
}).reset_index()
tiktok_lookup_dict = {}
tiktok_content_type_dict = {}
for _, row in tiktok_lookup.iterrows():
    key = (str(row['Order ID']), str(row['sku']))
    tiktok_lookup_dict[key] = row['sales_channel']
    tiktok_content_type_dict[key] = normalize_content_type(row['Content Type'])

print(f"Created lookup dictionaries with {len(tiktok_lookup_dict)} entries (Order ID + SKU)")
print(f"Created Order ID lookup with {len(tiktok_order_content_type)} entries")
print(f"Sample content types in lookup: {list(set(list(tiktok_content_type_dict.values())[:20]))}")


# Process BigSeller data
print("Processing BigSeller data and linking with TikTok...")
bigseller_filtered['order_no'] = bigseller_filtered['order_no'].astype(str)
bigseller_filtered['sku'] = bigseller_filtered['sku'].astype(str)
bigseller_filtered['quantity'] = pd.to_numeric(bigseller_filtered['quantity'], errors='coerce').fillna(0)

# Create sales channel and content type: use creator/content type from TikTok data when available
# Otherwise use TikTok store name
def get_sales_channel(row):
    # Try to find in TikTok lookup (has creator/content type info)
    key = (str(row['order_no']), str(row['sku']))
    if key in tiktok_lookup_dict:
        return tiktok_lookup_dict[key]
    # If not found, use default TikTok format with store name
    return f"TikTok - {row['marketplace_store']}" if pd.notna(row['marketplace_store']) and row['marketplace_store'] != '' else "TikTok - Unknown"

def get_content_type(row):
    order_id = str(row['order_no']).strip()
    sku = str(row['sku']).strip()
    # First try exact match with Order ID + SKU
    key = (order_id, sku)
    if key in tiktok_content_type_dict:
        return tiktok_content_type_dict[key]
    # If not found, try lookup by Order ID only (fallback)
    if order_id in tiktok_order_content_type:
        return tiktok_order_content_type[order_id]
    # If still not found, return Unknown
    return 'Unknown'

bigseller_filtered['sales_channel'] = bigseller_filtered.apply(get_sales_channel, axis=1)
bigseller_filtered['content_type'] = bigseller_filtered.apply(get_content_type, axis=1)

# Separate orders: those with content type (from FACT TABLES) vs those without
bigseller_with_content_type = bigseller_filtered[bigseller_filtered['content_type'] != 'Unknown'].copy()
bigseller_without_content_type = bigseller_filtered[bigseller_filtered['content_type'] == 'Unknown'].copy()

print(f"\nContent type distribution after lookup:")
print(bigseller_filtered['content_type'].value_counts())
print(f"\nTotal rows: {len(bigseller_filtered)}")
print(f"Rows with content type (from FACT TABLES): {len(bigseller_with_content_type)}")
print(f"Rows without content type (to be listed separately): {len(bigseller_without_content_type)}")


# Save orders without content type to a separate table
if len(bigseller_without_content_type) > 0:
    unknown_content_type_table = bigseller_without_content_type[['order_no', 'order_date', 'order_status', 'marketplace', 'marketplace_store', 'sku', 'quantity', 'price', 'product_subtotal', 'order_total']].copy()
    unknown_content_type_table.to_csv('tiktok_orders_unknown_content_type.csv', index=False)
    print(f"\nSaved {len(unknown_content_type_table)} TikTok orders without content type to: tiktok_orders_unknown_content_type.csv")

# Create SKU mapping
print("\nCreating SKU mapping from combo to single SKUs...")
sku_mapping = create_sku_mapping()
print(f"Created mapping for {len(sku_mapping)} SKUs")

# Break down combo SKUs into single SKUs
# ONLY process orders from FACT TABLES (those with content_type != 'Unknown')
print("\nBreaking down combo SKUs into individual units (FACT TABLE orders only)...")
expanded_sales = []

for _, row in bigseller_with_content_type.iterrows():
    sales_channel = row['sales_channel']
    content_type = row['content_type']
    combo_sku = str(row['sku']).strip()
    combo_quantity = row['quantity']
    combo_price = pd.to_numeric(row.get('price', 0), errors='coerce') or 0
    
    # Check if this SKU is in our mapping
    if combo_sku in sku_mapping:
        # Break down the combo SKU
        breakdown = sku_mapping[combo_sku]
        # Calculate revenue distribution
        revenue_dict = calculate_combo_revenue(breakdown, combo_price)
        
        for single_sku, multiplier in breakdown:
            quantity = combo_quantity * multiplier
            # Get revenue for this product (per unit)
            revenue_per_unit = revenue_dict.get(single_sku, 0) / multiplier if multiplier > 0 else 0
            total_revenue = revenue_per_unit * quantity
            
            expanded_sales.append({
                'sales_channel': sales_channel,
                'content_type': content_type,
                'sku': single_sku,
                'quantity_sold': quantity,
                'revenue': total_revenue
            })
    else:
        # SKU not in mapping - try to infer from pattern
        breakdown = []
        
        # HIM[number] pattern (e.g., HIM3 = 3 boxes of HIM Coffee)
        if re.match(r'^HIM(\d+)(-.*)?$', combo_sku):
            num = int(re.match(r'^HIM(\d+)(-.*)?$', combo_sku).group(1))
            breakdown.append(('COF1', num))
        
        # HER[number] pattern (e.g., HER3 = 3 boxes of HER Coffee)
        elif re.match(r'^HER(\d+)(\+.*|-.*)?$', combo_sku):
            num = int(re.match(r'^HER(\d+)(\+.*|-.*)?$', combo_sku).group(1))
            breakdown.append(('HERCOF1', num))
            # HER3+1 might mean 3 HER + 1 something, but for now just count the HER
            if '+1' in combo_sku:
                breakdown.append(('HERCOF1', 1))  # Add 1 more HER
        
        # SPU or SPU-A = 1 bottle of Spray Up
        elif combo_sku == 'SPU' or combo_sku.startswith('SPU-'):
            breakdown.append(('spr/x1', 1))
        
        # SPUHIM pattern (HIM Coffee + Spray Up)
        elif 'SPUHIM' in combo_sku:
            breakdown.append(('COF1', 1))
            breakdown.append(('spr/x1', 1))
        
        # 2HIMVGO pattern (2 HIM Coffee + 1 VIGOMAX)
        elif combo_sku == '2HIMVGO':
            breakdown.append(('COF1', 2))
            breakdown.append(('VGOMX', 1))
        
        # HIM1-A = 1 box of HIM Coffee
        elif combo_sku.startswith('HIM1-'):
            breakdown.append(('COF1', 1))
        
        # COFFEECUP-V1 or COFFEE CUP V1 pattern
        elif 'COFFEECUP' in combo_sku or 'COFFEE CUP' in combo_sku:
            breakdown.append(('COFFEE CUP V1', 1))
        
        # SHA-V2 pattern (Shaker)
        elif 'SHA-V2' in combo_sku:
            breakdown.append(('SHAKER', 1))
        
        # If we found a breakdown, use it
        if breakdown:
            # Calculate revenue distribution
            revenue_dict = calculate_combo_revenue(breakdown, combo_price)
            
            for single_sku, multiplier in breakdown:
                quantity = combo_quantity * multiplier
                # Get revenue for this product (per unit)
                revenue_per_unit = revenue_dict.get(single_sku, 0) / multiplier if multiplier > 0 else 0
                total_revenue = revenue_per_unit * quantity
                
                expanded_sales.append({
                    'sales_channel': sales_channel,
                    'content_type': content_type,
                    'sku': single_sku,
                    'quantity_sold': quantity,
                    'revenue': total_revenue
                })
        else:
            # SKU not in mapping and no pattern match - check if it's a single product
            if combo_sku in PRODUCT_PRICES:
                # Single product, use individual price
                total_revenue = PRODUCT_PRICES[combo_sku] * combo_quantity
            else:
                # Unknown product, use combo price
                total_revenue = combo_price * combo_quantity
            
            expanded_sales.append({
                'sales_channel': sales_channel,
                'content_type': content_type,
                'sku': combo_sku,
                'quantity_sold': combo_quantity,
                'revenue': total_revenue
            })

# Convert to DataFrame
expanded_df = pd.DataFrame(expanded_sales)


# Aggregate by content type and product (focus on Content Type → Product)
print("Aggregating by content type and product...")
final_sales = expanded_df.groupby(['content_type', 'sku']).agg({
    'quantity_sold': 'sum',
    'revenue': 'sum'
}).reset_index()


# Round revenue to 2 decimal places
final_sales['revenue'] = final_sales['revenue'].round(2)

# Sort by content type and quantity (focus on Content Type → Product)
final_sales = final_sales.sort_values(['content_type', 'quantity_sold'], ascending=[True, False])

print(f"\nFinal sales table shape: {final_sales.shape}")
print(f"Unique content types: {final_sales['content_type'].nunique()}")
print(f"Unique SKUs: {final_sales['sku'].nunique()}")
print(f"Total Revenue: RM {final_sales['revenue'].sum():,.2f}")
print(f"\nNOTE: This table only includes orders from FACT TABLES (DrSamhanWellness and HIM Clinic)")
print(f"Structure: Content Type -> Product (with quantity_sold and revenue)")
print(f"Orders without content type are saved separately in: tiktok_orders_unknown_content_type.csv")

# Save to CSV
output_file = 'final_sales_table_quantity.csv'
try:
    final_sales.to_csv(output_file, index=False)
    print(f"\nSaved final sales table to: {output_file}")
except PermissionError:
    print(f"\nWarning: Could not save to {output_file} (file may be open).")
    print("Please close the file and run the script again, or the data is available in memory.")
    print("\nFirst few rows of the data:")
    print(final_sales.head(20))

# Display summary
print("\n=== SALES BY CONTENT TYPE (Quantity) ===")
content_type_qty = final_sales.groupby('content_type')['quantity_sold'].sum().sort_values(ascending=False)
print(content_type_qty)

print("\n=== SALES BY CONTENT TYPE (Revenue) ===")
content_type_rev = final_sales.groupby('content_type')['revenue'].sum().sort_values(ascending=False)
print(content_type_rev)

print("\n=== TOP 20 PRODUCTS BY QUANTITY ===")
product_summary = final_sales.groupby('sku')['quantity_sold'].sum().sort_values(ascending=False).head(20)
print(product_summary)

print("\n=== SALES BY CONTENT TYPE ===")
content_type_summary = final_sales.groupby('content_type')['quantity_sold'].sum().sort_values(ascending=False)
print(content_type_summary)

print("\n=== SAMPLE OF FINAL TABLE ===")
print(final_sales.head(20))

