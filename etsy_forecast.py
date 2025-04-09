import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from datetime import datetime, timedelta

# --- App Setup ---
st.set_page_config(page_title="🛍️ Etsy Restock Pro", layout="centered")
st.title("🛍️ Etsy Restock Manager")

# --- Data Processing ---
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        # Flexible column naming
        date_col = next((col for col in df.columns if 'date' in col.lower()), 'date')
        sales_col = next((col for col in df.columns if 'units' in col.lower() or 'sales' in col.lower()), 'units_sold')
        product_col = next((col for col in df.columns if 'product' in col.lower()), 'product')
        
        df = df.rename(columns={
            date_col: 'date',
            sales_col: 'units_sold',
            product_col: 'product'
        })
        
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date')
    
    except Exception as e:
        st.error(f"❌ Data loading failed: {str(e)}")
        st.stop()

# --- Plotting Function ---
def create_compact_plot(actual, forecast, product):
    fig, ax = plt.subplots(figsize=(8, 3))  # Smaller figure size
    
    # Plot actual data
    ax.plot(actual['ds'], actual['y'], 'b-', linewidth=1.5, marker='o', markersize=4, label='Actual')
    
    # Plot forecast
    ax.plot(forecast['ds'], forecast['yhat'], 'r--', linewidth=1.5, label='Forecast')
    ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='red', alpha=0.1)
    
    # Formatting
    ax.set_title(f"{product} Sales", fontsize=10)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))  # Show every 5th day
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    ax.legend(fontsize=8)
    ax.grid(True, linestyle=':', alpha=0.3)
    
    plt.tight_layout()  # Prevent label overlap
    return fig

# --- Reorder Logic ---
def calculate_reorder(forecast, current_stock, lead_time=7, safety_factor=1.2):
    avg_daily = forecast['yhat'].mean()
    reorder_point = avg_daily * lead_time * safety_factor
    days_remaining = current_stock / avg_daily if avg_daily > 0 else 0
    
    return {
        'reorder_point': round(reorder_point),
        'reorder_qty': round(avg_daily * lead_time * 1.5),  # 1.5x lead time demand
        'days_remaining': round(days_remaining),
        'stockout_date': (datetime.now() + timedelta(days=days_remaining)).strftime('%b %d')
    }

# --- Main App ---
uploaded_file = st.file_uploader("Upload sales CSV", type=["csv"])
df = load_data(uploaded_file) if uploaded_file else None

if df is not None:
    # Inventory Settings
    with st.sidebar:
        st.header("⚙️ Inventory Settings")
        lead_time = st.slider("Lead Time (days)", 1, 30, 7)
        safety_stock = st.slider("Safety Factor", 1.0, 2.0, 1.2, step=0.1)
        
    # Product Selection
    products = df['product'].unique()
    selected_product = st.selectbox("Select Product", products)
    
    if selected_product:
        product_df = df[df['product'] == selected_product]
        
        # Forecasting
        model = Prophet(weekly_seasonality=True, daily_seasonality=False)
        model.fit(product_df.rename(columns={'date':'ds', 'units_sold':'y'}))
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        
        # Current Stock Input
        current_stock = st.number_input(
            f"Current {selected_product} Inventory", 
            min_value=0,
            value=int(product_df['units_sold'].mean() * 10)  # Default stock
        )
        
        # Display Plot
        st.pyplot(create_compact_plot(
            product_df.rename(columns={'date':'ds', 'units_sold':'y'}),
            forecast,
            selected_product
        ))
        
        # Reorder Alert
        reorder = calculate_reorder(forecast, current_stock, lead_time, safety_stock)
        
        if current_stock <= reorder['reorder_point']:
            st.error(f"""
            **🚨 REORDER NOW**  
            - **Suggested Qty:** {reorder['reorder_qty']} units  
            - **Projected Stockout:** {reorder['stockout_date']}  
            - **Lead Time:** {lead_time} days  
            """)
        else:
            st.success(f"""
            **✅ Inventory OK**  
            - **Reorder Point:** {reorder['reorder_point']} units  
            - **Current Stock:** {current_stock} units  
            - **Days Remaining:** {reorder['days_remaining']}  
            - **Next Check:** {(datetime.now() + timedelta(days=3)).strftime('%b %d')}  
            """)
            
        # Raw Data
        with st.expander("📊 View Raw Data"):
            st.dataframe(product_df)
else:
    st.info("ℹ️ Please upload a CSV file with columns: date, units_sold, product")
