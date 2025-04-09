# MUST BE FIRST COMMAND
import streamlit as st
st.set_page_config(
    page_title="📊 Etsy Inventory Pro", 
    layout="wide",
    page_icon="📊"
)

# Rest of imports AFTER set_page_config
import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
import plotly.graph_objects as go

# --- Streamlit Style Setup ---
st.markdown("""
<style>
    .stPlotlyChart {
        border: 1px solid #f0f2f6 !important;
        border-radius: 8px !important;
        padding: 10px !important;
        background: white !important;
    }
    [data-testid="stMetric"] {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- App Title ---
st.title("📊 Professional Inventory Dashboard")

# --- Data Processing ---
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        
        # Flexible column detection (fixed syntax)
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

# --- Enhanced Plotly Visualization ---
def create_forecast_chart(actual_df, forecast_df):
    colors = {
        'actual': '#4C78A8',
        'forecast': '#E45756',
        'confidence': 'rgba(228, 87, 86, 0.1)',
        'today': '#2D3A4E'
    }
    
    fig = go.Figure()
    
    # Actual sales
    fig.add_trace(go.Scatter(
        x=actual_df['date'],
        y=actual_df['units_sold'],
        mode='markers+lines',
        name='ACTUAL SALES',
        marker=dict(color=colors['actual'], size=8, opacity=0.8, line=dict(width=1, color='white')),
        line=dict(color=colors['actual'], width=1.5, dash='dot'),
        hovertemplate='<b>%{x|%b %d %Y}</b><br>%{y} units<extra></extra>'
    ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['yhat'],
        mode='lines',
        name='FORECAST',
        line=dict(color=colors['forecast'], width=3, shape='spline'),
        hovertemplate='<b>%{x|%b %d %Y}</b><br>%{y:.1f} units<extra></extra>'
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'].tolist() + forecast_df['ds'].tolist()[::-1],
        y=forecast_df['yhat_upper'].tolist() + forecast_df['yhat_lower'].tolist()[::-1],
        fill='toself',
        fillcolor=colors['confidence'],
        line=dict(color='rgba(255,255,255,0)'),
        name='CONFIDENCE RANGE',
        hoverinfo='skip'
    ))
    
    # Today's line
    fig.add_vline(
        x=datetime.now(),
        line=dict(color=colors['today'], width=2, dash='dash'),
        annotation=dict(text=" TODAY", font=dict(size=10, color=colors['today']), bgcolor="white")
    )
    
    # Layout
    fig.update_layout(
        title='<b>SALES FORECAST & INVENTORY PROJECTION</b>',
        xaxis_title='DATE',
        yaxis_title='UNITS SOLD',
        plot_bgcolor='white',
        hovermode='x unified',
        height=500
    )
    
    return fig

# --- Forecasting Logic ---
def run_forecast(product_df, current_stock, safety_stock, lead_time):
    model = Prophet(weekly_seasonality=True, daily_seasonality=False)
    model.fit(product_df.rename(columns={'date':'ds', 'units_sold':'y'}))
    future = model.make_future_dataframe(periods=180)
    forecast = model.predict(future)
    
    avg_daily = forecast['yhat'].mean()
    reorder_point = (avg_daily * lead_time) + safety_stock
    days_remaining = max(0, (current_stock - reorder_point) / avg_daily) if avg_daily > 0 else 0
    
    return {
        'forecast': forecast,
        'avg_daily': round(avg_daily, 1),
        'reorder_point': round(reorder_point),
        'order_qty': max(round(avg_daily * lead_time * 1.5), 10),
        'stockout_date': (datetime.now() + timedelta(days=current_stock/avg_daily)).strftime('%b %d')
    }

# --- Main App ---
uploaded_file = st.file_uploader("📤 Upload Sales CSV", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    product = st.selectbox("SELECT PRODUCT", df['product'].unique())
    product_df = df[df['product'] == product]
    
    # Inventory controls
    with st.expander("⚙️ INVENTORY SETTINGS", expanded=True):
        current_stock = st.number_input("CURRENT STOCK (UNITS)", min_value=0, value=50)
        safety_stock = st.number_input("SAFETY STOCK (UNITS)", min_value=0, value=10)
        lead_time = st.number_input("LEAD TIME (DAYS)", min_value=1, value=7)
    
    # Run forecast
    results = run_forecast(product_df, current_stock, safety_stock, lead_time)
    
    # Display
    st.plotly_chart(create_forecast_chart(product_df, results['forecast']), use_container_width=True)
    
    # Metrics
    cols = st.columns(3)
    cols[0].metric("Avg Daily", f"{results['avg_daily']} units")
    cols[1].metric("Reorder Point", f"{results['reorder_point']} units")
    cols[2].metric("Order Qty", f"{results['order_qty']} units")
    
    # Alerts
    if current_stock <= results['reorder_point']:
        st.error(f"🚨 Stockout in ~{results['stockout_date']} | Order {results['order_qty']} units now")
    else:
        st.success(f"✅ Stock healthy until ~{results['stockout_date']}")

else:
    st.info("ℹ️ Please upload a CSV with columns: date, units_sold, product")
