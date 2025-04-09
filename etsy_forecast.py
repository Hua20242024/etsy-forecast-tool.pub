# MUST BE FIRST COMMAND
import streamlit as st
st.set_page_config(
    page_title="📊 Etsy Inventory Pro", 
    layout="wide",
    page_icon="📊"
)

# Rest of imports
import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
import plotly.graph_objects as go

# --- Streamlit Style Setup ---
st.markdown("""
<style>
    .stPlotlyChart {
        border: 1px solid #f0f2f6;
        border-radius: 8px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- App Title ---
st.title("📊 Professional Inventory Dashboard")

# --- Data Processing ---
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
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
        st.error(f"❌ Data Error: {str(e)}")
        st.stop()

# --- Fixed Plotly Visualization ---
def create_forecast_chart(actual_df, forecast_df):
    fig = go.Figure()
    
    # Convert datetime to timestamp for vline
    today_timestamp = datetime.now().timestamp() * 1000
    
    # Actual sales
    fig.add_trace(go.Scatter(
        x=actual_df['date'],
        y=actual_df['units_sold'],
        mode='markers+lines',
        name='Actual Sales',
        line=dict(color='#636EFA', dash='dot')
    ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['yhat'],
        mode='lines',
        name='Forecast',
        line=dict(color='#FF7F0E')
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['yhat_upper'],
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['yhat_lower'],
        fill='tonexty',
        fillcolor='rgba(255, 127, 14, 0.2)',
        line=dict(width=0),
        name='Confidence'
    ))
    
    # Today's line (using timestamp)
    fig.add_vline(
        x=today_timestamp,
        line_dash="dash",
        line_color="gray",
        annotation_text="Today"
    )
    
    fig.update_layout(
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

# --- Forecasting Logic ---
def run_forecast(product_df, current_stock, safety_stock, lead_time):
    model = Prophet(weekly_seasonality=True)
    model.fit(product_df.rename(columns={'date':'ds', 'units_sold':'y'}))
    future = model.make_future_dataframe(periods=180)
    forecast = model.predict(future)
    
    avg_daily = forecast['yhat'].mean()
    reorder_point = (avg_daily * lead_time) + safety_stock
    
    return {
        'forecast': forecast,
        'avg_daily': round(avg_daily, 1),
        'reorder_point': round(reorder_point),
        'order_qty': max(round(avg_daily * lead_time * 1.5), 10)
    }

# --- Main App ---
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    product = st.selectbox("Select Product", df['product'].unique())
    product_df = df[df['product'] == product]
    
    current_stock = st.number_input("Current Stock", value=50)
    safety_stock = st.number_input("Safety Stock", value=10)
    lead_time = st.number_input("Lead Time (days)", value=7)
    
    results = run_forecast(product_df, current_stock, safety_stock, lead_time)
    
    st.plotly_chart(
        create_forecast_chart(product_df, results['forecast']),
        use_container_width=True
    )
    
    if current_stock <= results['reorder_point']:
        st.error(f"🚨 Order {results['order_qty']} units now!")
    else:
        st.success("✅ Inventory sufficient")

else:
    st.info("Please upload a CSV file")
