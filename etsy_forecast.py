import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# --- App Setup ---
st.set_page_config(page_title="📦 Inventory Optimizer Pro", layout="centered")
st.title("📦 Smart Inventory Manager")

# --- Data Processing ---
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        date_col = next((col for col in df.columns if 'date' in col.lower()), 'date')
        sales_col = next((col for col in df.columns if any(x in col.lower() for x in ['units', 'sales', 'qty']), 'units_sold')
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
    model = Prophet(
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative'
    )
    model.fit(train_df)
    future = model.make_future_dataframe(periods=180)  # 6-month forecast
    forecast = model.predict(future)
    
    # Calculate metrics
    avg_daily = forecast['yhat'].mean()
    avg_monthly = avg_daily * 30
    weekly_seasonality = (forecast['weekly'].max() - forecast['weekly'].min()) * 100
    
    reorder_point = (avg_daily * lead_time) + safety_stock
    days_remaining = (current_stock - reorder_point) / avg_daily if avg_daily > 0 else 0
    
    return {
        'forecast': forecast,
        'avg_daily': round(avg_daily, 1),
        'avg_monthly': round(avg_monthly),
        'weekly_seasonality': round(weekly_seasonality),
        'reorder_point': round(reorder_point),
        'days_remaining': max(0, round(days_remaining)),
        'order_qty': max(round(avg_daily * lead_time * 1.5), 10),
        'stockout_date': (datetime.now() + timedelta(days=current_stock/avg_daily)).strftime('%b %d') if avg_daily > 0 else "N/A"
    }

# --- Main App ---
uploaded_file = st.file_uploader("Upload sales CSV (date, units_sold, product)", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    # Product selection
    product = st.selectbox("Select product", df['product'].unique())
    product_df = df[df['product'] == product]
    
    # Inventory controls
    col1, col2, col3 = st.columns(3)
    with col1:
        current_stock = st.number_input("Current inventory (units)", min_value=0, value=50)
    with col2:
        safety_stock = st.number_input("Safety stock (units)", min_value=0, value=10)
    with col3:
        lead_time = st.number_input("Lead time (days)", min_value=1, value=7)
    
    # Run forecast
    results = run_forecast(product_df, current_stock, safety_stock, lead_time)
    
    # --- Inventory Dashboard ---
    st.subheader("📊 Inventory Dashboard")
    
    # Metrics row
    m1, m2, m3 = st.columns(3)
    m1.metric("Avg Daily Sales", f"{results['avg_daily']} units")
    m2.metric("Avg Monthly Sales", f"{results['avg_monthly']} units")
    m3.metric("Weekly Fluctuation", f"±{results['weekly_seasonality']}%")
    
    st.markdown("---")
    
    # Alerts
    if current_stock <= results['reorder_point']:
        st.error(f"""
        🚨 **URGENT REORDER NEEDED**
        - Suggested quantity: {results['order_qty']} units  
        - Stockout in: ~{results['days_remaining']} days  
        - Projected stockout date: {results['stockout_date']}
        """)
    else:
        st.success(f"""
        ✅ **Inventory Healthy**
        - Reorder point: {results['reorder_point']} units  
        - Current stock lasts: {results['days_remaining'] + lead_time} days  
        - Suggested order date: {(datetime.now() + timedelta(days=results['days_remaining'])).strftime('%b %d')}
        """)
    
    # Forecast plot
    st.subheader("📈 6-Month Sales Forecast")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(product_df['date'], product_df['units_sold'], 'bo', markersize=3, label='Actual Sales')
    ax.plot(results['forecast']['ds'], results['forecast']['yhat'], 'r-', label='Forecast')
    ax.fill_between(results['forecast']['ds'], 
                   results['forecast']['yhat_lower'], 
                   results['forecast']['yhat_upper'], 
                   color='pink', alpha=0.3)
    ax.axvline(datetime.now(), color='gray', linestyle=':', label='Today')
    ax.legend()
    st.pyplot(fig)

else:
    st.info("ℹ️ Please upload a CSV file with columns: date, units_sold, product")
    st.download_button(
        "📥 Download sample CSV",
        pd.DataFrame({
            'date': pd.date_range(end=datetime.today(), periods=30).strftime('%Y-%m-%d'),
            'units_sold': np.random.randint(5, 20, 30),
            'product': "Example Product"
        }).to_csv(index=False),
        "sample_sales_data.csv"
    )
