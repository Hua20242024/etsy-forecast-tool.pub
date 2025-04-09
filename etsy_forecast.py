import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- App Setup ---
st.set_page_config(page_title="🛍️ Etsy Restock Pro", layout="centered")
st.title("🛍️ Inventory Manager")

# --- Data Processing ---
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        # Find relevant columns (case insensitive)
        date_col = next((col for col in df.columns if 'date' in col.lower()), 'date')
        sales_col = next((col for col in df.columns if any(x in col.lower() for x in ['units', 'sales', 'qty'])), 'units_sold')
        product_col = next((col for col in df.columns if 'product' in col.lower()), 'product')
        
        df = df.rename(columns={
            date_col: 'date',
            sales_col: 'units_sold',
            product_col: 'product'
        })
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date')
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

# --- Forecasting & Inventory Logic ---
def run_forecast(product_df, current_stock, safety_stock, lead_time):
    # Prepare Prophet data
    train_df = product_df.rename(columns={'date':'ds', 'units_sold':'y'})[['ds','y']]
    
    # Model and forecast
    model = Prophet(weekly_seasonality=True, daily_seasonality=False)
    model.fit(train_df)
    future = model.make_future_dataframe(periods=30)  # 30-day forecast
    forecast = model.predict(future)
    
    # Calculate inventory metrics
    avg_daily = forecast['yhat'].mean()
    reorder_point = (avg_daily * lead_time) + safety_stock
    days_remaining = (current_stock - reorder_point) / avg_daily if avg_daily > 0 else 0
    
    return {
        'forecast': forecast,
        'avg_daily': round(avg_daily, 1),
        'reorder_point': round(reorder_point),
        'days_remaining': max(0, round(days_remaining)),
        'order_qty': max(round(avg_daily * lead_time * 1.5), 10)  # Min 10 units
    }

# --- Main App ---
uploaded_file = st.file_uploader("Upload sales CSV (date, units_sold, product)", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    # Product selection
    product = st.selectbox("Select product", df['product'].unique())
    product_df = df[df['product'] == product]
    
    # Inventory settings
    current_stock = st.number_input(
        "Current inventory (units)", 
        min_value=0, 
        value=50,  # Default 50 units
        help="Your current stock level"
    )
    
    safety_stock = st.number_input(
        "Safety stock (units)", 
        min_value=0, 
        value=10,  # Default 10 units
        help="Extra buffer inventory"
    )
    
    lead_time = st.number_input(
        "Lead time (days)", 
        min_value=1, 
        value=7,  # Default 7 days
        help="Days needed to restock"
    )
    
    # Run forecast
    results = run_forecast(product_df, current_stock, safety_stock, lead_time)
    
    # Display results
    st.subheader("📈 Sales Forecast")
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(product_df['date'], product_df['units_sold'], 'b-', label='Actual')
    ax.plot(results['forecast']['ds'], results['forecast']['yhat'], 'r--', label='Forecast')
    ax.axvline(datetime.now(), color='gray', linestyle=':', label='Today')
    ax.legend()
    st.pyplot(fig)
    
    # Inventory alerts
    st.subheader("🛒 Inventory Status")
    if current_stock <= results['reorder_point']:
        st.error(f"""
        🚨 **Time to reorder!**
        - Suggested quantity: {results['order_qty']} units
        - Stockout in: ~{results['days_remaining']} days
        """)
    else:
        st.success(f"""
        ✅ **Inventory sufficient**
        - Reorder when stock reaches: {results['reorder_point']} units
        - Next check in: {max(3, results['days_remaining'] - lead_time)} days
        """)
    
else:
    st.info("ℹ️ Please upload a CSV file with columns: date, units_sold, product")
    st.download_button(
        "Download sample CSV",
        pd.DataFrame({
            'date': pd.date_range(end=datetime.today(), periods=10).strftime('%Y-%m-%d'),
            'units_sold': np.random.randint(5, 20, 10),
            'product': "Example Product"
        }).to_csv(index=False),
        "sample_sales_data.csv"
    )
