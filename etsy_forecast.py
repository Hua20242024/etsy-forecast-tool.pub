import streamlit as st
import pandas as pd
from prophet import Prophet

st.title("🛍️ Etsy Restocking Alerts")

# 1. CSV Upload
uploaded_file = st.file_uploader("Upload Etsy Sales CSV (Needs 'ds' and 'y' columns)")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # 2. Rename columns to Prophet's required format
    df = df.rename(columns={'date': 'ds', 'units_sold': 'y'})  # CHANGE THESE TO MATCH YOUR CSV
    
    # 3. Train model
    model = Prophet()
    model.fit(df)
    
    # 4. Forecast
    future = model.make_future_dataframe(periods=90)
    forecast = model.predict(future)
    
    # 5. Show results
    st.subheader("📈 90-Day Demand Forecast")
    st.line_chart(forecast.set_index('ds')[['yhat']])
    
    # 6. Restock alert
    st.warning(f"🚨 Reorder when inventory drops below: {int(forecast['yhat'].mean())} units")
