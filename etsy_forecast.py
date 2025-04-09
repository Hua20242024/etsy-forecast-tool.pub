import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from datetime import datetime, timedelta

# --- App Setup ---
st.set_page_config(page_title="📦 Inventory Optimizer Pro", layout="centered")
st.title("📦 Smart Inventory Manager")

# --- Data Processing ---
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        # Flexible column detection
        date_col = next((col for col in df.columns if 'date' in col.lower()), None)
        sales_col = next((col for col in df.columns if any(x in col.lower() for x in ['units', 'sales', 'qty'])), None)
        product_col = next((col for col in df.columns if 'product' in col.lower()), None)
        
        if not all([date_col, sales_col, product_col]):
            st.error("❌ Required columns not found. Need: date, units_sold, product")
            st.stop()
            
        df = df.rename(columns={
            date_col: 'date',
            sales_col: 'units_sold',
            product_col: 'product'
        })
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date').dropna(subset=['date', 'units_sold'])
    
    except Exception as e:
        st.error(f"❌ Data error: {str(e)}")
        st.stop()

# --- Inventory Calculations ---
def calculate_inventory(forecast, current_stock, days_on_hand, safety_stock=10, lead_time=7):
    avg_daily = forecast['yhat'].mean()
    
    # Convert days on hand to unit count
    current_inventory_units = avg_daily * days_on_hand if days_on_hand else current_stock
    
    # Calculate critical metrics
    reorder_point = (avg_daily * lead_time) + safety_stock
    days_remaining = (current_inventory_units - reorder_point) / avg_daily if avg_daily > 0 else 0
    stockout_date = (datetime.now() + timedelta(days=current_inventory_units/avg_daily)).strftime('%b %d') if avg_daily > 0 else "N/A"
    
    return {
        'avg_daily': round(avg_daily, 1),
        'reorder_point': round(reorder_point),
        'safety_stock': safety_stock,
        'current_units': round(current_inventory_units),
        'days_remaining': round(days_remaining, 1),
        'stockout_date': stockout_date,
        'reorder_date': (datetime.now() + timedelta(days=days_remaining)).strftime('%b %d') if days_remaining > 0 else "NOW",
        'order_qty': max(round(avg_daily * lead_time * 1.5), 10)  # Minimum 10 units
    }

# --- Main App ---
uploaded_file = st.file_uploader("Upload sales CSV", type=["csv"])
df = load_data(uploaded_file) if uploaded_file else None

if df is not None:
    # Product Selection
    products = df['product'].unique()
    selected_product = st.selectbox("Select Product", products)
    
    if selected_product:
        product_df = df[df['product'] == selected_product]
        
        # Forecasting
        model = Prophet(weekly_seasonality=True, daily_seasonality=False)
        model.fit(product_df.rename(columns={'date':'ds', 'units_sold':'y'}))
        future = model.make_future_dataframe(periods=60)  # 60-day forecast
        forecast = model.predict(future)
        
        # --- Inventory Control Panel ---
        st.subheader("🛒 Inventory Controls")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            days_on_hand = st.number_input(
                "Current Inventory (days supply)", 
                min_value=1, 
                max_value=365, 
                value=30,
                help="How many days of inventory you currently have"
            )
        
        with col2:
            safety_stock = st.number_input(
                "Safety Stock (units)", 
                min_value=0, 
                max_value=100, 
                value=10,
                help="Extra buffer inventory"
            )
        
        with col3:
            lead_time = st.number_input(
                "Lead Time (days)", 
                min_value=1, 
                max_value=30, 
                value=7,
                help="Days needed to receive new stock"
            )
        
        # Calculate inventory status
        inventory = calculate_inventory(
            forecast, 
            product_df['units_sold'].iloc[-1],  # Fallback if days_on_hand not used
            days_on_hand,
            safety_stock,
            lead_time
        )
        
        # --- Display Results ---
        st.subheader("📊 Inventory Status")
        
        # Color-coded alert
        if inventory['days_remaining'] <= lead_time:
            alert = st.error
            icon = "🚨"
            message = f"**URGENT REORDER NEEDED** (Stockout: {inventory['stockout_date']})"
        else:
            alert = st.success
            icon = "✅"
            message = f"**Inventory Healthy** (Stockout: {inventory['stockout_date']})"
        
        alert(f"""
        {icon} **Status:** {message}  
        **Avg Daily Sales:** {inventory['avg_daily']} units/day  
        **Current Stock:** ~{inventory['current_units']} units ({days_on_hand} days)  
        **Safety Stock:** {safety_stock} units  
        **Reorder Point:** {inventory['reorder_point']} units  
        """)
        
        # Recommendation cards
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Suggested Order Date", 
                inventory['reorder_date'],
                help="When to place your next order"
            )
        
        with col2:
            st.metric(
                "Suggested Order Qty", 
                f"{inventory['order_qty']} units",
                help="Based on 1.5x lead time demand"
            )
        
        # Compact plot
        st.subheader("📈 Sales Forecast")
        fig, ax =
