import streamlit as st
import pandas as pd
from prophet import Prophet

st.title("🛍️ Etsy Restocking Alerts")

# 1. CSV Upload
uploaded_file = st.file_uploader("Upload your Etsy sales CSV")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # 2. Train model
    model = Prophet()
    model.fit(df)
    
    # 3. Forecast
    future = model.make_future_dataframe(periods=90)  # 3 months
    forecast = model.predict(future)
    
    # 4. Show results
    st.subheader("📈 Next 90-Day Demand Forecast")
    st.line_chart(forecast.set_index('ds')[['yhat']])
    
    # 5. Restock alert
    st.warning(f"🚨 Order more when stock drops below: {int(forecast['yhat'].mean())} units")