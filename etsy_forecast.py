import streamlit as st
import pandas as pd
from prophet import Prophet
import numpy as np

# --- App Config ---
st.set_page_config(page_title="Etsy Restock Pro", layout="wide")
st.title("📦 Etsy Restock Pro: AI-Powered Inventory Alerts")

# --- 1. Data Upload + Prep ---
uploaded_file = st.file_uploader("Upload your Etsy sales CSV (columns: 'date', 'units_sold')")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = df.rename(columns={'date': 'ds', 'units_sold': 'y'})
    df['ds'] = pd.to_datetime(df['ds'])
    
    # --- 2. Auto-Adapt Prophet Model ---
    with st.spinner("🧠 Optimizing forecast for your data..."):
        # Detect data size to adjust seasonality
        days_of_data = (df['ds'].max() - df['ds'].min()).days
        is_new_seller = days_of_data < 60
        
        # Configure Prophet dynamically
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=days_of_data >= 14,  # Only enable if 2+ weeks
            yearly_seasonality=days_of_data >= 365,
            changepoint_prior_scale=0.05 if is_new_seller else 0.2,
            seasonality_mode='additive'
        )
        
        # Fit model
        model.fit(df)
        
        # Forecast 90 days
        future = model.make_future_dataframe(periods=90)
        forecast = model.predict(future)
    
    # --- 3. Visualize Forecast ---
    tab1, tab2 = st.tabs(["📈 Forecast", "🛍️ Restock Plan"])
    
    with tab1:
        fig = model.plot(forecast)
        st.pyplot(fig)
    
    with tab2:
        # --- Smart Inventory Logic ---
        lead_time = st.slider("Lead time (days until new stock arrives)", 7, 30, 14)
        safety_stock = st.slider("Safety stock (extra buffer units)", 0, 50, 10)
        
        # Calculate reorder point (demand during lead time + buffer)
        daily_demand = forecast['yhat'].mean()
        reorder_point = int(daily_demand * lead_time + safety_stock)
        
        # Current inventory simulation
        current_stock = st.number_input("Current inventory units", min_value=0, value=100)
        
        # Alert logic
        if current_stock <= reorder_point:
            st.error(f"🚨 REORDER NOW! Projected stockout in {lead_time} days.")
            st.metric("Optimal reorder quantity", f"{int(reorder_point * 1.5)} units")
        else:
            st.success(f"✅ Inventory healthy. Reorder at {reorder_point} units.")
        
        st.progress(min(100, int(current_stock / reorder_point * 100)))

# --- 4. Empty State ---
else:
    st.markdown("""
    ## How It Works:
    1. Upload your Etsy sales CSV (columns: `date`, `units_sold`)
    2. We predict demand 90 days ahead
    3. Get AI-powered reorder alerts
    """)
    st.image("https://via.placeholder.com/600x300?text=Demo+Etsy+Sales+Data")
