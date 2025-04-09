import streamlit as st
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

# --- App Config ---
st.set_page_config(
    page_title="📊 Etsy Inventory Pro", 
    layout="wide",
    page_icon="📊"
)
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

# --- Enhanced Plotly Visualization ---
def create_forecast_chart(actual_df, forecast_df):
    # Color palette
    colors = {
        'actual': '#4C78A8',
        'forecast': '#E45756',
        'confidence': 'rgba(228, 87, 86, 0.1)',
        'today': '#2D3A4E'
    }
    
    fig = go.Figure()
    
    # Actual sales (markers + line)
    fig.add_trace(go.Scatter(
        x=actual_df['date'],
        y=actual_df['units_sold'],
        mode='markers+lines',
        name='ACTUAL SALES',
        marker=dict(
            color=colors['actual'],
            size=8,
            opacity=0.8,
            line=dict(width=1, color='white')
        ),
        line=dict(
            color=colors['actual'], 
            width=1.5,
            dash='dot'),
        hovertemplate='<b>%{x|%b %d %Y}</b><br>%{y} units<extra></extra>'
    ))
    
    # Forecast (smooth line)
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['yhat'],
        mode='lines',
        name='FORECAST',
        line=dict(
            color=colors['forecast'],
            width=3,
            shape='spline'),
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
        line=dict(
            color=colors['today'],
            width=2,
            dash='dash'),
        annotation=dict(
            text=" TODAY",
            font=dict(size=10, color=colors['today']),
            bgcolor="white",
            borderpad=3)
    )
    
    # Layout
    fig.update_layout(
        title='<b>SALES FORECAST & INVENTORY PROJECTION</b>',
        title_font=dict(size=18, family="Arial"),
        xaxis=dict(
            title='DATE',
            gridcolor='rgba(200,200,200,0.2)',
            showline=True,
            linecolor='lightgray',
            tickformat="%b %d<br>%Y"),
        yaxis=dict(
            title='UNITS SOLD',
            gridcolor='rgba(200,200,200,0.2)'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            bordercolor='lightgray'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5),
        margin=dict(l=20, r=20, t=80, b=20),
        height=500
    )
    
    return fig

# --- Forecasting Logic ---
def run_forecast(product_df, current_stock, safety_stock, lead_time):
    model = Prophet(
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative'
    )
    model.fit(product_df.rename(columns={'date':'ds', 'units_sold':'y'}))
    future = model.make_future_dataframe(periods=180)
    forecast = model.predict(future)
    
    avg_daily = forecast['yhat'].mean()
    
    return {
        'forecast': forecast,
        'avg_daily': round(avg_daily, 1),
        'avg_monthly': round(avg_daily * 30),
        'reorder_point': round((avg_daily * lead_time) + safety_stock),
        'order_qty': max(round(avg_daily * lead_time * 1.5), 10),
        'stockout_date': (datetime.now() + timedelta(days=current_stock/avg_daily)).strftime('%b %d')
    }

# --- Main App ---
uploaded_file = st.file_uploader("📤 Upload Sales CSV", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    # Product selection
    col1, col2 = st.columns([3, 1])
    with col1:
        product = st.selectbox("SELECT PRODUCT", df['product'].unique())
    with col2:
        st.metric("Total Products", len(df['product'].unique()))
    
    product_df = df[df['product'] == product]
    
    # Inventory controls
    with st.expander("⚙️ INVENTORY SETTINGS", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            current_stock = st.number_input("CURRENT STOCK (UNITS)", min_value=0, value=50)
        with c2:
            safety_stock = st.number_input("SAFETY STOCK (UNITS)", min_value=0, value=10)
        with c3:
            lead_time = st.number_input("LEAD TIME (DAYS)", min_value=1, value=7)
    
    # Run forecast
    results = run_forecast(product_df, current_stock, safety_stock, lead_time)
    
    # Dashboard
    st.plotly_chart(
        create_forecast_chart(product_df, results['forecast']), 
        use_container_width=True
    )
    
    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Avg Daily Sales", f"{results['avg_daily']} units")
    m2.metric("Projected Monthly", f"{results['avg_monthly']} units")
    m3.metric("Reorder Point", f"{results['reorder_point']} units")
    
    # Alerts
    if current_stock <= results['reorder_point']:
        st.error(f"""
        🚨 **URGENT REORDER NEEDED**  
        - Suggested Quantity: **{results['order_qty']} units**  
        - Projected Stockout: **{results['stockout_date']}**
        """)
    else:
        st.success(f"""
        ✅ **INVENTORY HEALTHY**  
        - Current Stock Lasts: **{(current_stock - results['reorder_point']) / results['avg_daily']:.0f} days**  
        - Suggested Order Date: **{(datetime.now() + timedelta(days=(current_stock - results['reorder_point']) / results['avg_daily'])).strftime('%b %d')}**
        """)

else:
    st.info("ℹ️ Please upload a CSV with columns: date, units_sold, product")
    if st.button("📥 Download Sample CSV"):
        sample_data = pd.DataFrame({
            'date': pd.date_range(end=datetime.today(), periods=30).strftime('%Y-%m-%d'),
            'units_sold': np.random.randint(5, 20, 30),
            'product': "Lavender Essential Oil"
        }).to_csv(index=False)
        st.download_button(
            label="⬇️ Download Now",
            data=sample_data,
            file_name="sample_sales_data.csv",
            mime="text/csv"
        )
