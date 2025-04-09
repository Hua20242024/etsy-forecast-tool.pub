import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from matplotlib import dates as mdates

# --- App Setup ---
st.set_page_config(page_title="📊 Sales Visualizer", layout="wide")
st.title("📊 Actual vs Forecasted Sales")

# --- Data Processing ---
def process_data(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    return df

# --- Sample Data (Jan 1-10) ---
def generate_sample_data():
    dates = pd.date_range(start="2024-01-01", periods=10)
    products = ["Blue T-Shirt", "White T-Shirt"]
    data = []
    
    for product in products:
        base = 10 if "Blue" in product else 8
        for i, date in enumerate(dates):
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "units_sold": base + (i % 3),  # Simple pattern
                "product": product
            })
    return pd.DataFrame(data)

# --- Main App ---
uploaded_file = st.file_uploader("Upload your sales CSV", type=["csv"])
df = process_data(pd.read_csv(uploaded_file)) if uploaded_file else process_data(generate_sample_data())

# --- Plotting Function ---
def plot_actual_vs_forecast(actual, forecast, product_name):
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Actual data (blue solid line)
    ax.plot(actual['ds'], actual['y'], 
            'b-', linewidth=2, label='Actual Sales')
    
    # Forecast (white dashed line)
    ax.plot(forecast['ds'], forecast['yhat'], 
            'w--', linewidth=2, label='Forecast')
    
    # Uncertainty interval
    ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'],
                   color='gray', alpha=0.2, label='Uncertainty')
    
    # Formatting
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.set_title(f"{product_name} Sales Forecast")
    ax.set_ylabel("Units Sold")
    ax.legend()
    ax.grid(True, linestyle=':', alpha=0.5)
    fig.patch.set_facecolor('#0E1117')  # Match Streamlit dark theme
    ax.set_facecolor('#0E1117')
    
    return fig

# --- Forecasting ---
products = df['product'].unique()
selected_products = st.multiselect("Select products", products, default=products)

for product in selected_products:
    st.subheader(product)
    product_df = df[df['product'] == product]
    
    # Prepare data
    train_df = product_df.rename(columns={'date':'ds', 'units_sold':'y'})[['ds','y']]
    
    # Model and forecast
    model = Prophet(weekly_seasonality=True)
    model.fit(train_df)
    future = model.make_future_dataframe(periods=30)  # 30-day forecast
    forecast = model.predict(future)
    
    # Plot
    fig = plot_actual_vs_forecast(train_df, forecast, product)
    st.pyplot(fig)
    
    # Inventory recommendations
    last_actual_date = train_df['ds'].max()
    st.caption(f"Last actual data point: {last_actual_date.strftime('%b %d')}")
    
    # Show data table
    with st.expander("View raw data"):
        st.dataframe(product_df)

# --- Theme Matching ---
st.markdown("""
<style>
    .stPlot { border-radius: 0.5rem; }
    .stAlert { font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)
