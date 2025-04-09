import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from matplotlib import dates as mdates

# --- App Setup ---
st.set_page_config(page_title="📊 Sales Visualizer", layout="wide")
st.title("📊 Actual vs Forecasted Sales")

# --- Smart Data Processing ---
def process_data(df):
    """Flexibly handles column names and converts dates"""
    # Auto-detect date column (case insensitive)
    date_col = next((col for col in df.columns if 'date' in col.lower()), None)
    
    if date_col is None:
        st.error("❌ No date column found. Please include a column named 'date'")
        st.stop()
    
    try:
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
        return df.rename(columns={date_col: 'date'})  # Standardize to 'date'
    except Exception as e:
        st.error(f"❌ Date conversion failed: {str(e)}")
        st.stop()

# --- Sample Data Generator ---
def generate_sample_data():
    dates = pd.date_range(start="2024-01-01", periods=10)
    products = ["Blue T-Shirt", "White T-Shirt"]
    return pd.DataFrame([{
        "date": date.strftime("%Y-%m-%d"),
        "units_sold": 10 + (i % 3) + (hash(product) % 5),
        "product": product
    } for product in products for i, date in enumerate(dates)])

# --- Main App ---
uploaded_file = st.file_uploader("Upload sales CSV", type=["csv"])

try:
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Loaded {len(df)} rows")
        df = process_data(df)
    else:
        df = process_data(generate_sample_data())
        st.info("ℹ️ Using sample data. Columns: date, units_sold, product")
        
except Exception as e:
    st.error(f"❌ Data loading failed: {str(e)}")
    st.stop()

# --- Plotting Function ---
def plot_actual_vs_forecast(actual, forecast, product_name):
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Actual data (blue solid line)
    ax.plot(actual['ds'], actual['y'], 
            'b-', linewidth=2, label='Actual Sales', marker='o')
    
    # Forecast (white dashed line)
    ax.plot(forecast['ds'], forecast['yhat'], 
            'w--', linewidth=2, label='Forecast')
    
    # Formatting
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.set_title(f"{product_name} Sales")
    ax.legend()
    ax.grid(True, linestyle=':', alpha=0.3)
    
    # Dark theme styling
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    
    return fig

# --- Forecasting ---
if 'product' not in df.columns:
    st.error("❌ Missing 'product' column")
else:
    products = df['product'].unique()
    selected_products = st.multiselect("Select products", products, default=products[:1])
    
    for product in selected_products:
        st.subheader(product)
        product_df = df[df['product'] == product]
        
        try:
            # Prepare Prophet data
            train_df = product_df.rename(columns={'date':'ds', 'units_sold':'y'})[['ds','y']]
            
            # Model and forecast
            model = Prophet(weekly_seasonality=True)
            model.fit(train_df)
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            
            # Plot
            st.pyplot(plot_actual_vs_forecast(train_df, forecast, product))
            
            # Show raw data
            with st.expander("📋 View raw data"):
                st.dataframe(product_df)
                
        except Exception as e:
            st.error(f"⚠️ Forecast failed for {product}: {str(e)}")

# --- CSV Template Download ---
st.download_button(
    label="📥 Download CSV Template",
    data=generate_sample_data().to_csv(index=False),
    file_name="sales_template.csv",
    mime="text/csv"
)
