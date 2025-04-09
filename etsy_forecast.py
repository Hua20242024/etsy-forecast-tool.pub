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
        future = model.make_future_dataframe(periods=60)
        forecast = model.predict(future)
        
        # --- Inventory Control Panel ---
        st.subheader("🛒 Inventory Controls")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            days_on_hand = st.number_input(
                "Current Inventory (days supply)", 
                min_value=1, 
                max_value=365, 
                value=30
            )
        
        with col2:
            safety_stock = st.number_input(
                "Safety Stock (units)", 
                min_value=0, 
                max_value=100, 
                value=10
            )
        
        with col3:
            lead_time = st.number_input(
                "Lead Time (days)", 
                min_value=1, 
                max_value=30, 
                value=7
            )
        
        # Calculate inventory status
        inventory = calculate_inventory(
            forecast, 
            product_df['units_sold'].iloc[-1],
            days_on_hand,
            safety_stock,
            lead_time
        )
        
        # --- Display Results ---
        st.subheader("📊 Inventory Status")
        
        if inventory['days_remaining'] <= lead_time:
            st.error(f"""
            🚨 **URGENT REORDER NEEDED**
            - Projected stockout: {inventory['stockout_date']}
            - Suggested order: {inventory['order_qty']} units
            - Order by: {inventory['reorder_date']}
            """)
        else:
            st.success(f"""
            ✅ **Inventory Healthy**
            - Projected stockout: {inventory['stockout_date']}
            - Suggested order date: {inventory['reorder_date']}
            - Suggested order qty: {inventory['order_qty']} units
            """)
        
        # Create compact plot
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot(product_df['date'], product_df['units_sold'], 'b-', label='Actual Sales')
        ax.plot(forecast['ds'], forecast['yhat'], 'r--', label='Forecast')
        ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='red', alpha=0.1)
        ax.axvline(x=datetime.now(), color='gray', linestyle=':', label='Today')
        ax.set_title(f"{selected_product} Sales Forecast")
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.3)
        st.pyplot(fig)
        
else:
    st.info("ℹ️ Please upload a CSV file with columns: date, units_sold, product")
    st.download_button(
        label="📥 Download Sample CSV",
        data=pd.DataFrame({
            'date': pd.date_range(end=datetime.today(), periods=10).strftime('%Y-%m-%d'),
            'units_sold': np.random.randint(5, 20, 10),
            'product': "Sample Product"
        }).to_csv(index=False),
        file_name="sample_inventory_data.csv"
    )
